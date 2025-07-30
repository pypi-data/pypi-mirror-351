import json
import re
import uuid
from typing import Dict, Optional, Callable

import nats
import os
import asyncio

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from codemie.logging import logger
from codemie.remote_tool import RemoteTool
import codemie.generated.proto.v1.service_pb2 as service_pb2


class NatsClient:

    session_id: str = str(uuid.uuid4())
    nc: Optional[nats.NATS]
    nats_config: dict
    nats_max_payload: str
    label: str
    tools: Dict[str, RemoteTool] = {}
    plugin_key: str
    timeout: int = 10

    _running: bool = False

    def __init__(self):
        self.plugin_key = os.getenv("PLUGIN_KEY")
        nats_uri = os.getenv("PLUGIN_ENGINE_URI")
        nats_options = {
            "user": self.plugin_key,
            "password": self.plugin_key,
            "max_reconnect_attempts": -1,
            "connect_timeout": 10
        }

        if nats_uri.startswith("tls://"):
            nats_options["tls_handshake_first"] = True

        self.nats_config = {
            "servers": [nats_uri],
            "options": nats_options
        }

        self.label = os.getenv("PLUGIN_LABEL") if os.getenv("PLUGIN_LABEL") else "default"
        self.nats_max_payload = os.environ.get("NATS_MAX_PAYLOAD", None)

    def add_tool(self, tool: BaseTool, tool_result_converter: Optional[Callable[[ToolMessage], str]] = None):
        if self._running:
            raise RuntimeError("Can't add new tools while running")
        self.tools[tool.name] = RemoteTool(
            tool=tool,
            subject=f"{self.plugin_key}.{self.session_id}.{self.label}.{tool.name}",
            tool_result_converter=tool_result_converter
        )

    async def connect(self):
        self.nc = await nats.connect(
            servers=self.nats_config["servers"],
            **self.nats_config["options"],
            error_cb=self._on_error,
            disconnected_cb=self._on_disconnect,
            reconnected_cb=self._on_reconnect,
            closed_cb=self._on_close
        )
        if self.nats_max_payload:
            separator = "=" * 50
            logger.info(f"\n{separator}\nSetting NATS max payload to {self.nats_max_payload} bytes")
            self.nc._max_payload = int(self.nats_max_payload)

        await self._subscribe()

    async def run(self):
        self._running = True
        try:
            await self._send_live_updates()
        except RuntimeError as e:
            if "already running" in str(e):
                logger.warning("Event loop is already running.")
                raise RuntimeError("Event loop is already running.")
            raise

    async def disconnect(self):
        self._running = False

        await self._publish(f"{self.plugin_key}.disconnected", self.session_id.encode("utf-8"))
        try:
            if self.nc:
                logger.info(f"Draining NATS connection")
                await self.nc.drain()
                self.nc = None
                logger.info(f"NATS connection drained")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def _publish(self, subject: str, payload: bytes):
        if not self.nc:
            raise RuntimeError("NATS client is not connected")
        
        try:
            await self.nc.publish(subject, payload)
        except Exception as e:
            logger.error(f"Error publishing message to subject {subject}: {str(e)}")
            raise

    async def _send_live_updates(self):
        while self._running:
            try:
                await self._send_live_update()
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                logger.info(f"Live updates were cancelled")
                break

    async def _send_live_update(self):
        await self._publish(f"{self.plugin_key}.live", self.session_id.encode("utf-8"))

    async def _on_error(self, e):
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"NATS error: {str(e)}\n{error_trace}")

    async def _on_disconnect(self):
        logger.warning(f"NATS disconnected")

    async def _on_reconnect(self):
        logger.info(f"NATS reconnected")

    async def _on_close(self):
        logger.info(f"NATS connection closed")
        self._running = False

    async def _subscribe(self):
        if not self.nc:
            raise RuntimeError("NATS client is not connected")

        await self.nc.subscribe(
            f"{self.plugin_key}.list",
            cb=self._handle_list_request
        )

        await self.nc.subscribe(
            f"{self.plugin_key}.{self.session_id}.{self.label}.*",
            cb=self._handle_tool_request
        )
        
        logger.info(f"Subscribed to NATS subjects, ready to serve {len(self.tools)} tools")
    
    async def _handle_list_request(self, msg):
        logger.info(f"Tool List request")
        await self.nc.publish(msg.reply, json.dumps(
            list(map(lambda tool: tool.tool_schema(), self.tools.values()))
        ).encode("utf-8"))

    async def _handle_tool_request(self, msg):
        pattern = '([^.]*)\\.([^.]*)\\.([^.]*)\\.([^.]*)'
        match = re.search(pattern, msg.subject, re.IGNORECASE)
        if not match:
            raise RuntimeError("Invalid subject " + msg.subject)

        plugin_key = match.group(1)
        session_id = match.group(2)
        label = match.group(3)
        tool_name = match.group(4)

        logger.info(f"Tool request for {tool_name}")
        if session_id != self.session_id:
            raise RuntimeError("Invalid session_id")

        if label != self.label:
            raise RuntimeError("Invalid label")

        if plugin_key != self.plugin_key:
            raise RuntimeError("Invalid plugin_key")

        if not tool_name in self.tools:
            raise RuntimeError("Invalid tool requested " + tool_name)

        tool: RemoteTool = self.tools[tool_name]

        request = service_pb2.ServiceRequest()
        request.ParseFromString(msg.data)
        if not request.IsInitialized() or request.meta.handler != service_pb2.Handler.RUN:
            raise RuntimeError("Invalid request")

        query = request.puppet_request.lc_tool.query
        response = service_pb2.ServiceResponse()
        response.meta.subject = msg.subject
        response.meta.handler = service_pb2.Handler.RUN
        response.meta.puppet = service_pb2.Puppet.LANGCHAIN_TOOL

        try:
            tool_response = await tool.execute_tool_with_timeout(query, self.timeout)
            converted_response = (
                tool.tool_result_converter(tool_response) if tool.tool_result_converter else str(tool_response)
            )
            response.puppet_response.lc_tool.result = converted_response
        except Exception as exc:
            separator = "!" * 50
            error_message = f"Tool '{tool_name}' got error: {exc}"
            logger.error(f"\n{separator}\n{error_message}\n{separator}", exc_info=True)
            response.puppet_response.lc_tool.error = error_message

        await self.nc.publish(msg.reply, response.SerializeToString())
    
    
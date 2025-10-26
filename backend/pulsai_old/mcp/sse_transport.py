"""
SSE (Server-Sent Events) Protocol Transport for MCP

Handles one-way streaming communication from MCP servers using SSE.
Combines SSE for server->client and HTTP POST for client->server.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, AsyncIterator, Optional
import time

import aiohttp

from .http_transport import HTTPTransport
from .protocols import MCPToolSchema, MCPToolResponse

log = logging.getLogger(__name__)


class SSETransport(HTTPTransport):
    """
    SSE protocol implementation for MCP
    
    Uses Server-Sent Events for real-time streaming from server,
    combined with HTTP POST for client requests.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SSE transport
        
        Config keys: Same as HTTPTransport, plus:
            - sse_endpoint: str - SSE endpoint path (default: "/v1/sse")
            - reconnect_interval: int - Reconnection interval in seconds (default: 5)
        """
        super().__init__(config)
        self.sse_endpoint = config.get("sse_endpoint", "/v1/sse")
        self.reconnect_interval = config.get("reconnect_interval", 5)
        self._sse_task: Optional[asyncio.Task] = None
        self._event_queue = asyncio.Queue()
        self._should_reconnect = True
        
    async def connect(self) -> bool:
        """Establish HTTP session and start SSE listener"""
        if not await super().connect():
            return False
        
        # Start SSE listener task
        self._should_reconnect = True
        self._sse_task = asyncio.create_task(self._sse_listener())
        
        log.info(f"SSE MCP client connected to {self.base_url}")
        return True
    
    async def disconnect(self) -> None:
        """Close SSE connection and HTTP session"""
        self._should_reconnect = False
        
        if self._sse_task:
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
        
        await super().disconnect()
        log.info("SSE MCP client disconnected")
    
    async def _sse_listener(self):
        """Background task to listen for SSE events"""
        while self._should_reconnect:
            try:
                await self._connect_sse()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.warning(f"SSE connection error: {e}")
                if self._should_reconnect:
                    await asyncio.sleep(self.reconnect_interval)
    
    async def _connect_sse(self):
        """Establish SSE connection and process events"""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        
        url = f"{self.base_url}{self.sse_endpoint}"
        headers = self._get_headers()
        headers["Accept"] = "text/event-stream"
        auth = self._get_auth()
        
        async with self.session.get(url, headers=headers, auth=auth) as resp:
            resp.raise_for_status()
            
            log.info("SSE connection established")
            
            async for line in resp.content:
                if not line:
                    continue
                
                line_str = line.decode().strip()
                
                # Parse SSE format
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    try:
                        event_data = json.loads(data_str)
                        await self._event_queue.put(event_data)
                    except json.JSONDecodeError as e:
                        log.warning(f"Invalid SSE JSON: {data_str}: {e}")
                
                elif line_str.startswith("event: "):
                    # Event type (can be used for filtering)
                    pass
                
                elif line_str.startswith("id: "):
                    # Event ID (can be used for resumption)
                    pass
    
    async def stream_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> AsyncIterator[str]:
        """Execute a tool with streaming response via SSE"""
        await self.ensure_connected()
        
        # Send request via HTTP POST
        request_data = {
            "tool": tool_name,
            "parameters": parameters,
            "stream": True
        }
        
        # Get a unique request ID
        request_id = f"req_{int(time.time() * 1000)}"
        request_data["request_id"] = request_id
        
        try:
            # Send request (fire and forget)
            response = await self._request("POST", "/v1/tools/execute", request_data)
            
            # Listen for SSE events matching this request
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    event = await asyncio.wait_for(
                        self._event_queue.get(),
                        timeout=1.0
                    )
                    
                    # Check if event is for our request
                    if event.get("request_id") == request_id:
                        if event.get("type") == "chunk":
                            yield event.get("data", "")
                        
                        elif event.get("type") == "done":
                            break
                        
                        elif event.get("type") == "error":
                            yield f"Error: {event.get('error')}"
                            break
                    
                    else:
                        # Put back events for other requests
                        await self._event_queue.put(event)
                        await asyncio.sleep(0.01)
                        
                except asyncio.TimeoutError:
                    # Check if deadline passed
                    if time.time() >= deadline:
                        break
                    continue
                    
        except Exception as e:
            yield f"Error: {str(e)}"


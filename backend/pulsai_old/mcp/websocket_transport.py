"""
WebSocket Protocol Transport for MCP

Handles bidirectional real-time communication with MCP servers via WebSocket.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, AsyncIterator, Optional
import time

import aiohttp
from aiohttp import WSMsgType

from .protocols import MCPProtocol, MCPToolSchema, MCPToolResponse

log = logging.getLogger(__name__)


class WebSocketTransport(MCPProtocol):
    """
    WebSocket protocol implementation for MCP
    
    Provides bidirectional real-time communication with MCP servers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize WebSocket transport
        
        Config keys:
            - url: str - WebSocket URL (ws:// or wss://)
            - auth_token: str - Authentication token (optional)
            - ping_interval: int - Heartbeat interval in seconds (default: 30)
            - ping_timeout: int - Heartbeat timeout in seconds (default: 10)
            - reconnect_interval: int - Reconnection interval in seconds (default: 5)
            - max_reconnect_attempts: int - Max reconnection attempts (default: 5)
        """
        super().__init__(config)
        self.url = config.get("url", "")
        self.auth_token = config.get("auth_token")
        self.ping_interval = config.get("ping_interval", 30)
        self.ping_timeout = config.get("ping_timeout", 10)
        self.reconnect_interval = config.get("reconnect_interval", 5)
        self.max_reconnect_attempts = config.get("max_reconnect_attempts", 5)
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._listener_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._response_queue = asyncio.Queue()
        self._request_id = 0
        self._should_reconnect = True
        
    async def connect(self) -> bool:
        """Establish WebSocket connection"""
        if self._connected and self.ws:
            return True
        
        try:
            # Create session if needed
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Prepare headers
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Connect WebSocket
            self.ws = await self.session.ws_connect(
                self.url,
                headers=headers,
                heartbeat=self.ping_interval,
                timeout=self.ping_timeout
            )
            
            self._connected = True
            log.info(f"WebSocket MCP client connected to {self.url}")
            
            # Start listener and ping tasks
            self._should_reconnect = True
            self._listener_task = asyncio.create_task(self._message_listener())
            self._ping_task = asyncio.create_task(self._ping_loop())
            
            return True
            
        except Exception as e:
            log.error(f"Failed to connect WebSocket: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close WebSocket connection"""
        self._should_reconnect = False
        
        # Cancel tasks
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
        
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        # Close session
        if self.session:
            await self.session.close()
            self.session = None
        
        self._connected = False
        log.info("WebSocket MCP client disconnected")
    
    async def _message_listener(self):
        """Background task to listen for WebSocket messages"""
        try:
            async for msg in self.ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._response_queue.put(data)
                    except json.JSONDecodeError as e:
                        log.warning(f"Invalid JSON from WebSocket: {msg.data}: {e}")
                
                elif msg.type == WSMsgType.ERROR:
                    log.error(f"WebSocket error: {self.ws.exception()}")
                    break
                
                elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING):
                    log.info("WebSocket connection closed")
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"WebSocket listener error: {e}")
    
    async def _ping_loop(self):
        """Background task to send periodic pings"""
        try:
            while self._connected and self.ws:
                await asyncio.sleep(self.ping_interval)
                if self.ws:
                    await self.ws.ping()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.warning(f"Ping loop error: {e}")
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request and wait for response"""
        if not self.ws:
            raise RuntimeError("WebSocket not connected")
        
        # Add request ID
        self._request_id += 1
        request["id"] = self._request_id
        
        # Send request
        await self.ws.send_json(request)
        
        # Wait for response with matching ID
        timeout = 30
        deadline = asyncio.get_event_loop().time() + timeout
        
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError()
            
            try:
                response = await asyncio.wait_for(
                    self._response_queue.get(),
                    timeout=remaining
                )
                
                if response.get("id") == self._request_id:
                    return response
                else:
                    # Put back responses for other requests
                    await self._response_queue.put(response)
                    await asyncio.sleep(0.01)
                    
            except asyncio.TimeoutError:
                raise TimeoutError(f"WebSocket request timed out after {timeout}s")
    
    async def health_check(self) -> bool:
        """Check if WebSocket is connected and responsive"""
        if not self._connected or not self.ws:
            return False
        
        if self.ws.closed:
            self._connected = False
            return False
        
        try:
            # Try a simple ping
            await self.ws.ping()
            return True
        except Exception:
            return False
    
    async def list_tools(self) -> List[MCPToolSchema]:
        """List available tools from the MCP server"""
        await self.ensure_connected()
        
        request = {
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")
        
        tools_data = response.get("result", {}).get("tools", [])
        return [MCPToolSchema(**tool) for tool in tools_data]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> MCPToolResponse:
        """Execute a tool on the MCP server"""
        await self.ensure_connected()
        
        start_time = time.time()
        
        request = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        try:
            response = await self._send_request(request)
            execution_time = time.time() - start_time
            
            if "error" in response:
                return MCPToolResponse(
                    success=False,
                    error=str(response["error"]),
                    execution_time=execution_time
                )
            
            result = response.get("result")
            return MCPToolResponse(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return MCPToolResponse(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def stream_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> AsyncIterator[str]:
        """Execute a tool with streaming response"""
        await self.ensure_connected()
        
        self._request_id += 1
        request_id = self._request_id
        
        request = {
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters,
                "stream": True
            }
        }
        
        try:
            # Send request
            await self.ws.send_json(request)
            
            # Listen for streaming responses
            deadline = time.time() + timeout
            while time.time() < deadline:
                try:
                    response = await asyncio.wait_for(
                        self._response_queue.get(),
                        timeout=1.0
                    )
                    
                    if response.get("id") == request_id:
                        if response.get("type") == "chunk":
                            yield response.get("data", "")
                        
                        elif response.get("type") == "done":
                            break
                        
                        elif response.get("type") == "error":
                            yield f"Error: {response.get('error')}"
                            break
                    
                    else:
                        # Put back responses for other requests
                        await self._response_queue.put(response)
                        await asyncio.sleep(0.01)
                        
                except asyncio.TimeoutError:
                    if time.time() >= deadline:
                        break
                    continue
                    
        except Exception as e:
            yield f"Error: {str(e)}"


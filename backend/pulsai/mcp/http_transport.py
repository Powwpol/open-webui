"""
HTTP/HTTPS Protocol Transport for MCP

Handles communication with MCP servers via HTTP REST API endpoints.
Supports authentication, retry logic, and circuit breaker pattern.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, AsyncIterator, Optional
from enum import Enum
import time

import aiohttp
from aiohttp import ClientTimeout, ClientSession

from .protocols import MCPProtocol, MCPToolSchema, MCPToolResponse

log = logging.getLogger(__name__)


class AuthType(str, Enum):
    """Supported authentication types"""
    NONE = "none"
    BEARER = "bearer"
    API_KEY = "api_key"
    BASIC = "basic"


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class HTTPTransport(MCPProtocol):
    """
    HTTP/HTTPS protocol implementation for MCP
    
    Communicates with MCP servers via REST API endpoints.
    Includes retry logic and circuit breaker for resilience.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize HTTP transport
        
        Config keys:
            - url: str - Base URL of MCP server
            - auth_type: str - Authentication type (none, bearer, api_key, basic)
            - token: str - Bearer token or API key
            - username: str - Username for basic auth
            - password: str - Password for basic auth
            - timeout: int - Request timeout in seconds (default: 30)
            - max_retries: int - Maximum retry attempts (default: 3)
            - retry_delay: float - Delay between retries in seconds (default: 1.0)
            - headers: Dict[str, str] - Custom headers
        """
        super().__init__(config)
        self.session: Optional[ClientSession] = None
        self.base_url = config.get("url", "").rstrip("/")
        self.auth_type = AuthType(config.get("auth_type", "none"))
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        
        # Circuit breaker
        self.circuit_state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = 5
        self.circuit_open_time: Optional[float] = None
        self.circuit_timeout = 60  # seconds
        
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add custom headers
        custom_headers = self.config.get("headers", {})
        headers.update(custom_headers)
        
        # Add authentication
        if self.auth_type == AuthType.BEARER:
            token = self.config.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
                
        elif self.auth_type == AuthType.API_KEY:
            api_key = self.config.get("token")
            if api_key:
                headers["X-API-Key"] = api_key
        
        return headers
    
    def _get_auth(self) -> Optional[aiohttp.BasicAuth]:
        """Get basic auth credentials if configured"""
        if self.auth_type == AuthType.BASIC:
            username = self.config.get("username")
            password = self.config.get("password")
            if username and password:
                return aiohttp.BasicAuth(username, password)
        return None
    
    def _check_circuit(self) -> bool:
        """Check circuit breaker state"""
        if self.circuit_state == CircuitState.CLOSED:
            return True
        
        if self.circuit_state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.circuit_open_time:
                elapsed = time.time() - self.circuit_open_time
                if elapsed >= self.circuit_timeout:
                    log.info("Circuit breaker entering half-open state")
                    self.circuit_state = CircuitState.HALF_OPEN
                    return True
            return False
        
        if self.circuit_state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def _record_success(self):
        """Record successful request"""
        self.failure_count = 0
        if self.circuit_state == CircuitState.HALF_OPEN:
            log.info("Circuit breaker closing (recovery successful)")
            self.circuit_state = CircuitState.CLOSED
    
    def _record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        
        if self.circuit_state == CircuitState.HALF_OPEN:
            log.warning("Circuit breaker opening (recovery failed)")
            self.circuit_state = CircuitState.OPEN
            self.circuit_open_time = time.time()
            
        elif self.failure_count >= self.failure_threshold:
            log.warning(f"Circuit breaker opening ({self.failure_count} failures)")
            self.circuit_state = CircuitState.OPEN
            self.circuit_open_time = time.time()
    
    async def connect(self) -> bool:
        """Establish HTTP client session"""
        if self._connected and self.session:
            return True
        
        try:
            timeout = ClientTimeout(total=self.timeout)
            self.session = ClientSession(timeout=timeout)
            self._connected = True
            log.info(f"HTTP MCP client connected to {self.base_url}")
            return True
            
        except Exception as e:
            log.error(f"Failed to create HTTP session: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close HTTP client session"""
        if self.session:
            await self.session.close()
            self.session = None
        self._connected = False
        log.info("HTTP MCP client disconnected")
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retry: int = 0
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        
        # Check circuit breaker
        if not self._check_circuit():
            raise RuntimeError("Circuit breaker is open, requests blocked")
        
        await self.ensure_connected()
        
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        auth = self._get_auth()
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers, auth=auth) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    self._record_success()
                    return result
            
            elif method == "POST":
                async with self.session.post(url, json=data, headers=headers, auth=auth) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    self._record_success()
                    return result
            
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except Exception as e:
            self._record_failure()
            
            # Retry logic
            if retry < self.max_retries:
                log.warning(f"HTTP request failed (attempt {retry + 1}/{self.max_retries}): {e}")
                await asyncio.sleep(self.retry_delay * (2 ** retry))  # Exponential backoff
                return await self._request(method, endpoint, data, retry + 1)
            else:
                log.error(f"HTTP request failed after {self.max_retries} retries: {e}")
                raise
    
    async def health_check(self) -> bool:
        """Check if the MCP server is healthy"""
        try:
            # Try to get server info or list tools
            await self._request("GET", "/health")
            return True
        except Exception as e:
            log.debug(f"Health check failed: {e}")
            return False
    
    async def list_tools(self) -> List[MCPToolSchema]:
        """List available tools from the MCP server"""
        response = await self._request("GET", "/v1/tools")
        
        tools_data = response.get("tools", [])
        return [MCPToolSchema(**tool) for tool in tools_data]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> MCPToolResponse:
        """Execute a tool on the MCP server"""
        start_time = time.time()
        
        request_data = {
            "tool": tool_name,
            "parameters": parameters
        }
        
        try:
            response = await self._request("POST", "/v1/tools/execute", request_data)
            execution_time = time.time() - start_time
            
            if response.get("success", False):
                return MCPToolResponse(
                    success=True,
                    result=response.get("result"),
                    execution_time=execution_time
                )
            else:
                return MCPToolResponse(
                    success=False,
                    error=response.get("error", "Unknown error"),
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
        
        if not self.session:
            raise RuntimeError("HTTP session not initialized")
        
        url = f"{self.base_url}/v1/tools/stream"
        headers = self._get_headers()
        auth = self._get_auth()
        
        request_data = {
            "tool": tool_name,
            "parameters": parameters
        }
        
        try:
            async with self.session.post(
                url,
                json=request_data,
                headers=headers,
                auth=auth
            ) as resp:
                resp.raise_for_status()
                
                # Read streaming response
                async for line in resp.content:
                    if line:
                        try:
                            # Try to parse as JSON (SSE format)
                            line_str = line.decode().strip()
                            if line_str.startswith("data: "):
                                data = json.loads(line_str[6:])
                                yield json.dumps(data)
                            else:
                                yield line_str
                        except:
                            yield line.decode()
                            
        except Exception as e:
            yield f"Error: {str(e)}"


"""
MCP Protocol Base Interface and Protocol Type Definitions
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator
from pydantic import BaseModel
import asyncio
from datetime import datetime


class ProtocolType(str, Enum):
    """Supported MCP protocol types"""
    STDIO = "stdio"
    HTTP = "http"
    HTTPS = "https"
    DOCKER = "docker"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPToolSchema(BaseModel):
    """Schema for an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = []


class MCPServerInfo(BaseModel):
    """Information about an MCP server"""
    id: str
    name: str
    protocol: ProtocolType
    enabled: bool
    health_status: str = "unknown"  # healthy, unhealthy, unknown
    last_check: Optional[datetime] = None
    tools: List[MCPToolSchema] = []


class MCPToolRequest(BaseModel):
    """Request to execute an MCP tool"""
    tool_name: str
    parameters: Dict[str, Any] = {}
    timeout: int = 30


class MCPToolResponse(BaseModel):
    """Response from an MCP tool execution"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class MCPProtocol(ABC):
    """
    Abstract base class for MCP protocol implementations
    
    All protocol transports must implement these methods to provide
    a consistent interface for the MCP client.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the protocol with configuration
        
        Args:
            config: Protocol-specific configuration dictionary
        """
        self.config = config
        self._connected = False
        self._connection_lock = asyncio.Lock()
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the MCP server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """
        Close connection to the MCP server
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the MCP server is healthy and responsive
        
        Returns:
            bool: True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_tools(self) -> List[MCPToolSchema]:
        """
        List all available tools from the MCP server
        
        Returns:
            List of tool schemas
        """
        pass
    
    @abstractmethod
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> MCPToolResponse:
        """
        Execute a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            timeout: Execution timeout in seconds
            
        Returns:
            MCPToolResponse with result or error
        """
        pass
    
    @abstractmethod
    async def stream_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> AsyncIterator[str]:
        """
        Execute a tool with streaming response
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            timeout: Execution timeout in seconds
            
        Yields:
            Chunks of the response
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if protocol is currently connected"""
        return self._connected
    
    async def ensure_connected(self) -> bool:
        """
        Ensure the protocol is connected, connecting if necessary
        
        Returns:
            bool: True if connected, False otherwise
        """
        async with self._connection_lock:
            if not self._connected:
                return await self.connect()
            return True


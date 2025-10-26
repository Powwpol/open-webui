"""
MCP Configuration Validation

Pydantic models for validating MCP server configurations.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from .protocols import ProtocolType


class StdioConfig(BaseModel):
    """Configuration for stdio protocol"""
    command: str = Field(..., description="Command to execute")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    cwd: Optional[str] = Field(None, description="Working directory")


class HTTPConfig(BaseModel):
    """Configuration for HTTP/HTTPS protocol"""
    url: str = Field(..., description="Base URL of MCP server")
    auth_type: str = Field(default="none", description="Authentication type")
    token: Optional[str] = Field(None, description="Bearer token or API key")
    username: Optional[str] = Field(None, description="Username for basic auth")
    password: Optional[str] = Field(None, description="Password for basic auth")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    
    @validator("auth_type")
    def validate_auth_type(cls, v):
        allowed = ["none", "bearer", "api_key", "basic"]
        if v not in allowed:
            raise ValueError(f"auth_type must be one of {allowed}")
        return v


class DockerConfig(BaseModel):
    """Configuration for Docker protocol"""
    image: str = Field(..., description="Docker image name")
    ports: Dict[str, str] = Field(default_factory=dict, description="Port mappings")
    volumes: Dict[str, str] = Field(default_factory=dict, description="Volume mounts")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    network: Optional[str] = Field(None, description="Docker network name")
    container_name: Optional[str] = Field(None, description="Container name")
    auto_pull: bool = Field(default=True, description="Auto-pull image if not found")
    auto_remove: bool = Field(default=True, description="Auto-remove container on stop")
    mem_limit: Optional[str] = Field(None, description="Memory limit (e.g., '512m')")
    cpu_limit: Optional[float] = Field(None, description="CPU limit (e.g., 1.0 for 1 CPU)")
    
    # Include HTTP config for communication with container
    auth_type: str = Field(default="none")
    token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    headers: Dict[str, str] = Field(default_factory=dict)


class SSEConfig(HTTPConfig):
    """Configuration for SSE protocol (extends HTTP)"""
    sse_endpoint: str = Field(default="/v1/sse", description="SSE endpoint path")
    reconnect_interval: int = Field(default=5, description="Reconnection interval in seconds")


class WebSocketConfig(BaseModel):
    """Configuration for WebSocket protocol"""
    url: str = Field(..., description="WebSocket URL (ws:// or wss://)")
    auth_token: Optional[str] = Field(None, description="Authentication token")
    ping_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    ping_timeout: int = Field(default=10, description="Heartbeat timeout in seconds")
    reconnect_interval: int = Field(default=5, description="Reconnection interval")
    max_reconnect_attempts: int = Field(default=5, description="Max reconnection attempts")


class MCPServerConfig(BaseModel):
    """Complete MCP server configuration"""
    id: str = Field(..., description="Unique server identifier")
    name: str = Field(..., description="Human-readable server name")
    description: Optional[str] = Field(None, description="Server description")
    protocol: ProtocolType = Field(..., description="Protocol type")
    config: Dict[str, Any] = Field(..., description="Protocol-specific configuration")
    enabled: bool = Field(default=True, description="Whether server is enabled")
    tags: List[str] = Field(default_factory=list, description="Server tags")
    
    @validator("config")
    def validate_config(cls, v, values):
        """Validate protocol-specific configuration"""
        if "protocol" not in values:
            return v
        
        protocol = values["protocol"]
        
        try:
            if protocol == ProtocolType.STDIO:
                StdioConfig(**v)
            elif protocol in (ProtocolType.HTTP, ProtocolType.HTTPS):
                HTTPConfig(**v)
            elif protocol == ProtocolType.DOCKER:
                DockerConfig(**v)
            elif protocol == ProtocolType.SSE:
                SSEConfig(**v)
            elif protocol == ProtocolType.WEBSOCKET:
                WebSocketConfig(**v)
        except Exception as e:
            raise ValueError(f"Invalid {protocol} configuration: {e}")
        
        return v
    
    class Config:
        use_enum_values = True


class MCPServersConfig(BaseModel):
    """Configuration for multiple MCP servers"""
    mcp_servers: List[MCPServerConfig] = Field(default_factory=list)


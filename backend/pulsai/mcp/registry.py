"""
MCP Server Registry

Manages registration and lifecycle of MCP server instances.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .protocols import MCPProtocol, MCPServerInfo, ProtocolType
from .stdio_transport import StdioTransport
from .http_transport import HTTPTransport
from .docker_transport import DockerTransport
from .sse_transport import SSETransport
from .websocket_transport import WebSocketTransport
from .validation import MCPServerConfig

log = logging.getLogger(__name__)


class MCPRegistry:
    """
    Registry for MCP servers
    
    Manages MCP server instances, their lifecycle, and health status.
    """
    
    def __init__(self):
        self._servers: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
        
    def _create_transport(self, config: MCPServerConfig) -> MCPProtocol:
        """Create appropriate transport instance based on protocol"""
        protocol = config.protocol
        transport_config = config.config
        
        if protocol == ProtocolType.STDIO:
            return StdioTransport(transport_config)
        
        elif protocol in (ProtocolType.HTTP, ProtocolType.HTTPS):
            return HTTPTransport(transport_config)
        
        elif protocol == ProtocolType.DOCKER:
            return DockerTransport(transport_config)
        
        elif protocol == ProtocolType.SSE:
            return SSETransport(transport_config)
        
        elif protocol == ProtocolType.WEBSOCKET:
            return WebSocketTransport(transport_config)
        
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    async def register(self, config: MCPServerConfig) -> bool:
        """
        Register a new MCP server
        
        Args:
            config: Server configuration
            
        Returns:
            True if registration successful, False otherwise
        """
        async with self._lock:
            server_id = config.id
            
            if server_id in self._servers:
                log.warning(f"Server {server_id} already registered")
                return False
            
            try:
                # Create transport instance
                transport = self._create_transport(config)
                
                # Store server info
                self._servers[server_id] = {
                    "config": config,
                    "transport": transport,
                    "registered_at": datetime.utcnow(),
                    "last_health_check": None,
                    "health_status": "unknown",
                    "tools": [],
                    "enabled": config.enabled
                }
                
                log.info(f"Registered MCP server: {server_id} ({config.protocol})")
                
                # Connect if enabled
                if config.enabled:
                    await self.connect(server_id)
                
                return True
                
            except Exception as e:
                log.error(f"Failed to register server {server_id}: {e}")
                return False
    
    async def unregister(self, server_id: str) -> bool:
        """
        Unregister an MCP server
        
        Args:
            server_id: Server identifier
            
        Returns:
            True if unregistration successful, False otherwise
        """
        async with self._lock:
            if server_id not in self._servers:
                log.warning(f"Server {server_id} not found")
                return False
            
            try:
                # Disconnect first
                await self.disconnect(server_id)
                
                # Remove from registry
                del self._servers[server_id]
                
                log.info(f"Unregistered MCP server: {server_id}")
                return True
                
            except Exception as e:
                log.error(f"Failed to unregister server {server_id}: {e}")
                return False
    
    async def connect(self, server_id: str) -> bool:
        """Connect to an MCP server"""
        server = self._servers.get(server_id)
        if not server:
            log.warning(f"Server {server_id} not found")
            return False
        
        transport = server["transport"]
        
        try:
            if await transport.connect():
                server["health_status"] = "healthy"
                server["last_health_check"] = datetime.utcnow()
                
                # Load tools
                try:
                    tools = await transport.list_tools()
                    server["tools"] = [tool.dict() for tool in tools]
                    log.info(f"Server {server_id}: Loaded {len(tools)} tools")
                except Exception as e:
                    log.warning(f"Failed to load tools from {server_id}: {e}")
                
                return True
            else:
                server["health_status"] = "unhealthy"
                return False
                
        except Exception as e:
            log.error(f"Failed to connect to server {server_id}: {e}")
            server["health_status"] = "unhealthy"
            return False
    
    async def disconnect(self, server_id: str) -> bool:
        """Disconnect from an MCP server"""
        server = self._servers.get(server_id)
        if not server:
            return False
        
        transport = server["transport"]
        
        try:
            await transport.disconnect()
            server["health_status"] = "disconnected"
            return True
        except Exception as e:
            log.error(f"Failed to disconnect from server {server_id}: {e}")
            return False
    
    async def health_check(self, server_id: str) -> bool:
        """Perform health check on an MCP server"""
        server = self._servers.get(server_id)
        if not server:
            return False
        
        transport = server["transport"]
        
        try:
            healthy = await transport.health_check()
            server["health_status"] = "healthy" if healthy else "unhealthy"
            server["last_health_check"] = datetime.utcnow()
            return healthy
        except Exception as e:
            log.debug(f"Health check failed for {server_id}: {e}")
            server["health_status"] = "unhealthy"
            server["last_health_check"] = datetime.utcnow()
            return False
    
    async def health_check_all(self):
        """Perform health check on all registered servers"""
        for server_id in list(self._servers.keys()):
            if self._servers[server_id]["enabled"]:
                await self.health_check(server_id)
    
    def get_server(self, server_id: str) -> Optional[MCPServerInfo]:
        """Get information about a specific server"""
        server = self._servers.get(server_id)
        if not server:
            return None
        
        config = server["config"]
        
        return MCPServerInfo(
            id=config.id,
            name=config.name,
            protocol=config.protocol,
            enabled=server["enabled"],
            health_status=server["health_status"],
            last_check=server["last_health_check"],
            tools=[MCPToolSchema(**tool) for tool in server["tools"]]
        )
    
    def list_servers(self, enabled_only: bool = False) -> List[MCPServerInfo]:
        """List all registered servers"""
        servers = []
        for server_id in self._servers:
            server = self._servers[server_id]
            if enabled_only and not server["enabled"]:
                continue
            
            info = self.get_server(server_id)
            if info:
                servers.append(info)
        
        return servers
    
    def get_transport(self, server_id: str) -> Optional[MCPProtocol]:
        """Get transport instance for a server"""
        server = self._servers.get(server_id)
        if server:
            return server["transport"]
        return None
    
    async def enable_server(self, server_id: str) -> bool:
        """Enable a server and connect"""
        server = self._servers.get(server_id)
        if not server:
            return False
        
        server["enabled"] = True
        return await self.connect(server_id)
    
    async def disable_server(self, server_id: str) -> bool:
        """Disable a server and disconnect"""
        server = self._servers.get(server_id)
        if not server:
            return False
        
        server["enabled"] = False
        return await self.disconnect(server_id)


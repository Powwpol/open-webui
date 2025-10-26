"""
MCP Client

Unified client interface for executing tools across all registered MCP servers.
"""

import logging
from typing import Dict, Any, List, Optional, AsyncIterator

from .protocols import MCPToolRequest, MCPToolResponse, MCPToolSchema
from .registry import MCPRegistry

log = logging.getLogger(__name__)


class MCPClient:
    """
    Unified MCP client
    
    Provides a simple interface to execute tools across all registered MCP servers.
    """
    
    def __init__(self, registry: MCPRegistry):
        self.registry = registry
    
    async def list_all_tools(self, enabled_only: bool = True) -> Dict[str, List[MCPToolSchema]]:
        """
        List all tools from all registered servers
        
        Args:
            enabled_only: Only include enabled servers
            
        Returns:
            Dictionary mapping server_id to list of tools
        """
        all_tools = {}
        
        for server_info in self.registry.list_servers(enabled_only=enabled_only):
            if server_info.tools:
                all_tools[server_info.id] = server_info.tools
        
        return all_tools
    
    async def find_tool(self, tool_name: str) -> Optional[tuple[str, MCPToolSchema]]:
        """
        Find a tool by name across all servers
        
        Args:
            tool_name: Name of the tool to find
            
        Returns:
            Tuple of (server_id, tool_schema) if found, None otherwise
        """
        all_tools = await self.list_all_tools()
        
        for server_id, tools in all_tools.items():
            for tool in tools:
                if tool.name == tool_name:
                    return (server_id, tool)
        
        return None
    
    async def execute_tool(
        self,
        server_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> MCPToolResponse:
        """
        Execute a tool on a specific server
        
        Args:
            server_id: Server identifier
            tool_name: Name of the tool
            parameters: Tool parameters
            timeout: Execution timeout
            
        Returns:
            MCPToolResponse with result or error
        """
        transport = self.registry.get_transport(server_id)
        
        if not transport:
            return MCPToolResponse(
                success=False,
                error=f"Server not found: {server_id}"
            )
        
        try:
            return await transport.execute_tool(tool_name, parameters, timeout)
        except Exception as e:
            log.error(f"Tool execution failed: {e}")
            return MCPToolResponse(
                success=False,
                error=str(e)
            )
    
    async def execute_tool_by_name(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> MCPToolResponse:
        """
        Execute a tool by name (auto-discover server)
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            timeout: Execution timeout
            
        Returns:
            MCPToolResponse with result or error
        """
        # Find which server has this tool
        result = await self.find_tool(tool_name)
        
        if not result:
            return MCPToolResponse(
                success=False,
                error=f"Tool not found: {tool_name}"
            )
        
        server_id, _ = result
        return await self.execute_tool(server_id, tool_name, parameters, timeout)
    
    async def stream_tool(
        self,
        server_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> AsyncIterator[str]:
        """
        Execute a tool with streaming response
        
        Args:
            server_id: Server identifier
            tool_name: Name of the tool
            parameters: Tool parameters
            timeout: Execution timeout
            
        Yields:
            Chunks of the response
        """
        transport = self.registry.get_transport(server_id)
        
        if not transport:
            yield f"Error: Server not found: {server_id}"
            return
        
        try:
            async for chunk in transport.stream_tool(tool_name, parameters, timeout):
                yield chunk
        except Exception as e:
            log.error(f"Streaming tool execution failed: {e}")
            yield f"Error: {str(e)}"


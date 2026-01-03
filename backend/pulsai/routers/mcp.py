"""
MCP API Router

FastAPI endpoints for managing MCP servers and executing tools.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from pulsai.mcp.manager import MCPManager
from pulsai.mcp.validation import MCPServerConfig
from pulsai.mcp.protocols import MCPServerInfo, MCPToolSchema, MCPToolRequest, MCPToolResponse
from pulsai.utils.logger import get_logger

log = get_logger(__name__)

router = APIRouter()

# Global MCP manager instance (will be initialized in main.py)
mcp_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """Dependency to get MCP manager"""
    if mcp_manager is None:
        raise HTTPException(status_code=503, detail="MCP system not initialized")
    return mcp_manager


# Pydantic models for requests/responses

class ServerRegisterRequest(BaseModel):
    """Request to register a new MCP server"""
    config: MCPServerConfig


class ServerUpdateRequest(BaseModel):
    """Request to update an MCP server"""
    config: MCPServerConfig


class ToolExecuteRequest(BaseModel):
    """Request to execute a tool"""
    server_id: Optional[str] = None
    tool_name: str
    parameters: Dict[str, Any] = {}
    timeout: int = 30
    stream: bool = False


class TestConnectionResponse(BaseModel):
    """Response from connection test"""
    server_id: str
    success: bool
    message: str
    health_status: str


# API Endpoints

@router.post("/servers", response_model=Dict[str, Any])
async def register_server(
    request: ServerRegisterRequest,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Register a new MCP server"""
    try:
        success = await manager.register_server(request.config)
        
        if success:
            return {
                "success": True,
                "message": f"Server {request.config.id} registered successfully",
                "server_id": request.config.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to register server")
            
    except Exception as e:
        log.error(f"Error registering server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers", response_model=List[MCPServerInfo])
async def list_servers(
    enabled_only: bool = False,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """List all configured MCP servers"""
    try:
        return manager.list_servers(enabled_only=enabled_only)
    except Exception as e:
        log.error(f"Error listing servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}", response_model=MCPServerInfo)
async def get_server(
    server_id: str,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Get details about a specific MCP server"""
    try:
        server = manager.get_server(server_id)
        
        if not server:
            raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")
        
        return server
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/servers/{server_id}", response_model=Dict[str, Any])
async def update_server(
    server_id: str,
    request: ServerUpdateRequest,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Update an MCP server configuration"""
    try:
        # Ensure IDs match
        if request.config.id != server_id:
            raise HTTPException(status_code=400, detail="Server ID mismatch")
        
        success = await manager.update_server(server_id, request.config)
        
        if success:
            return {
                "success": True,
                "message": f"Server {server_id} updated successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update server")
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/servers/{server_id}", response_model=Dict[str, Any])
async def delete_server(
    server_id: str,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Remove an MCP server"""
    try:
        success = await manager.unregister_server(server_id)
        
        if success:
            return {
                "success": True,
                "message": f"Server {server_id} removed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/test", response_model=TestConnectionResponse)
async def test_server_connection(
    server_id: str,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Test connection to an MCP server"""
    try:
        server = manager.get_server(server_id)
        
        if not server:
            raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")
        
        success = await manager.test_server(server_id)
        
        return TestConnectionResponse(
            server_id=server_id,
            success=success,
            message="Connection successful" if success else "Connection failed",
            health_status="healthy" if success else "unhealthy"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error testing server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/servers/{server_id}/tools", response_model=List[MCPToolSchema])
async def list_server_tools(
    server_id: str,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """List available tools from a specific MCP server"""
    try:
        server = manager.get_server(server_id)
        
        if not server:
            raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")
        
        return server.tools
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools", response_model=Dict[str, List[MCPToolSchema]])
async def list_all_tools(
    enabled_only: bool = True,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """List all tools from all MCP servers"""
    try:
        return await manager.client.list_all_tools(enabled_only=enabled_only)
    except Exception as e:
        log.error(f"Error listing all tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/execute", response_model=MCPToolResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Execute an MCP tool"""
    try:
        if request.stream:
            # Return error for non-streaming endpoint
            raise HTTPException(
                status_code=400,
                detail="Use /tools/stream endpoint for streaming responses"
            )
        
        if request.server_id:
            # Execute on specific server
            return await manager.client.execute_tool(
                request.server_id,
                request.tool_name,
                request.parameters,
                request.timeout
            )
        else:
            # Auto-discover server
            return await manager.client.execute_tool_by_name(
                request.tool_name,
                request.parameters,
                request.timeout
            )
            
    except Exception as e:
        log.error(f"Error executing tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/stream")
async def stream_tool(
    request: ToolExecuteRequest,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Execute an MCP tool with streaming response"""
    try:
        if not request.server_id:
            # Find server for tool
            result = await manager.client.find_tool(request.tool_name)
            if not result:
                raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool_name}")
            request.server_id = result[0]
        
        async def generate():
            async for chunk in manager.client.stream_tool(
                request.server_id,
                request.tool_name,
                request.parameters,
                request.timeout
            ):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error streaming tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/enable", response_model=Dict[str, Any])
async def enable_server(
    server_id: str,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Enable an MCP server"""
    try:
        success = await manager.enable_server(server_id)
        
        if success:
            return {
                "success": True,
                "message": f"Server {server_id} enabled"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to enable server")
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error enabling server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servers/{server_id}/disable", response_model=Dict[str, Any])
async def disable_server(
    server_id: str,
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Disable an MCP server"""
    try:
        success = await manager.disable_server(server_id)
        
        if success:
            return {
                "success": True,
                "message": f"Server {server_id} disabled"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to disable server")
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error disabling server: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload", response_model=Dict[str, Any])
async def reload_configuration(
    manager: MCPManager = Depends(get_mcp_manager)
):
    """Reload MCP configuration from file"""
    try:
        await manager.reload_config()
        return {
            "success": True,
            "message": "Configuration reloaded successfully"
        }
    except Exception as e:
        log.error(f"Error reloading configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


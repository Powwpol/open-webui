"""
Pulsai Custom MCP Server

FastAPI-based MCP server with custom tools for Pulsai.
"""

import logging
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from .config import Config
from .schemas import TOOL_SCHEMAS, ToolRequest, ToolResponse
from .tools import recursive_chat_tool, model_info_tool, context_summary_tool

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Pulsai Custom MCP Server",
    description="Custom MCP server with recursive chat and model tools",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/Kubernetes."""
    return {"status": "healthy", "service": "pulsai-mcp", "version": "1.0.0"}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication dependency
async def verify_auth(authorization: Optional[str] = Header(None)):
    """Verify authentication token"""
    if not Config.AUTH_ENABLED:
        return True
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        if token != Config.AUTH_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return True
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "pulsai-mcp"
    }


# List available tools
@app.get("/v1/tools")
async def list_tools(authenticated: bool = Depends(verify_auth)):
    """List all available MCP tools"""
    return {
        "tools": [schema.dict() for schema in TOOL_SCHEMAS]
    }


# Execute a tool
@app.post("/v1/tools/execute")
async def execute_tool(
    request: ToolRequest,
    authenticated: bool = Depends(verify_auth)
) -> ToolResponse:
    """Execute an MCP tool"""
    
    tool_name = request.name
    arguments = request.arguments
    
    log.info(f"Executing tool: {tool_name}")
    
    try:
        # Route to appropriate tool
        if tool_name == "recursive_chat":
            result = await recursive_chat_tool(
                prompt=arguments.get("prompt"),
                strategy=arguments.get("strategy", "breadth_first"),
                max_depth=arguments.get("max_depth", 3),
                backend_url=Config.PULSAI_BACKEND_URL
            )
            
        elif tool_name == "model_info":
            result = await model_info_tool(
                model_name=arguments.get("model_name"),
                backend_url=Config.PULSAI_BACKEND_URL
            )
            
        elif tool_name == "context_summary":
            result = await context_summary_tool(
                messages=arguments.get("messages", []),
                max_length=arguments.get("max_length", 500)
            )
            
        else:
            return ToolResponse(
                success=False,
                error=f"Unknown tool: {tool_name}"
            )
        
        return ToolResponse(
            success=True,
            result=result
        )
        
    except Exception as e:
        log.error(f"Tool execution error: {e}")
        return ToolResponse(
            success=False,
            error=str(e)
        )


# Stream tool execution (for future use)
@app.post("/v1/tools/stream")
async def stream_tool(
    request: ToolRequest,
    authenticated: bool = Depends(verify_auth)
):
    """Execute a tool with streaming response"""
    # Placeholder for streaming implementation
    return {"message": "Streaming not yet implemented"}


def main():
    """Main entry point"""
    log.info(f"Starting Pulsai MCP Server on {Config.HOST}:{Config.PORT}")
    log.info(f"Backend URL: {Config.PULSAI_BACKEND_URL}")
    log.info(f"Auth enabled: {Config.AUTH_ENABLED}")
    
    uvicorn.run(
        "pulsai_mcp.server:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
        log_level=Config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()


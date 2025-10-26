"""
Pulsai MCP (Model Context Protocol) Module

This module provides a flexible, multi-protocol MCP client system supporting:
- stdio: Standard input/output communication
- HTTP/HTTPS: REST API endpoints
- Docker: Containerized MCP servers
- SSE: Server-Sent Events
- WebSocket: Real-time bidirectional communication
"""

from .client import MCPClient
from .manager import MCPManager
from .registry import MCPRegistry
from .protocols import MCPProtocol, ProtocolType

__all__ = [
    "MCPClient",
    "MCPManager",
    "MCPRegistry",
    "MCPProtocol",
    "ProtocolType",
]

__version__ = "1.0.0"


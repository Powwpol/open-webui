"""
MCP Configuration

Global configuration for the MCP system.
"""

import os
from typing import Optional


class MCPConfig:
    """Global MCP configuration"""
    
    # Configuration file path
    CONFIG_PATH: Optional[str] = os.getenv("MCP_CONFIG_PATH", "config/mcp-servers.yaml")
    
    # Enable auto-register from config file on startup
    AUTO_REGISTER: bool = os.getenv("MCP_AUTO_REGISTER", "true").lower() == "true"
    
    # Health check interval in seconds
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("MCP_HEALTH_CHECK_INTERVAL", "60"))
    
    # Config file watch interval in seconds
    CONFIG_WATCH_INTERVAL: int = int(os.getenv("MCP_CONFIG_WATCH_INTERVAL", "30"))
    
    # Enable hot-reload of configuration
    HOT_RELOAD_ENABLED: bool = os.getenv("MCP_HOT_RELOAD", "true").lower() == "true"
    
    # Default timeout for MCP operations
    DEFAULT_TIMEOUT: int = int(os.getenv("MCP_DEFAULT_TIMEOUT", "30"))
    
    # Maximum concurrent MCP operations
    MAX_CONCURRENT_OPERATIONS: int = int(os.getenv("MCP_MAX_CONCURRENT", "10"))


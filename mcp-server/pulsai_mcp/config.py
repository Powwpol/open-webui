"""
Pulsai MCP Server Configuration
"""

import os
from typing import Optional


class Config:
    """Server configuration"""
    
    # Server settings
    HOST: str = os.getenv("PULSAI_MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PULSAI_MCP_PORT", "8400"))
    
    # Pulsai backend URL
    PULSAI_BACKEND_URL: str = os.getenv("PULSAI_BACKEND_URL", "http://localhost:8080")
    
    # Authentication
    AUTH_ENABLED: bool = os.getenv("PULSAI_MCP_AUTH_ENABLED", "true").lower() == "true"
    AUTH_TOKEN: Optional[str] = os.getenv("PULSAI_MCP_TOKEN")
    
    # Logging
    LOG_LEVEL: str = os.getenv("PULSAI_MCP_LOG_LEVEL", "INFO")
    
    # Tool settings
    MAX_RECURSION_DEPTH: int = int(os.getenv("PULSAI_MCP_MAX_RECURSION", "10"))
    DEFAULT_RECURSION_STRATEGY: str = os.getenv("PULSAI_MCP_RECURSION_STRATEGY", "breadth_first")


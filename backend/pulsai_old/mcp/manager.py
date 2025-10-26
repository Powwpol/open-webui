"""
MCP Manager

High-level manager for MCP system lifecycle, configuration loading, and health monitoring.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import yaml

from .registry import MCPRegistry
from .client import MCPClient
from .validation import MCPServerConfig, MCPServersConfig
from .config import MCPConfig

log = logging.getLogger(__name__)


class MCPManager:
    """
    MCP System Manager
    
    Manages the entire MCP system including:
    - Configuration loading
    - Server registration and lifecycle
    - Health monitoring
    - Hot-reload of configuration
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.registry = MCPRegistry()
        self.client = MCPClient(self.registry)
        self._health_check_task: Optional[asyncio.Task] = None
        self._config_watch_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Start the MCP manager and load configuration"""
        if self._running:
            log.warning("MCP manager already running")
            return
        
        log.info("Starting MCP manager")
        
        # Load configuration
        await self.load_config()
        
        # Start health check loop
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Start config watch if path provided
        if self.config_path:
            self._config_watch_task = asyncio.create_task(self._config_watch_loop())
        
        log.info("MCP manager started")
    
    async def stop(self):
        """Stop the MCP manager and disconnect all servers"""
        if not self._running:
            return
        
        log.info("Stopping MCP manager")
        self._running = False
        
        # Cancel tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._config_watch_task:
            self._config_watch_task.cancel()
            try:
                await self._config_watch_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect all servers
        servers = self.registry.list_servers()
        for server in servers:
            await self.registry.disconnect(server.id)
        
        log.info("MCP manager stopped")
    
    async def load_config(self, config_path: Optional[str] = None):
        """
        Load MCP server configuration from file
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        path = config_path or self.config_path
        
        if not path:
            log.info("No MCP configuration path specified, using defaults")
            return
        
        try:
            config_file = Path(path)
            
            if not config_file.exists():
                log.warning(f"MCP configuration file not found: {path}")
                return
            
            # Load file
            with open(config_file, 'r') as f:
                if config_file.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif config_file.suffix == '.json':
                    data = json.load(f)
                else:
                    log.error(f"Unsupported config format: {config_file.suffix}")
                    return
            
            # Validate configuration
            config = MCPServersConfig(**data)
            
            # Register servers
            for server_config in config.mcp_servers:
                await self.registry.register(server_config)
            
            log.info(f"Loaded {len(config.mcp_servers)} MCP servers from {path}")
            
        except Exception as e:
            log.error(f"Failed to load MCP configuration: {e}")
    
    async def reload_config(self):
        """Reload configuration from file"""
        if not self.config_path:
            return
        
        log.info("Reloading MCP configuration")
        
        # Get current servers
        current_servers = {s.id for s in self.registry.list_servers()}
        
        # Load new config
        await self.load_config()
        
        # Get new servers
        new_servers = {s.id for s in self.registry.list_servers()}
        
        # Remove servers that are no longer in config
        removed = current_servers - new_servers
        for server_id in removed:
            await self.registry.unregister(server_id)
            log.info(f"Removed server: {server_id}")
    
    async def _health_check_loop(self):
        """Background task for periodic health checks"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.registry.health_check_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Health check loop error: {e}")
    
    async def _config_watch_loop(self):
        """Background task to watch for config file changes"""
        if not self.config_path:
            return
        
        config_file = Path(self.config_path)
        last_mtime = config_file.stat().st_mtime if config_file.exists() else 0
        
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if config_file.exists():
                    current_mtime = config_file.stat().st_mtime
                    if current_mtime > last_mtime:
                        log.info("Configuration file changed, reloading")
                        await self.reload_config()
                        last_mtime = current_mtime
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Config watch loop error: {e}")
    
    async def register_server(self, config: MCPServerConfig) -> bool:
        """Register a new MCP server"""
        return await self.registry.register(config)
    
    async def unregister_server(self, server_id: str) -> bool:
        """Unregister an MCP server"""
        return await self.registry.unregister(server_id)
    
    async def update_server(self, server_id: str, config: MCPServerConfig) -> bool:
        """Update an existing server's configuration"""
        # Unregister old
        await self.registry.unregister(server_id)
        
        # Register new
        return await self.registry.register(config)
    
    def list_servers(self, enabled_only: bool = False):
        """List all registered servers"""
        return self.registry.list_servers(enabled_only)
    
    def get_server(self, server_id: str):
        """Get information about a specific server"""
        return self.registry.get_server(server_id)
    
    async def test_server(self, server_id: str) -> bool:
        """Test connection to a server"""
        return await self.registry.health_check(server_id)
    
    async def enable_server(self, server_id: str) -> bool:
        """Enable a server"""
        return await self.registry.enable_server(server_id)
    
    async def disable_server(self, server_id: str) -> bool:
        """Disable a server"""
        return await self.registry.disable_server(server_id)


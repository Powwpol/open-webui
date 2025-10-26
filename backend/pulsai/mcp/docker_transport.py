"""
Docker Protocol Transport for MCP

Manages MCP servers running in Docker containers with orchestration,
health checks, and automatic cleanup.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, AsyncIterator, Optional
import time

try:
    import docker
    from docker.errors import DockerException, NotFound, APIError
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

from .http_transport import HTTPTransport
from .protocols import MCPToolSchema, MCPToolResponse

log = logging.getLogger(__name__)


class DockerTransport(HTTPTransport):
    """
    Docker protocol implementation for MCP
    
    Manages MCP servers in Docker containers. Uses HTTP transport for
    communication after container is running.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Docker transport
        
        Config keys:
            - image: str - Docker image name
            - ports: Dict[str, str] - Port mappings {"8000": "8000"}
            - volumes: Dict[str, str] - Volume mounts {"/host/path": "/container/path"}
            - environment: Dict[str, str] - Environment variables
            - network: str - Docker network name (optional)
            - auto_pull: bool - Auto-pull image if not found (default: True)
            - auto_remove: bool - Auto-remove container on stop (default: True)
            - mem_limit: str - Memory limit (e.g., "512m")
            - cpu_limit: float - CPU limit (e.g., 1.0 for 1 CPU)
        """
        # Don't call super().__init__ yet, need to set up container first
        self.docker_config = config
        self.container = None
        self.docker_client = None
        self.container_name = config.get("container_name", f"pulsai-mcp-{int(time.time())}")
        
        # Determine the internal container URL for HTTP communication
        exposed_port = list(config.get("ports", {}).keys())[0] if config.get("ports") else "8000"
        local_port = config.get("ports", {}).get(exposed_port, exposed_port)
        
        # Update config for HTTP transport
        http_config = {
            "url": f"http://localhost:{local_port}",
            "auth_type": config.get("auth_type", "none"),
            "token": config.get("token"),
            "timeout": config.get("timeout", 30),
            "max_retries": config.get("max_retries", 3),
            "headers": config.get("headers", {})
        }
        
        super().__init__(http_config)
        self._container_ready = False
        
    async def connect(self) -> bool:
        """Start Docker container and establish connection"""
        if not DOCKER_AVAILABLE:
            log.error("Docker library not available. Install with: pip install docker")
            return False
        
        if self._connected and self.container:
            return True
        
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Check if container already exists
            try:
                existing = self.docker_client.containers.get(self.container_name)
                log.info(f"Found existing container: {self.container_name}")
                if existing.status != "running":
                    existing.start()
                self.container = existing
            except NotFound:
                # Create new container
                await self._create_container()
            
            # Wait for container to be ready
            await self._wait_for_ready()
            
            # Now connect via HTTP
            if await super().connect():
                self._connected = True
                self._container_ready = True
                log.info(f"Docker MCP container ready: {self.container_name}")
                return True
            
            return False
            
        except Exception as e:
            log.error(f"Failed to start Docker MCP container: {e}")
            await self._cleanup_container()
            return False
    
    async def _create_container(self):
        """Create and start Docker container"""
        image = self.docker_config.get("image")
        if not image:
            raise ValueError("Docker transport requires 'image' in config")
        
        # Pull image if configured
        if self.docker_config.get("auto_pull", True):
            log.info(f"Pulling Docker image: {image}")
            self.docker_client.images.pull(image)
        
        # Prepare container configuration
        ports = self.docker_config.get("ports", {})
        volumes = self.docker_config.get("volumes", {})
        environment = self.docker_config.get("environment", {})
        network = self.docker_config.get("network")
        mem_limit = self.docker_config.get("mem_limit")
        cpu_quota = int(self.docker_config.get("cpu_limit", 1.0) * 100000)
        
        container_args = {
            "image": image,
            "name": self.container_name,
            "ports": ports,
            "volumes": volumes,
            "environment": environment,
            "detach": True,
            "auto_remove": False,  # We manage removal
        }
        
        if network:
            container_args["network"] = network
        
        if mem_limit:
            container_args["mem_limit"] = mem_limit
        
        if cpu_quota:
            container_args["cpu_quota"] = cpu_quota
        
        # Create and start container
        self.container = self.docker_client.containers.run(**container_args)
        log.info(f"Docker container started: {self.container_name}")
    
    async def _wait_for_ready(self, timeout: int = 60):
        """Wait for container to be ready and accepting connections"""
        if not self.container:
            raise RuntimeError("Container not started")
        
        deadline = time.time() + timeout
        
        while time.time() < deadline:
            # Check container status
            self.container.reload()
            if self.container.status != "running":
                raise RuntimeError(f"Container stopped unexpectedly: {self.container.status}")
            
            # Try health check via HTTP
            try:
                if await super().health_check():
                    return
            except Exception:
                pass
            
            await asyncio.sleep(2)
        
        raise TimeoutError(f"Container did not become ready within {timeout}s")
    
    async def disconnect(self) -> None:
        """Stop and optionally remove Docker container"""
        # Disconnect HTTP first
        await super().disconnect()
        
        # Stop container
        await self._cleanup_container()
        
        if self.docker_client:
            self.docker_client.close()
        
        self._connected = False
        self._container_ready = False
        log.info(f"Docker MCP container stopped: {self.container_name}")
    
    async def _cleanup_container(self):
        """Stop and optionally remove container"""
        if not self.container:
            return
        
        try:
            # Stop container
            self.container.stop(timeout=10)
            
            # Remove if configured
            if self.docker_config.get("auto_remove", True):
                self.container.remove(force=True)
                log.info(f"Container removed: {self.container_name}")
            
        except Exception as e:
            log.warning(f"Error cleaning up container: {e}")
        finally:
            self.container = None
    
    async def health_check(self) -> bool:
        """Check if Docker container is healthy"""
        if not self.container:
            return False
        
        try:
            # Check container status
            self.container.reload()
            if self.container.status != "running":
                return False
            
            # Check HTTP health
            return await super().health_check()
            
        except Exception as e:
            log.debug(f"Docker health check failed: {e}")
            return False
    
    def get_container_logs(self, tail: int = 100) -> str:
        """Get container logs for debugging"""
        if not self.container:
            return ""
        
        try:
            logs = self.container.logs(tail=tail)
            return logs.decode()
        except Exception as e:
            return f"Error getting logs: {e}"


"""
stdio Protocol Transport for MCP

Handles communication with MCP servers via standard input/output streams.
Uses subprocess to launch and communicate with the MCP server process.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, AsyncIterator
import subprocess
import os

from .protocols import MCPProtocol, MCPToolSchema, MCPToolResponse

log = logging.getLogger(__name__)


class StdioTransport(MCPProtocol):
    """
    stdio protocol implementation for MCP
    
    Launches an MCP server as a subprocess and communicates via stdin/stdout.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize stdio transport
        
        Config keys:
            - command: str - Command to execute (e.g., "python")
            - args: List[str] - Command arguments (e.g., ["-m", "mcp_server"])
            - env: Dict[str, str] - Environment variables
            - cwd: str - Working directory (optional)
        """
        super().__init__(config)
        self.process: Optional[asyncio.subprocess.Process] = None
        self._stdout_task: Optional[asyncio.Task] = None
        self._response_queue = asyncio.Queue()
        self._request_id = 0
        
    async def connect(self) -> bool:
        """Launch the MCP server subprocess"""
        if self._connected:
            return True
        
        try:
            command = self.config.get("command")
            args = self.config.get("args", [])
            env = self.config.get("env", {})
            cwd = self.config.get("cwd")
            
            if not command:
                raise ValueError("stdio transport requires 'command' in config")
            
            # Merge environment variables
            full_env = os.environ.copy()
            full_env.update(env)
            
            # Launch subprocess
            full_command = [command] + args
            self.process = await asyncio.create_subprocess_exec(
                *full_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=full_env,
                cwd=cwd
            )
            
            # Start stdout reader task
            self._stdout_task = asyncio.create_task(self._read_stdout())
            
            self._connected = True
            log.info(f"stdio MCP server started: {' '.join(full_command)}")
            
            # Wait a bit for initialization
            await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            log.error(f"Failed to start stdio MCP server: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Terminate the MCP server subprocess"""
        if not self._connected:
            return
        
        try:
            # Cancel stdout reader
            if self._stdout_task:
                self._stdout_task.cancel()
                try:
                    await self._stdout_task
                except asyncio.CancelledError:
                    pass
            
            # Terminate process
            if self.process:
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    self.process.kill()
                    await self.process.wait()
            
            self._connected = False
            log.info("stdio MCP server stopped")
            
        except Exception as e:
            log.error(f"Error disconnecting stdio transport: {e}")
    
    async def _read_stdout(self):
        """Background task to read and parse stdout from subprocess"""
        try:
            while self.process and self.process.stdout:
                line = await self.process.stdout.readline()
                if not line:
                    break
                
                try:
                    data = json.loads(line.decode().strip())
                    await self._response_queue.put(data)
                except json.JSONDecodeError as e:
                    log.warning(f"Invalid JSON from MCP server: {line.decode()}: {e}")
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.error(f"Error reading stdout: {e}")
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request and wait for response"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server not connected")
        
        # Add request ID
        self._request_id += 1
        request["id"] = self._request_id
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Wait for response with matching ID
        timeout = 30
        try:
            deadline = asyncio.get_event_loop().time() + timeout
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    raise asyncio.TimeoutError()
                
                response = await asyncio.wait_for(
                    self._response_queue.get(),
                    timeout=remaining
                )
                
                if response.get("id") == self._request_id:
                    return response
                else:
                    # Put back responses for other requests
                    await self._response_queue.put(response)
                    await asyncio.sleep(0.01)
                    
        except asyncio.TimeoutError:
            raise TimeoutError(f"MCP request timed out after {timeout}s")
    
    async def health_check(self) -> bool:
        """Check if the MCP server is responsive"""
        if not self._connected or not self.process:
            return False
        
        # Check if process is still running
        if self.process.returncode is not None:
            self._connected = False
            return False
        
        try:
            # Try listing tools as a health check
            await asyncio.wait_for(self.list_tools(), timeout=5.0)
            return True
        except Exception:
            return False
    
    async def list_tools(self) -> List[MCPToolSchema]:
        """List available tools from the MCP server"""
        await self.ensure_connected()
        
        request = {
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")
        
        tools_data = response.get("result", {}).get("tools", [])
        return [MCPToolSchema(**tool) for tool in tools_data]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> MCPToolResponse:
        """Execute a tool on the MCP server"""
        await self.ensure_connected()
        
        import time
        start_time = time.time()
        
        request = {
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        try:
            response = await self._send_request(request)
            execution_time = time.time() - start_time
            
            if "error" in response:
                return MCPToolResponse(
                    success=False,
                    error=str(response["error"]),
                    execution_time=execution_time
                )
            
            result = response.get("result")
            return MCPToolResponse(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return MCPToolResponse(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def stream_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        timeout: int = 30
    ) -> AsyncIterator[str]:
        """Execute a tool with streaming response (if supported)"""
        await self.ensure_connected()
        
        # For now, execute tool and yield result as single chunk
        # Full streaming support would require MCP server protocol extension
        response = await self.execute_tool(tool_name, parameters, timeout)
        
        if response.success and response.result:
            if isinstance(response.result, str):
                yield response.result
            else:
                yield json.dumps(response.result)
        elif not response.success:
            yield f"Error: {response.error}"


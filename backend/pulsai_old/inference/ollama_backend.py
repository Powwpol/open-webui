"""
Ollama inference backend implementation
"""

import httpx
import time
from typing import AsyncIterator, List, Dict, Any, Optional
from loguru import logger as log

from .base import (
    InferenceBackend,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    HealthStatus,
    BackendType,
    BackendStatus
)


class OllamaBackend(InferenceBackend):
    """Ollama inference backend"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.backend_type = BackendType.OLLAMA
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.timeout = config.get("timeout", 120)
        
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate completion using Ollama"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build Ollama request
                ollama_request = {
                    "model": request.model,
                    "prompt": request.prompt if request.prompt else None,
                    "messages": request.messages if request.messages else None,
                    "stream": False,
                    "options": {
                        "temperature": request.temperature,
                        "top_p": request.top_p,
                    }
                }
                
                if request.max_tokens:
                    ollama_request["options"]["num_predict"] = request.max_tokens
                if request.top_k:
                    ollama_request["options"]["top_k"] = request.top_k
                if request.stop:
                    ollama_request["options"]["stop"] = request.stop
                
                # Choose endpoint based on request type
                endpoint = "/api/chat" if request.messages else "/api/generate"
                
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=ollama_request
                )
                response.raise_for_status()
                
                data = response.json()
                content = data.get("message", {}).get("content") if request.messages else data.get("response", "")
                
                latency = (time.time() - start_time) * 1000
                
                return InferenceResponse(
                    model=request.model,
                    content=content,
                    finish_reason="stop",
                    usage=None,  # Ollama doesn't provide usage stats in same format
                    backend="ollama",
                    latency_ms=latency
                )
                
        except Exception as e:
            log.error(f"Ollama generate error: {e}")
            latency = (time.time() - start_time) * 1000
            return InferenceResponse(
                model=request.model,
                content="",
                backend="ollama",
                latency_ms=latency,
                error=str(e)
            )
    
    async def generate_stream(self, request: InferenceRequest) -> AsyncIterator[str]:
        """Generate streaming completion using Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                ollama_request = {
                    "model": request.model,
                    "prompt": request.prompt if request.prompt else None,
                    "messages": request.messages if request.messages else None,
                    "stream": True,
                    "options": {
                        "temperature": request.temperature,
                        "top_p": request.top_p,
                    }
                }
                
                if request.max_tokens:
                    ollama_request["options"]["num_predict"] = request.max_tokens
                
                endpoint = "/api/chat" if request.messages else "/api/generate"
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}{endpoint}",
                    json=ollama_request
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                import json
                                data = json.loads(line)
                                
                                if request.messages:
                                    content = data.get("message", {}).get("content", "")
                                else:
                                    content = data.get("response", "")
                                
                                if content:
                                    yield content
                                    
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            log.error(f"Ollama stream error: {e}")
            yield f"[Error: {str(e)}]"
    
    async def list_models(self) -> List[ModelInfo]:
        """List available Ollama models"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = []
                
                for model in data.get("models", []):
                    models.append(ModelInfo(
                        id=model["name"],
                        name=model["name"],
                        backend=BackendType.OLLAMA,
                        context_window=None,  # Would need to parse from model details
                        capabilities=["chat", "completion"],
                        parameters={"size": model.get("size", 0)},
                        available=True
                    ))
                
                return models
                
        except Exception as e:
            log.error(f"Ollama list_models error: {e}")
            return []
    
    async def health_check(self) -> HealthStatus:
        """Check Ollama backend health"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                latency = (time.time() - start_time) * 1000
                models_count = len(response.json().get("models", []))
                
                self._healthy = True
                
                return HealthStatus(
                    backend="ollama",
                    status=BackendStatus.HEALTHY,
                    latency_ms=latency,
                    models_count=models_count,
                    error=None,
                    last_check=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                )
                
        except Exception as e:
            log.error(f"Ollama health check failed: {e}")
            self._healthy = False
            
            return HealthStatus(
                backend="ollama",
                status=BackendStatus.UNHEALTHY,
                latency_ms=None,
                models_count=0,
                error=str(e),
                last_check=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            )
    
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get detailed Ollama model information"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/api/show",
                    json={"name": model_id}
                )
                response.raise_for_status()
                
                data = response.json()
                
                return ModelInfo(
                    id=model_id,
                    name=model_id,
                    backend=BackendType.OLLAMA,
                    context_window=None,
                    capabilities=["chat", "completion"],
                    parameters=data.get("parameters", {}),
                    available=True
                )
                
        except Exception as e:
            log.error(f"Ollama get_model_info error: {e}")
            return None


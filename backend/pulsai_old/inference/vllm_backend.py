"""
vLLM inference backend implementation
Uses OpenAI-compatible API
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


class VLLMBackend(InferenceBackend):
    """vLLM inference backend (OpenAI-compatible API)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.backend_type = BackendType.VLLM
        self.base_url = config.get("base_url", "http://localhost:8000")
        self.api_key = config.get("api_key")
        self.timeout = config.get("timeout", 300)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional API key"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Generate completion using vLLM (OpenAI-compatible)"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build OpenAI-compatible request
                vllm_request = {
                    "model": request.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens or 2048,
                    "top_p": request.top_p,
                    "stream": False,
                }
                
                if request.top_k:
                    vllm_request["top_k"] = request.top_k
                if request.stop:
                    vllm_request["stop"] = request.stop
                
                # Handle chat vs completion
                if request.messages:
                    vllm_request["messages"] = request.messages
                    endpoint = "/v1/chat/completions"
                else:
                    vllm_request["prompt"] = request.prompt
                    endpoint = "/v1/completions"
                
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=vllm_request,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract content
                if request.messages:
                    content = data["choices"][0]["message"]["content"]
                    finish_reason = data["choices"][0]["finish_reason"]
                else:
                    content = data["choices"][0]["text"]
                    finish_reason = data["choices"][0]["finish_reason"]
                
                usage = data.get("usage", {})
                latency = (time.time() - start_time) * 1000
                
                return InferenceResponse(
                    model=request.model,
                    content=content,
                    finish_reason=finish_reason,
                    usage=usage,
                    backend="vllm",
                    latency_ms=latency
                )
                
        except Exception as e:
            log.error(f"vLLM generate error: {e}")
            latency = (time.time() - start_time) * 1000
            return InferenceResponse(
                model=request.model,
                content="",
                backend="vllm",
                latency_ms=latency,
                error=str(e)
            )
    
    async def generate_stream(self, request: InferenceRequest) -> AsyncIterator[str]:
        """Generate streaming completion using vLLM"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                vllm_request = {
                    "model": request.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens or 2048,
                    "top_p": request.top_p,
                    "stream": True,
                }
                
                if request.messages:
                    vllm_request["messages"] = request.messages
                    endpoint = "/v1/chat/completions"
                else:
                    vllm_request["prompt"] = request.prompt
                    endpoint = "/v1/completions"
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}{endpoint}",
                    json=vllm_request,
                    headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                import json
                                data = json.loads(data_str)
                                
                                if request.messages:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                else:
                                    content = data["choices"][0].get("text", "")
                                
                                if content:
                                    yield content
                                    
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            log.error(f"vLLM stream error: {e}")
            yield f"[Error: {str(e)}]"
    
    async def list_models(self) -> List[ModelInfo]:
        """List available vLLM models"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                models = []
                
                for model in data.get("data", []):
                    models.append(ModelInfo(
                        id=model["id"],
                        name=model["id"],
                        backend=BackendType.VLLM,
                        context_window=None,  # vLLM doesn't expose this directly
                        capabilities=["chat", "completion"],
                        parameters={
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by", "vllm")
                        },
                        available=True
                    ))
                
                return models
                
        except Exception as e:
            log.error(f"vLLM list_models error: {e}")
            return []
    
    async def health_check(self) -> HealthStatus:
        """Check vLLM backend health"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                latency = (time.time() - start_time) * 1000
                models_count = len(response.json().get("data", []))
                
                self._healthy = True
                
                return HealthStatus(
                    backend="vllm",
                    status=BackendStatus.HEALTHY,
                    latency_ms=latency,
                    models_count=models_count,
                    error=None,
                    last_check=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                )
                
        except Exception as e:
            log.error(f"vLLM health check failed: {e}")
            self._healthy = False
            
            return HealthStatus(
                backend="vllm",
                status=BackendStatus.UNHEALTHY,
                latency_ms=None,
                models_count=0,
                error=str(e),
                last_check=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            )
    
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get detailed vLLM model information"""
        try:
            models = await self.list_models()
            for model in models:
                if model.id == model_id:
                    return model
            return None
                
        except Exception as e:
            log.error(f"vLLM get_model_info error: {e}")
            return None


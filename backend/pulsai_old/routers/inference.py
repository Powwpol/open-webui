"""
Pulsai Inference Router API

Unified inference endpoints with multi-backend support
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from loguru import logger as log

from open_webui.inference import (
    InferenceRequest,
    InferenceResponse,
    InferenceRouter,
    HealthMonitor,
    OllamaBackend,
    VLLMBackend,
    ModelInfo
)
from open_webui.config import OLLAMA_BASE_URLS, VLLM_ENABLED, VLLM_BASE_URL, VLLM_API_KEY


router = APIRouter()

# Global inference router instance
inference_router: Optional[InferenceRouter] = None
health_monitor: Optional[HealthMonitor] = None


class GenerateRequest(BaseModel):
    """API request for generation"""
    model: str = Field(..., description="Model identifier")
    prompt: Optional[str] = Field(None, description="Prompt for completion")
    messages: Optional[List[Dict[str, str]]] = Field(None, description="Chat messages")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    top_p: float = Field(0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, ge=1)
    stop: Optional[List[str]] = None
    stream: bool = False
    backend: Optional[str] = Field(None, description="Preferred backend (ollama/vllm)")


class BackendConfigRequest(BaseModel):
    """Backend configuration"""
    backend_type: str = Field(..., description="Backend type (ollama/vllm)")
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 120


def get_inference_router() -> InferenceRouter:
    """Get or initialize inference router"""
    global inference_router, health_monitor
    
    if inference_router is None:
        backends = []
        
        # Initialize Ollama backend
        try:
            ollama_config = {
                "base_url": OLLAMA_BASE_URLS[0] if OLLAMA_BASE_URLS else "http://localhost:11434",
                "timeout": 120
            }
            ollama_backend = OllamaBackend(ollama_config)
            backends.append(ollama_backend)
            log.info("Ollama backend initialized")
        except Exception as e:
            log.error(f"Failed to initialize Ollama backend: {e}")
        
        # Initialize vLLM backend if enabled
        if VLLM_ENABLED and VLLM_BASE_URL:
            try:
                vllm_config = {
                    "base_url": VLLM_BASE_URL,
                    "api_key": VLLM_API_KEY,
                    "timeout": 300
                }
                vllm_backend = VLLMBackend(vllm_config)
                backends.append(vllm_backend)
                log.info("vLLM backend initialized")
            except Exception as e:
                log.error(f"Failed to initialize vLLM backend: {e}")
        
        if not backends:
            raise RuntimeError("No inference backends available")
        
        # Create router with priority: vLLM > Ollama
        priorities = ["vllm", "ollama"] if VLLM_ENABLED else ["ollama"]
        inference_router = InferenceRouter(
            backends=backends,
            strategy="priority",
            priorities=priorities
        )
        
        # Start health monitoring
        health_monitor = HealthMonitor(
            backends=backends,
            check_interval=30,
            auto_start=True
        )
        
        log.info(f"Inference router initialized with {len(backends)} backends")
    
    return inference_router


@router.post("/generate", response_model=InferenceResponse)
async def generate(
    request: GenerateRequest,
    router: InferenceRouter = Depends(get_inference_router)
):
    """
    Generate completion (non-streaming)
    
    Supports both chat (messages) and completion (prompt) modes.
    """
    try:
        # Convert to internal request
        inference_request = InferenceRequest(
            model=request.model,
            prompt=request.prompt,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k,
            stop=request.stop,
            stream=False
        )
        
        response = await router.generate(
            inference_request,
            preferred_backend=request.backend
        )
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inference error: {response.error}"
            )
        
        return response
        
    except Exception as e:
        log.error(f"Generate error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate/stream")
async def generate_stream(
    request: GenerateRequest,
    router: InferenceRouter = Depends(get_inference_router)
):
    """
    Generate completion (streaming)
    
    Returns Server-Sent Events stream
    """
    try:
        inference_request = InferenceRequest(
            model=request.model,
            prompt=request.prompt,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k,
            stop=request.stop,
            stream=True
        )
        
        async def event_generator():
            async for token in router.generate_stream(
                inference_request,
                preferred_backend=request.backend
            ):
                yield f"data: {token}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        log.error(f"Stream error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/models", response_model=Dict[str, List[ModelInfo]])
async def list_models(
    router: InferenceRouter = Depends(get_inference_router)
):
    """List all available models from all backends"""
    try:
        models = await router.list_all_models()
        return models
    except Exception as e:
        log.error(f"List models error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/backends/status")
async def get_backends_status(
    router: InferenceRouter = Depends(get_inference_router)
):
    """Get status of all backends"""
    try:
        stats = await router.get_backend_stats()
        return stats
    except Exception as e:
        log.error(f"Backend status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/backends/health")
async def get_backends_health():
    """Get health monitoring data"""
    if health_monitor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health monitor not initialized"
        )
    
    try:
        summary = health_monitor.get_summary()
        return summary
    except Exception as e:
        log.error(f"Health summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/backends/add")
async def add_backend(
    config: BackendConfigRequest,
    router: InferenceRouter = Depends(get_inference_router)
):
    """Add a new backend dynamically"""
    try:
        if config.backend_type == "ollama":
            backend = OllamaBackend({
                "base_url": config.base_url,
                "timeout": config.timeout
            })
        elif config.backend_type == "vllm":
            backend = VLLMBackend({
                "base_url": config.base_url,
                "api_key": config.api_key,
                "timeout": config.timeout
            })
        else:
            raise ValueError(f"Unsupported backend type: {config.backend_type}")
        
        router.add_backend(backend)
        
        # Add to health monitor
        if health_monitor:
            health_monitor.backends.append(backend)
        
        return {"status": "success", "backend": config.backend_type}
        
    except Exception as e:
        log.error(f"Add backend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/backends/{backend_name}")
async def remove_backend(
    backend_name: str,
    router: InferenceRouter = Depends(get_inference_router)
):
    """Remove a backend"""
    try:
        router.remove_backend(backend_name)
        return {"status": "success", "backend": backend_name}
    except Exception as e:
        log.error(f"Remove backend error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


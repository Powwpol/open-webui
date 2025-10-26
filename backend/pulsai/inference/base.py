"""
Base classes for inference backend abstraction
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class BackendType(str, Enum):
    """Inference backend types"""
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class BackendStatus(str, Enum):
    """Backend health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class InferenceRequest(BaseModel):
    """Unified inference request"""
    model: str
    prompt: str
    messages: Optional[List[Dict[str, str]]] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.9
    top_k: Optional[int] = None
    stop: Optional[List[str]] = None
    stream: bool = False
    system_prompt: Optional[str] = None
    
    # Backend-specific parameters
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class InferenceResponse(BaseModel):
    """Unified inference response"""
    model: str
    content: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    
    # Metadata
    backend: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class ModelInfo(BaseModel):
    """Model metadata"""
    id: str
    name: str
    backend: BackendType
    context_window: Optional[int] = None
    capabilities: List[str] = Field(default_factory=list)  # ["chat", "completion", "vision"]
    parameters: Optional[Dict[str, Any]] = None
    available: bool = True


class HealthStatus(BaseModel):
    """Backend health status"""
    backend: str
    status: BackendStatus
    latency_ms: Optional[float] = None
    models_count: int = 0
    error: Optional[str] = None
    last_check: Optional[str] = None


class InferenceBackend(ABC):
    """Abstract base class for inference backends"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backend_type = BackendType.OLLAMA  # Override in subclasses
        self._healthy = False
        self._last_health_check = None
    
    @abstractmethod
    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """
        Generate completion (non-streaming)
        
        Args:
            request: Inference request
            
        Returns:
            Complete inference response
        """
        pass
    
    @abstractmethod
    async def generate_stream(self, request: InferenceRequest) -> AsyncIterator[str]:
        """
        Generate completion (streaming)
        
        Args:
            request: Inference request
            
        Yields:
            Token strings as they're generated
        """
        pass
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """
        List available models
        
        Returns:
            List of model metadata
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """
        Check backend health
        
        Returns:
            Health status with metrics
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get detailed model information
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model metadata or None if not found
        """
        pass
    
    def is_healthy(self) -> bool:
        """Check if backend is currently healthy"""
        return self._healthy
    
    def get_backend_type(self) -> BackendType:
        """Get backend type"""
        return self.backend_type


"""
Pulsai Inference Abstraction Layer

Provides unified interface for multiple inference backends:
- Ollama
- vLLM
- External APIs (OpenAI, Anthropic)

Supports load balancing, failover, and health monitoring.
"""

from .base import InferenceBackend, InferenceRequest, InferenceResponse
from .ollama_backend import OllamaBackend
from .vllm_backend import VLLMBackend
from .router import InferenceRouter
from .health import HealthMonitor

__all__ = [
    "InferenceBackend",
    "InferenceRequest",
    "InferenceResponse",
    "OllamaBackend",
    "VLLMBackend",
    "InferenceRouter",
    "HealthMonitor",
]


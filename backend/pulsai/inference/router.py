"""
Inference router with load balancing and failover
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum
from loguru import logger as log

from .base import (
    InferenceBackend,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    BackendType
)


class RoutingStrategy(str, Enum):
    """Routing strategies for inference requests"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    FAILOVER = "failover"
    PRIORITY = "priority"


class InferenceRouter:
    """Routes inference requests across multiple backends"""
    
    def __init__(
        self,
        backends: List[InferenceBackend],
        strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN,
        priorities: Optional[List[str]] = None
    ):
        self.backends = {backend.get_backend_type().value: backend for backend in backends}
        self.strategy = strategy
        self.priorities = priorities or []
        self._round_robin_index = 0
        self._request_counts = {name: 0 for name in self.backends.keys()}
        
    async def generate(
        self,
        request: InferenceRequest,
        preferred_backend: Optional[str] = None
    ) -> InferenceResponse:
        """
        Generate completion using routing strategy
        
        Args:
            request: Inference request
            preferred_backend: Optional backend preference
            
        Returns:
            Inference response
        """
        backend = await self._select_backend(preferred_backend)
        
        if not backend:
            return InferenceResponse(
                model=request.model,
                content="",
                backend="none",
                error="No healthy backend available"
            )
        
        try:
            response = await backend.generate(request)
            self._request_counts[backend.get_backend_type().value] += 1
            return response
            
        except Exception as e:
            log.error(f"Backend {backend.get_backend_type().value} failed: {e}")
            
            # Try failover to next backend
            if self.strategy == RoutingStrategy.FAILOVER:
                log.info("Attempting failover to next backend...")
                alternative_backend = await self._select_backend(
                    exclude=[backend.get_backend_type().value]
                )
                if alternative_backend:
                    try:
                        response = await alternative_backend.generate(request)
                        self._request_counts[alternative_backend.get_backend_type().value] += 1
                        return response
                    except Exception as e2:
                        log.error(f"Failover backend also failed: {e2}")
            
            return InferenceResponse(
                model=request.model,
                content="",
                backend=backend.get_backend_type().value,
                error=str(e)
            )
    
    async def generate_stream(
        self,
        request: InferenceRequest,
        preferred_backend: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Generate streaming completion"""
        backend = await self._select_backend(preferred_backend)
        
        if not backend:
            yield "[Error: No healthy backend available]"
            return
        
        try:
            async for token in backend.generate_stream(request):
                yield token
            self._request_counts[backend.get_backend_type().value] += 1
            
        except Exception as e:
            log.error(f"Stream from {backend.get_backend_type().value} failed: {e}")
            yield f"[Error: {str(e)}]"
    
    async def list_all_models(self) -> Dict[str, List[ModelInfo]]:
        """List models from all backends"""
        all_models = {}
        
        for backend_name, backend in self.backends.items():
            if backend.is_healthy():
                try:
                    models = await backend.list_models()
                    all_models[backend_name] = models
                except Exception as e:
                    log.error(f"Failed to list models from {backend_name}: {e}")
                    all_models[backend_name] = []
            else:
                all_models[backend_name] = []
        
        return all_models
    
    async def get_backend_stats(self) -> Dict[str, Any]:
        """Get statistics for all backends"""
        stats = {}
        
        for backend_name, backend in self.backends.items():
            health = await backend.health_check()
            stats[backend_name] = {
                "healthy": backend.is_healthy(),
                "latency_ms": health.latency_ms,
                "models_count": health.models_count,
                "request_count": self._request_counts[backend_name],
                "status": health.status.value,
                "error": health.error
            }
        
        return stats
    
    async def _select_backend(
        self,
        preferred: Optional[str] = None,
        exclude: Optional[List[str]] = None
    ) -> Optional[InferenceBackend]:
        """Select backend based on strategy"""
        exclude = exclude or []
        available_backends = [
            (name, backend)
            for name, backend in self.backends.items()
            if backend.is_healthy() and name not in exclude
        ]
        
        if not available_backends:
            # Try to find any backend, even if not healthy
            available_backends = [
                (name, backend)
                for name, backend in self.backends.items()
                if name not in exclude
            ]
            if not available_backends:
                return None
        
        # Preferred backend
        if preferred and preferred in self.backends:
            backend = self.backends[preferred]
            if backend.is_healthy():
                return backend
        
        # Apply routing strategy
        if self.strategy == RoutingStrategy.ROUND_ROBIN:
            if available_backends:
                self._round_robin_index = (self._round_robin_index + 1) % len(available_backends)
                return available_backends[self._round_robin_index][1]
        
        elif self.strategy == RoutingStrategy.LEAST_LOADED:
            # Select backend with fewest requests
            least_loaded = min(
                available_backends,
                key=lambda x: self._request_counts[x[0]]
            )
            return least_loaded[1]
        
        elif self.strategy == RoutingStrategy.PRIORITY or self.strategy == RoutingStrategy.FAILOVER:
            # Use priority order
            for priority_backend in self.priorities:
                for name, backend in available_backends:
                    if name == priority_backend:
                        return backend
            
            # Fallback to first available
            if available_backends:
                return available_backends[0][1]
        
        return None
    
    def add_backend(self, backend: InferenceBackend):
        """Add a new backend to the router"""
        backend_name = backend.get_backend_type().value
        self.backends[backend_name] = backend
        self._request_counts[backend_name] = 0
        log.info(f"Added backend: {backend_name}")
    
    def remove_backend(self, backend_name: str):
        """Remove a backend from the router"""
        if backend_name in self.backends:
            del self.backends[backend_name]
            del self._request_counts[backend_name]
            log.info(f"Removed backend: {backend_name}")


"""
Health monitoring for inference backends
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger as log

from .base import InferenceBackend, HealthStatus


class HealthMonitor:
    """Monitors health of inference backends"""
    
    def __init__(
        self,
        backends: List[InferenceBackend],
        check_interval: int = 30,  # seconds
        auto_start: bool = True
    ):
        self.backends = backends
        self.check_interval = check_interval
        self._running = False
        self._task = None
        self._health_history: Dict[str, List[HealthStatus]] = {}
        
        if auto_start:
            asyncio.create_task(self.start())
    
    async def start(self):
        """Start health monitoring"""
        if self._running:
            log.warning("Health monitor already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        log.info(f"Health monitor started (interval: {self.check_interval}s)")
    
    async def stop(self):
        """Stop health monitoring"""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        log.info("Health monitor stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                await self.check_all()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_all(self) -> Dict[str, HealthStatus]:
        """Check health of all backends"""
        results = {}
        
        tasks = [
            self._check_backend(backend)
            for backend in self.backends
        ]
        
        health_statuses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for backend, health in zip(self.backends, health_statuses):
            backend_name = backend.get_backend_type().value
            
            if isinstance(health, Exception):
                log.error(f"Health check failed for {backend_name}: {health}")
                continue
            
            results[backend_name] = health
            
            # Store in history
            if backend_name not in self._health_history:
                self._health_history[backend_name] = []
            
            self._health_history[backend_name].append(health)
            
            # Keep only last 100 checks
            if len(self._health_history[backend_name]) > 100:
                self._health_history[backend_name] = self._health_history[backend_name][-100:]
        
        return results
    
    async def _check_backend(self, backend: InferenceBackend) -> HealthStatus:
        """Check health of a single backend"""
        try:
            return await backend.health_check()
        except Exception as e:
            log.error(f"Health check error for {backend.get_backend_type().value}: {e}")
            return HealthStatus(
                backend=backend.get_backend_type().value,
                status="unhealthy",
                latency_ms=None,
                models_count=0,
                error=str(e),
                last_check=datetime.utcnow().isoformat() + "Z"
            )
    
    def get_health_history(
        self,
        backend_name: str,
        limit: int = 20
    ) -> List[HealthStatus]:
        """Get health history for a backend"""
        history = self._health_history.get(backend_name, [])
        return history[-limit:]
    
    def get_uptime_percentage(
        self,
        backend_name: str,
        hours: int = 24
    ) -> float:
        """Calculate uptime percentage for last N hours"""
        history = self._health_history.get(backend_name, [])
        
        if not history:
            return 0.0
        
        # Filter to last N hours
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_checks = [
            h for h in history
            if datetime.fromisoformat(h.last_check.replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_checks:
            return 0.0
        
        healthy_count = sum(
            1 for h in recent_checks
            if h.status == "healthy"
        )
        
        return (healthy_count / len(recent_checks)) * 100
    
    def get_average_latency(
        self,
        backend_name: str,
        limit: int = 20
    ) -> Optional[float]:
        """Get average latency for a backend"""
        history = self.get_health_history(backend_name, limit)
        
        if not history:
            return None
        
        latencies = [
            h.latency_ms for h in history
            if h.latency_ms is not None
        ]
        
        if not latencies:
            return None
        
        return sum(latencies) / len(latencies)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all backends"""
        summary = {}
        
        for backend in self.backends:
            backend_name = backend.get_backend_type().value
            
            summary[backend_name] = {
                "current_status": "healthy" if backend.is_healthy() else "unhealthy",
                "uptime_24h": self.get_uptime_percentage(backend_name, hours=24),
                "avg_latency_ms": self.get_average_latency(backend_name),
                "checks_count": len(self._health_history.get(backend_name, []))
            }
        
        return summary


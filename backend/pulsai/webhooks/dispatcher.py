"""
Webhook event dispatcher with retry logic
"""

import asyncio
import httpx
from typing import Optional, List
from datetime import datetime
from loguru import logger as log

from .events import WebhookEvent
from .registry import WebhookRegistry, WebhookSubscription
from .security import WebhookSecurity


class DeliveryResult:
    """Result of webhook delivery attempt"""
    
    def __init__(
        self,
        success: bool,
        status_code: Optional[int] = None,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None
    ):
        self.success = success
        self.status_code = status_code
        self.error = error
        self.latency_ms = latency_ms


class WebhookDispatcher:
    """Dispatches webhook events to registered endpoints"""
    
    def __init__(self, registry: WebhookRegistry):
        self.registry = registry
        self.delivery_queue = asyncio.Queue()
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        log.info("Webhook dispatcher initialized")
    
    async def start(self):
        """Start webhook delivery worker"""
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._delivery_worker())
        log.info("Webhook dispatcher started")
    
    async def stop(self):
        """Stop webhook delivery worker"""
        if not self._running:
            return
        
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        log.info("Webhook dispatcher stopped")
    
    async def dispatch(self, event: WebhookEvent):
        """
        Dispatch event to all matching subscriptions
        
        Args:
            event: Webhook event to dispatch
        """
        subscriptions = self.registry.list_subscriptions(enabled_only=True)
        
        # Filter subscriptions based on event
        matching_subscriptions = [
            sub for sub in subscriptions
            if sub.event_filter.matches(event)
        ]
        
        if not matching_subscriptions:
            log.debug(f"No matching subscriptions for event {event.event_type}")
            return
        
        log.info(f"Dispatching event {event.event_type} to {len(matching_subscriptions)} subscriptions")
        
        # Queue deliveries
        for subscription in matching_subscriptions:
            await self.delivery_queue.put((event, subscription))
    
    async def _delivery_worker(self):
        """Background worker for processing webhook deliveries"""
        while self._running:
            try:
                # Get next delivery from queue
                event, subscription = await asyncio.wait_for(
                    self.delivery_queue.get(),
                    timeout=1.0
                )
                
                # Attempt delivery with retries
                await self._deliver_with_retries(event, subscription)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                log.error(f"Delivery worker error: {e}")
    
    async def _deliver_with_retries(
        self,
        event: WebhookEvent,
        subscription: WebhookSubscription
    ):
        """
        Attempt webhook delivery with exponential backoff retry
        
        Args:
            event: Event to deliver
            subscription: Target subscription
        """
        max_retries = subscription.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                result = await self._deliver_once(event, subscription)
                
                if result.success:
                    self.registry.update_statistics(
                        subscription.id,
                        success=True
                    )
                    log.info(
                        f"Webhook delivered successfully to {subscription.name} "
                        f"(status={result.status_code}, latency={result.latency_ms:.1f}ms)"
                    )
                    return
                
                # Failed, check if we should retry
                if attempt < max_retries:
                    # Exponential backoff: 1s, 2s, 4s, 8s...
                    delay = 2 ** attempt
                    log.warning(
                        f"Webhook delivery failed to {subscription.name} "
                        f"(attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay}s: {result.error}"
                    )
                    await asyncio.sleep(delay)
                else:
                    # Max retries reached
                    self.registry.update_statistics(
                        subscription.id,
                        success=False,
                        error=result.error
                    )
                    log.error(
                        f"Webhook delivery failed to {subscription.name} "
                        f"after {max_retries + 1} attempts: {result.error}"
                    )
                    
            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries:
                    delay = 2 ** attempt
                    log.warning(
                        f"Webhook delivery exception for {subscription.name}, "
                        f"retrying in {delay}s: {error_msg}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.registry.update_statistics(
                        subscription.id,
                        success=False,
                        error=error_msg
                    )
                    log.error(
                        f"Webhook delivery failed with exception for {subscription.name}: {error_msg}"
                    )
    
    async def _deliver_once(
        self,
        event: WebhookEvent,
        subscription: WebhookSubscription
    ) -> DeliveryResult:
        """
        Single webhook delivery attempt
        
        Args:
            event: Event to deliver
            subscription: Target subscription
            
        Returns:
            Delivery result
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare payload
            payload = event.model_dump_json().encode('utf-8')
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Pulsai-Webhook/1.0',
                'X-Pulsai-Event': event.event_type.value,
                'X-Pulsai-Event-Id': event.event_id,
                'X-Pulsai-Timestamp': event.timestamp.isoformat(),
                **subscription.custom_headers
            }
            
            # Add signature if secret is provided
            if subscription.secret:
                signature_header = WebhookSecurity.get_signature_header(
                    payload,
                    subscription.secret
                )
                headers.update(signature_header)
            
            # Send request
            async with httpx.AsyncClient(timeout=subscription.timeout) as client:
                response = await client.post(
                    str(subscription.url),
                    content=payload,
                    headers=headers
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Check response
                if 200 <= response.status_code < 300:
                    return DeliveryResult(
                        success=True,
                        status_code=response.status_code,
                        latency_ms=latency_ms
                    )
                else:
                    return DeliveryResult(
                        success=False,
                        status_code=response.status_code,
                        error=f"HTTP {response.status_code}: {response.text[:200]}",
                        latency_ms=latency_ms
                    )
                    
        except httpx.TimeoutException:
            latency_ms = (time.time() - start_time) * 1000
            return DeliveryResult(
                success=False,
                error="Request timeout",
                latency_ms=latency_ms
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return DeliveryResult(
                success=False,
                error=str(e),
                latency_ms=latency_ms
            )


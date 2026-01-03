"""
Pulsai Webhooks API Router

Endpoints for managing webhook subscriptions and testing deliveries
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, Field
from loguru import logger as log

from pulsai.webhooks import (
    WebhookEvent,
    EventType,
    WebhookDispatcher,
    WebhookRegistry,
    WebhookSecurity
)
from pulsai.webhooks.registry import WebhookSubscription
from pulsai.webhooks.events import EventFilter


router = APIRouter()

# Global instances
webhook_registry: Optional[WebhookRegistry] = None
webhook_dispatcher: Optional[WebhookDispatcher] = None


def get_webhook_registry() -> WebhookRegistry:
    """Get or initialize webhook registry"""
    global webhook_registry
    if webhook_registry is None:
        webhook_registry = WebhookRegistry()
    return webhook_registry


def get_webhook_dispatcher() -> WebhookDispatcher:
    """Get or initialize webhook dispatcher"""
    global webhook_dispatcher, webhook_registry
    if webhook_dispatcher is None:
        if webhook_registry is None:
            webhook_registry = WebhookRegistry()
        webhook_dispatcher = WebhookDispatcher(webhook_registry)
    return webhook_dispatcher


class CreateWebhookRequest(BaseModel):
    """Request to create webhook subscription"""
    name: str = Field(..., description="Subscription name")
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    event_types: List[EventType] = Field(default_factory=list, description="Event types to subscribe to")
    secret: Optional[str] = Field(None, description="Webhook secret (auto-generated if not provided)")
    max_retries: int = Field(3, ge=0, le=10)
    timeout: int = Field(30, ge=1, le=300)
    custom_headers: Dict[str, str] = Field(default_factory=dict)


class UpdateWebhookRequest(BaseModel):
    """Request to update webhook subscription"""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    event_types: Optional[List[EventType]] = None
    enabled: Optional[bool] = None
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    timeout: Optional[int] = Field(None, ge=1, le=300)
    custom_headers: Optional[Dict[str, str]] = None


class TestWebhookRequest(BaseModel):
    """Request to test webhook delivery"""
    url: HttpUrl
    event_type: EventType = EventType.CUSTOM
    test_data: Dict[str, Any] = Field(default_factory=dict)
    secret: Optional[str] = None


@router.get("/webhooks", response_model=List[WebhookSubscription])
async def list_webhooks(
    enabled_only: bool = False,
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """List all webhook subscriptions"""
    return registry.list_subscriptions(enabled_only=enabled_only)


@router.post("/webhooks", status_code=status.HTTP_201_CREATED, response_model=WebhookSubscription)
async def create_webhook(
    request: CreateWebhookRequest,
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """Create a new webhook subscription"""
    try:
        # Generate secret if not provided
        secret = request.secret or WebhookSecurity.generate_secret()
        
        # Create subscription
        subscription = WebhookSubscription(
            name=request.name,
            url=request.url,
            secret=secret,
            event_filter=EventFilter(event_types=request.event_types),
            max_retries=request.max_retries,
            timeout=request.timeout,
            custom_headers=request.custom_headers,
            enabled=True
        )
        
        subscription_id = registry.add_subscription(subscription)
        
        log.info(f"Webhook subscription created: {request.name} ({subscription_id})")
        
        return subscription
        
    except Exception as e:
        log.error(f"Failed to create webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/webhooks/{subscription_id}", response_model=WebhookSubscription)
async def get_webhook(
    subscription_id: str,
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """Get webhook subscription details"""
    subscription = registry.get_subscription(subscription_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook subscription not found: {subscription_id}"
        )
    
    return subscription


@router.patch("/webhooks/{subscription_id}", response_model=WebhookSubscription)
async def update_webhook(
    subscription_id: str,
    request: UpdateWebhookRequest,
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """Update webhook subscription"""
    # Prepare updates
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.url is not None:
        updates["url"] = request.url
    if request.event_types is not None:
        updates["event_filter"] = EventFilter(event_types=request.event_types)
    if request.enabled is not None:
        updates["enabled"] = request.enabled
    if request.max_retries is not None:
        updates["max_retries"] = request.max_retries
    if request.timeout is not None:
        updates["timeout"] = request.timeout
    if request.custom_headers is not None:
        updates["custom_headers"] = request.custom_headers
    
    subscription = registry.update_subscription(subscription_id, updates)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook subscription not found: {subscription_id}"
        )
    
    return subscription


@router.delete("/webhooks/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    subscription_id: str,
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """Delete webhook subscription"""
    success = registry.remove_subscription(subscription_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook subscription not found: {subscription_id}"
        )


@router.post("/webhooks/test")
async def test_webhook(
    request: TestWebhookRequest,
    dispatcher: WebhookDispatcher = Depends(get_webhook_dispatcher)
):
    """Test webhook delivery"""
    try:
        import uuid
        from datetime import datetime
        
        # Create test event
        test_event = WebhookEvent(
            event_id=str(uuid.uuid4()),
            event_type=request.event_type,
            timestamp=datetime.utcnow(),
            data=request.test_data,
            source="pulsai-test"
        )
        
        # Create temporary subscription
        temp_subscription = WebhookSubscription(
            name="Test Webhook",
            url=request.url,
            secret=request.secret,
            max_retries=0,
            timeout=10
        )
        
        # Attempt delivery
        result = await dispatcher._deliver_once(test_event, temp_subscription)
        
        if result.success:
            return {
                "success": True,
                "status_code": result.status_code,
                "latency_ms": result.latency_ms
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "status_code": result.status_code,
                "latency_ms": result.latency_ms
            }
            
    except Exception as e:
        log.error(f"Webhook test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/webhooks/statistics/overview")
async def get_webhook_statistics(
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """Get overall webhook statistics"""
    return registry.get_statistics()


@router.get("/webhooks/events/types")
async def list_event_types():
    """List all available event types"""
    return {
        "event_types": [
            {
                "type": event_type.value,
                "description": event_type.name.replace('_', ' ').title()
            }
            for event_type in EventType
        ]
    }


@router.post("/webhooks/{subscription_id}/regenerate-secret")
async def regenerate_webhook_secret(
    subscription_id: str,
    registry: WebhookRegistry = Depends(get_webhook_registry)
):
    """Regenerate webhook secret"""
    new_secret = WebhookSecurity.generate_secret()
    
    subscription = registry.update_subscription(
        subscription_id,
        {"secret": new_secret}
    )
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook subscription not found: {subscription_id}"
        )
    
    return {"secret": new_secret}


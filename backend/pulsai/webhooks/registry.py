"""
Webhook registry for managing webhook subscriptions
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from loguru import logger as log

from .events import EventType, EventFilter


class WebhookSubscription(BaseModel):
    """Webhook subscription configuration"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Subscription name")
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    secret: Optional[str] = Field(None, description="Webhook secret for HMAC signature")
    
    # Filtering
    event_filter: EventFilter = Field(default_factory=EventFilter)
    
    # Configuration
    enabled: bool = True
    max_retries: int = Field(3, ge=0, le=10)
    timeout: int = Field(30, ge=1, le=300)
    
    # Headers
    custom_headers: Dict[str, str] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    # Statistics
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    last_delivery_at: Optional[datetime] = None
    last_error: Optional[str] = None


class WebhookRegistry:
    """Manages webhook subscriptions"""
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        log.info("Webhook registry initialized")
    
    def add_subscription(self, subscription: WebhookSubscription) -> str:
        """
        Add a new webhook subscription
        
        Args:
            subscription: Webhook subscription configuration
            
        Returns:
            Subscription ID
        """
        self.subscriptions[subscription.id] = subscription
        log.info(f"Webhook subscription added: {subscription.name} ({subscription.id})")
        return subscription.id
    
    def remove_subscription(self, subscription_id: str) -> bool:
        """
        Remove a webhook subscription
        
        Args:
            subscription_id: Subscription identifier
            
        Returns:
            True if removed, False if not found
        """
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            log.info(f"Webhook subscription removed: {subscription_id}")
            return True
        return False
    
    def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        """Get subscription by ID"""
        return self.subscriptions.get(subscription_id)
    
    def list_subscriptions(
        self,
        enabled_only: bool = False,
        event_type: Optional[EventType] = None
    ) -> List[WebhookSubscription]:
        """
        List webhook subscriptions
        
        Args:
            enabled_only: Only return enabled subscriptions
            event_type: Filter by event type
            
        Returns:
            List of subscriptions
        """
        subscriptions = list(self.subscriptions.values())
        
        if enabled_only:
            subscriptions = [s for s in subscriptions if s.enabled]
        
        if event_type:
            subscriptions = [
                s for s in subscriptions
                if not s.event_filter.event_types or event_type in s.event_filter.event_types
            ]
        
        return subscriptions
    
    def update_subscription(
        self,
        subscription_id: str,
        updates: Dict[str, Any]
    ) -> Optional[WebhookSubscription]:
        """
        Update subscription configuration
        
        Args:
            subscription_id: Subscription identifier
            updates: Dictionary of fields to update
            
        Returns:
            Updated subscription or None if not found
        """
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(subscription, key):
                setattr(subscription, key, value)
        
        subscription.updated_at = datetime.utcnow()
        log.info(f"Webhook subscription updated: {subscription_id}")
        
        return subscription
    
    def update_statistics(
        self,
        subscription_id: str,
        success: bool,
        error: Optional[str] = None
    ):
        """Update delivery statistics for a subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return
        
        subscription.total_deliveries += 1
        subscription.last_delivery_at = datetime.utcnow()
        
        if success:
            subscription.successful_deliveries += 1
            subscription.last_error = None
        else:
            subscription.failed_deliveries += 1
            subscription.last_error = error
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall webhook statistics"""
        total_subscriptions = len(self.subscriptions)
        enabled_subscriptions = sum(1 for s in self.subscriptions.values() if s.enabled)
        
        total_deliveries = sum(s.total_deliveries for s in self.subscriptions.values())
        successful_deliveries = sum(s.successful_deliveries for s in self.subscriptions.values())
        failed_deliveries = sum(s.failed_deliveries for s in self.subscriptions.values())
        
        success_rate = (
            (successful_deliveries / total_deliveries * 100)
            if total_deliveries > 0
            else 0
        )
        
        return {
            "total_subscriptions": total_subscriptions,
            "enabled_subscriptions": enabled_subscriptions,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "success_rate": round(success_rate, 2)
        }


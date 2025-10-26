"""
Webhook event definitions and types
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Available webhook event types"""
    
    # Chat events
    CHAT_CREATED = "chat.created"
    CHAT_UPDATED = "chat.updated"
    CHAT_DELETED = "chat.deleted"
    CHAT_MESSAGE_ADDED = "chat.message.added"
    CHAT_COMPLETED = "chat.completed"
    
    # Model events
    MODEL_ADDED = "model.added"
    MODEL_REMOVED = "model.removed"
    MODEL_UPDATED = "model.updated"
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    
    # Fine-tuning events
    FINE_TUNE_STARTED = "fine_tune.started"
    FINE_TUNE_COMPLETED = "fine_tune.completed"
    FINE_TUNE_FAILED = "fine_tune.failed"
    
    # System events
    BACKEND_HEALTHY = "backend.healthy"
    BACKEND_UNHEALTHY = "backend.unhealthy"
    SYSTEM_ERROR = "system.error"
    
    # MCP events
    MCP_SERVER_ADDED = "mcp.server.added"
    MCP_SERVER_REMOVED = "mcp.server.removed"
    MCP_TOOL_EXECUTED = "mcp.tool.executed"
    
    # Custom events
    CUSTOM = "custom"


class WebhookEvent(BaseModel):
    """Webhook event payload"""
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Source information
    source: str = Field("pulsai", description="Event source identifier")
    user_id: Optional[str] = Field(None, description="User who triggered the event")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventFilter(BaseModel):
    """Filter configuration for webhook subscriptions"""
    
    event_types: list[EventType] = Field(default_factory=list, description="Event types to filter")
    user_ids: list[str] = Field(default_factory=list, description="Filter by user IDs")
    exclude_event_types: list[EventType] = Field(default_factory=list, description="Event types to exclude")
    
    def matches(self, event: WebhookEvent) -> bool:
        """Check if event matches filter criteria"""
        
        # Check event type inclusion
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check event type exclusion
        if event.event_type in self.exclude_event_types:
            return False
        
        # Check user ID filter
        if self.user_ids and event.user_id not in self.user_ids:
            return False
        
        return True


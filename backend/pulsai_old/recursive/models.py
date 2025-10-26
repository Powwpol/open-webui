"""
Recursive Chat Models

Database models for managing hierarchical chat trees.
"""

from peewee import *
from datetime import datetime
from open_webui.internal.db import DB


class RecursiveChat(Model):
    """
    Represents a chat node in the recursive chat tree.
    Each chat can have a parent (making it a sub-chat) and multiple children.
    """
    
    id = AutoField()
    chat_id = CharField(max_length=255, unique=True, index=True)
    
    # Tree Structure
    parent_chat_id = CharField(max_length=255, null=True, index=True)  # Parent chat (null for root)
    root_chat_id = CharField(max_length=255, index=True)  # Root of the tree
    depth = IntegerField(default=0, index=True)  # Depth in tree (0 = root)
    path = TextField()  # Full path from root (e.g., "root/child1/grandchild2")
    
    # Chat Information
    user_id = CharField(max_length=255, index=True)
    title = CharField(max_length=255)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    updated_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField(null=True, index=True)
    
    # Status
    status = CharField(max_length=50, default="active", index=True)
    # active, completed, failed, cancelled
    
    # Execution Context
    trigger_type = CharField(max_length=50, null=True)
    # manual, auto, conditional, scheduled
    
    trigger_condition = TextField(null=True)  # JSON condition that triggered this sub-chat
    
    # Results
    summary = TextField(null=True)  # Summary of this chat's results
    key_insights = TextField(null=True)  # JSON array of key insights
    
    # Metadata
    model_used = CharField(max_length=255, null=True)
    total_messages = IntegerField(default=0)
    total_tokens = IntegerField(default=0)
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "recursive_chats"
        indexes = (
            (("root_chat_id", "created_at"), False),
            (("parent_chat_id", "created_at"), False),
            (("user_id", "status"), False),
        )


class RecursiveTrigger(Model):
    """
    Defines rules for automatically triggering sub-chats.
    """
    
    id = AutoField()
    name = CharField(max_length=255)
    description = TextField(null=True)
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Trigger Conditions
    trigger_type = CharField(max_length=50, index=True)
    # keyword, sentiment, length, quality_score, custom
    
    condition = TextField()  # JSON condition definition
    
    # Action
    sub_chat_template = TextField(null=True)  # Template for sub-chat prompt
    max_depth = IntegerField(default=3)  # Maximum recursion depth
    model_override = CharField(max_length=255, null=True)  # Use specific model
    
    # Status
    enabled = BooleanField(default=True, index=True)
    
    # Statistics
    trigger_count = IntegerField(default=0)
    success_count = IntegerField(default=0)
    
    # Metadata
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "recursive_triggers"


class ChatRelationship(Model):
    """
    Explicit parent-child relationships between chats.
    Provides faster querying than traversing RecursiveChat.
    """
    
    id = AutoField()
    parent_chat_id = CharField(max_length=255, index=True)
    child_chat_id = CharField(max_length=255, index=True)
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    # Relationship metadata
    relationship_type = CharField(max_length=50, default="sub_chat")
    # sub_chat, parallel, continuation, branch
    
    order = IntegerField(default=0)  # Order among siblings
    
    class Meta:
        database = DB
        table_name = "chat_relationships"
        indexes = (
            (("parent_chat_id", "order"), False),
            (("child_chat_id",), False),
        )


class RecursiveExecution(Model):
    """
    Tracks execution of recursive chat workflows.
    """
    
    id = AutoField()
    execution_id = CharField(max_length=255, unique=True, index=True)
    root_chat_id = CharField(max_length=255, index=True)
    user_id = CharField(max_length=255, index=True)
    
    # Timestamps
    started_at = DateTimeField(default=datetime.utcnow, index=True)
    completed_at = DateTimeField(null=True, index=True)
    
    # Status
    status = CharField(max_length=50, default="running", index=True)
    # running, completed, failed, cancelled
    
    # Execution Stats
    total_chats_created = IntegerField(default=0)
    total_messages = IntegerField(default=0)
    total_tokens = IntegerField(default=0)
    max_depth_reached = IntegerField(default=0)
    
    # Configuration
    max_depth_limit = IntegerField(default=5)
    max_chats_limit = IntegerField(default=20)
    timeout_seconds = IntegerField(default=3600)  # 1 hour default
    
    # Results
    result_summary = TextField(null=True)
    error_message = TextField(null=True)
    
    # Metadata
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "recursive_executions"


# Initialize tables
def create_tables():
    """Create recursive chat tables if they don't exist."""
    with DB.atomic():
        DB.create_tables([
            RecursiveChat,
            RecursiveTrigger,
            ChatRelationship,
            RecursiveExecution
        ], safe=True)


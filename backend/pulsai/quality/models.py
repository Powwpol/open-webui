"""
Quality Scoring Models

Defines database models for tracking interaction quality metrics.
"""

from peewee import *
from datetime import datetime
from pulsai.internal.db import DB

# Quality Score Model
class QualityScore(Model):
    """
    Stores quality metrics for chat interactions.
    Used for monitoring conversation quality and feeding fine-tuning pipeline.
    """
    
    id = AutoField()
    chat_id = CharField(max_length=255, index=True)
    message_id = CharField(max_length=255, index=True, null=True)
    user_id = CharField(max_length=255, index=True)
    
    # Timestamp
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    
    # Quality Metrics (0-1 range)
    user_feedback_score = FloatField(null=True)  # Explicit user rating
    engagement_score = FloatField(null=True)     # Interaction depth
    coherence_score = FloatField(null=True)      # Response quality
    relevance_score = FloatField(null=True)      # Topic relevance
    helpfulness_score = FloatField(null=True)    # Perceived helpfulness
    
    # Composite Score
    overall_score = FloatField(null=True, index=True)  # Weighted average
    
    # Behavioral Signals
    response_length = IntegerField(null=True)
    user_continued = BooleanField(default=False)  # Did user continue chat?
    user_edited = BooleanField(default=False)     # Did user edit prompt?
    user_regenerated = BooleanField(default=False) # Did user regenerate?
    time_to_next_message = FloatField(null=True)  # Seconds to next message
    
    # Context
    model_used = CharField(max_length=255, null=True)
    backend_used = CharField(max_length=50, null=True)
    prompt_tokens = IntegerField(null=True)
    completion_tokens = IntegerField(null=True)
    latency_ms = FloatField(null=True)
    
    # Metadata
    metadata = TextField(null=True)  # JSON for additional data
    
    class Meta:
        database = DB
        table_name = "quality_scores"
        indexes = (
            (("chat_id", "created_at"), False),
            (("user_id", "created_at"), False),
            (("overall_score", "created_at"), False),
        )


# User Feedback Model
class UserFeedback(Model):
    """
    Explicit user feedback on AI responses.
    """
    
    id = AutoField()
    chat_id = CharField(max_length=255, index=True)
    message_id = CharField(max_length=255, index=True)
    user_id = CharField(max_length=255, index=True)
    
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    
    # Feedback Type
    feedback_type = CharField(max_length=50)  # thumbs_up, thumbs_down, rating, custom
    rating = IntegerField(null=True)  # 1-5 stars
    
    # Detailed Feedback
    comment = TextField(null=True)
    categories = TextField(null=True)  # JSON array: ["helpful", "accurate", "clear"]
    
    # Action Taken
    regenerated = BooleanField(default=False)
    edited = BooleanField(default=False)
    copied = BooleanField(default=False)
    
    class Meta:
        database = DB
        table_name = "user_feedback"
        indexes = (
            (("user_id", "created_at"), False),
            (("feedback_type", "created_at"), False),
        )


# Quality Aggregation Model
class QualityAggregate(Model):
    """
    Aggregated quality metrics per model/user/time period.
    """
    
    id = AutoField()
    
    # Aggregation Dimensions
    period = CharField(max_length=20)  # hourly, daily, weekly
    timestamp = DateTimeField(index=True)
    model = CharField(max_length=255, null=True, index=True)
    backend = CharField(max_length=50, null=True, index=True)
    user_id = CharField(max_length=255, null=True, index=True)
    
    # Aggregated Metrics
    total_interactions = IntegerField(default=0)
    avg_overall_score = FloatField(null=True)
    avg_engagement_score = FloatField(null=True)
    avg_coherence_score = FloatField(null=True)
    avg_relevance_score = FloatField(null=True)
    
    # Behavioral Aggregates
    continuation_rate = FloatField(null=True)  # % of chats continued
    regeneration_rate = FloatField(null=True)  # % of responses regenerated
    avg_response_length = FloatField(null=True)
    avg_latency_ms = FloatField(null=True)
    
    # Feedback Aggregates
    positive_feedback_count = IntegerField(default=0)
    negative_feedback_count = IntegerField(default=0)
    feedback_rate = FloatField(null=True)  # % of interactions with feedback
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    class Meta:
        database = DB
        table_name = "quality_aggregates"
        indexes = (
            (("period", "timestamp", "model"), False),
            (("timestamp", "avg_overall_score"), False),
        )


# Initialize tables
def create_tables():
    """Create quality scoring tables if they don't exist."""
    with DB.atomic():
        DB.create_tables([QualityScore, UserFeedback, QualityAggregate], safe=True)


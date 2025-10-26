"""
Fine-Tuning Models

Database models for managing fine-tuning jobs and datasets.
"""

from peewee import *
from datetime import datetime
from open_webui.internal.db import DB


class FineTuneDataset(Model):
    """
    Training datasets built from high-quality interactions.
    """
    
    id = AutoField()
    name = CharField(max_length=255, index=True)
    description = TextField(null=True)
    
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    # Dataset Configuration
    source_model = CharField(max_length=255, null=True)  # Model to improve
    min_quality_score = FloatField(default=0.7)  # Minimum score for inclusion
    max_samples = IntegerField(null=True)  # Maximum number of samples
    
    # Dataset Stats
    total_samples = IntegerField(default=0)
    avg_quality_score = FloatField(null=True)
    date_range_start = DateTimeField(null=True)
    date_range_end = DateTimeField(null=True)
    
    # Storage
    file_path = CharField(max_length=512, null=True)  # Path to .jsonl file
    file_size_bytes = IntegerField(null=True)
    
    # Status
    status = CharField(max_length=50, default="building")  # building, ready, archived
    
    # Metadata
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "finetune_datasets"


class FineTuneJob(Model):
    """
    Fine-tuning job tracker.
    """
    
    id = AutoField()
    job_id = CharField(max_length=255, unique=True, index=True)  # Unique job identifier
    
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    started_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    
    # Job Configuration
    dataset_id = IntegerField(index=True)  # FK to FineTuneDataset
    base_model = CharField(max_length=255)  # Base model to fine-tune
    output_model_name = CharField(max_length=255)  # Name for fine-tuned model
    backend = CharField(max_length=50, default="ollama")  # ollama, vllm, openai
    
    # Training Parameters
    epochs = IntegerField(default=3)
    learning_rate = FloatField(default=1e-5)
    batch_size = IntegerField(default=4)
    temperature = FloatField(default=1.0, null=True)
    
    # Status
    status = CharField(max_length=50, default="pending", index=True)
    # pending, queued, running, completed, failed, cancelled
    
    progress = FloatField(default=0.0)  # 0.0 to 1.0
    
    # Results
    final_loss = FloatField(null=True)
    validation_accuracy = FloatField(null=True)
    training_duration_seconds = IntegerField(null=True)
    
    # Error Handling
    error_message = TextField(null=True)
    retry_count = IntegerField(default=0)
    max_retries = IntegerField(default=3)
    
    # Resources
    gpu_used = BooleanField(default=False)
    memory_peak_mb = IntegerField(null=True)
    
    # Metadata
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "finetune_jobs"
        indexes = (
            (("status", "created_at"), False),
            (("backend", "status"), False),
        )


class FineTuneSample(Model):
    """
    Individual training samples in datasets.
    """
    
    id = AutoField()
    dataset_id = IntegerField(index=True)  # FK to FineTuneDataset
    
    # Sample Data
    prompt = TextField()
    completion = TextField()
    
    # Quality Metrics
    quality_score = FloatField(index=True)
    source_chat_id = CharField(max_length=255, null=True)
    source_message_id = CharField(max_length=255, null=True)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    model_used = CharField(max_length=255, null=True)
    user_id = CharField(max_length=255, null=True, index=True)
    
    # Tags for filtering
    tags = TextField(null=True)  # JSON array
    
    class Meta:
        database = DB
        table_name = "finetune_samples"
        indexes = (
            (("dataset_id", "quality_score"), False),
        )


class FineTuneSchedule(Model):
    """
    Scheduled automatic fine-tuning runs.
    """
    
    id = AutoField()
    name = CharField(max_length=255)
    enabled = BooleanField(default=True, index=True)
    
    created_at = DateTimeField(default=datetime.utcnow)
    last_run_at = DateTimeField(null=True, index=True)
    next_run_at = DateTimeField(null=True, index=True)
    
    # Schedule Configuration
    schedule_type = CharField(max_length=50)  # daily, weekly, monthly, quality_threshold
    schedule_cron = CharField(max_length=100, null=True)  # Cron expression
    
    # Trigger Conditions
    min_new_samples = IntegerField(default=100)  # Minimum new high-quality samples
    quality_threshold = FloatField(default=0.75)  # Quality threshold to trigger
    
    # Job Configuration (for auto-created jobs)
    base_model = CharField(max_length=255)
    backend = CharField(max_length=50, default="ollama")
    epochs = IntegerField(default=3)
    learning_rate = FloatField(default=1e-5)
    
    # Statistics
    total_runs = IntegerField(default=0)
    successful_runs = IntegerField(default=0)
    failed_runs = IntegerField(default=0)
    
    # Metadata
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "finetune_schedules"


class ModelPerformance(Model):
    """
    Track performance metrics of fine-tuned models.
    """
    
    id = AutoField()
    model_name = CharField(max_length=255, index=True)
    job_id = CharField(max_length=255, null=True)  # FK to FineTuneJob
    
    created_at = DateTimeField(default=datetime.utcnow, index=True)
    
    # Performance Metrics (measured after deployment)
    avg_quality_score = FloatField(null=True)
    avg_user_rating = FloatField(null=True)
    total_inferences = IntegerField(default=0)
    positive_feedback_count = IntegerField(default=0)
    negative_feedback_count = IntegerField(default=0)
    
    # Comparison with Base Model
    base_model = CharField(max_length=255, null=True)
    improvement_percentage = FloatField(null=True)  # % improvement over base
    
    # Deployment Status
    is_deployed = BooleanField(default=False, index=True)
    deployed_at = DateTimeField(null=True)
    deprecated_at = DateTimeField(null=True)
    
    # Metadata
    metadata = TextField(null=True)  # JSON
    
    class Meta:
        database = DB
        table_name = "model_performance"


# Initialize tables
def create_tables():
    """Create fine-tuning tables if they don't exist."""
    with DB.atomic():
        DB.create_tables([
            FineTuneDataset,
            FineTuneJob,
            FineTuneSample,
            FineTuneSchedule,
            ModelPerformance
        ], safe=True)


"""
Fine-Tuning Scheduler

Automated scheduling for fine-tuning jobs.
"""

import asyncio
from typing import Optional
from datetime import datetime, timedelta
from loguru import logger as log
from croniter import croniter

from .models import FineTuneSchedule, FineTuneJob, FineTuneDataset
from .dataset_builder import DatasetBuilder
from .job_runner import JobRunner
from open_webui.quality.models import QualityScore


class FineTuneScheduler:
    """
    Manages automatic fine-tuning job scheduling.
    """
    
    def __init__(self):
        self.dataset_builder = DatasetBuilder()
        self.job_runner = JobRunner()
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduler background task."""
        if not self._task or self._task.done():
            self._stop_event.clear()
            self._task = asyncio.create_task(self._scheduler_loop())
            log.info("Fine-tuning scheduler started")
    
    async def stop(self):
        """Stop the scheduler."""
        if self._task:
            self._stop_event.set()
            await self._task
            log.info("Fine-tuning scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop - checks schedules every minute."""
        
        while not self._stop_event.is_set():
            try:
                await self._check_schedules()
            except Exception as e:
                log.error(f"Scheduler error: {e}")
            
            # Wait 1 minute before next check
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                pass
    
    async def _check_schedules(self):
        """
        Check all active schedules and trigger jobs if needed.
        """
        
        now = datetime.utcnow()
        
        schedules = (
            FineTuneSchedule
            .select()
            .where(FineTuneSchedule.enabled == True)
        )
        
        for schedule in schedules:
            try:
                should_run = False
                
                # Check schedule type
                if schedule.schedule_type == "cron":
                    should_run = self._check_cron_schedule(schedule, now)
                elif schedule.schedule_type == "quality_threshold":
                    should_run = await self._check_quality_threshold(schedule)
                elif schedule.schedule_type == "sample_count":
                    should_run = await self._check_sample_count(schedule)
                
                if should_run:
                    await self._trigger_schedule(schedule)
                    
            except Exception as e:
                log.error(f"Error checking schedule {schedule.id}: {e}")
    
    def _check_cron_schedule(
        self, schedule: FineTuneSchedule, now: datetime
    ) -> bool:
        """Check if cron schedule should trigger."""
        
        if not schedule.schedule_cron:
            return False
        
        try:
            cron = croniter(schedule.schedule_cron, schedule.last_run_at or now)
            next_run = cron.get_next(datetime)
            
            # Update next_run_at if needed
            if schedule.next_run_at is None or schedule.next_run_at != next_run:
                schedule.next_run_at = next_run
                schedule.save()
            
            # Should run if next_run is in the past
            return next_run <= now
            
        except Exception as e:
            log.error(f"Invalid cron expression for schedule {schedule.id}: {e}")
            return False
    
    async def _check_quality_threshold(self, schedule: FineTuneSchedule) -> bool:
        """
        Check if quality threshold is met.
        
        Triggers when:
        - Average quality score drops below threshold
        - OR significant new high-quality samples available
        """
        
        try:
            # Get recent quality scores
            since = schedule.last_run_at or (datetime.utcnow() - timedelta(days=7))
            
            recent_scores = (
                QualityScore
                .select()
                .where(QualityScore.created_at >= since)
                .where(QualityScore.model_used == schedule.base_model)
            )
            
            if not recent_scores:
                return False
            
            scores_list = list(recent_scores)
            avg_score = sum(s.overall_score or 0 for s in scores_list) / len(scores_list)
            
            # Count high-quality samples
            high_quality = sum(
                1 for s in scores_list
                if s.overall_score and s.overall_score >= schedule.quality_threshold
            )
            
            # Trigger if:
            # 1. Enough new high-quality samples
            if high_quality >= schedule.min_new_samples:
                log.info(f"Schedule {schedule.id}: {high_quality} new high-quality samples")
                return True
            
            # 2. Average quality below threshold (model degradation)
            if avg_score < schedule.quality_threshold:
                log.info(f"Schedule {schedule.id}: quality below threshold ({avg_score:.2f} < {schedule.quality_threshold})")
                return True
            
            return False
            
        except Exception as e:
            log.error(f"Error checking quality threshold: {e}")
            return False
    
    async def _check_sample_count(self, schedule: FineTuneSchedule) -> bool:
        """Check if enough new samples accumulated."""
        
        try:
            since = schedule.last_run_at or (datetime.utcnow() - timedelta(days=30))
            
            new_samples = (
                QualityScore
                .select()
                .where(QualityScore.created_at >= since)
                .where(QualityScore.overall_score >= schedule.quality_threshold)
                .where(QualityScore.model_used == schedule.base_model)
                .count()
            )
            
            if new_samples >= schedule.min_new_samples:
                log.info(f"Schedule {schedule.id}: {new_samples} new samples (>= {schedule.min_new_samples})")
                return True
            
            return False
            
        except Exception as e:
            log.error(f"Error checking sample count: {e}")
            return False
    
    async def _trigger_schedule(self, schedule: FineTuneSchedule):
        """
        Trigger a scheduled fine-tuning job.
        """
        
        try:
            log.info(f"Triggering schedule: {schedule.name}")
            
            # Build dataset
            dataset = self.dataset_builder.build_dataset(
                name=f"{schedule.name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                source_model=schedule.base_model,
                min_quality_score=schedule.quality_threshold,
                max_samples=None,
                days_back=30
            )
            
            if not dataset:
                log.error(f"Failed to build dataset for schedule {schedule.id}")
                schedule.failed_runs += 1
                schedule.save()
                return
            
            # Create job
            job = await self.job_runner.create_job(
                dataset_id=dataset.id,
                base_model=schedule.base_model,
                output_model_name=f"{schedule.base_model}_finetuned_{datetime.utcnow().strftime('%Y%m%d')}",
                backend=schedule.backend,
                epochs=schedule.epochs,
                learning_rate=schedule.learning_rate
            )
            
            # Update schedule
            schedule.last_run_at = datetime.utcnow()
            schedule.total_runs += 1
            
            # Calculate next run for cron schedules
            if schedule.schedule_type == "cron" and schedule.schedule_cron:
                cron = croniter(schedule.schedule_cron, schedule.last_run_at)
                schedule.next_run_at = cron.get_next(datetime)
            
            schedule.save()
            
            log.info(f"Scheduled job {job.job_id} created for schedule {schedule.name}")
            
        except Exception as e:
            log.error(f"Failed to trigger schedule {schedule.id}: {e}")
            schedule.failed_runs += 1
            schedule.save()
    
    def create_schedule(
        self,
        name: str,
        schedule_type: str,
        base_model: str,
        backend: str = "ollama",
        schedule_cron: Optional[str] = None,
        min_new_samples: int = 100,
        quality_threshold: float = 0.75,
        epochs: int = 3,
        learning_rate: float = 1e-5
    ) -> Optional[FineTuneSchedule]:
        """
        Create a new fine-tuning schedule.
        
        Args:
            name: Schedule name
            schedule_type: "cron", "quality_threshold", or "sample_count"
            base_model: Model to fine-tune
            backend: "ollama" or "vllm"
            schedule_cron: Cron expression (for cron type)
            min_new_samples: Minimum new samples to trigger
            quality_threshold: Quality threshold
            epochs: Training epochs
            learning_rate: Learning rate
        
        Returns:
            FineTuneSchedule instance or None
        """
        
        try:
            # Validate cron expression if provided
            if schedule_type == "cron":
                if not schedule_cron:
                    raise ValueError("Cron expression required for cron schedule")
                croniter(schedule_cron)  # Validate
            
            schedule = FineTuneSchedule.create(
                name=name,
                enabled=True,
                schedule_type=schedule_type,
                schedule_cron=schedule_cron,
                min_new_samples=min_new_samples,
                quality_threshold=quality_threshold,
                base_model=base_model,
                backend=backend,
                epochs=epochs,
                learning_rate=learning_rate
            )
            
            # Set initial next_run_at for cron schedules
            if schedule_type == "cron" and schedule_cron:
                cron = croniter(schedule_cron, datetime.utcnow())
                schedule.next_run_at = cron.get_next(datetime)
                schedule.save()
            
            log.info(f"Created schedule: {name}")
            return schedule
            
        except Exception as e:
            log.error(f"Failed to create schedule: {e}")
            return None
    
    def get_schedule_status(self, schedule_id: int) -> dict:
        """Get status of a schedule."""
        
        try:
            schedule = FineTuneSchedule.get(FineTuneSchedule.id == schedule_id)
            
            return {
                "id": schedule.id,
                "name": schedule.name,
                "enabled": schedule.enabled,
                "schedule_type": schedule.schedule_type,
                "last_run_at": schedule.last_run_at.isoformat() if schedule.last_run_at else None,
                "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None,
                "total_runs": schedule.total_runs,
                "successful_runs": schedule.successful_runs,
                "failed_runs": schedule.failed_runs,
                "success_rate": (schedule.successful_runs / schedule.total_runs * 100) if schedule.total_runs > 0 else 0,
                "base_model": schedule.base_model,
                "backend": schedule.backend
            }
            
        except Exception as e:
            log.error(f"Failed to get schedule status: {e}")
            return {"error": str(e)}


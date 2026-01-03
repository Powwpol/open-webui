"""
Fine-Tuning API Router

Endpoints for managing fine-tuning datasets, jobs, and schedules.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger as log

from pulsai.finetuning.dataset_builder import DatasetBuilder
from pulsai.finetuning.job_runner import JobRunner
from pulsai.finetuning.scheduler import FineTuneScheduler
from pulsai.finetuning.models import FineTuneDataset, FineTuneJob, FineTuneSchedule


router = APIRouter()


# Pydantic Models
class DatasetCreateRequest(BaseModel):
    name: str = Field(..., description="Dataset name")
    source_model: Optional[str] = None
    min_quality_score: float = Field(0.7, ge=0.0, le=1.0)
    max_samples: Optional[int] = Field(None, ge=1)
    days_back: int = Field(30, ge=1, le=365)
    include_user_feedback_only: bool = False
    tags: Optional[List[str]] = None


class JobCreateRequest(BaseModel):
    dataset_id: int
    base_model: str
    output_model_name: str
    backend: str = Field("ollama", pattern="^(ollama|vllm)$")
    epochs: int = Field(3, ge=1, le=100)
    learning_rate: float = Field(1e-5, gt=0, le=1)
    batch_size: int = Field(4, ge=1, le=128)
    temperature: Optional[float] = Field(None, ge=0, le=2)


class ScheduleCreateRequest(BaseModel):
    name: str
    schedule_type: str = Field(..., pattern="^(cron|quality_threshold|sample_count)$")
    base_model: str
    backend: str = Field("ollama", pattern="^(ollama|vllm)$")
    schedule_cron: Optional[str] = None
    min_new_samples: int = Field(100, ge=1)
    quality_threshold: float = Field(0.75, ge=0.0, le=1.0)
    epochs: int = Field(3, ge=1, le=100)
    learning_rate: float = Field(1e-5, gt=0, le=1)


# Initialize managers
dataset_builder = DatasetBuilder()
job_runner = JobRunner()
scheduler = FineTuneScheduler()


# ======================================
# DATASET ENDPOINTS
# ======================================

@router.post("/datasets", status_code=status.HTTP_201_CREATED)
async def create_dataset(request: DatasetCreateRequest):
    """
    Create a new fine-tuning dataset from high-quality interactions.
    """
    
    try:
        dataset = dataset_builder.build_dataset(
            name=request.name,
            source_model=request.source_model,
            min_quality_score=request.min_quality_score,
            max_samples=request.max_samples,
            days_back=request.days_back,
            include_user_feedback_only=request.include_user_feedback_only,
            tags=request.tags
        )
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create dataset"
            )
        
        return {
            "dataset_id": dataset.id,
            "name": dataset.name,
            "total_samples": dataset.total_samples,
            "avg_quality_score": dataset.avg_quality_score,
            "file_path": dataset.file_path,
            "status": dataset.status
        }
    
    except Exception as e:
        log.error(f"Dataset creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/datasets")
async def list_datasets(limit: int = 50, status_filter: Optional[str] = None):
    """
    List all fine-tuning datasets.
    """
    
    try:
        query = FineTuneDataset.select().order_by(FineTuneDataset.created_at.desc()).limit(limit)
        
        if status_filter:
            query = query.where(FineTuneDataset.status == status_filter)
        
        datasets = []
        for ds in query:
            datasets.append({
                "dataset_id": ds.id,
                "name": ds.name,
                "total_samples": ds.total_samples,
                "avg_quality_score": ds.avg_quality_score,
                "source_model": ds.source_model,
                "status": ds.status,
                "created_at": ds.created_at.isoformat(),
                "file_size_mb": ds.file_size_bytes / (1024 * 1024) if ds.file_size_bytes else 0
            })
        
        return {"datasets": datasets}
    
    except Exception as e:
        log.error(f"List datasets error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: int):
    """
    Get detailed information about a dataset.
    """
    
    try:
        stats = dataset_builder.get_dataset_stats(dataset_id)
        return stats
    
    except Exception as e:
        log.error(f"Get dataset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset {dataset_id} not found"
        )


@router.post("/datasets/{dataset_id}/augment")
async def augment_dataset(dataset_id: int, additional_samples: int = 100):
    """
    Add more samples to an existing dataset.
    """
    
    try:
        success = dataset_builder.augment_dataset(dataset_id, additional_samples)
        
        if success:
            return {"message": f"Dataset {dataset_id} augmented successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to augment dataset"
            )
    
    except Exception as e:
        log.error(f"Augment dataset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ======================================
# JOB ENDPOINTS
# ======================================

@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(request: JobCreateRequest):
    """
    Create a new fine-tuning job.
    """
    
    try:
        job = await job_runner.create_job(
            dataset_id=request.dataset_id,
            base_model=request.base_model,
            output_model_name=request.output_model_name,
            backend=request.backend,
            epochs=request.epochs,
            learning_rate=request.learning_rate,
            batch_size=request.batch_size,
            temperature=request.temperature
        )
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create fine-tuning job"
            )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "base_model": job.base_model,
            "output_model_name": job.output_model_name,
            "backend": job.backend,
            "created_at": job.created_at.isoformat()
        }
    
    except Exception as e:
        log.error(f"Job creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/jobs")
async def list_jobs(
    status_filter: Optional[str] = None,
    backend: Optional[str] = None,
    limit: int = 50
):
    """
    List fine-tuning jobs.
    """
    
    try:
        jobs = job_runner.list_jobs(
            status=status_filter,
            backend=backend,
            limit=limit
        )
        
        return {"jobs": jobs}
    
    except Exception as e:
        log.error(f"List jobs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get status of a specific fine-tuning job.
    """
    
    try:
        status_info = job_runner.get_job_status(job_id)
        
        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_info["error"]
            )
        
        return status_info
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Get job status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """
    Cancel a running fine-tuning job.
    """
    
    try:
        success = await job_runner.cancel_job(job_id)
        
        if success:
            return {"message": f"Job {job_id} cancelled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel job {job_id}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Cancel job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: str):
    """
    Retry a failed fine-tuning job.
    """
    
    try:
        success = await job_runner.retry_job(job_id)
        
        if success:
            return {"message": f"Job {job_id} retry initiated"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot retry job {job_id}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Retry job error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ======================================
# SCHEDULE ENDPOINTS
# ======================================

@router.post("/schedules", status_code=status.HTTP_201_CREATED)
async def create_schedule(request: ScheduleCreateRequest):
    """
    Create a new automatic fine-tuning schedule.
    """
    
    try:
        schedule = scheduler.create_schedule(
            name=request.name,
            schedule_type=request.schedule_type,
            base_model=request.base_model,
            backend=request.backend,
            schedule_cron=request.schedule_cron,
            min_new_samples=request.min_new_samples,
            quality_threshold=request.quality_threshold,
            epochs=request.epochs,
            learning_rate=request.learning_rate
        )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create schedule"
            )
        
        return {
            "schedule_id": schedule.id,
            "name": schedule.name,
            "schedule_type": schedule.schedule_type,
            "enabled": schedule.enabled,
            "next_run_at": schedule.next_run_at.isoformat() if schedule.next_run_at else None
        }
    
    except Exception as e:
        log.error(f"Schedule creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/schedules")
async def list_schedules():
    """
    List all fine-tuning schedules.
    """
    
    try:
        schedules = list(FineTuneSchedule.select().order_by(FineTuneSchedule.created_at.desc()))
        
        results = []
        for s in schedules:
            results.append({
                "schedule_id": s.id,
                "name": s.name,
                "enabled": s.enabled,
                "schedule_type": s.schedule_type,
                "base_model": s.base_model,
                "backend": s.backend,
                "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
                "next_run_at": s.next_run_at.isoformat() if s.next_run_at else None,
                "total_runs": s.total_runs,
                "success_rate": (s.successful_runs / s.total_runs * 100) if s.total_runs > 0 else 0
            })
        
        return {"schedules": results}
    
    except Exception as e:
        log.error(f"List schedules error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: int):
    """
    Get detailed information about a schedule.
    """
    
    try:
        status_info = scheduler.get_schedule_status(schedule_id)
        
        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_info["error"]
            )
        
        return status_info
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Get schedule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/schedules/{schedule_id}")
async def update_schedule(schedule_id: int, enabled: Optional[bool] = None):
    """
    Update schedule settings (e.g., enable/disable).
    """
    
    try:
        schedule = FineTuneSchedule.get(FineTuneSchedule.id == schedule_id)
        
        if enabled is not None:
            schedule.enabled = enabled
            schedule.save()
        
        return {"message": f"Schedule {schedule_id} updated successfully"}
    
    except FineTuneSchedule.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    except Exception as e:
        log.error(f"Update schedule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    """
    Delete a fine-tuning schedule.
    """
    
    try:
        schedule = FineTuneSchedule.get(FineTuneSchedule.id == schedule_id)
        schedule.delete_instance()
        
        return {"message": f"Schedule {schedule_id} deleted successfully"}
    
    except FineTuneSchedule.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule {schedule_id} not found"
        )
    except Exception as e:
        log.error(f"Delete schedule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


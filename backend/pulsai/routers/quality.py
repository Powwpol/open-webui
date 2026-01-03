"""
Quality Scoring API Router

Endpoints for interaction quality scoring and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger as log

from pulsai.quality.scorer import QualityScorer
from pulsai.quality.models import QualityScore, UserFeedback, QualityAggregate


router = APIRouter()


# Pydantic Models
class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str = Field(..., description="thumbs_up, thumbs_down, rating")
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    categories: Optional[List[str]] = None


class QualityStatsRequest(BaseModel):
    model: Optional[str] = None
    days: int = Field(7, ge=1, le=365)


class QualityScoreResponse(BaseModel):
    message_id: str
    overall_score: float
    engagement_score: float
    coherence_score: float
    relevance_score: float
    helpfulness_score: float
    user_feedback_score: Optional[float] = None


# Initialize scorer
scorer = QualityScorer()


@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback for a message.
    
    Updates the quality score with explicit user feedback.
    """
    
    try:
        success = scorer.update_user_feedback(
            message_id=feedback.message_id,
            feedback_type=feedback.feedback_type,
            rating=feedback.rating,
            comment=feedback.comment,
            categories=feedback.categories
        )
        
        if success:
            return {"message": "Feedback recorded successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record feedback"
            )
    
    except Exception as e:
        log.error(f"Feedback submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/scores/{message_id}", response_model=QualityScoreResponse)
async def get_message_score(message_id: str):
    """
    Get quality score for a specific message.
    """
    
    try:
        score = QualityScore.get(QualityScore.message_id == message_id)
        
        return QualityScoreResponse(
            message_id=score.message_id,
            overall_score=score.overall_score or 0.0,
            engagement_score=score.engagement_score or 0.0,
            coherence_score=score.coherence_score or 0.0,
            relevance_score=score.relevance_score or 0.0,
            helpfulness_score=score.helpfulness_score or 0.0,
            user_feedback_score=score.user_feedback_score
        )
    
    except QualityScore.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality score not found for message {message_id}"
        )
    except Exception as e:
        log.error(f"Get score error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/stats/model")
async def get_model_stats(request: QualityStatsRequest):
    """
    Get quality statistics for a specific model.
    
    Returns aggregated metrics over the specified time period.
    """
    
    try:
        stats = scorer.get_model_quality_stats(
            model=request.model or "all",
            days=request.days
        )
        
        return stats
    
    except Exception as e:
        log.error(f"Model stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats/overview")
async def get_quality_overview(days: int = 7):
    """
    Get overall quality statistics across all models.
    """
    
    try:
        from datetime import datetime, timedelta
        
        since = datetime.utcnow() - timedelta(days=days)
        
        all_scores = (
            QualityScore
            .select()
            .where(QualityScore.created_at >= since)
        )
        
        if not all_scores:
            return {
                "period_days": days,
                "total_interactions": 0,
                "message": "No data available for this period"
            }
        
        scores_list = list(all_scores)
        
        # Calculate aggregates
        overall_scores = [s.overall_score for s in scores_list if s.overall_score]
        feedback_scores = [s.user_feedback_score for s in scores_list if s.user_feedback_score is not None]
        
        return {
            "period_days": days,
            "total_interactions": len(scores_list),
            "avg_overall_score": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
            "median_overall_score": sorted(overall_scores)[len(overall_scores) // 2] if overall_scores else 0,
            "interactions_with_feedback": len(feedback_scores),
            "feedback_rate": len(feedback_scores) / len(scores_list) * 100 if scores_list else 0,
            "avg_feedback_score": sum(feedback_scores) / len(feedback_scores) if feedback_scores else None,
            "high_quality_interactions": sum(1 for s in overall_scores if s >= 0.8),
            "low_quality_interactions": sum(1 for s in overall_scores if s < 0.5)
        }
    
    except Exception as e:
        log.error(f"Overview stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/scores/recent", response_model=List[QualityScoreResponse])
async def get_recent_scores(limit: int = 50, min_score: Optional[float] = None):
    """
    Get recent quality scores.
    
    Optionally filter by minimum score.
    """
    
    try:
        query = (
            QualityScore
            .select()
            .order_by(QualityScore.created_at.desc())
            .limit(limit)
        )
        
        if min_score is not None:
            query = query.where(QualityScore.overall_score >= min_score)
        
        results = []
        for score in query:
            results.append(QualityScoreResponse(
                message_id=score.message_id,
                overall_score=score.overall_score or 0.0,
                engagement_score=score.engagement_score or 0.0,
                coherence_score=score.coherence_score or 0.0,
                relevance_score=score.relevance_score or 0.0,
                helpfulness_score=score.helpfulness_score or 0.0,
                user_feedback_score=score.user_feedback_score
            ))
        
        return results
    
    except Exception as e:
        log.error(f"Recent scores error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/feedback/stats")
async def get_feedback_stats(days: int = 30):
    """
    Get user feedback statistics.
    """
    
    try:
        from datetime import datetime, timedelta
        
        since = datetime.utcnow() - timedelta(days=days)
        
        feedback_list = list(
            UserFeedback
            .select()
            .where(UserFeedback.created_at >= since)
        )
        
        if not feedback_list:
            return {
                "period_days": days,
                "total_feedback": 0,
                "message": "No feedback data available"
            }
        
        thumbs_up = sum(1 for f in feedback_list if f.feedback_type == "thumbs_up")
        thumbs_down = sum(1 for f in feedback_list if f.feedback_type == "thumbs_down")
        ratings = [f.rating for f in feedback_list if f.rating is not None]
        
        return {
            "period_days": days,
            "total_feedback": len(feedback_list),
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "positive_rate": thumbs_up / len(feedback_list) * 100 if feedback_list else 0,
            "total_ratings": len(ratings),
            "avg_rating": sum(ratings) / len(ratings) if ratings else None,
            "feedback_with_comments": sum(1 for f in feedback_list if f.comment),
            "regenerated_responses": sum(1 for f in feedback_list if f.regenerated)
        }
    
    except Exception as e:
        log.error(f"Feedback stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


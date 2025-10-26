"""
Quality Scoring Engine

Calculates quality scores for chat interactions based on multiple signals.
"""

import json
import math
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger as log

from .models import QualityScore, UserFeedback, QualityAggregate


class QualityScorer:
    """
    Calculates quality scores for chat interactions.
    """
    
    # Scoring weights (sum to 1.0)
    WEIGHTS = {
        "user_feedback": 0.35,    # Explicit user feedback (most important)
        "engagement": 0.25,       # Behavioral engagement signals
        "coherence": 0.20,        # Response quality
        "relevance": 0.15,        # Topic relevance
        "helpfulness": 0.05,      # Perceived helpfulness
    }
    
    def __init__(self):
        self.weights = self.WEIGHTS.copy()
    
    def score_interaction(
        self,
        chat_id: str,
        message_id: str,
        user_id: str,
        response_text: str,
        prompt_text: str,
        model: str,
        backend: str,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Score a single chat interaction.
        
        Returns a dictionary of scores:
        {
            "engagement_score": 0.0-1.0,
            "coherence_score": 0.0-1.0,
            "relevance_score": 0.0-1.0,
            "helpfulness_score": 0.0-1.0,
            "overall_score": 0.0-1.0
        }
        """
        
        scores = {}
        
        # 1. Engagement Score (behavioral signals)
        scores["engagement_score"] = self._calculate_engagement_score(
            response_text, prompt_text, metadata or {}
        )
        
        # 2. Coherence Score (response quality)
        scores["coherence_score"] = self._calculate_coherence_score(
            response_text, prompt_text
        )
        
        # 3. Relevance Score (topic relevance)
        scores["relevance_score"] = self._calculate_relevance_score(
            response_text, prompt_text
        )
        
        # 4. Helpfulness Score (perceived value)
        scores["helpfulness_score"] = self._calculate_helpfulness_score(
            response_text, prompt_text, metadata or {}
        )
        
        # 5. User Feedback Score (if available, will be updated later)
        scores["user_feedback_score"] = None
        
        # Calculate overall score (weighted average, excluding user feedback initially)
        scores["overall_score"] = self._calculate_overall_score(scores)
        
        # Store in database
        try:
            quality_score = QualityScore.create(
                chat_id=chat_id,
                message_id=message_id,
                user_id=user_id,
                engagement_score=scores["engagement_score"],
                coherence_score=scores["coherence_score"],
                relevance_score=scores["relevance_score"],
                helpfulness_score=scores["helpfulness_score"],
                overall_score=scores["overall_score"],
                response_length=len(response_text),
                model_used=model,
                backend_used=backend,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                metadata=json.dumps(metadata) if metadata else None
            )
            log.debug(f"Quality score created for message {message_id}: {scores['overall_score']:.2f}")
        except Exception as e:
            log.error(f"Failed to create quality score: {e}")
        
        return scores
    
    def _calculate_engagement_score(
        self, response: str, prompt: str, metadata: Dict[str, Any]
    ) -> float:
        """
        Calculate engagement score based on behavioral signals.
        
        Factors:
        - Response length (longer = more engaged)
        - Prompt-response ratio
        - Presence of code blocks, lists, formatting
        """
        
        score = 0.5  # Base score
        
        # Response length factor (0-0.3)
        response_len = len(response)
        if response_len > 1000:
            score += 0.3
        elif response_len > 500:
            score += 0.2
        elif response_len > 200:
            score += 0.1
        
        # Prompt-response ratio (0-0.2)
        prompt_len = len(prompt)
        if prompt_len > 0:
            ratio = response_len / prompt_len
            if 2 < ratio < 10:  # Sweet spot
                score += 0.2
            elif ratio >= 1:
                score += 0.1
        
        # Structured content bonus (0-0.3)
        if "```" in response:  # Code blocks
            score += 0.1
        if any(marker in response for marker in ["\n- ", "\n* ", "\n1. ", "\n2. "]):  # Lists
            score += 0.1
        if any(marker in response for marker in ["**", "__", "##", "###"]):  # Formatting
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_coherence_score(self, response: str, prompt: str) -> float:
        """
        Calculate coherence score (response quality).
        
        Factors:
        - Sentence structure
        - Paragraph breaks
        - No repeated patterns
        - Proper punctuation
        """
        
        score = 0.5  # Base score
        
        # Sentence count (0-0.2)
        sentences = response.split(". ")
        if 3 <= len(sentences) <= 20:  # Well-structured
            score += 0.2
        elif len(sentences) > 1:
            score += 0.1
        
        # Paragraph breaks (0-0.2)
        paragraphs = response.split("\n\n")
        if len(paragraphs) >= 2:
            score += 0.2
        elif len(paragraphs) > 1:
            score += 0.1
        
        # Check for repetition (penalty)
        words = response.lower().split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio > 0.7:
                score += 0.2
            elif unique_ratio > 0.5:
                score += 0.1
            else:
                score -= 0.2  # Penalty for repetition
        
        # Proper endings (0-0.1)
        if response.strip().endswith((".", "!", "?", ")", "]", "}")):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_relevance_score(self, response: str, prompt: str) -> float:
        """
        Calculate relevance score (topic alignment).
        
        Factors:
        - Keyword overlap
        - Topic coherence
        - Direct answer patterns
        """
        
        score = 0.5  # Base score
        
        # Keyword overlap (0-0.3)
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        prompt_words -= stop_words
        response_words -= stop_words
        
        if prompt_words:
            overlap = len(prompt_words & response_words) / len(prompt_words)
            score += overlap * 0.3
        
        # Direct answer patterns (0-0.3)
        response_lower = response.lower()
        if any(pattern in response_lower for pattern in [
            "here is", "here are", "the answer is", "to answer",
            "you can", "you should", "i recommend"
        ]):
            score += 0.3
        elif any(pattern in response_lower for pattern in ["yes", "no", "maybe"]):
            score += 0.1
        
        # Question answering bonus (0-0.2)
        if "?" in prompt:
            if any(pattern in response_lower for pattern in [
                "because", "the reason", "this is due to", "explanation"
            ]):
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_helpfulness_score(
        self, response: str, prompt: str, metadata: Dict[str, Any]
    ) -> float:
        """
        Calculate helpfulness score (perceived value).
        
        Factors:
        - Actionable advice
        - Examples provided
        - Step-by-step instructions
        - External resources
        """
        
        score = 0.5  # Base score
        
        response_lower = response.lower()
        
        # Actionable advice (0-0.2)
        if any(pattern in response_lower for pattern in [
            "step 1", "first", "second", "next", "then", "finally"
        ]):
            score += 0.2
        
        # Examples provided (0-0.2)
        if any(pattern in response_lower for pattern in [
            "for example", "such as", "like", "e.g.", "example:"
        ]):
            score += 0.2
        
        # Code or commands (0-0.2)
        if "```" in response or "`" in response:
            score += 0.2
        
        # Resources/links (0-0.2)
        if "http" in response or "www." in response:
            score += 0.2
        
        # Explanatory content (0-0.2)
        if any(pattern in response_lower for pattern in [
            "this means", "in other words", "to clarify", "essentially"
        ]):
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_overall_score(self, scores: Dict[str, Optional[float]]) -> float:
        """
        Calculate weighted overall score.
        """
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for metric, weight in self.weights.items():
            score_key = f"{metric}_score"
            if scores.get(score_key) is not None:
                weighted_sum += scores[score_key] * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.5  # Default score if no metrics available
        
        return weighted_sum / total_weight
    
    def update_user_feedback(
        self,
        message_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> bool:
        """
        Update quality score with explicit user feedback.
        """
        
        try:
            # Create feedback record
            UserFeedback.create(
                chat_id="",  # Will be filled from QualityScore
                message_id=message_id,
                user_id="",  # Will be filled from QualityScore
                feedback_type=feedback_type,
                rating=rating,
                comment=comment,
                categories=json.dumps(categories) if categories else None
            )
            
            # Calculate feedback score
            feedback_score = self._feedback_to_score(feedback_type, rating)
            
            # Update quality score
            quality_score = QualityScore.get(QualityScore.message_id == message_id)
            quality_score.user_feedback_score = feedback_score
            
            # Recalculate overall score with feedback
            scores = {
                "user_feedback_score": feedback_score,
                "engagement_score": quality_score.engagement_score,
                "coherence_score": quality_score.coherence_score,
                "relevance_score": quality_score.relevance_score,
                "helpfulness_score": quality_score.helpfulness_score,
            }
            quality_score.overall_score = self._calculate_overall_score(scores)
            quality_score.save()
            
            log.info(f"Updated quality score with user feedback: {message_id}")
            return True
            
        except Exception as e:
            log.error(f"Failed to update user feedback: {e}")
            return False
    
    def _feedback_to_score(self, feedback_type: str, rating: Optional[int]) -> float:
        """Convert user feedback to 0-1 score."""
        
        if feedback_type == "thumbs_up":
            return 1.0
        elif feedback_type == "thumbs_down":
            return 0.0
        elif feedback_type == "rating" and rating is not None:
            return rating / 5.0  # Convert 1-5 to 0-1
        else:
            return 0.5  # Neutral
    
    def get_model_quality_stats(
        self, model: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get quality statistics for a specific model.
        """
        
        since = datetime.utcnow() - timedelta(days=days)
        
        scores = (
            QualityScore
            .select()
            .where(
                (QualityScore.model_used == model) &
                (QualityScore.created_at >= since)
            )
        )
        
        if not scores:
            return {"error": "No data available"}
        
        scores_list = list(scores)
        
        return {
            "model": model,
            "period_days": days,
            "total_interactions": len(scores_list),
            "avg_overall_score": sum(s.overall_score or 0 for s in scores_list) / len(scores_list),
            "avg_engagement": sum(s.engagement_score or 0 for s in scores_list) / len(scores_list),
            "avg_coherence": sum(s.coherence_score or 0 for s in scores_list) / len(scores_list),
            "avg_relevance": sum(s.relevance_score or 0 for s in scores_list) / len(scores_list),
            "feedback_count": sum(1 for s in scores_list if s.user_feedback_score is not None),
        }


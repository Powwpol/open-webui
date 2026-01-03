"""
Dataset Builder

Builds training datasets from high-quality chat interactions.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger as log

from .models import FineTuneDataset, FineTuneSample
from pulsai.quality.models import QualityScore


class DatasetBuilder:
    """
    Builds fine-tuning datasets from quality-scored interactions.
    """
    
    def __init__(self, data_dir: str = "data/finetune"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def build_dataset(
        self,
        name: str,
        source_model: Optional[str] = None,
        min_quality_score: float = 0.7,
        max_samples: Optional[int] = None,
        days_back: int = 30,
        include_user_feedback_only: bool = False,
        tags: Optional[List[str]] = None
    ) -> Optional[FineTuneDataset]:
        """
        Build a training dataset from high-quality interactions.
        
        Args:
            name: Dataset name
            source_model: Filter by model (optional)
            min_quality_score: Minimum quality threshold (0-1)
            max_samples: Maximum number of samples
            days_back: Look back this many days
            include_user_feedback_only: Only include interactions with explicit feedback
            tags: Optional tags for categorization
        
        Returns:
            FineTuneDataset instance or None if failed
        """
        
        log.info(f"Building dataset '{name}' with min_quality={min_quality_score}")
        
        try:
            # Create dataset record
            dataset = FineTuneDataset.create(
                name=name,
                source_model=source_model,
                min_quality_score=min_quality_score,
                max_samples=max_samples,
                date_range_start=datetime.utcnow() - timedelta(days=days_back),
                date_range_end=datetime.utcnow(),
                status="building"
            )
            
            # Query high-quality interactions
            query = (
                QualityScore
                .select()
                .where(QualityScore.overall_score >= min_quality_score)
                .where(QualityScore.created_at >= dataset.date_range_start)
                .order_by(QualityScore.overall_score.desc())
            )
            
            if source_model:
                query = query.where(QualityScore.model_used == source_model)
            
            if include_user_feedback_only:
                query = query.where(QualityScore.user_feedback_score.is_null(False))
            
            if max_samples:
                query = query.limit(max_samples)
            
            # Build samples
            samples = []
            total_quality = 0.0
            
            for score in query:
                # Fetch original chat data
                prompt, completion = self._fetch_chat_data(
                    score.chat_id, score.message_id
                )
                
                if not prompt or not completion:
                    continue
                
                # Create sample
                sample = FineTuneSample.create(
                    dataset_id=dataset.id,
                    prompt=prompt,
                    completion=completion,
                    quality_score=score.overall_score,
                    source_chat_id=score.chat_id,
                    source_message_id=score.message_id,
                    model_used=score.model_used,
                    user_id=score.user_id,
                    tags=json.dumps(tags) if tags else None
                )
                
                samples.append(sample)
                total_quality += score.overall_score
            
            # Update dataset stats
            dataset.total_samples = len(samples)
            dataset.avg_quality_score = total_quality / len(samples) if samples else 0
            
            # Export to JSONL file
            file_path = self._export_to_jsonl(dataset, samples)
            dataset.file_path = file_path
            dataset.file_size_bytes = os.path.getsize(file_path) if file_path else 0
            dataset.status = "ready"
            dataset.save()
            
            log.info(f"Dataset '{name}' built with {len(samples)} samples (avg quality: {dataset.avg_quality_score:.2f})")
            return dataset
            
        except Exception as e:
            log.error(f"Failed to build dataset: {e}")
            if 'dataset' in locals():
                dataset.status = "failed"
                dataset.save()
            return None
    
    def _fetch_chat_data(
        self, chat_id: str, message_id: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Fetch original chat prompt and completion.
        
        Returns:
            (prompt, completion) tuple
        """
        
        try:
            # Import here to avoid circular imports
            from pulsai.models.chats import Chats, Messages
            
            # Get the message
            message = Messages.get(Messages.id == message_id)
            
            # Get previous user message as prompt
            chat = Chats.get(Chats.id == chat_id)
            messages = json.loads(chat.chat) if hasattr(chat, 'chat') else []
            
            # Find the message in chat history
            for i, msg in enumerate(messages):
                if msg.get("id") == message_id:
                    # Get previous user message as prompt
                    for j in range(i - 1, -1, -1):
                        if messages[j].get("role") == "user":
                            prompt = messages[j].get("content", "")
                            completion = msg.get("content", "")
                            return prompt, completion
            
            return None, None
            
        except Exception as e:
            log.error(f"Failed to fetch chat data for {message_id}: {e}")
            return None, None
    
    def _export_to_jsonl(
        self, dataset: FineTuneDataset, samples: List[FineTuneSample]
    ) -> Optional[str]:
        """
        Export dataset to JSONL format for training.
        
        Format:
        {"prompt": "...", "completion": "..."}
        """
        
        try:
            filename = f"{dataset.name.replace(' ', '_')}_{dataset.id}.jsonl"
            file_path = os.path.join(self.data_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for sample in samples:
                    line = json.dumps({
                        "prompt": sample.prompt,
                        "completion": sample.completion,
                        "quality_score": sample.quality_score,
                        "metadata": {
                            "model": sample.model_used,
                            "chat_id": sample.source_chat_id,
                            "message_id": sample.source_message_id
                        }
                    }, ensure_ascii=False)
                    f.write(line + '\n')
            
            log.info(f"Dataset exported to {file_path}")
            return file_path
            
        except Exception as e:
            log.error(f"Failed to export dataset: {e}")
            return None
    
    def augment_dataset(
        self, dataset_id: int, additional_samples: int = 100
    ) -> bool:
        """
        Add more samples to an existing dataset.
        """
        
        try:
            dataset = FineTuneDataset.get(FineTuneDataset.id == dataset_id)
            
            # Find latest sample date
            latest_sample = (
                FineTuneSample
                .select()
                .where(FineTuneSample.dataset_id == dataset_id)
                .order_by(FineTuneSample.created_at.desc())
                .first()
            )
            
            since = latest_sample.created_at if latest_sample else dataset.date_range_start
            
            # Query new high-quality interactions
            new_scores = (
                QualityScore
                .select()
                .where(QualityScore.overall_score >= dataset.min_quality_score)
                .where(QualityScore.created_at > since)
                .order_by(QualityScore.overall_score.desc())
                .limit(additional_samples)
            )
            
            if dataset.source_model:
                new_scores = new_scores.where(
                    QualityScore.model_used == dataset.source_model
                )
            
            # Add new samples
            added = 0
            total_quality = dataset.avg_quality_score * dataset.total_samples
            
            for score in new_scores:
                prompt, completion = self._fetch_chat_data(
                    score.chat_id, score.message_id
                )
                
                if not prompt or not completion:
                    continue
                
                FineTuneSample.create(
                    dataset_id=dataset.id,
                    prompt=prompt,
                    completion=completion,
                    quality_score=score.overall_score,
                    source_chat_id=score.chat_id,
                    source_message_id=score.message_id,
                    model_used=score.model_used,
                    user_id=score.user_id
                )
                
                added += 1
                total_quality += score.overall_score
            
            # Update dataset
            dataset.total_samples += added
            dataset.avg_quality_score = total_quality / dataset.total_samples
            dataset.date_range_end = datetime.utcnow()
            dataset.updated_at = datetime.utcnow()
            dataset.save()
            
            # Re-export
            samples = list(
                FineTuneSample
                .select()
                .where(FineTuneSample.dataset_id == dataset_id)
            )
            self._export_to_jsonl(dataset, samples)
            
            log.info(f"Added {added} samples to dataset {dataset.name}")
            return True
            
        except Exception as e:
            log.error(f"Failed to augment dataset: {e}")
            return False
    
    def get_dataset_stats(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get detailed statistics for a dataset.
        """
        
        try:
            dataset = FineTuneDataset.get(FineTuneDataset.id == dataset_id)
            
            samples = list(
                FineTuneSample
                .select()
                .where(FineTuneSample.dataset_id == dataset_id)
            )
            
            if not samples:
                return {"error": "No samples found"}
            
            quality_scores = [s.quality_score for s in samples]
            prompt_lengths = [len(s.prompt) for s in samples]
            completion_lengths = [len(s.completion) for s in samples]
            
            return {
                "dataset_id": dataset_id,
                "name": dataset.name,
                "total_samples": len(samples),
                "avg_quality_score": sum(quality_scores) / len(quality_scores),
                "min_quality_score": min(quality_scores),
                "max_quality_score": max(quality_scores),
                "avg_prompt_length": sum(prompt_lengths) / len(prompt_lengths),
                "avg_completion_length": sum(completion_lengths) / len(completion_lengths),
                "file_size_mb": dataset.file_size_bytes / (1024 * 1024) if dataset.file_size_bytes else 0,
                "created_at": dataset.created_at.isoformat(),
                "status": dataset.status
            }
            
        except Exception as e:
            log.error(f"Failed to get dataset stats: {e}")
            return {"error": str(e)}


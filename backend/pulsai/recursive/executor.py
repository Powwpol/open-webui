"""
Recursive Chat Executor

Manages execution of recursive chat workflows.
"""

import asyncio
import uuid
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger as log

from .models import (
    RecursiveChat,
    RecursiveTrigger,
    ChatRelationship,
    RecursiveExecution
)
from .tree import ChatTree


class RecursiveExecutor:
    """
    Executes recursive chat workflows.
    """
    
    def __init__(self):
        self.running_executions: Dict[str, asyncio.Task] = {}
    
    async def create_root_chat(
        self,
        user_id: str,
        title: str,
        prompt: str,
        model: str,
        max_depth: int = 5,
        max_chats: int = 20
    ) -> Optional[str]:
        """
        Create a new recursive chat workflow.
        
        Args:
            user_id: User initiating the chat
            title: Chat title
            prompt: Initial prompt
            model: Model to use
            max_depth: Maximum recursion depth
            max_chats: Maximum total chats
        
        Returns:
            Root chat_id or None if failed
        """
        
        try:
            # Generate IDs
            chat_id = f"rc-{uuid.uuid4().hex[:12]}"
            execution_id = f"ex-{uuid.uuid4().hex[:12]}"
            
            # Create root chat
            root_chat = RecursiveChat.create(
                chat_id=chat_id,
                parent_chat_id=None,
                root_chat_id=chat_id,
                depth=0,
                path=chat_id,
                user_id=user_id,
                title=title,
                status="active",
                trigger_type="manual",
                model_used=model
            )
            
            # Create execution tracker
            execution = RecursiveExecution.create(
                execution_id=execution_id,
                root_chat_id=chat_id,
                user_id=user_id,
                status="running",
                max_depth_limit=max_depth,
                max_chats_limit=max_chats,
                total_chats_created=1
            )
            
            log.info(f"Created recursive chat root: {chat_id}")
            
            # Start execution in background
            task = asyncio.create_task(
                self._execute_chat(chat_id, prompt, execution_id)
            )
            self.running_executions[execution_id] = task
            
            return chat_id
            
        except Exception as e:
            log.error(f"Failed to create root chat: {e}")
            return None
    
    async def create_sub_chat(
        self,
        parent_chat_id: str,
        title: str,
        prompt: str,
        trigger_type: str = "manual",
        trigger_condition: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a sub-chat under an existing chat.
        
        Args:
            parent_chat_id: Parent chat ID
            title: Sub-chat title
            prompt: Sub-chat prompt
            trigger_type: Type of trigger (manual, auto, conditional)
            trigger_condition: Condition that triggered this sub-chat
        
        Returns:
            Sub-chat chat_id or None if failed
        """
        
        try:
            # Get parent chat
            parent = RecursiveChat.get(RecursiveChat.chat_id == parent_chat_id)
            
            # Get execution
            execution = RecursiveExecution.get(
                RecursiveExecution.root_chat_id == parent.root_chat_id
            )
            
            # Check limits
            if parent.depth + 1 >= execution.max_depth_limit:
                log.warning(f"Max depth reached for execution {execution.execution_id}")
                return None
            
            if execution.total_chats_created >= execution.max_chats_limit:
                log.warning(f"Max chats limit reached for execution {execution.execution_id}")
                return None
            
            # Generate sub-chat ID
            sub_chat_id = f"rc-{uuid.uuid4().hex[:12]}"
            
            # Create sub-chat
            sub_chat = RecursiveChat.create(
                chat_id=sub_chat_id,
                parent_chat_id=parent_chat_id,
                root_chat_id=parent.root_chat_id,
                depth=parent.depth + 1,
                path=f"{parent.path}/{sub_chat_id}",
                user_id=parent.user_id,
                title=title,
                status="active",
                trigger_type=trigger_type,
                trigger_condition=json.dumps(trigger_condition) if trigger_condition else None,
                model_used=parent.model_used
            )
            
            # Create relationship
            order = (
                ChatRelationship
                .select()
                .where(ChatRelationship.parent_chat_id == parent_chat_id)
                .count()
            )
            
            ChatRelationship.create(
                parent_chat_id=parent_chat_id,
                child_chat_id=sub_chat_id,
                relationship_type="sub_chat",
                order=order
            )
            
            # Update execution stats
            execution.total_chats_created += 1
            if sub_chat.depth > execution.max_depth_reached:
                execution.max_depth_reached = sub_chat.depth
            execution.save()
            
            # Update parent max depth
            execution.max_depth_reached = max(execution.max_depth_reached, sub_chat.depth)
            execution.save()
            
            log.info(f"Created sub-chat {sub_chat_id} under {parent_chat_id} (depth {sub_chat.depth})")
            
            # Execute sub-chat
            task = asyncio.create_task(
                self._execute_chat(sub_chat_id, prompt, execution.execution_id)
            )
            
            return sub_chat_id
            
        except Exception as e:
            log.error(f"Failed to create sub-chat: {e}")
            return None
    
    async def _execute_chat(
        self,
        chat_id: str,
        prompt: str,
        execution_id: str
    ):
        """
        Execute a single chat (send prompt, get response, check triggers).
        """
        
        try:
            chat = RecursiveChat.get(RecursiveChat.chat_id == chat_id)
            
            log.info(f"Executing chat {chat_id} with prompt: {prompt[:50]}...")
            
            # Send prompt to inference backend
            response = await self._send_to_model(
                prompt=prompt,
                model=chat.model_used,
                chat_id=chat_id
            )
            
            if not response:
                log.error(f"No response from model for chat {chat_id}")
                chat.status = "failed"
                chat.save()
                return
            
            # Update chat
            chat.total_messages += 2  # User + assistant
            chat.total_tokens = response.get("tokens", 0)
            chat.summary = response.get("content", "")[:500]  # First 500 chars as summary
            chat.updated_at = datetime.utcnow()
            chat.save()
            
            # Update execution
            execution = RecursiveExecution.get(
                RecursiveExecution.execution_id == execution_id
            )
            execution.total_messages += 2
            execution.total_tokens += response.get("tokens", 0)
            execution.save()
            
            # Check for triggers to create sub-chats
            await self._check_triggers(chat, response)
            
            # Mark chat as completed
            chat.status = "completed"
            chat.completed_at = datetime.utcnow()
            chat.save()
            
            log.info(f"Chat {chat_id} completed successfully")
            
        except Exception as e:
            log.error(f"Chat execution error: {e}")
            try:
                chat = RecursiveChat.get(RecursiveChat.chat_id == chat_id)
                chat.status = "failed"
                chat.save()
            except:
                pass
    
    async def _send_to_model(
        self,
        prompt: str,
        model: str,
        chat_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Send prompt to inference backend.
        """
        
        try:
            # Import inference router
            from pulsai.inference.router import InferenceRouter
            from pulsai.inference.base import InferenceRequest, ChatMessage
            
            router = InferenceRouter()
            
            request = InferenceRequest(
                messages=[ChatMessage(role="user", content=prompt)],
                model=model,
                stream=False
            )
            
            response = await router.chat_completion(request)
            
            return {
                "content": response.choices[0]["message"]["content"],
                "tokens": response.usage.get("total_tokens", 0) if response.usage else 0
            }
            
        except Exception as e:
            log.error(f"Model invocation error: {e}")
            return None
    
    async def _check_triggers(
        self,
        chat: RecursiveChat,
        response: Dict[str, Any]
    ):
        """
        Check if any triggers should fire based on chat response.
        """
        
        try:
            # Get active triggers
            triggers = list(
                RecursiveTrigger
                .select()
                .where(RecursiveTrigger.enabled == True)
            )
            
            for trigger in triggers:
                if await self._evaluate_trigger(trigger, chat, response):
                    log.info(f"Trigger '{trigger.name}' fired for chat {chat.chat_id}")
                    
                    # Create sub-chat
                    sub_prompt = await self._build_sub_prompt(
                        trigger.sub_chat_template,
                        chat,
                        response
                    )
                    
                    await self.create_sub_chat(
                        parent_chat_id=chat.chat_id,
                        title=f"{trigger.name} - {chat.title}",
                        prompt=sub_prompt,
                        trigger_type="auto",
                        trigger_condition={"trigger_id": trigger.id, "trigger_name": trigger.name}
                    )
                    
                    # Update trigger stats
                    trigger.trigger_count += 1
                    trigger.success_count += 1
                    trigger.save()
                    
        except Exception as e:
            log.error(f"Trigger check error: {e}")
    
    async def _evaluate_trigger(
        self,
        trigger: RecursiveTrigger,
        chat: RecursiveChat,
        response: Dict[str, Any]
    ) -> bool:
        """
        Evaluate if a trigger condition is met.
        """
        
        try:
            condition = json.loads(trigger.condition)
            trigger_type = trigger.trigger_type
            content = response.get("content", "")
            
            if trigger_type == "keyword":
                # Check if keywords present
                keywords = condition.get("keywords", [])
                return any(kw.lower() in content.lower() for kw in keywords)
            
            elif trigger_type == "length":
                # Check response length
                min_length = condition.get("min_length", 0)
                max_length = condition.get("max_length", float('inf'))
                return min_length <= len(content) <= max_length
            
            elif trigger_type == "quality_score":
                # Check quality score (if available)
                min_score = condition.get("min_score", 0.7)
                # Would integrate with quality scoring system
                return True  # Placeholder
            
            elif trigger_type == "custom":
                # Custom condition evaluation
                # Would use safe eval or custom DSL
                return False  # Placeholder
            
            return False
            
        except Exception as e:
            log.error(f"Trigger evaluation error: {e}")
            return False
    
    async def _build_sub_prompt(
        self,
        template: str,
        parent_chat: RecursiveChat,
        parent_response: Dict[str, Any]
    ) -> str:
        """
        Build sub-chat prompt from template.
        
        Template variables:
        - {parent_title}: Parent chat title
        - {parent_response}: Parent response content
        - {depth}: Current depth
        """
        
        try:
            if not template:
                return f"Continue the discussion from: {parent_chat.title}"
            
            return template.format(
                parent_title=parent_chat.title,
                parent_response=parent_response.get("content", "")[:200],
                depth=parent_chat.depth + 1
            )
            
        except Exception as e:
            log.error(f"Prompt building error: {e}")
            return "Continue the discussion."
    
    def get_tree(self, root_chat_id: str) -> Optional[ChatTree]:
        """
        Get the chat tree for a root chat.
        """
        
        tree = ChatTree(root_chat_id)
        tree.build_tree()
        return tree
    
    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get status of a recursive execution.
        """
        
        try:
            execution = RecursiveExecution.get(
                RecursiveExecution.execution_id == execution_id
            )
            
            # Get tree stats
            tree = ChatTree(execution.root_chat_id)
            tree.build_tree()
            
            return {
                "execution_id": execution.execution_id,
                "root_chat_id": execution.root_chat_id,
                "status": execution.status,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "total_chats_created": execution.total_chats_created,
                "total_messages": execution.total_messages,
                "total_tokens": execution.total_tokens,
                "max_depth_reached": execution.max_depth_reached,
                "max_depth_limit": execution.max_depth_limit,
                "tree_visualization": tree.visualize("ascii") if tree.root else None
            }
            
        except Exception as e:
            log.error(f"Get execution status error: {e}")
            return {"error": str(e)}
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running execution.
        """
        
        try:
            execution = RecursiveExecution.get(
                RecursiveExecution.execution_id == execution_id
            )
            
            if execution.status != "running":
                return False
            
            # Cancel running task
            if execution_id in self.running_executions:
                self.running_executions[execution_id].cancel()
                self.running_executions.pop(execution_id)
            
            # Update status
            execution.status = "cancelled"
            execution.completed_at = datetime.utcnow()
            execution.save()
            
            # Cancel all active chats
            RecursiveChat.update(
                status="cancelled"
            ).where(
                (RecursiveChat.root_chat_id == execution.root_chat_id) &
                (RecursiveChat.status == "active")
            ).execute()
            
            log.info(f"Execution {execution_id} cancelled")
            return True
            
        except Exception as e:
            log.error(f"Cancel execution error: {e}")
            return False


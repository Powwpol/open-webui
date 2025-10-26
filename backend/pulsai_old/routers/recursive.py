"""
Recursive Chat API Router

Endpoints for managing recursive chat trees.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger as log

from open_webui.recursive.executor import RecursiveExecutor
from open_webui.recursive.tree import ChatTree
from open_webui.recursive.models import RecursiveChat, RecursiveTrigger, RecursiveExecution


router = APIRouter()


# Pydantic Models
class ChatCreateRequest(BaseModel):
    title: str = Field(..., max_length=255)
    prompt: str = Field(..., min_length=1)
    model: str = Field("llama2")
    max_depth: int = Field(5, ge=1, le=10)
    max_chats: int = Field(20, ge=1, le=100)


class SubChatCreateRequest(BaseModel):
    parent_chat_id: str
    title: str = Field(..., max_length=255)
    prompt: str = Field(..., min_length=1)
    trigger_type: str = Field("manual", pattern="^(manual|auto|conditional)$")


class TriggerCreateRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    trigger_type: str = Field(..., pattern="^(keyword|sentiment|length|quality_score|custom)$")
    condition: Dict[str, Any]
    sub_chat_template: Optional[str] = None
    max_depth: int = Field(3, ge=1, le=10)
    model_override: Optional[str] = None


# Initialize executor
executor = RecursiveExecutor()


# ======================================
# CHAT ENDPOINTS
# ======================================

@router.post("/chats", status_code=status.HTTP_201_CREATED)
async def create_recursive_chat(request: ChatCreateRequest, user_id: str = "default_user"):
    """
    Create a new recursive chat workflow.
    
    This creates the root chat and starts the execution.
    """
    
    try:
        root_chat_id = await executor.create_root_chat(
            user_id=user_id,
            title=request.title,
            prompt=request.prompt,
            model=request.model,
            max_depth=request.max_depth,
            max_chats=request.max_chats
        )
        
        if not root_chat_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create recursive chat"
            )
        
        return {
            "chat_id": root_chat_id,
            "message": "Recursive chat created successfully"
        }
    
    except Exception as e:
        log.error(f"Create recursive chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/chats/sub", status_code=status.HTTP_201_CREATED)
async def create_sub_chat(request: SubChatCreateRequest):
    """
    Create a sub-chat under an existing chat.
    """
    
    try:
        sub_chat_id = await executor.create_sub_chat(
            parent_chat_id=request.parent_chat_id,
            title=request.title,
            prompt=request.prompt,
            trigger_type=request.trigger_type
        )
        
        if not sub_chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create sub-chat (limits may be reached)"
            )
        
        return {
            "chat_id": sub_chat_id,
            "message": "Sub-chat created successfully"
        }
    
    except Exception as e:
        log.error(f"Create sub-chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    """
    Get details of a specific chat.
    """
    
    try:
        chat = RecursiveChat.get(RecursiveChat.chat_id == chat_id)
        
        return {
            "chat_id": chat.chat_id,
            "parent_chat_id": chat.parent_chat_id,
            "root_chat_id": chat.root_chat_id,
            "depth": chat.depth,
            "path": chat.path,
            "title": chat.title,
            "status": chat.status,
            "trigger_type": chat.trigger_type,
            "created_at": chat.created_at.isoformat(),
            "completed_at": chat.completed_at.isoformat() if chat.completed_at else None,
            "total_messages": chat.total_messages,
            "total_tokens": chat.total_tokens,
            "summary": chat.summary,
            "model_used": chat.model_used
        }
    
    except RecursiveChat.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat {chat_id} not found"
        )
    except Exception as e:
        log.error(f"Get chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/chats/{chat_id}/children")
async def get_chat_children(chat_id: str):
    """
    Get all direct children of a chat.
    """
    
    try:
        chat = RecursiveChat.get(RecursiveChat.chat_id == chat_id)
        tree = executor.get_tree(chat.root_chat_id)
        
        if not tree:
            return {"children": []}
        
        children = tree.get_children(chat_id)
        
        return {
            "children": [
                {
                    "chat_id": child.chat_id,
                    "title": child.title,
                    "status": child.status,
                    "depth": child.depth,
                    "created_at": child.created_at.isoformat()
                }
                for child in children
            ]
        }
    
    except Exception as e:
        log.error(f"Get children error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/chats/{chat_id}/descendants")
async def get_chat_descendants(chat_id: str):
    """
    Get all descendants (children, grandchildren, etc.) of a chat.
    """
    
    try:
        chat = RecursiveChat.get(RecursiveChat.chat_id == chat_id)
        tree = executor.get_tree(chat.root_chat_id)
        
        if not tree:
            return {"descendants": []}
        
        descendants = tree.get_descendants(chat_id)
        
        return {
            "descendants": [
                {
                    "chat_id": desc.chat_id,
                    "title": desc.title,
                    "status": desc.status,
                    "depth": desc.depth,
                    "created_at": desc.created_at.isoformat()
                }
                for desc in descendants
            ]
        }
    
    except Exception as e:
        log.error(f"Get descendants error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ======================================
# TREE ENDPOINTS
# ======================================

@router.get("/trees/{root_chat_id}")
async def get_tree(root_chat_id: str, format: str = "json"):
    """
    Get the complete chat tree.
    
    Formats: json, ascii, mermaid
    """
    
    try:
        tree = executor.get_tree(root_chat_id)
        
        if not tree or not tree.root:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tree not found for root chat {root_chat_id}"
            )
        
        if format == "ascii":
            return {
                "format": "ascii",
                "visualization": tree.visualize("ascii")
            }
        elif format == "mermaid":
            return {
                "format": "mermaid",
                "visualization": tree.visualize("mermaid")
            }
        else:  # json
            return tree.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Get tree error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/trees/{root_chat_id}/stats")
async def get_tree_stats(root_chat_id: str):
    """
    Get statistics about the chat tree.
    """
    
    try:
        tree = executor.get_tree(root_chat_id)
        
        if not tree or not tree.root:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tree not found for root chat {root_chat_id}"
            )
        
        leaf_nodes = tree.get_leaf_nodes()
        active_branches = tree.get_active_branches()
        
        return {
            "root_chat_id": root_chat_id,
            "total_nodes": len(tree.nodes),
            "max_depth": tree.get_max_depth(),
            "leaf_nodes_count": len(leaf_nodes),
            "active_branches_count": len(active_branches),
            "completed_chats": sum(1 for node in tree.nodes.values() if node.chat.status == "completed"),
            "active_chats": sum(1 for node in tree.nodes.values() if node.chat.status == "active"),
            "failed_chats": sum(1 for node in tree.nodes.values() if node.chat.status == "failed")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Get tree stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ======================================
# EXECUTION ENDPOINTS
# ======================================

@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """
    Get status of a recursive execution.
    """
    
    try:
        status_info = executor.get_execution_status(execution_id)
        
        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_info["error"]
            )
        
        return status_info
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Get execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """
    Cancel a running execution.
    """
    
    try:
        success = await executor.cancel_execution(execution_id)
        
        if success:
            return {"message": f"Execution {execution_id} cancelled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel execution {execution_id}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Cancel execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/executions")
async def list_executions(
    user_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50
):
    """
    List recursive executions.
    """
    
    try:
        query = RecursiveExecution.select().order_by(RecursiveExecution.started_at.desc()).limit(limit)
        
        if user_id:
            query = query.where(RecursiveExecution.user_id == user_id)
        
        if status_filter:
            query = query.where(RecursiveExecution.status == status_filter)
        
        executions = []
        for ex in query:
            executions.append({
                "execution_id": ex.execution_id,
                "root_chat_id": ex.root_chat_id,
                "status": ex.status,
                "started_at": ex.started_at.isoformat(),
                "completed_at": ex.completed_at.isoformat() if ex.completed_at else None,
                "total_chats_created": ex.total_chats_created,
                "max_depth_reached": ex.max_depth_reached
            })
        
        return {"executions": executions}
    
    except Exception as e:
        log.error(f"List executions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ======================================
# TRIGGER ENDPOINTS
# ======================================

@router.post("/triggers", status_code=status.HTTP_201_CREATED)
async def create_trigger(request: TriggerCreateRequest):
    """
    Create a new recursive trigger.
    
    Triggers automatically create sub-chats when conditions are met.
    """
    
    try:
        import json
        
        trigger = RecursiveTrigger.create(
            name=request.name,
            description=request.description,
            trigger_type=request.trigger_type,
            condition=json.dumps(request.condition),
            sub_chat_template=request.sub_chat_template,
            max_depth=request.max_depth,
            model_override=request.model_override,
            enabled=True
        )
        
        return {
            "trigger_id": trigger.id,
            "name": trigger.name,
            "message": "Trigger created successfully"
        }
    
    except Exception as e:
        log.error(f"Create trigger error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/triggers")
async def list_triggers(enabled_only: bool = False):
    """
    List all recursive triggers.
    """
    
    try:
        query = RecursiveTrigger.select().order_by(RecursiveTrigger.created_at.desc())
        
        if enabled_only:
            query = query.where(RecursiveTrigger.enabled == True)
        
        triggers = []
        for trig in query:
            triggers.append({
                "trigger_id": trig.id,
                "name": trig.name,
                "description": trig.description,
                "trigger_type": trig.trigger_type,
                "enabled": trig.enabled,
                "trigger_count": trig.trigger_count,
                "success_count": trig.success_count,
                "created_at": trig.created_at.isoformat()
            })
        
        return {"triggers": triggers}
    
    except Exception as e:
        log.error(f"List triggers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/triggers/{trigger_id}")
async def update_trigger(trigger_id: int, enabled: Optional[bool] = None):
    """
    Update trigger settings (e.g., enable/disable).
    """
    
    try:
        trigger = RecursiveTrigger.get(RecursiveTrigger.id == trigger_id)
        
        if enabled is not None:
            trigger.enabled = enabled
            trigger.save()
        
        return {"message": f"Trigger {trigger_id} updated successfully"}
    
    except RecursiveTrigger.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trigger {trigger_id} not found"
        )
    except Exception as e:
        log.error(f"Update trigger error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/triggers/{trigger_id}")
async def delete_trigger(trigger_id: int):
    """
    Delete a trigger.
    """
    
    try:
        trigger = RecursiveTrigger.get(RecursiveTrigger.id == trigger_id)
        trigger.delete_instance()
        
        return {"message": f"Trigger {trigger_id} deleted successfully"}
    
    except RecursiveTrigger.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trigger {trigger_id} not found"
        )
    except Exception as e:
        log.error(f"Delete trigger error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


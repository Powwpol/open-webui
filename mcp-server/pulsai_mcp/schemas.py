"""
Pulsai MCP Server Schemas
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class ToolSchema(BaseModel):
    """Schema for an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = []


class ToolRequest(BaseModel):
    """Request to execute a tool"""
    name: str
    arguments: Dict[str, Any] = {}


class ToolResponse(BaseModel):
    """Response from tool execution"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


# Tool schemas for Pulsai MCP

TOOL_SCHEMAS = [
    ToolSchema(
        name="recursive_chat",
        description="Execute a recursive chat workflow for complex problem-solving",
        parameters={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Initial prompt for the recursive chat"
                },
                "strategy": {
                    "type": "string",
                    "enum": ["breadth_first", "depth_first", "adaptive"],
                    "description": "Recursion strategy to use",
                    "default": "breadth_first"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum recursion depth",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 3
                }
            },
            "required": ["prompt"]
        },
        required=["prompt"]
    ),
    ToolSchema(
        name="model_info",
        description="Get information about available AI models",
        parameters={
            "type": "object",
            "properties": {
                "model_name": {
                    "type": "string",
                    "description": "Specific model name to get info about (optional)"
                }
            },
            "required": []
        },
        required=[]
    ),
    ToolSchema(
        name="context_summary",
        description="Summarize a conversation context",
        parameters={
            "type": "object",
            "properties": {
                "messages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    },
                    "description": "List of messages to summarize"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum summary length",
                    "default": 500
                }
            },
            "required": ["messages"]
        },
        required=["messages"]
    )
]


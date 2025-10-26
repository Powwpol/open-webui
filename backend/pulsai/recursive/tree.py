"""
Recursive Chat Tree Manager

Manages the hierarchical structure of recursive chats.
"""

import json
from typing import List, Dict, Any, Optional
from loguru import logger as log

from .models import RecursiveChat, ChatRelationship


class ChatTreeNode:
    """
    Represents a node in the chat tree.
    """
    
    def __init__(self, chat: RecursiveChat):
        self.chat = chat
        self.children: List[ChatTreeNode] = []
        self.parent: Optional[ChatTreeNode] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "chat_id": self.chat.chat_id,
            "title": self.chat.title,
            "depth": self.chat.depth,
            "status": self.chat.status,
            "created_at": self.chat.created_at.isoformat(),
            "total_messages": self.chat.total_messages,
            "summary": self.chat.summary,
            "children": [child.to_dict() for child in self.children]
        }


class ChatTree:
    """
    Manages the tree structure of recursive chats.
    """
    
    def __init__(self, root_chat_id: str):
        self.root_chat_id = root_chat_id
        self.root: Optional[ChatTreeNode] = None
        self.nodes: Dict[str, ChatTreeNode] = {}
    
    def build_tree(self) -> Optional[ChatTreeNode]:
        """
        Build the complete tree structure from database.
        """
        
        try:
            # Load all chats in this tree
            chats = list(
                RecursiveChat
                .select()
                .where(RecursiveChat.root_chat_id == self.root_chat_id)
                .order_by(RecursiveChat.depth.asc())
            )
            
            if not chats:
                log.warning(f"No chats found for root {self.root_chat_id}")
                return None
            
            # Create nodes
            for chat in chats:
                node = ChatTreeNode(chat)
                self.nodes[chat.chat_id] = node
                
                if chat.parent_chat_id is None:
                    self.root = node
            
            # Build relationships
            relationships = list(
                ChatRelationship
                .select()
                .where(ChatRelationship.parent_chat_id.in_([c.chat_id for c in chats]))
                .order_by(ChatRelationship.order.asc())
            )
            
            for rel in relationships:
                parent_node = self.nodes.get(rel.parent_chat_id)
                child_node = self.nodes.get(rel.child_chat_id)
                
                if parent_node and child_node:
                    parent_node.children.append(child_node)
                    child_node.parent = parent_node
            
            log.info(f"Built tree with {len(self.nodes)} nodes")
            return self.root
            
        except Exception as e:
            log.error(f"Failed to build tree: {e}")
            return None
    
    def get_node(self, chat_id: str) -> Optional[ChatTreeNode]:
        """Get a specific node by chat_id."""
        return self.nodes.get(chat_id)
    
    def get_path(self, chat_id: str) -> List[str]:
        """
        Get the path from root to a specific chat.
        Returns list of chat_ids.
        """
        
        node = self.nodes.get(chat_id)
        if not node:
            return []
        
        path = []
        current = node
        while current:
            path.insert(0, current.chat.chat_id)
            current = current.parent
        
        return path
    
    def get_children(self, chat_id: str) -> List[RecursiveChat]:
        """Get all direct children of a chat."""
        
        node = self.nodes.get(chat_id)
        if not node:
            return []
        
        return [child.chat for child in node.children]
    
    def get_descendants(self, chat_id: str) -> List[RecursiveChat]:
        """Get all descendants (children, grandchildren, etc.) of a chat."""
        
        node = self.nodes.get(chat_id)
        if not node:
            return []
        
        descendants = []
        self._collect_descendants(node, descendants)
        return descendants
    
    def _collect_descendants(self, node: ChatTreeNode, result: List[RecursiveChat]):
        """Recursively collect all descendants."""
        for child in node.children:
            result.append(child.chat)
            self._collect_descendants(child, result)
    
    def get_siblings(self, chat_id: str) -> List[RecursiveChat]:
        """Get all sibling chats (same parent)."""
        
        node = self.nodes.get(chat_id)
        if not node or not node.parent:
            return []
        
        return [
            sibling.chat
            for sibling in node.parent.children
            if sibling.chat.chat_id != chat_id
        ]
    
    def get_depth(self, chat_id: str) -> int:
        """Get the depth of a chat in the tree."""
        node = self.nodes.get(chat_id)
        return node.chat.depth if node else 0
    
    def get_max_depth(self) -> int:
        """Get the maximum depth in the tree."""
        if not self.nodes:
            return 0
        return max(node.chat.depth for node in self.nodes.values())
    
    def get_leaf_nodes(self) -> List[RecursiveChat]:
        """Get all leaf nodes (chats with no children)."""
        return [
            node.chat
            for node in self.nodes.values()
            if not node.children
        ]
    
    def get_active_branches(self) -> List[List[str]]:
        """
        Get all active branches (root to leaf paths with status='active').
        """
        
        if not self.root:
            return []
        
        branches = []
        self._collect_branches(self.root, [], branches, status_filter="active")
        return branches
    
    def _collect_branches(
        self,
        node: ChatTreeNode,
        current_path: List[str],
        result: List[List[str]],
        status_filter: Optional[str] = None
    ):
        """Recursively collect all branches."""
        
        current_path = current_path + [node.chat.chat_id]
        
        # If leaf node, add path to results
        if not node.children:
            if not status_filter or node.chat.status == status_filter:
                result.append(current_path)
        else:
            # Continue with children
            for child in node.children:
                self._collect_branches(child, current_path, result, status_filter)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire tree to dictionary."""
        
        if not self.root:
            return {"error": "No root node"}
        
        return {
            "root_chat_id": self.root_chat_id,
            "total_nodes": len(self.nodes),
            "max_depth": self.get_max_depth(),
            "tree": self.root.to_dict()
        }
    
    def visualize(self, format: str = "ascii") -> str:
        """
        Generate a visual representation of the tree.
        
        Args:
            format: "ascii", "json", or "mermaid"
        """
        
        if format == "json":
            return json.dumps(self.to_dict(), indent=2)
        elif format == "mermaid":
            return self._generate_mermaid()
        else:  # ascii
            return self._generate_ascii()
    
    def _generate_ascii(self) -> str:
        """Generate ASCII tree visualization."""
        
        if not self.root:
            return "Empty tree"
        
        lines = []
        self._print_node_ascii(self.root, "", True, lines)
        return "\n".join(lines)
    
    def _print_node_ascii(
        self,
        node: ChatTreeNode,
        prefix: str,
        is_last: bool,
        lines: List[str]
    ):
        """Recursively print node in ASCII format."""
        
        connector = "└── " if is_last else "├── "
        status_icon = "✓" if node.chat.status == "completed" else "○"
        
        lines.append(
            f"{prefix}{connector}{status_icon} {node.chat.title} ({node.chat.chat_id[:8]})"
        )
        
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension
        
        for i, child in enumerate(node.children):
            self._print_node_ascii(
                child,
                new_prefix,
                i == len(node.children) - 1,
                lines
            )
    
    def _generate_mermaid(self) -> str:
        """Generate Mermaid diagram syntax."""
        
        if not self.root:
            return "graph TD\n  empty[Empty Tree]"
        
        lines = ["graph TD"]
        self._add_mermaid_node(self.root, lines)
        return "\n".join(lines)
    
    def _add_mermaid_node(self, node: ChatTreeNode, lines: List[str]):
        """Recursively add nodes to Mermaid diagram."""
        
        node_id = node.chat.chat_id.replace("-", "_")[:8]
        node_label = node.chat.title[:30]
        
        # Add node
        lines.append(f"  {node_id}[\"{node_label}\"]")
        
        # Add children
        for child in node.children:
            child_id = child.chat.chat_id.replace("-", "_")[:8]
            lines.append(f"  {node_id} --> {child_id}")
            self._add_mermaid_node(child, lines)


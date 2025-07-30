"""Model Context Protocol (MCP) support for pyTigerGraph.

This module implements the Model Context Protocol for interacting with TigerGraph databases.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class MCPContext:
    """Represents an MCP context for TigerGraph operations."""
    
    def __init__(self, 
                 graph_name: str,
                 vertex_types: Optional[List[str]] = None,
                 edge_types: Optional[List[str]] = None,
                 attributes: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize an MCP context.
        
        Args:
            graph_name: Name of the TigerGraph graph
            vertex_types: List of vertex types to include in context
            edge_types: List of edge types to include in context 
            attributes: Additional attributes for the context
            metadata: Metadata about the context
        """
        self.graph_name = graph_name
        self.vertex_types = vertex_types or []
        self.edge_types = edge_types or []
        self.attributes = attributes or {}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary format."""
        return {
            "graph_name": self.graph_name,
            "vertex_types": self.vertex_types,
            "edge_types": self.edge_types,
            "attributes": self.attributes,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPContext':
        """Create context from dictionary."""
        return cls(
            graph_name=data["graph_name"],
            vertex_types=data.get("vertex_types"),
            edge_types=data.get("edge_types"),
            attributes=data.get("attributes"),
            metadata=data.get("metadata")
        )

class MCPRequest:
    """Represents an MCP request to TigerGraph."""

    def __init__(self,
                 operation: str,
                 context: MCPContext,
                 parameters: Optional[Dict[str, Any]] = None):
        """Initialize an MCP request.
        
        Args:
            operation: The operation to perform
            context: The MCP context
            parameters: Additional parameters for the operation
        """
        self.operation = operation
        self.context = context
        self.parameters = parameters or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary format."""
        return {
            "operation": self.operation,
            "context": self.context.to_dict(),
            "parameters": self.parameters
        }

class MCPResponse:
    """Represents an MCP response from TigerGraph."""

    def __init__(self,
                 success: bool,
                 data: Any = None,
                 error: Optional[str] = None):
        """Initialize an MCP response.
        
        Args:
            success: Whether the operation was successful
            data: The response data
            error: Error message if operation failed
        """
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPResponse':
        """Create response from dictionary."""
        return cls(
            success=data["success"],
            data=data.get("data"),
            error=data.get("error")
        )
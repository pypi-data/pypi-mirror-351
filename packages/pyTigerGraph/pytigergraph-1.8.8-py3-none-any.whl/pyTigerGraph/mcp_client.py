"""MCP Client implementation for pyTigerGraph.

This module provides a client implementation for making Model Context Protocol (MCP) requests.
"""

import json
import logging
import requests
from typing import Any, Dict, Optional
from .mcp import MCPContext, MCPRequest, MCPResponse

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for making MCP requests to a TigerGraph MCP server."""
    
    def __init__(self, server_url: str):
        """Initialize MCP Client.
        
        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url.rstrip('/')
        
    def execute_request(self, request: MCPRequest) -> MCPResponse:
        """Execute an MCP request.
        
        Args:
            request: The MCPRequest to execute
            
        Returns:
            MCPResponse with results
        """
        try:
            response = requests.post(
                f"{self.server_url}/mcp",
                json=request.to_dict(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            return MCPResponse.from_dict(response.json())
            
        except requests.exceptions.RequestException as e:
            return MCPResponse(success=False, error=str(e))
            
    def query(self, 
             query: str,
             context: MCPContext,
             parameters: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Execute a query using MCP.
        
        Args:
            query: Query to execute
            context: MCP context
            parameters: Optional query parameters
            
        Returns:
            Query results
        """
        request = MCPRequest(
            operation="query",
            context=context,
            parameters={
                "query": query,
                **(parameters or {})
            }
        )
        return self.execute_request(request)
        
    def run_query(self,
                  query_name: str,
                  context: MCPContext,
                  parameters: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Run an installed query using MCP.
        
        Args:
            query_name: Name of installed query
            context: MCP context
            parameters: Optional query parameters
            
        Returns:
            Query results
        """
        request = MCPRequest(
            operation="run_query",
            context=context,
            parameters={
                "query_name": query_name,
                **(parameters or {})
            }
        )
        return self.execute_request(request)
        
    def interpret_query(self,
                       query_text: str,
                       context: MCPContext,
                       parameters: Optional[Dict[str, Any]] = None) -> MCPResponse:
        """Interpret and run a query using MCP.
        
        Args:
            query_text: Query text to interpret
            context: MCP context
            parameters: Optional query parameters
            
        Returns:
            Query results
        """
        request = MCPRequest(
            operation="interpret_query",
            context=context,
            parameters={
                "query_text": query_text,
                **(parameters or {})
            }
        )
        return self.execute_request(request)
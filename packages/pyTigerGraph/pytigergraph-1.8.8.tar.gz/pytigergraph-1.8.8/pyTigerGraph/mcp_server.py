"""MCP Server implementation for pyTigerGraph.

This module provides a server implementation that handles Model Context Protocol (MCP) requests.
"""

import json
import logging
from typing import Any, Dict, Optional
from flask import Flask, request, jsonify
from .mcp import MCPContext, MCPRequest, MCPResponse
from .pyTigerGraph import TigerGraphConnection

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server for TigerGraph operations."""
    
    def __init__(self, conn: TigerGraphConnection, host: str = "0.0.0.0", port: int = 5000):
        """Initialize MCP Server.
        
        Args:
            conn: TigerGraph connection instance
            host: Host to bind server to
            port: Port to listen on
        """
        self.conn = conn
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes for MCP endpoints."""
        
        @self.app.route('/mcp', methods=['POST'])
        def handle_mcp_request():
            try:
                # Parse request
                data = request.json
                if not data:
                    return jsonify({"error": "No data provided"}), 400

                # Create MCP context
                context = MCPContext.from_dict(data.get("context", {}))
                
                # Create and execute MCP request
                mcp_request = MCPRequest(
                    operation=data.get("operation"),
                    context=context,
                    parameters=data.get("parameters")
                )
                
                # Execute request based on operation type
                if mcp_request.operation == "query":
                    response = self._handle_query(mcp_request)
                elif mcp_request.operation == "run_query":
                    response = self._handle_run_query(mcp_request)
                elif mcp_request.operation == "interpret_query":
                    response = self._handle_interpret_query(mcp_request)
                else:
                    response = MCPResponse(
                        success=False,
                        error=f"Unknown operation: {mcp_request.operation}"
                    )
                
                return jsonify(response.to_dict())
                
            except Exception as e:
                return jsonify(MCPResponse(
                    success=False,
                    error=str(e)
                ).to_dict()), 500

    def _handle_query(self, request: MCPRequest) -> MCPResponse:
        """Handle a generic query request."""
        try:
            query = request.parameters.get("query")
            if not query:
                return MCPResponse(success=False, error="No query provided")
            
            result = self.conn.gsql(query)
            return MCPResponse(success=True, data=result)
        except Exception as e:
            return MCPResponse(success=False, error=str(e))

    def _handle_run_query(self, request: MCPRequest) -> MCPResponse:
        """Handle running an installed query."""
        try:
            query_name = request.parameters.get("query_name")
            if not query_name:
                return MCPResponse(success=False, error="No query name provided")
            
            params = request.parameters.get("params", {})
            result = self.conn.runInstalledQuery(query_name, params)
            return MCPResponse(success=True, data=result)
        except Exception as e:
            return MCPResponse(success=False, error=str(e))

    def _handle_interpret_query(self, request: MCPRequest) -> MCPResponse:
        """Handle interpreting a query."""
        try:
            query_text = request.parameters.get("query_text")
            if not query_text:
                return MCPResponse(success=False, error="No query text provided")
            
            result = self.conn.runInterpretedQuery(query_text)
            return MCPResponse(success=True, data=result)
        except Exception as e:
            return MCPResponse(success=False, error=str(e))

    def start(self):
        """Start the MCP server."""
        self.app.run(host=self.host, port=self.port)
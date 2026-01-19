#!/usr/bin/env python3
"""
MCP Server for Claude Crypto Agent
Allows Claude Desktop to invoke crypto operations
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.orchestrator import create_agent


class CryptoAgentMCPServer:
    """MCP Server for Crypto Agent"""
    
    def __init__(self):
        self.agent = None
        self.initialized = False
    
    async def initialize_agent(self):
        """Initialize the crypto agent"""
        if not self.initialized:
            self.agent = await create_agent()
            self.initialized = True
    
    async def handle_request(self, method: str, params: dict):
        """Handle MCP requests"""
        
        # Handle MCP initialize method (required!)
        if method == "initialize":
            return {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "crypto-agent",
                    "version": "1.0.0"
                }
            }
        
        # Initialize agent if needed (lazy initialization after handshake)
        if not self.initialized and method in ["tools/list", "tools/call"]:
            await self.initialize_agent()
        
        if method == "tools/list":
            # List available tools
            return {
                "tools": [
                    {
                        "name": "generate_certificate",
                        "description": "Generate a TLS/SSL certificate for a domain",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "domain": {
                                    "type": "string",
                                    "description": "Domain name for the certificate"
                                },
                                "certificate_type": {
                                    "type": "string",
                                    "enum": ["tls_server", "tls_client", "code_signing"],
                                    "description": "Type of certificate"
                                },
                                "validity_days": {
                                    "type": "integer",
                                    "description": "Validity period in days (max 397)"
                                }
                            },
                            "required": ["domain"]
                        }
                    },
                    {
                        "name": "validate_policy",
                        "description": "Check if a certificate request complies with policies",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "description": "Operation to validate"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Parameters to check"
                                }
                            },
                            "required": ["operation", "parameters"]
                        }
                    },
                    {
                        "name": "get_certificate_info",
                        "description": "Get information about a certificate",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "certificate_pem": {
                                    "type": "string",
                                    "description": "Certificate in PEM format"
                                }
                            },
                            "required": ["certificate_pem"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            # Execute tool
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})
            
            # Map MCP tool calls to agent operations
            if tool_name == "generate_certificate":
                query = f"Generate a {tool_params.get('certificate_type', 'tls_server')} certificate for {tool_params['domain']}"
                if 'validity_days' in tool_params:
                    query += f" valid for {tool_params['validity_days']} days"
                
                result = await self.agent.process_request(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('response', str(result))
                        }
                    ]
                }
            
            elif tool_name == "validate_policy":
                # Use the agent to validate
                query = f"Can I perform {tool_params['operation']} with parameters: {json.dumps(tool_params['parameters'])}"
                result = await self.agent.process_request(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('response', str(result))
                        }
                    ]
                }
            
            elif tool_name == "get_certificate_info":
                query = f"Parse this certificate and give me information: {tool_params['certificate_pem']}"
                result = await self.agent.process_request(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result.get('response', str(result))
                        }
                    ]
                }
        
        return {"error": "Unknown method"}
    
    async def run(self):
        """Run MCP server (stdio mode)"""
        # Read from stdin, write to stdout
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")
                
                # Ignore notifications (they don't have an id and don't expect a response)
                if request_id is None:
                    continue
                
                response = await self.handle_request(method, params)
                
                # Write response to stdout (only for requests, not notifications)
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": response
                }))
                sys.stdout.flush()
                
            except Exception as e:
                # Debug: write errors to stderr
                print(f"Error: {str(e)}", file=sys.stderr)
                sys.stderr.flush()
                
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id", None),
                    "error": {"code": -1, "message": str(e)}
                }))
                sys.stdout.flush()


if __name__ == "__main__":
    server = CryptoAgentMCPServer()
    asyncio.run(server.run())
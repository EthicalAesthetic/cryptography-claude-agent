#!/usr/bin/env python3
"""
MCP Server for Claude Crypto Agent
Works with Claude Desktop - Fixed notification handling
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging to file instead of stdout (MCP uses stdout for protocol)
import logging
logging.basicConfig(
    filename=str(project_root / 'mcp_server.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info("Loaded .env file")

# Now import agent after path is set
from src.agent.orchestrator import create_agent


class CryptoAgentMCPServer:
    """MCP Server for Crypto Agent"""
    
    def __init__(self):
        self.agent = None
        logger.info("MCP Server initialized")
    
    async def initialize(self):
        """Initialize the crypto agent"""
        try:
            logger.info("Creating agent...")
            self.agent = await create_agent()
            logger.info("Agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create agent: {e}", exc_info=True)
            raise
    
    async def handle_request(self, request: dict):
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Handling request: {method}")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "crypto-agent",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "notifications/initialized":
                # This is a notification - no response needed
                logger.info("Client sent initialized notification")
                return None
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "generate_certificate",
                                "description": "Generate a TLS/SSL certificate for a domain. Handles the complete workflow: key generation, CSR creation, and certificate issuance.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "domain": {
                                            "type": "string",
                                            "description": "Domain name for the certificate (e.g., api.example.com)"
                                        },
                                        "validity_days": {
                                            "type": "integer",
                                            "description": "Certificate validity in days (max 397, default 365)",
                                            "default": 365
                                        }
                                    },
                                    "required": ["domain"]
                                }
                            },
                            {
                                "name": "check_policy",
                                "description": "Check if a certificate request complies with organizational policies",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "validity_days": {
                                            "type": "integer",
                                            "description": "Requested validity period in days"
                                        },
                                        "key_size": {
                                            "type": "integer",
                                            "description": "Requested RSA key size in bits"
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")
                
                if tool_name == "generate_certificate":
                    domain = tool_args.get("domain")
                    validity_days = tool_args.get("validity_days", 365)
                    
                    # Create natural language query for agent
                    query = f"Generate a TLS server certificate for {domain} valid for {validity_days} days"
                    
                    logger.info(f"Sending to agent: {query}")
                    result = await self.agent.process_request(query)
                    
                    if result['status'] == 'success':
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"✅ Certificate generated successfully!\n\n{result['response']}\n\nCorrelation ID: {result['correlation_id']}"
                                    }
                                ]
                            }
                        }
                    else:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"❌ Error generating certificate: {result.get('error', 'Unknown error')}"
                                    }
                                ],
                                "isError": True
                            }
                        }
                
                elif tool_name == "check_policy":
                    validity_days = tool_args.get("validity_days")
                    key_size = tool_args.get("key_size")
                    
                    query = f"Check policy compliance for: validity={validity_days} days, key_size={key_size} bits"
                    
                    result = await self.agent.process_request(query)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result.get('response', 'Policy check completed')
                                }
                            ]
                        }
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Run MCP server (stdio mode)"""
        try:
            await self.initialize()
            logger.info("MCP Server ready, listening on stdin...")
            
            # Read from stdin line by line
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        logger.info("EOF received, shutting down")
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    logger.info(f"Received: {line[:100]}...")
                    
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    
                    # Only write response if not None (notifications don't need responses)
                    if response is not None:
                        response_str = json.dumps(response)
                        print(response_str, flush=True)
                        logger.info(f"Sent response for request {request.get('id')}")
                    else:
                        logger.info(f"No response needed for {request.get('method')}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error in main loop: {e}", exc_info=True)
                    continue
        
        except Exception as e:
            logger.error(f"Fatal error in server: {e}", exc_info=True)
            raise


async def main():
    logger.info("Starting MCP Server...")
    server = CryptoAgentMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
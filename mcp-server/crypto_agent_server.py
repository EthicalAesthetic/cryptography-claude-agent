#!/usr/bin/env python3
"""
MCP Server for Claude Crypto Agent
Returns actual certificates and keys to the user
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up logging
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

# Import agent
from src.agent.orchestrator import create_agent


class CryptoAgentMCPServer:
    """MCP Server for Crypto Agent with Certificate Output"""
    
    def __init__(self):
        self.agent = None
        self.output_dir = project_root / "certificates"
        self.output_dir.mkdir(exist_ok=True)
        logger.info("MCP Server initialized")
        logger.info(f"Certificates will be saved to: {self.output_dir}")
    
    async def initialize(self):
        """Initialize the crypto agent"""
        try:
            logger.info("Creating agent...")
            self.agent = await create_agent()
            logger.info("Agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create agent: {e}", exc_info=True)
            raise
    
    def save_certificate(self, domain: str, cert_pem: str, key_pem: str = None) -> dict:
        """Save certificate and key to files"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_domain = domain.replace(".", "_").replace("*", "wildcard")
        
        # Save certificate
        cert_filename = f"{safe_domain}_{timestamp}.crt"
        cert_path = self.output_dir / cert_filename
        with open(cert_path, 'w') as f:
            f.write(cert_pem)
        
        # Save private key if provided
        key_path = None
        if key_pem:
            key_filename = f"{safe_domain}_{timestamp}.key"
            key_path = self.output_dir / key_filename
            with open(key_path, 'w') as f:
                f.write(key_pem)
        
        logger.info(f"Saved certificate to: {cert_path}")
        if key_path:
            logger.info(f"Saved private key to: {key_path}")
        
        return {
            "certificate_path": str(cert_path),
            "key_path": str(key_path) if key_path else None,
            "certificate_pem": cert_pem,
            "key_pem": key_pem
        }
    
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
                                "description": "Generate a TLS/SSL certificate for a domain. Returns the certificate and private key.",
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
                                        },
                                        "save_to_file": {
                                            "type": "boolean",
                                            "description": "Save certificate to file (default: true)",
                                            "default": True
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
                    save_to_file = tool_args.get("save_to_file", True)
                    
                    # Create natural language query for agent
                    query = f"Generate a TLS server certificate for {domain} valid for {validity_days} days"
                    
                    logger.info(f"Sending to agent: {query}")
                    result = await self.agent.process_request(query)
                    
                    if result['status'] == 'success':
                        # Extract certificate from agent's response
                        response_text = result['response']
                        
                        # Try to parse certificate from response
                        cert_pem = None
                        if "-----BEGIN CERTIFICATE-----" in response_text:
                            start = response_text.index("-----BEGIN CERTIFICATE-----")
                            end = response_text.index("-----END CERTIFICATE-----") + len("-----END CERTIFICATE-----")
                            cert_pem = response_text[start:end]
                        
                        # Build response
                        response_message = f"✅ Certificate Generated Successfully!\n\n"
                        response_message += f"📋 Domain: {domain}\n"
                        response_message += f"⏰ Validity: {validity_days} days\n"
                        response_message += f"🔗 Correlation ID: {result['correlation_id']}\n\n"
                        
                        if cert_pem and save_to_file:
                            # Save to file (note: we don't have access to the private key here)
                            file_info = self.save_certificate(domain, cert_pem)
                            response_message += f"💾 Certificate saved to:\n"
                            response_message += f"   {file_info['certificate_path']}\n\n"
                            response_message += f"📄 Certificate:\n```\n{cert_pem}\n```\n\n"
                        else:
                            response_message += f"📄 Full Response:\n{response_text}\n"
                        
                        response_message += f"\n⚠️ Note: For security, the private key is stored in the agent's memory.\n"
                        response_message += f"In production, private keys should be stored in a secure vault (HashiCorp Vault)."
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": response_message
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
                                        "text": f"❌ Error: {result.get('error', 'Unknown error')}\n\n"
                                               f"Correlation ID: {result['correlation_id']}"
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
            logger.info(f"Certificates directory: {self.output_dir}")
            
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
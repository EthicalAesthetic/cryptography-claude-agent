"""
Claude Cryptographic Agent - Main Orchestrator
Fixed version with workflow guidance and session state
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agent.bedrock_client import BedrockClient
from src.tools.registry import ToolRegistry
from src.policies.engine import PolicyEngine
from src.audit.logger import AuditLogger

logger = logging.getLogger(__name__)


class CryptoAgent:
    """
    Main orchestrator for cryptographic operations using Claude AI.
    """
    
    def __init__(
        self,
        bedrock_client: BedrockClient,
        tool_registry: ToolRegistry,
        policy_engine: PolicyEngine,
        audit_logger: AuditLogger
    ):
        self.bedrock = bedrock_client
        self.tools = tool_registry
        self.policy_engine = policy_engine
        self.audit = audit_logger
        
        # Session state to track generated keys/CSRs
        self.session_state = {}
        
        # System prompt for Claude
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the enhanced system prompt for Claude"""
        return """You are a cryptographic operations expert assistant. Your role is to help users manage PKI certificates and cryptographic keys safely and in compliance with organizational policies.

CRITICAL WORKFLOW FOR CERTIFICATE GENERATION:
When a user asks for a certificate (e.g., "I need a TLS certificate for example.com"), you MUST follow this exact sequence:

STEP 1: Generate Key Pair
- Use generate_key_pair tool FIRST
- Choose RSA-2048 (recommended) or ECDSA-P256
- Store the returned key_id for next step
- Example: {"algorithm": "RSA", "key_size": 2048}

STEP 2: Create CSR (Certificate Signing Request)
- Use create_csr tool with the key_id from Step 1
- Specify the domain name (common_name)
- Store the returned csr_pem for next step
- Example: {"key_id": "key_abc123", "common_name": "example.com"}

STEP 3: Issue Certificate
- Use issue_certificate tool with csr_pem from Step 2
- Specify certificate_type (usually "tls_server")
- Specify validity_days (max 397 days)
- Example: {"csr_pem": "...", "certificate_type": "tls_server", "validity_days": 365}

IMPORTANT RULES:
- You CANNOT skip steps! create_csr requires a key_id from Step 1
- You CANNOT create a CSR without first generating a key
- Always validate against policies before executing operations
- NEVER expose or return private keys to users
- Provide clear status updates at each step

Available Tools:
- generate_key_pair: Generate RSA or ECDSA key pairs
- create_csr: Create Certificate Signing Request (REQUIRES existing key_id)
- issue_certificate: Issue certificate (REQUIRES existing csr_pem)
- validate_policy: Check policy compliance
- get_certificate_info: Parse certificate details

Policy Constraints:
- RSA minimum: 2048 bits
- ECDSA curves: P-256, P-384, P-521 only
- Certificate validity: Maximum 397 days
- Allowed types: tls_server, tls_client, code_signing

Always explain what you're doing and confirm success at each step."""

    async def process_request(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user request through Claude with tool calling.
        
        Args:
            user_query: Natural language request from user
            context: Optional context (user info, previous operations, etc.)
        
        Returns:
            Dict with operation result and metadata
        """
        correlation_id = f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        
        logger.info(f"[{correlation_id}] Processing request: {user_query[:100]}...")
        
        try:
            # Prepare conversation with session context
            user_message = user_query
            
            # Add session context if we have generated keys/CSRs
            if self.session_state:
                context_info = "\n\n[Session Context]"
                if 'last_key_id' in self.session_state:
                    context_info += f"\nLast generated key: {self.session_state['last_key_id']}"
                if 'last_csr' in self.session_state:
                    context_info += f"\nLast generated CSR: Available"
                user_message += context_info
            
            messages = [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            
            # Get available tools
            tools = self.tools.get_bedrock_tools()
            
            # Start conversation with Claude
            response = await self._execute_agent_loop(
                messages=messages,
                tools=tools,
                correlation_id=correlation_id,
                max_iterations=12  # Increased for multi-step workflows
            )
            
            # Audit the operation
            await self.audit.log_operation(
                operation="agent_request",
                correlation_id=correlation_id,
                user_query=user_query,
                result=response,
                status="success"
            )
            
            return {
                "status": "success",
                "correlation_id": correlation_id,
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[{correlation_id}] Error processing request: {str(e)}", exc_info=True)
            
            await self.audit.log_operation(
                operation="agent_request",
                correlation_id=correlation_id,
                user_query=user_query,
                error=str(e),
                status="error"
            )
            
            return {
                "status": "error",
                "correlation_id": correlation_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_agent_loop(
        self,
        messages: List[Dict],
        tools: List[Dict],
        correlation_id: str,
        max_iterations: int = 12
    ) -> str:
        """
        Execute the agent loop with Claude, handling tool calls.
        """
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"[{correlation_id}] Agent iteration {iteration}/{max_iterations}")
            
            # Call Claude
            response = await self.bedrock.converse(
                messages=messages,
                tools=tools,
                system_prompt=self.system_prompt,
                temperature=0.0,  # Deterministic for security operations
                max_tokens=4096
            )
            
            # Get the content from response
            content = response.get("content", [])
            stop_reason = response.get("stopReason")
            
            logger.debug(f"[{correlation_id}] Stop reason: {stop_reason}")
            
            # Add assistant response to conversation
            messages.append({
                "role": "assistant",
                "content": content
            })
            
            # Check if we're done (no tool calls)
            if stop_reason == "end_turn":
                # Extract final text response
                final_text = self._extract_text_from_content(content)
                logger.info(f"[{correlation_id}] Agent completed after {iteration} iterations")
                return final_text
            
            elif stop_reason == "tool_use":
                # Execute tools
                tool_results = await self._execute_tools(content, correlation_id)
                
                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continue loop for next iteration
                continue
            
            else:
                logger.warning(f"[{correlation_id}] Unexpected stop reason: {stop_reason}")
                break
        
        logger.warning(f"[{correlation_id}] Max iterations ({max_iterations}) reached")
        return "⚠️ Operation exceeded maximum iterations. This might indicate a complex workflow. Please try breaking it into smaller steps."
    
    async def _execute_tools(self, content_blocks: List[Dict], correlation_id: str) -> List[Dict]:
        """
        Execute tool calls from Claude's response.
        Updated to track session state.
        """
        tool_results = []
        
        for block in content_blocks:
            if block.get("type") == "tool_use":
                tool_name = block.get("name")
                tool_input = block.get("input", {})
                tool_use_id = block.get("id")
                
                logger.info(f"[{correlation_id}] Executing tool: {tool_name}")
                logger.debug(f"[{correlation_id}] Tool input: {json.dumps(tool_input, indent=2)}")
                
                try:
                    # Execute the tool
                    result = await self.tools.execute_tool(tool_name, tool_input)
                    
                    # Track session state for key generation
                    if tool_name == "generate_key_pair" and "key_id" in result:
                        self.session_state['last_key_id'] = result['key_id']
                        logger.info(f"[{correlation_id}] Stored key_id: {result['key_id']}")
                    
                    # Track session state for CSR generation
                    if tool_name == "create_csr" and "csr_pem" in result:
                        self.session_state['last_csr'] = result['csr_pem']
                        logger.info(f"[{correlation_id}] Stored CSR in session")
                    
                    # Format result for Anthropic Messages API
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result, indent=2)
                    })
                    
                    logger.info(f"[{correlation_id}] Tool {tool_name} completed successfully")
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"[{correlation_id}] Tool {tool_name} failed: {error_msg}")
                    
                    # Format error result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps({
                            "error": error_msg,
                            "tool": tool_name,
                            "timestamp": datetime.utcnow().isoformat()
                        }),
                        "is_error": True
                    })
        
        return tool_results
    
    def _extract_text_from_content(self, content: List[Dict]) -> str:
        """Extract text from Claude's content blocks"""
        text_parts = []
        for block in content:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts)
    
    def reset_session(self):
        """Reset session state (useful for starting fresh)"""
        self.session_state = {}
        logger.info("Session state reset")


# Convenience function for simple usage
async def create_agent() -> CryptoAgent:
    """Create and initialize the crypto agent"""
    from src.agent.bedrock_client import create_bedrock_client
    from src.tools.registry import create_tool_registry
    from src.policies.engine import create_policy_engine
    from src.audit.logger import create_audit_logger
    
    bedrock = await create_bedrock_client()
    tools = await create_tool_registry()
    policies = await create_policy_engine()
    audit = await create_audit_logger()
    
    return CryptoAgent(
        bedrock_client=bedrock,
        tool_registry=tools,
        policy_engine=policies,
        audit_logger=audit
    )
"""
Claude Cryptographic Agent - Main Orchestrator
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
        
        # System prompt for Claude
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude"""
        return """You are a cryptographic operations expert assistant. Your role is to help users manage PKI certificates and cryptographic keys safely and in compliance with organizational policies.

You have access to the following tools for cryptographic operations:
- generate_key_pair: Generate asymmetric key pairs (RSA, ECDSA)
- create_csr: Create Certificate Signing Requests
- issue_certificate: Issue certificates through the CA
- validate_policy: Check if operations comply with policies
- get_certificate_info: Retrieve certificate details
- list_certificates: List certificates in inventory

CRITICAL SECURITY RULES:
1. NEVER expose or return private keys
2. ALWAYS validate against policies before operations
3. For sensitive operations (revocation), confirm with user first
4. Provide clear explanations of what you're doing

When a user requests a cryptographic operation:
1. First, validate the request against applicable policies
2. Plan the sequence of operations needed
3. Execute the tools in the correct order
4. Verify the results
5. Provide a clear summary to the user

Be helpful, secure, and policy-compliant."""

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
        
        logger.info(f"[{correlation_id}] Processing request: {user_query}")
        
        try:
            # Prepare conversation
            messages = [
                {
                    "role": "user",
                    "content": user_query
                }
            ]
            
            # Get available tools
            tools = self.tools.get_bedrock_tools()
            
            # Start conversation with Claude
            response = await self._execute_agent_loop(
                messages=messages,
                tools=tools,
                correlation_id=correlation_id,
                max_iterations=10
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
            logger.error(f"[{correlation_id}] Error processing request: {str(e)}")
            
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
        max_iterations: int = 10
    ) -> str:
        """
        Execute the agent loop with Claude, handling tool calls.
        """
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"[{correlation_id}] Agent iteration {iteration}")
            
            # Call Claude
            response = await self.bedrock.converse(
                messages=messages,
                tools=tools,
                system_prompt=self.system_prompt
            )
            
            # Add assistant response to conversation
            messages.append({
                "role": "assistant",
                "content": response.get("content", [])
            })
            
            # Check if we're done (no tool calls)
            stop_reason = response.get("stopReason")
            
            if stop_reason == "end_turn":
                # Extract final text response
                final_text = self._extract_text_from_content(response.get("content", []))
                logger.info(f"[{correlation_id}] Agent completed successfully")
                return final_text
            
            elif stop_reason == "tool_use":
                # Execute tools
                content_blocks = response.get("content", [])
                tool_results = await self._execute_tools(content_blocks, correlation_id)
                
                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            else:
                logger.warning(f"[{correlation_id}] Unexpected stop reason: {stop_reason}")
                break
        
        logger.warning(f"[{correlation_id}] Max iterations reached")
        return "Operation exceeded maximum iterations. Please try again with a simpler request."
    
    async def _execute_tools(self, content_blocks: List[Dict], correlation_id: str) -> List[Dict]:
        """
        Execute tool calls from Claude's response.
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
                    
                    tool_results.append({
                        "type": "tool_result",
                        "toolUseId": tool_use_id,
                        "content": [
                            {
                                "type": "json",
                                "json": result
                            }
                        ]
                    })
                    
                    logger.info(f"[{correlation_id}] Tool {tool_name} completed successfully")
                    
                except Exception as e:
                    logger.error(f"[{correlation_id}] Tool {tool_name} failed: {str(e)}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "toolUseId": tool_use_id,
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing tool: {str(e)}"
                            }
                        ],
                        "status": "error"
                    })
        
        return tool_results
    
    def _extract_text_from_content(self, content: List[Dict]) -> str:
        """Extract text from Claude's content blocks"""
        text_parts = []
        for block in content:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts)


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

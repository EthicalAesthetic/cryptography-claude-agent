"""
AWS Bedrock client for Claude AI integration
"""
import os
import logging
from typing import List, Dict, Any, Optional
import boto3
from botocore.config import Config

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Client for AWS Bedrock Claude API with tool calling support.
    """
    
    def __init__(
        self,
        model_id: str = None,
        region: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None
    ):
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        # Configure boto3 client
        config = Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )
        
        # Create Bedrock client
        session_kwargs = {}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs = {
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            }
        
        self.client = boto3.client(
            'bedrock-runtime',
            config=config,
            **session_kwargs
        )
        
        logger.info(f"Initialized Bedrock client with model: {self.model_id}")
    
    async def converse(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Call Claude via Bedrock Converse API with tool support.
        
        Args:
            messages: Conversation history
            tools: Available tools for Claude to use
            system_prompt: System instructions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Claude's response with potential tool calls
        """
        try:
            # Build request
            request = {
                "modelId": self.model_id,
                "messages": messages,
                "inferenceConfig": {
                    "temperature": temperature,
                    "maxTokens": max_tokens
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                request["system"] = [{"text": system_prompt}]
            
            # Add tools if provided
            if tools:
                request["toolConfig"] = {
                    "tools": tools
                }
            
            logger.debug(f"Bedrock request: {len(messages)} messages, {len(tools) if tools else 0} tools")
            
            # Call Bedrock
            response = self.client.converse(**request)
            
            # Extract output
            output = response.get("output", {})
            
            logger.debug(f"Bedrock response: stop_reason={response.get('stopReason')}")
            
            return {
                "content": output.get("message", {}).get("content", []),
                "stopReason": response.get("stopReason"),
                "usage": response.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"Bedrock API error: {str(e)}")
            raise


async def create_bedrock_client() -> BedrockClient:
    """Factory function to create Bedrock client"""
    return BedrockClient(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

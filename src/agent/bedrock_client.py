"""
AWS Bedrock client for Claude AI integration
"""
import os
import json
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
        model_id: Optional[str] = None,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        self.model_id = model_id or os.getenv(
            "BEDROCK_MODEL_ID",
            "us.anthropic.claude-3-sonnet-20240229-v1:0"
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
        Call Claude via Bedrock with tool support.
        Uses invoke_model API for compatibility.
        """
        try:
            # Build Anthropic Messages API format request
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            # Add system prompt if provided
            if system_prompt:
                request_body["system"] = system_prompt
            
            # Add tools if provided
            if tools:
                # Convert Bedrock tool format to Anthropic format
                anthropic_tools = []
                for tool in tools:
                    tool_spec = tool.get("toolSpec", {})
                    anthropic_tools.append({
                        "name": tool_spec.get("name"),
                        "description": tool_spec.get("description"),
                        "input_schema": tool_spec.get("inputSchema", {}).get("json", {})
                    })
                request_body["tools"] = anthropic_tools
            
            logger.debug(f"Bedrock request: {len(messages)} messages, {len(tools) if tools else 0} tools")
            
            # Call Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Convert Anthropic response to Bedrock converse format
            content = response_body.get("content", [])
            stop_reason = response_body.get("stop_reason")
            
            # Map stop reasons
            stop_reason_map = {
                "end_turn": "end_turn",
                "tool_use": "tool_use",
                "max_tokens": "max_tokens",
                "stop_sequence": "stop_sequence"
            }
            
            logger.debug(f"Bedrock response: stop_reason={stop_reason}")
            
            return {
                "content": content,
                "stopReason": stop_reason_map.get(stop_reason, stop_reason),
                "usage": response_body.get("usage", {})
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
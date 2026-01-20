"""
AWS Bedrock client for Claude AI integration (Fixed with better retry logic)
"""
import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Client for AWS Bedrock Claude API with tool calling support.
    Enhanced with exponential backoff retry logic.
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
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0"  # Updated to latest
        )
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        # Configure boto3 client with custom retry config
        config = Config(
            region_name=self.region,
            retries={
                'max_attempts': 1,  # We'll handle retries manually
                'mode': 'standard'
            },
            connect_timeout=60,
            read_timeout=60
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
        logger.info(f"Region: {self.region}")
    
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
        Uses invoke_model API with exponential backoff retry.
        """
        
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
        
        # Retry logic with exponential backoff
        max_retries = 3
        base_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                # Call Bedrock
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                # Parse response
                response_body = json.loads(response['body'].read())
                
                # Log token usage
                usage = response_body.get("usage", {})
                logger.info(f"Bedrock tokens - Input: {usage.get('input_tokens', 0)}, "
                           f"Output: {usage.get('output_tokens', 0)}")
                
                # Convert Anthropic response format
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
                    "usage": usage
                }
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                
                # Handle throttling with exponential backoff
                if error_code == 'ThrottlingException':
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Throttled by Bedrock (attempt {attempt + 1}/{max_retries}). "
                            f"Waiting {delay}s before retry..."
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error("Max retries exceeded for throttling")
                        raise Exception(
                            "Bedrock API rate limit exceeded. Please wait a moment and try again."
                        )
                
                # Handle other AWS errors
                elif error_code == 'ValidationException':
                    logger.error(f"Validation error: {error_message}")
                    raise Exception(f"Invalid request to Bedrock: {error_message}")
                
                elif error_code == 'ModelNotReadyException':
                    logger.error(f"Model not ready: {error_message}")
                    raise Exception(f"The model is not ready. Please check model access in AWS Bedrock console.")
                
                elif error_code == 'AccessDeniedException':
                    logger.error(f"Access denied: {error_message}")
                    raise Exception(
                        "Access denied to Bedrock. Please check:\n"
                        "1. AWS credentials are correct\n"
                        "2. Model access is enabled in Bedrock console\n"
                        "3. IAM permissions include bedrock:InvokeModel"
                    )
                
                else:
                    logger.error(f"Bedrock API error [{error_code}]: {error_message}")
                    raise Exception(f"Bedrock API error: {error_message}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Bedrock response: {str(e)}")
                raise Exception("Invalid response from Bedrock API")
                
            except Exception as e:
                logger.error(f"Unexpected error calling Bedrock: {str(e)}", exc_info=True)
                raise
        
        # Should not reach here
        raise Exception("Max retries exceeded")
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model"""
        return {
            "model_id": self.model_id,
            "region": self.region,
            "provider": "Anthropic",
            "model_name": "Claude 3.5 Sonnet"
        }


async def create_bedrock_client() -> BedrockClient:
    """Factory function to create Bedrock client"""
    return BedrockClient(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region=os.getenv("AWS_REGION")
    )
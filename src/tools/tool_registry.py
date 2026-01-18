"""
Tool Registry - Manages all available tools for the agent
"""
import logging
from typing import Dict, Any, List
from src.tools.crypto_tools import GenerateKeyPairTool, CreateCSRTool
from src.tools.pki_tools import IssueCertificateTool, GetCertificateInfoTool
from src.tools.policy_tools import ValidatePolicyTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for all cryptographic operation tools.
    """
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        tools = [
            GenerateKeyPairTool(),
            CreateCSRTool(),
            IssueCertificateTool(),
            ValidatePolicyTool(),
            GetCertificateInfoTool()
        ]
        
        for tool in tools:
            self.register_tool(tool)
    
    def register_tool(self, tool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_bedrock_tools(self) -> List[Dict]:
        """
        Get tools in AWS Bedrock format.
        
        Returns:
            List of tool specifications for Bedrock API
        """
        return [tool.to_bedrock_format() for tool in self.tools.values()]
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
        
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        
        try:
            logger.info(f"Executing tool: {tool_name}")
            result = await tool.execute(**parameters)
            logger.info(f"Tool {tool_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {str(e)}")
            raise


async def create_tool_registry() -> ToolRegistry:
    """Factory function to create tool registry"""
    return ToolRegistry()

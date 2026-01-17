"""
LLM Client abstraction using unified OpenAI SDK for all providers.
Follows industry best practices with OpenAI-compatible API endpoints (Jan 2026 standard).
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI

from config.settings import LLM_CONFIGS


class LLMClient:
    """
    Unified LLM client using OpenAI SDK for multiple providers.
    
    This implementation leverages the industry-standard OpenAI-compatible API format
    that most LLM providers support as of 2026. By using a single SDK with different
    base URLs and API keys, we achieve:
    - Simplified dependency management (single SDK)
    - Consistent interface across providers
    - Easy provider switching via configuration
    - Native tool/function calling support
    """

    def __init__(self, provider: str = "openai") -> None:
        """
        Initialize LLM client for specified provider.
        
        Args:
            provider: Provider name ("openai", "gemini", etc.)
            
        Raises:
            ValueError: If provider is not configured
        """
        if provider not in LLM_CONFIGS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Available providers: {', '.join(LLM_CONFIGS.keys())}"
            )
        
        config = LLM_CONFIGS[provider]
        self.provider = provider
        self.model = config["model"]
        
        
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"],
        )

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        """
        Execute chat completion with tool calling support.
        
        Args:
            messages: List of message dictionaries in OpenAI format
            tools: Optional list of tool definitions in OpenAI format
            
        Returns:
            OpenAI ChatCompletion response object
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            kwargs["tools"] = tools
        
        response = self.client.chat.completions.create(**kwargs)
        return response

    def parse_tool_calls(self, response) -> List[Dict[str, Any]]:
        """
        Parse tool calls from response in unified format.
        
        Args:
            response: OpenAI ChatCompletion response
            
        Returns:
            List of tool call dictionaries with 'id', 'name', and 'arguments'
        """
        tool_calls = []
        
        if (
            hasattr(response.choices[0].message, 'tool_calls') 
            and response.choices[0].message.tool_calls
        ):
            for call in response.choices[0].message.tool_calls:
                tool_calls.append({
                    'id': call.id,
                    'name': call.function.name,
                    'arguments': call.function.arguments,
                })
        
        return tool_calls


def create_llm_client(provider: str = "openai") -> LLMClient:
    """
    Factory function to create LLM client instance.
    
    Args:
        provider: Provider name ("openai", "gemini", etc.)
        
    Returns:
        Initialized LLM client instance
        
    Raises:
        ValueError: If provider is not supported
    """
    return LLMClient(provider=provider)

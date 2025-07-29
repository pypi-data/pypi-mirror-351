"""Azure OpenAI LLM Provider"""

import os
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from openai import AsyncAzureOpenAI, AzureOpenAI

from .base import BaseLLMProvider, LLMResponse, LLMConfig


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)
        
        # Azure-specific configuration
        self.api_key = self.get_api_key("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", self.config.base_url)
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", self.config.model)
        
        if self.api_key and self.endpoint:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            self.async_client = AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        else:
            self.client = None
            self.async_client = None
    
    def _validate_config(self):
        """Validate Azure OpenAI configuration"""
        if not self.endpoint:
            raise ValueError("Azure OpenAI endpoint not configured")
        
        if not self.deployment_name:
            raise ValueError("Azure OpenAI deployment name not configured")
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from Azure OpenAI"""
        if not self.async_client:
            raise ValueError("Azure OpenAI not properly configured")
        
        # Prepare messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Use deployment name instead of model
        params = {
            "model": kwargs.get("deployment_name", self.deployment_name),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        # Make API call
        try:
            response = await self.async_client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Azure uses same pricing as OpenAI
            cost = self._calculate_cost(
                usage["input_tokens"],
                usage["output_tokens"]
            )
            
            return LLMResponse(
                content=content,
                model=self.deployment_name,
                usage=usage,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                    "deployment": self.deployment_name
                },
                cost=cost
            )
            
        except Exception as e:
            raise Exception(f"Azure OpenAI API error: {str(e)}")
    
    async def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from Azure OpenAI"""
        if not self.async_client:
            raise ValueError("Azure OpenAI not properly configured")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": kwargs.get("deployment_name", self.deployment_name),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True
        }
        
        try:
            stream = await self.async_client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"Azure OpenAI streaming error: {str(e)}")
    
    def estimate_cost(self, prompt: str, completion: str) -> float:
        """Estimate cost for Azure OpenAI API call"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(completion)
        
        return self._calculate_cost(input_tokens, output_tokens)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        # Default pricing - Azure typically uses same as OpenAI
        # This should be configured based on your Azure agreement
        input_cost = (input_tokens / 1000) * 0.002
        output_cost = (output_tokens / 1000) * 0.002
        
        return input_cost + output_cost
    
    def list_models(self) -> List[str]:
        """List available deployments"""
        # In practice, this would query Azure for available deployments
        return [self.deployment_name] if self.deployment_name else []
    
    def sync_complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Synchronous completion for CLI usage"""
        return asyncio.run(self.complete(prompt, **kwargs))
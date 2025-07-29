"""OpenAI LLM Provider"""

import os
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from openai import AsyncOpenAI, OpenAI

from .base import BaseLLMProvider, LLMResponse, LLMConfig


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""
    
    MODELS = [
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4",
        "gpt-4-32k",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-instruct"
    ]
    
    COST_PER_1K_TOKENS = {
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-32k": {"input": 0.06, "output": 0.12},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-16k": {"input": 0.001, "output": 0.002},
        "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002},
        "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002}
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)
        self.api_key = self.get_api_key("OPENAI_API_KEY")
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.async_client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            self.async_client = None
    
    def _validate_config(self):
        """Validate OpenAI configuration"""
        if self.config.model == "default":
            self.config.model = "gpt-3.5-turbo"
        
        if self.config.model not in self.MODELS:
            # Allow custom/new models
            pass
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from OpenAI"""
        if not self.async_client:
            raise ValueError("OpenAI API key not configured")
        
        # Prepare messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Merge kwargs with config
        params = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            params["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            params["presence_penalty"] = kwargs["presence_penalty"]
        
        # Make API call
        try:
            response = await self.async_client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            cost = self._calculate_cost(
                params["model"],
                usage["input_tokens"],
                usage["output_tokens"]
            )
            
            return LLMResponse(
                content=content,
                model=params["model"],
                usage=usage,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id
                },
                cost=cost
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from OpenAI"""
        if not self.async_client:
            raise ValueError("OpenAI API key not configured")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": kwargs.get("model", self.config.model),
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
            raise Exception(f"OpenAI streaming error: {str(e)}")
    
    def estimate_cost(self, prompt: str, completion: str) -> float:
        """Estimate cost for OpenAI API call"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(completion)
        
        return self._calculate_cost(
            self.config.model,
            input_tokens,
            output_tokens
        )
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost based on token usage"""
        # Default to GPT-3.5 pricing if model not found
        costs = self.COST_PER_1K_TOKENS.get(model, self.COST_PER_1K_TOKENS["gpt-3.5-turbo"])
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def list_models(self) -> List[str]:
        """List available OpenAI models"""
        return self.MODELS.copy()
    
    def sync_complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Synchronous completion for CLI usage"""
        return asyncio.run(self.complete(prompt, **kwargs))
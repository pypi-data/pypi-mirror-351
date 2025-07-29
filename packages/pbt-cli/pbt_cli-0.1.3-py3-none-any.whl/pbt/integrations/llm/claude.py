"""Claude (Anthropic) LLM Provider"""

import os
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from anthropic import AsyncAnthropic, Anthropic
from anthropic.types import Message

from .base import BaseLLMProvider, LLMResponse, LLMConfig


class ClaudeProvider(BaseLLMProvider):
    """Claude/Anthropic provider implementation"""
    
    MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229", 
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2"
    ]
    
    COST_PER_1K_TOKENS = {
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        "claude-2.1": {"input": 0.008, "output": 0.024},
        "claude-2.0": {"input": 0.008, "output": 0.024},
        "claude-instant-1.2": {"input": 0.00163, "output": 0.00551}
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)
        self.api_key = self.get_api_key("ANTHROPIC_API_KEY")
        
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
            self.async_client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None
            self.async_client = None
    
    def _validate_config(self):
        """Validate Claude configuration"""
        if self.config.model == "default":
            self.config.model = "claude-3-sonnet-20240229"
        
        if self.config.model not in self.MODELS:
            raise ValueError(f"Invalid Claude model: {self.config.model}")
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from Claude"""
        if not self.async_client:
            raise ValueError("Anthropic API key not configured")
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Merge kwargs with config
        params = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens or 1000),
            "temperature": kwargs.get("temperature", self.config.temperature),
        }
        
        if system:
            params["system"] = system
        
        # Make API call
        try:
            response = await self.async_client.messages.create(**params)
            
            content = response.content[0].text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
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
                    "stop_reason": response.stop_reason,
                    "id": response.id
                },
                cost=cost
            )
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    async def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from Claude"""
        if not self.async_client:
            raise ValueError("Anthropic API key not configured")
        
        messages = [{"role": "user", "content": prompt}]
        
        params = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens or 1000),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True
        }
        
        if system:
            params["system"] = system
        
        try:
            async with self.async_client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            raise Exception(f"Claude streaming error: {str(e)}")
    
    def estimate_cost(self, prompt: str, completion: str) -> float:
        """Estimate cost for Claude API call"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(completion)
        
        return self._calculate_cost(
            self.config.model,
            input_tokens,
            output_tokens
        )
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost based on token usage"""
        costs = self.COST_PER_1K_TOKENS.get(model, self.COST_PER_1K_TOKENS["claude-3-sonnet-20240229"])
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def list_models(self) -> List[str]:
        """List available Claude models"""
        return self.MODELS.copy()
    
    def sync_complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Synchronous completion for CLI usage"""
        return asyncio.run(self.complete(prompt, **kwargs))
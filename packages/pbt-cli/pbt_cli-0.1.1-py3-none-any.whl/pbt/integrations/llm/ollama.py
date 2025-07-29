"""Ollama Local LLM Provider"""

import os
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, AsyncIterator

from .base import BaseLLMProvider, LLMResponse, LLMConfig


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider implementation"""
    
    DEFAULT_MODELS = [
        "llama2",
        "llama2-uncensored",
        "codellama",
        "mistral",
        "mixtral",
        "neural-chat",
        "starling-lm",
        "orca-mini",
        "vicuna",
        "phi"
    ]
    
    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)
        self.base_url = self.config.base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    def _validate_config(self):
        """Validate Ollama configuration"""
        if self.config.model == "default":
            self.config.model = "llama2"
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from Ollama"""
        
        # Prepare request
        data = {
            "model": kwargs.get("model", self.config.model),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
            }
        }
        
        if system:
            data["system"] = system
        
        if "max_tokens" in kwargs or self.config.max_tokens:
            data["options"]["num_predict"] = kwargs.get("max_tokens", self.config.max_tokens)
        
        # Make API call
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")
                    
                    result = await response.json()
                    
                    content = result.get("response", "")
                    
                    # Ollama provides limited usage stats
                    usage = {
                        "input_tokens": self.count_tokens(prompt),
                        "output_tokens": self.count_tokens(content),
                        "total_tokens": self.count_tokens(prompt) + self.count_tokens(content)
                    }
                    
                    return LLMResponse(
                        content=content,
                        model=data["model"],
                        usage=usage,
                        metadata={
                            "total_duration": result.get("total_duration"),
                            "load_duration": result.get("load_duration"),
                            "eval_count": result.get("eval_count"),
                            "eval_duration": result.get("eval_duration")
                        },
                        cost=0.0  # Local models have no API cost
                    )
                    
        except asyncio.TimeoutError:
            raise Exception(f"Ollama request timed out after {self.config.timeout}s")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    async def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from Ollama"""
        
        data = {
            "model": kwargs.get("model", self.config.model),
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
            }
        }
        
        if system:
            data["system"] = system
        
        if "max_tokens" in kwargs or self.config.max_tokens:
            data["options"]["num_predict"] = kwargs.get("max_tokens", self.config.max_tokens)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")
                    
                    async for line in response.content:
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            raise Exception(f"Ollama streaming error: {str(e)}")
    
    def estimate_cost(self, prompt: str, completion: str) -> float:
        """Estimate cost (always 0 for local models)"""
        return 0.0
    
    async def list_models_async(self) -> List[str]:
        """List available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    else:
                        return self.DEFAULT_MODELS
        except:
            return self.DEFAULT_MODELS
    
    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            return asyncio.run(self.list_models_async())
        except:
            return self.DEFAULT_MODELS
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {"name": model_name, "stream": False}
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour timeout for large models
                ) as response:
                    if response.status == 200:
                        return True
                    return False
        except:
            return False
    
    def sync_complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Synchronous completion for CLI usage"""
        return asyncio.run(self.complete(prompt, **kwargs))
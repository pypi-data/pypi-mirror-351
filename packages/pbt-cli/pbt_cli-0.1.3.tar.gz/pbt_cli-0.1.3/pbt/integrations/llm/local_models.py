"""Local Model Provider for running models without cloud"""

import os
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .base import BaseLLMProvider, LLMResponse, LLMConfig


class LocalModelProvider(BaseLLMProvider):
    """Local model provider using HuggingFace transformers"""
    
    SUPPORTED_MODELS = {
        "gpt2": "gpt2",
        "gpt2-medium": "gpt2-medium",
        "gpt2-large": "gpt2-large",
        "gpt2-xl": "gpt2-xl",
        "bloom": "bigscience/bloom-560m",
        "flan-t5": "google/flan-t5-base",
        "falcon": "tiiuae/falcon-rw-1b",
        "phi-2": "microsoft/phi-2",
        "mistral-7b": "mistralai/Mistral-7B-v0.1",
        "llama-2-7b": "meta-llama/Llama-2-7b-hf"
    }
    
    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)
        if not TORCH_AVAILABLE:
            raise ImportError(
                "Local models require torch and transformers. "
                "Install with: pip install torch transformers"
            )
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _validate_config(self):
        """Validate local model configuration"""
        if self.config.model == "default":
            self.config.model = "gpt2"
    
    def _load_model(self):
        """Load the model and tokenizer"""
        model_name = self.SUPPORTED_MODELS.get(self.config.model, self.config.model)
        
        try:
            # Check if model is already cached
            cache_dir = os.path.expanduser("~/.cache/pbt/models")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                trust_remote_code=True
            )
            
            # Set padding token if not exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                cache_dir=cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
        except Exception as e:
            raise Exception(f"Failed to load local model {model_name}: {str(e)}")
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from local model"""
        if not self.pipeline:
            raise ValueError("Local model not loaded")
        
        # Combine system prompt if provided
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        # Generate parameters
        generate_kwargs = {
            "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens or 256),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "do_sample": kwargs.get("temperature", self.config.temperature) > 0,
            "top_p": kwargs.get("top_p", 0.95),
            "return_full_text": False
        }
        
        # Run generation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.pipeline(full_prompt, **generate_kwargs)
        )
        
        # Extract generated text
        content = result[0]["generated_text"]
        
        # Calculate token usage
        input_tokens = len(self.tokenizer.encode(full_prompt))
        output_tokens = len(self.tokenizer.encode(content))
        
        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
        
        return LLMResponse(
            content=content,
            model=self.config.model,
            usage=usage,
            metadata={
                "device": self.device,
                "model_path": self.SUPPORTED_MODELS.get(self.config.model, self.config.model)
            },
            cost=0.0  # No cost for local models
        )
    
    async def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from local model"""
        # For simplicity, we'll generate the full response and yield it in chunks
        response = await self.complete(prompt, system, **kwargs)
        
        # Yield response in chunks
        chunk_size = 10  # characters per chunk
        content = response.content
        
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            yield chunk
            await asyncio.sleep(0.01)  # Small delay to simulate streaming
    
    def estimate_cost(self, prompt: str, completion: str) -> float:
        """No cost for local models"""
        return 0.0
    
    def list_models(self) -> List[str]:
        """List available local models"""
        return list(self.SUPPORTED_MODELS.keys())
    
    def download_model(self, model_name: str) -> bool:
        """Download a model for offline use"""
        try:
            model_path = self.SUPPORTED_MODELS.get(model_name, model_name)
            cache_dir = os.path.expanduser("~/.cache/pbt/models")
            
            # Download tokenizer and model
            AutoTokenizer.from_pretrained(model_path, cache_dir=cache_dir)
            AutoModelForCausalLM.from_pretrained(model_path, cache_dir=cache_dir)
            
            return True
        except Exception:
            return False
    
    def sync_complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Synchronous completion for CLI usage"""
        return asyncio.run(self.complete(prompt, **kwargs))
"""Base LLM Provider interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncIterator
from dataclasses import dataclass
import os


@dataclass
class LLMResponse:
    """Standard response from LLM providers"""
    content: str
    model: str
    usage: Dict[str, int]
    metadata: Dict[str, Any]
    cost: float


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "default"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    retry_attempts: int = 3
    stream: bool = False


class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Generate completion from prompt"""
        pass
    
    @abstractmethod
    async def complete_stream(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion from prompt"""
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt: str, completion: str) -> float:
        """Estimate cost for prompt and completion"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models"""
        pass
    
    def get_api_key(self, env_var: str) -> Optional[str]:
        """Get API key from config or environment"""
        if self.config.api_key:
            return self.config.api_key
        return os.getenv(env_var)
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # More accurate counting would use tiktoken or similar
        return len(text) // 4
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel

class ProviderResult(BaseModel):
    content: str
    provider: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    warning: Optional[str] = None

class ProviderHealth(BaseModel):
    available: bool
    configured: bool
    provider: str
    model: str
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider, e.g. 'openai' or 'ollama'"""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model name"""
        pass

    @abstractmethod
    async def check_health(self) -> ProviderHealth:
        """Check if provider is configured and reachable"""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResult:
        """Generate a response text synchronously or through await"""
        pass

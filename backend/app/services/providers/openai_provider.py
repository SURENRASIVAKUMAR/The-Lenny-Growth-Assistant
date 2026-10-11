import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI, APIError, AuthenticationError
from backend.app.core.config import settings
from backend.app.services.providers.base import BaseLLMProvider, ProviderResult, ProviderHealth

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self._model = model or settings.OPENAI_MODEL
        self._client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._model

    async def check_health(self) -> ProviderHealth:
        if not self.api_key:
            return ProviderHealth(
                available=False,
                configured=False,
                provider=self.provider_name,
                model=self._model,
                error="OPENAI_API_KEY is not configured in environment or .env file",
            )
        try:
            # Check model list or lightweight call
            models = await self._client.models.list()
            return ProviderHealth(
                available=True,
                configured=True,
                provider=self.provider_name,
                model=self._model,
                details={"status": "connected", "model_count": len(models.data)}
            )
        except AuthenticationError:
            return ProviderHealth(
                available=False,
                configured=True,
                provider=self.provider_name,
                model=self._model,
                error="Invalid OpenAI API Key",
            )
        except Exception as e:
            return ProviderHealth(
                available=False,
                configured=True,
                provider=self.provider_name,
                model=self._model,
                error=f"OpenAI connection error: {str(e)}",
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResult:
        if not self.api_key or not self._client:
            raise ValueError(
                "OpenAI is not configured. Please supply OPENAI_API_KEY in .env or switch to Ollama local inference."
            )
        
        target_model = model or self._model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.chat.completions.create(
                model=target_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            prompt_tokens = response.usage.prompt_tokens if response.usage else None
            completion_tokens = response.usage.completion_tokens if response.usage else None
            return ProviderResult(
                content=content,
                provider=self.provider_name,
                model=target_model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
        except AuthenticationError as e:
            raise ValueError(f"OpenAI Authentication Failed: {str(e)}")
        except APIError as e:
            raise ValueError(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAIProvider: {e}")
            raise

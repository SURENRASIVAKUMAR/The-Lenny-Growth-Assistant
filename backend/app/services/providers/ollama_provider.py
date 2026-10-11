import logging
from typing import Optional, Dict, Any
import httpx
from backend.app.core.config import settings
from backend.app.services.providers.base import BaseLLMProvider, ProviderResult, ProviderHealth

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._model = model or settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return self._model

    async def check_health(self) -> ProviderHealth:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_found = any(self._model in m for m in models) if models else False
                    return ProviderHealth(
                        available=True,
                        configured=True,
                        provider=self.provider_name,
                        model=self._model,
                        details={
                            "status": "connected",
                            "available_models": models,
                            "target_model_installed": model_found,
                        },
                        error=None if model_found else f"Model '{self._model}' not found in Ollama. Available: {models}"
                    )
                return ProviderHealth(
                    available=False,
                    configured=True,
                    provider=self.provider_name,
                    model=self._model,
                    error=f"Ollama returned HTTP status {res.status_code}"
                )
        except httpx.ConnectError:
            return ProviderHealth(
                available=False,
                configured=True,
                provider=self.provider_name,
                model=self._model,
                error=f"Cannot connect to Ollama at {self.base_url}. Ensure Ollama is installed and running (`ollama serve`)."
            )
        except Exception as e:
            return ProviderHealth(
                available=False,
                configured=True,
                provider=self.provider_name,
                model=self._model,
                error=f"Ollama error: {str(e)}"
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResult:
        target_model = model or self._model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                res = await client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code != 200:
                    raise ValueError(f"Ollama error ({res.status_code}): {res.text}")
                data = res.json()
                content = data.get("message", {}).get("content", "")
                return ProviderResult(
                    content=content,
                    provider=self.provider_name,
                    model=target_model,
                    prompt_tokens=data.get("prompt_eval_count"),
                    completion_tokens=data.get("eval_count"),
                )
        except httpx.ConnectError:
            raise ValueError(
                f"Failed to connect to Ollama at {self.base_url}. Make sure Ollama is running or configure OpenAI in .env."
            )
        except httpx.TimeoutException:
            raise ValueError(f"Ollama request timed out after {self.timeout}s.")
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            raise

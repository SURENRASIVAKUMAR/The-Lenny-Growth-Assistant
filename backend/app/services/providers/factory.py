import logging
from typing import Optional, Tuple
from backend.app.core.config import settings
from backend.app.services.providers.base import BaseLLMProvider, ProviderHealth
from backend.app.services.providers.openai_provider import OpenAIProvider
from backend.app.services.providers.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

def get_provider(provider_name: Optional[str] = None, model: Optional[str] = None) -> BaseLLMProvider:
    """Instantiate the requested or configured provider."""
    name = (provider_name or settings.AI_PROVIDER).lower()
    if name == "openai":
        return OpenAIProvider(model=model)
    elif name == "ollama":
        return OllamaProvider(model=model)
    else:
        # Default fallback to configured setting or ollama
        logger.warning(f"Unknown provider '{provider_name}', falling back to default configured: {settings.AI_PROVIDER}")
        if settings.AI_PROVIDER.lower() == "openai":
            return OpenAIProvider(model=model)
        return OllamaProvider(model=model)

async def check_all_providers() -> dict:
    """Checks the status and health of both OpenAI and Ollama."""
    openai_prov = OpenAIProvider()
    ollama_prov = OllamaProvider()

    openai_health = await openai_prov.check_health()
    ollama_health = await ollama_prov.check_health()

    return {
        "active_provider": settings.AI_PROVIDER,
        "openai": openai_health.model_dump(),
        "ollama": ollama_health.model_dump(),
    }

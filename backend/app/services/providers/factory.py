import logging
from typing import Optional
from backend.app.core.config import settings
from backend.app.services.providers.base import BaseLLMProvider
from backend.app.services.providers.openai_provider import OpenAIProvider
from backend.app.services.providers.ollama_provider import OllamaProvider
from backend.app.services.providers.demo_provider import DemoSynthesizerProvider

logger = logging.getLogger(__name__)

def get_provider(provider_name: Optional[str] = None, model: Optional[str] = None) -> BaseLLMProvider:
    """Instantiate the requested or configured provider."""
    name = (provider_name or settings.AI_PROVIDER).lower()
    
    if name in ("demo", "demo_synthesizer"):
        return DemoSynthesizerProvider()
    elif name == "openai":
        return OpenAIProvider(model=model)
    elif name == "ollama":
        return OllamaProvider(model=model)
    else:
        logger.warning(f"Unknown provider '{provider_name}', checking defaults.")
        if settings.AI_PROVIDER.lower() == "openai":
            return OpenAIProvider(model=model)
        elif settings.AI_PROVIDER.lower() == "demo":
            return DemoSynthesizerProvider()
        return OllamaProvider(model=model)

async def check_all_providers() -> dict:
    """Checks the status and health of all providers."""
    openai_prov = OpenAIProvider()
    ollama_prov = OllamaProvider()
    demo_prov = DemoSynthesizerProvider()

    openai_health = await openai_prov.check_health()
    ollama_health = await ollama_prov.check_health()
    demo_health = await demo_prov.check_health()

    return {
        "active_provider": settings.AI_PROVIDER,
        "openai": openai_health.model_dump(),
        "ollama": ollama_health.model_dump(),
        "demo": demo_health.model_dump(),
    }

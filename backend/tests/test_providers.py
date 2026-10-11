import pytest
from backend.app.services.providers.openai_provider import OpenAIProvider
from backend.app.services.providers.ollama_provider import OllamaProvider
from backend.app.services.providers.factory import get_provider

@pytest.mark.asyncio
async def test_openai_provider_missing_key():
    provider = OpenAIProvider(api_key=None)
    health = await provider.check_health()
    assert health.configured is False
    assert health.available is False
    assert "OPENAI_API_KEY is not configured" in health.error

    with pytest.raises(ValueError, match="OpenAI is not configured"):
        await provider.generate_text("Hello test")

@pytest.mark.asyncio
async def test_ollama_provider_health_check():
    provider = OllamaProvider(base_url="http://localhost:11434")
    health = await provider.check_health()
    assert health.provider == "ollama"
    # Even if Ollama service is stopped on this machine, it must return a clean structured health object
    assert isinstance(health.available, bool)
    if not health.available:
        assert health.error is not None

def test_provider_factory():
    openai_inst = get_provider("openai")
    assert openai_inst.provider_name == "openai"

    ollama_inst = get_provider("ollama")
    assert ollama_inst.provider_name == "ollama"

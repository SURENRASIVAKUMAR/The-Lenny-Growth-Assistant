from unittest.mock import AsyncMock, patch
from backend.app.services.providers.base import ProviderResult

def test_chat_endpoint_with_mocked_llm(client):
    # Mock the provider's generate_text method
    mock_llm_result = ProviderResult(
        content="""According to Elena Verna and Casey Winters, retention is the foundation of growth.
If your retention curve does not flatten parallel to the x-axis, you have a bucket with no bottom.

<<<ARTIFACT:MARKDOWN:title="Retention Playbook Summary">>>
# Retention Playbook
1. Setup Phase: Day 0-1
2. Habit Formation: Week 1 to Month 1
3. Sustained Retention: Month 1+
<<<END_ARTIFACT>>>
""",
        provider="mocked_provider",
        model="test-model-v1",
    )

    with patch(
        "backend.app.services.providers.base.BaseLLMProvider.generate_text",
        new=AsyncMock(return_value=mock_llm_result),
    ), patch(
        "backend.app.services.providers.ollama_provider.OllamaProvider.generate_text",
        new=AsyncMock(return_value=mock_llm_result),
    ), patch(
        "backend.app.services.providers.openai_provider.OpenAIProvider.generate_text",
        new=AsyncMock(return_value=mock_llm_result),
    ):
        res = client.post("/api/chat", json={
            "message": "What is the fundamental law of retention according to Elena Verna?",
            "mode": "standard"
        })

        assert res.status_code == 200
        data = res.json()
        assert "session_id" in data
        assert "message" in data
        assert "citations" in data
        assert len(data["citations"]) > 0  # Grounded in retention document!
        assert data["artifact"] is not None
        assert data["artifact"]["title"] == "Retention Playbook Summary"
        assert data["artifact"]["artifact_type"] == "markdown"
        assert "# Retention Playbook" in data["artifact"]["content"]

def test_chat_ship30_mode_with_mocked_llm(client):
    mock_ship30_result = ProviderResult(
        content="""The biggest lie in product management is that user acquisition solves growth.

<<<ARTIFACT:ESSAY:title="Why Your Activation Metric is Lying">>>
# Why Your Activation Metric is Lying

## The Hook: The Leaky Bucket Illusion
Most growth teams celebrate when top-of-funnel signup volume doubles. But as Casey Winters notes, acquisition without retention is simply renting users.

## The Big Idea
Your activation metric must predict long-term habit formation, not superficial clicks.

## Tactical Playbook
1. Audit Day 7 correlation.
2. Remove friction before the Aha! milestone.

## The Memorable Takeaway
Optimize for value realization, not registration completion.
<<<END_ARTIFACT>>>
""",
        provider="mocked_provider",
        model="ship30-model",
    )

    with patch(
        "backend.app.services.providers.ollama_provider.OllamaProvider.generate_text",
        new=AsyncMock(return_value=mock_ship30_result),
    ), patch(
        "backend.app.services.providers.openai_provider.OpenAIProvider.generate_text",
        new=AsyncMock(return_value=mock_ship30_result),
    ):
        res = client.post("/api/chat", json={
            "message": "Why activation metrics lie in B2B SaaS",
            "mode": "ship30",
            "ship30_params": {
                "topic": "Why activation metrics lie in B2B SaaS",
                "audience": "Founders & VP of Growth",
                "tone": "Direct & analytical",
                "target_length": 1250
            }
        })

        assert res.status_code == 200
        data = res.json()
        assert data["artifact"] is not None
        assert data["artifact"]["artifact_type"] == "essay"
        assert "Why Your Activation Metric is Lying" in data["artifact"]["title"]

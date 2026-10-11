from backend.app.services.skills.ship30 import build_ship30_system_prompt, build_ship30_user_prompt

def test_ship30_prompt_construction():
    sys_prompt = build_ship30_system_prompt(
        audience="Seed stage founders",
        tone="Direct, contrarian, analytical",
        target_length=1250,
        title="Why Your Activation Metric is Lying to You",
    )
    assert "Ship 30 for 30" in sys_prompt
    assert "1250" in sys_prompt
    assert "Seed stage founders" in sys_prompt
    assert "Direct, contrarian, analytical" in sys_prompt
    assert "<<<ARTIFACT:ESSAY:title=" in sys_prompt
    assert "THE HOOK" in sys_prompt
    assert "THE ONE BIG IDEA" in sys_prompt
    assert "THE MEMORABLE TAKEAWAY" in sys_prompt

def test_ship30_user_prompt_with_rag():
    rag_context = "[Elena Verna on Retention]\nRetention without activation is renting users."
    user_prompt = build_ship30_user_prompt(
        topic="How to improve activation in B2B SaaS",
        rag_context=rag_context,
    )
    assert "How to improve activation in B2B SaaS" in user_prompt
    assert "Elena Verna on Retention" in user_prompt
    assert "<<<ARTIFACT:ESSAY:title=" in user_prompt

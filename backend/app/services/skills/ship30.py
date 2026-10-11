import re
from typing import Optional, Dict, Any, List

SHIP_30_CORE_GUIDELINES = """
You are a master essayist and growth strategist writing in the high-impact "Ship 30 for 30" style pioneered for digital writing.
Your mission is to produce a compelling, authoritative, and deeply practical essay of approximately {target_length} words based on the provided topic and grounded in Lenny's Growth Knowledge Base.

ESSAY STRUCTURE & ARCHITECTURE:
1. THE HOOK (First 2-3 sentences):
   - Open with a counter-intuitive observation, a sharp question, or a bold reality check.
   - Establish the immediate stakes: why traditional advice is failing product builders or growth operators today.
2. THE ONE BIG IDEA:
   - State the central thesis clearly. Do not dilute the focus with multiple unrelated concepts.
3. NARRATIVE PROGRESSION WITH HIGH-SIGNAL HEADINGS:
   - Use bold, punchy subheadings (Markdown ## and ###).
   - Each section must advance the narrative logically from problem diagnosis -> root cause -> strategic mechanism -> concrete execution.
4. CONCRETE EXAMPLES & EVIDENCE-GROUNDED CITATIONS:
   - Ground insights in concrete principles from the provided knowledge base (citing guests, frameworks, and metrics).
   - If citing a claim from Lenny's podcast or newsletter sources, reference the source explicitly.
   - Distinguish real empirical findings from illustrative hypotheticals.
   - Never fabricate guest quotes or statistics that are not supported by the context.
5. ACTIONABLE PLAYBOOK / TACTICAL BREAKDOWN:
   - Deliver clear, battle-tested operational advice that a reader can implement this week.
   - Use bullet points, comparison tables, or clear steps where they heighten clarity.
6. THE MEMORABLE TAKEAWAY (Closing section):
   - Synthesize the lesson into a single lasting heuristic or question.
   - End on an energetic call to thoughtful action.

STYLE CONSTRAINTS:
- TARGET LENGTH: Approximately {target_length} words.
- NO AI FLUFF: Strictly avoid clichés like "In today's fast-paced digital world", "Delve into", "Tapestry", "Crucial first step", or "In conclusion".
- TONE: {tone}
- AUDIENCE: {audience}

ARTIFACT FORMAT:
Wrap the complete generated essay inside an artifact block so the system and reader can view, copy, and export it:
<<<ARTIFACT:ESSAY:title="{title}">>>
[Full Markdown essay content here]
<<<END_ARTIFACT>>>
"""

def build_ship30_system_prompt(
    audience: Optional[str] = None,
    tone: Optional[str] = None,
    target_length: int = 1250,
    title: str = "Growth Essay",
) -> str:
    audience_str = audience or "Product managers, growth practitioners, and tech founders"
    tone_str = tone or "Sharp, analytical, conversational, authoritative, and tactical"
    return SHIP_30_CORE_GUIDELINES.format(
        target_length=target_length,
        audience=audience_str,
        tone=tone_str,
        title=title,
    )

def build_ship30_user_prompt(
    topic: str,
    rag_context: Optional[str] = None,
    additional_instructions: Optional[str] = None,
) -> str:
    prompt_parts = [
        f"TOPIC / PROMPT:\n{topic}\n"
    ]

    if rag_context:
        prompt_parts.append(
            f"KNOWLEDGE BASE EVIDENCE (Use these real insights, guest case studies, and frameworks where applicable):\n"
            f"----------------------------------------\n"
            f"{rag_context}\n"
            f"----------------------------------------\n"
        )
    else:
        prompt_parts.append(
            "Note: No specific knowledge base documents matched. Reason from first principles of modern product growth while clearly stating assumptions.\n"
        )

    if additional_instructions:
        prompt_parts.append(f"ADDITIONAL GUIDANCE:\n{additional_instructions}\n")

    prompt_parts.append(
        "Generate the complete Ship 30 for 30 essay now, formatted cleanly in Markdown and enclosed within the <<<ARTIFACT:ESSAY:title=\"...\">>> block."
    )

    return "\n".join(prompt_parts)

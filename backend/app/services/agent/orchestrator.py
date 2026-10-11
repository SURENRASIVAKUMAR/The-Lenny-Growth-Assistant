import re
import json
import logging
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.session import ChatSession, Message
from backend.app.models.artifact import Artifact
from backend.app.schemas.message import ChatRequest, ChatResponse, MessageResponse, Citation, GeneratedArtifactData
from backend.app.services.providers.factory import get_provider
from backend.app.services.providers.demo_provider import DemoSynthesizerProvider
from backend.app.services.rag.retriever import retrieve_relevant_chunks
from backend.app.services.skills.ship30 import build_ship30_system_prompt, build_ship30_user_prompt

logger = logging.getLogger(__name__)

UNRELATED_TOPIC_KEYWORDS = {
    "code", "python", "javascript", "typescript", "c++", "java", "sql", "syntax",
    "math", "calculus", "integral", "derivative", "algebra", "theorem", "equation",
    "recipe", "cooking", "dinner", "cake", "bake",
    "medicine", "symptom", "disease", "treatment", "doctor",
    "weather", "forecast", "climate", "temperature",
    "movie", "actor", "hollywood", "celebrity", "football", "basketball", "cricket",
    "quantum", "physics", "chemistry", "biology", "gravity"
}

def is_unrelated_topic(query: str) -> bool:
    tokens = set(re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", query.lower()))
    if tokens.intersection(UNRELATED_TOPIC_KEYWORDS):
        return True
    return False

STANDARD_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an authoritative product and growth advisory intelligence strictly grounded in Lenny's Podcast and Newsletter transcripts.

STRICT SOURCE-DATA-ONLY POLICY:
1. ONLY USE RETRIEVED EXCERPTS: Answer questions about Lenny's Podcast, guests, frameworks, and advice ONLY using the retrieved transcript excerpts provided below.
2. DO NOT USE PRETRAINED/EXTERNAL KNOWLEDGE: Never invent podcast episodes, guest quotes, advice, or external URLs.
3. PARTIAL EVIDENCE: If the source material supports only part of the question, answer only the supported portion and explicitly declare what could not be verified from the available repository content.
4. CITATIONS: Every claim must be traceable to the retrieved episode title and guest.
5. ARTIFACTS: When the user asks for a structured guide, checklist, code, or standalone document, encapsulate it in an artifact block:
<<<ARTIFACT:TYPE:title="Descriptive Title">>>
[Full document content here]
<<<END_ARTIFACT>>>
Supported TYPE values: markdown, html, essay, code.

RETRIEVED KNOWLEDGE BASE EXCERPTS:
----------------------------------------
{context}
----------------------------------------
"""

def extract_artifact(text: str) -> Tuple[Optional[GeneratedArtifactData], str]:
    """
    Finds and extracts artifact blocks from model response, returning the artifact
    data and the cleaned display text.
    """
    pattern = r'<<<ARTIFACT:(?P<type>[a-zA-Z0-9_-]+):title="(?P<title>[^"]+)"(?:.*?)>>>(?P<content>.*?)<<<END_ARTIFACT>>>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        atype = match.group("type").strip().lower()
        title = match.group("title").strip()
        content = match.group("content").strip()
        
        cleaned_text = re.sub(
            pattern,
            f"\n\n*Created artifact: **{title}** ({atype.upper()}) — Viewable in the Artifact Viewer panel.*\n\n",
            text,
            flags=re.DOTALL
        ).strip()

        artifact_data = GeneratedArtifactData(
            title=title,
            artifact_type=atype,
            content=content,
            metadata={"extracted": True}
        )
        return artifact_data, cleaned_text

    # Secondary check: html code fences
    html_block = re.search(r'```html\n(<!DOCTYPE html>.*?)```', text, re.DOTALL | re.IGNORECASE)
    if html_block:
        content = html_block.group(1).strip()
        artifact_data = GeneratedArtifactData(
            title="Generated Web Artifact",
            artifact_type="html",
            content=content,
            metadata={"auto_detected": True}
        )
        return artifact_data, text

    return None, text

async def execute_agent_chat(request: ChatRequest, db: Session) -> ChatResponse:
    """
    Orchestrates the complete agent chat request lifecycle with RAG grounding,
    provider execution, transparent fallback, artifact extraction, and persistence.
    """
    # 1. Resolve Session
    session_id = request.session_id
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(id=session_id, title=request.message[:40])
            db.add(session)
            db.commit()
    else:
        session = ChatSession(title=request.message[:40])
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    # 2. Persist User Message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()

    # 2b. Pre-Retrieval Gate: If topic is strictly unrelated (Case D), return immediate refusal
    if is_unrelated_topic(request.message):
        if request.mode == "ship30":
            refusal_content = (
                "I couldn't find sufficient supporting information for this topic in the indexed "
                "Lenny’s Podcast / Newsletter repository to write an authoritative, source-grounded essay. "
                "The Lenny Growth Assistant only creates Ship 30 for 30 essays when backed by indexed podcast episodes."
            )
        else:
            refusal_content = (
                "I don't have sufficient information about this topic in the specified "
                "Lenny’s Podcast / Newsletter repository to provide a source-grounded answer."
            )
        asst_msg = Message(
            session_id=session_id,
            role="assistant",
            content=refusal_content,
            model_used="lenny-strict-guard-v1",
            provider_used="system_grounding_policy",
            citations=None,
        )
        db.add(asst_msg)
        db.commit()
        db.refresh(asst_msg)

        return ChatResponse(
            session_id=session_id,
            message=MessageResponse.model_validate(asst_msg),
            citations=[],
            artifact=None,
            provider_used="system_grounding_policy",
            model_used="lenny-strict-guard-v1",
            rag_used=False,
            warning="Answer blocked: Query is outside the scope of Lenny's Podcast repository.",
        )

    # 3. RAG Retrieval
    chunks, citations, has_evidence = await retrieve_relevant_chunks(
        query=request.message,
        db=db,
        top_k=settings.RAG_TOP_K,
    )
    
    # STRICT GROUNDING POLICY ENFORCEMENT:
    # If the retrieved knowledge from ChatPRD/lennys-podcast-transcripts lacks sufficient evidence,
    # block normal generation and return the explicit source-grounding limitation message.
    if not has_evidence or not chunks:
        if request.mode == "ship30":
            refusal_content = (
                "I couldn't find sufficient supporting information for this topic in the indexed "
                "Lenny’s Podcast / Newsletter repository to write an authoritative, source-grounded essay. "
                "The Lenny Growth Assistant only creates Ship 30 for 30 essays when backed by indexed podcast episodes."
            )
        else:
            refusal_content = (
                "I couldn't find sufficient supporting information for this question in the indexed "
                "Lenny’s Podcast / Newsletter repository. I can answer only when the available "
                "source material supports the response."
            )

        asst_msg = Message(
            session_id=session_id,
            role="assistant",
            content=refusal_content,
            model_used="lenny-strict-guard-v1",
            provider_used="system_grounding_policy",
            citations=None,
        )
        db.add(asst_msg)
        db.commit()
        db.refresh(asst_msg)

        return ChatResponse(
            session_id=session_id,
            message=MessageResponse.model_validate(asst_msg),
            citations=[],
            artifact=None,
            provider_used="system_grounding_policy",
            model_used="lenny-strict-guard-v1",
            rag_used=False,
            warning="Answer blocked: Query lacked sufficient authoritative repository evidence.",
        )

    rag_context_parts = []
    for c in chunks:
        author = f" (Guest: {c['author_or_guest']})" if c.get("author_or_guest") else ""
        provenance = f" [File: {c.get('provenance_file', '')}]" if c.get("provenance_file") else ""
        rag_context_parts.append(f"[{c['source_title']}{author}{provenance}]\n{c['content']}")
    rag_context = "\n\n".join(rag_context_parts) if rag_context_parts else "No matching documents found in knowledge base."

    # 4. Prompt Assembly
    if request.mode == "ship30":
        ship_params = request.ship30_params or {}
        if hasattr(ship_params, "model_dump"):
            ship_params = ship_params.model_dump()
        target_len = ship_params.get("target_length") or 1250
        audience = ship_params.get("audience")
        tone = ship_params.get("tone")
        title = ship_params.get("topic") or request.message[:40]

        sys_prompt = build_ship30_system_prompt(
            audience=audience,
            tone=tone,
            target_length=target_len,
            title=title,
        )
        user_prompt = build_ship30_user_prompt(
            topic=request.message,
            rag_context=rag_context if has_evidence else None,
        )
    else:
        sys_prompt = STANDARD_SYSTEM_PROMPT.format(context=rag_context)
        user_prompt = request.message

    # 5. Call LLM Provider with graceful fallback
    provider_name = request.provider or settings.AI_PROVIDER
    provider = get_provider(provider_name=provider_name, model=request.model)
    
    warning = None
    try:
        provider_result = await provider.generate_text(
            prompt=user_prompt,
            system_prompt=sys_prompt,
            model=request.model,
        )
        raw_text = provider_result.content
        model_used = provider_result.model
        active_provider_used = provider_result.provider
    except Exception as e:
        logger.warning(f"Provider '{provider_name}' failed: {e}. Falling back to demo synthesizer.")
        # Fall back to DemoSynthesizerProvider with explicit disclosure
        demo_provider = DemoSynthesizerProvider()
        provider_result = await demo_provider.generate_text(
            prompt=user_prompt,
            system_prompt=sys_prompt,
        )
        raw_text = provider_result.content
        model_used = demo_provider.default_model
        active_provider_used = demo_provider.provider_name
        warning = f"Primary provider '{provider_name}' was unavailable. Response was formulated using the Built-in Knowledge Base Synthesizer."

    # 6. Extract Artifact
    artifact_data, display_content = extract_artifact(raw_text)
    saved_artifact = None

    if artifact_data:
        saved_artifact = Artifact(
            session_id=session_id,
            title=artifact_data.title,
            artifact_type=artifact_data.artifact_type,
            content=artifact_data.content,
            metadata_json=json.dumps(artifact_data.metadata or {}),
        )
        db.add(saved_artifact)
        db.commit()
        db.refresh(saved_artifact)
        artifact_data.id = saved_artifact.id

    # 7. Persist Assistant Message
    citation_json = json.dumps([c.model_dump() for c in citations]) if citations else None
    asst_msg = Message(
        session_id=session_id,
        role="assistant",
        content=display_content,
        model_used=model_used,
        provider_used=active_provider_used,
        citations=citation_json,
    )
    db.add(asst_msg)
    
    session.title = session.title or request.message[:35]
    db.commit()
    db.refresh(asst_msg)

    # 8. Return response
    return ChatResponse(
        session_id=session_id,
        message=MessageResponse(
            id=asst_msg.id,
            session_id=asst_msg.session_id,
            role=asst_msg.role,
            content=asst_msg.content,
            model_used=asst_msg.model_used,
            provider_used=asst_msg.provider_used,
            citations=citations,
            created_at=asst_msg.created_at,
        ),
        citations=citations,
        artifact=artifact_data,
        provider_used=active_provider_used,
        model_used=model_used,
        rag_used=has_evidence,
        warning=warning,
    )

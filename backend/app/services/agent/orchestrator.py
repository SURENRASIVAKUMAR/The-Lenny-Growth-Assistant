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
from backend.app.services.rag.retriever import retrieve_relevant_chunks
from backend.app.services.skills.ship30 import build_ship30_system_prompt, build_ship30_user_prompt

logger = logging.getLogger(__name__)

STANDARD_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an elite product and growth advisory intelligence grounded in Lenny Rachitsky's podcast interviews, newsletters, and growth essays.

CORE RESPONSIBILITIES:
1. GROUNDED REASONING: Ground answers firmly in the retrieved knowledge base excerpts provided below.
2. SOURCE ATTRIBUTION: Reference specific insights by citing the guest or newsletter topic (e.g. "[Guest / Topic]"). Never invent podcast episodes, guest quotes, or external URLs.
3. HONEST BOUNDARIES: If the provided knowledge base does not contain sufficient evidence to answer the user's question with confidence, clearly declare:
   "Based on the currently indexed knowledge base, there is insufficient evidence to answer this question accurately."
   Then, provide an objective first-principles response while clearly disclosing that it is not derived from Lenny's sources.
4. ARTIFACTS: When the user asks for an essay, guide, code, checklist, or standalone HTML document, encapsulate the complete deliverable in an artifact block:
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
        
        # Replace the artifact block in chat text with a clean summary banner
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

    # Secondary check: markdown or html code fences if user asked for page or essay
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
    Orchestrates the complete agent chat request lifecycle:
    1. Resolve or create ChatSession
    2. Retrieve relevant knowledge base chunks (RAG)
    3. Construct system and user prompt (standard or Ship 30 for 30)
    4. Call active LLM provider (Ollama or OpenAI)
    5. Extract any generated artifacts and persist to database
    6. Persist user and assistant messages
    7. Return structured ChatResponse
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

    # 3. RAG Retrieval
    chunks, citations, has_evidence = await retrieve_relevant_chunks(
        query=request.message,
        db=db,
        top_k=settings.RAG_TOP_K,
    )
    
    rag_context_parts = []
    for c in chunks:
        author = f" (Guest: {c['author_or_guest']})" if c.get("author_or_guest") else ""
        rag_context_parts.append(f"[{c['source_title']}{author}]\n{c['content']}")
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

    # 5. Call LLM Provider
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
        logger.warning(f"Primary provider '{provider_name}' failed: {e}. Checking fallback.")
        # Attempt fallback if OpenAI failed and Ollama might be available, or vice versa
        fallback_target = "ollama" if provider_name == "openai" else "openai"
        try:
            fallback_provider = get_provider(provider_name=fallback_target)
            fb_health = await fallback_provider.check_health()
            if fb_health.available:
                provider_result = await fallback_provider.generate_text(
                    prompt=user_prompt,
                    system_prompt=sys_prompt,
                )
                raw_text = provider_result.content
                model_used = provider_result.model
                active_provider_used = fallback_provider.provider_name
                warning = f"Original provider '{provider_name}' failed ({str(e)}). Automatically handled by {active_provider_used}:{model_used}."
            else:
                raise e
        except Exception:
            # Raise original descriptive error
            raise ValueError(f"AI Provider '{provider_name}' error: {str(e)}")

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
    
    # Update session updated_at
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

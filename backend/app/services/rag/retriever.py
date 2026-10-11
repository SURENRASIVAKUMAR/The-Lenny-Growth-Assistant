import json
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk
from backend.app.schemas.message import Citation
from backend.app.services.rag.embedder import get_embedding, cosine_similarity

logger = logging.getLogger(__name__)

CONVERSATIONAL_STOPWORDS = {
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were",
    "how", "what", "why", "who", "when", "where", "which", "according", "lennys", "lenny",
    "podcast", "podcasts", "transcript", "transcripts", "newsletter", "tell", "explain",
    "describe", "can", "could", "should", "would", "most", "effective", "strategies", "best",
    "give", "me", "does", "say", "about", "you", "please", "some", "any", "from", "do", "did",
    "that", "this", "these", "those", "guest", "guests", "recommend", "recommends", "recommended",
    "recommendation", "talk", "talks", "talked", "mention", "mentions", "mentioned", "view", "views",
    "fundamental", "law"
}

def re_tokenize(text: str) -> List[str]:
    import re
    tokens = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
    return [t for t in tokens if t not in CONVERSATIONAL_STOPWORDS]

def compute_keyword_score(query: str, text: str, title: str, author_or_guest: str = "") -> Tuple[float, float]:
    """Calculate term-overlap score focused on domain signal tokens with phrase boosting.
    Returns (kw_score, term_recall)."""
    query_tokens = set(re_tokenize(query))
    if not query_tokens:
        return 0.0, 0.0

    text_lower = text.lower()
    text_tokens = set(re_tokenize(text))
    title_tokens = set(re_tokenize(title))
    guest_tokens = set(re_tokenize(author_or_guest or ""))

    matched_content = query_tokens.intersection(text_tokens.union(title_tokens).union(guest_tokens))
    term_recall = len(matched_content) / max(len(query_tokens), 1)

    overlap_text = len(query_tokens.intersection(text_tokens))
    overlap_title = len(query_tokens.intersection(title_tokens))
    overlap_guest = len(query_tokens.intersection(guest_tokens))

    # Base score combines text match with title & guest emphasis
    base_score = (overlap_text + overlap_title * 1.5 + overlap_guest * 2.0) / max(len(query_tokens), 1)

    # Multi-word phrase bonus
    phrase_bonus = 0.0
    for phrase in [
        "activation milestone", "user activation", "aha moment", "growth loop",
        "growth tactics", "retention loop", "setup moment", "habit moment", "pmf survey",
        "retention curve", "retention"
    ]:
        if phrase in query.lower() and (phrase in text_lower or phrase in title.lower()):
            phrase_bonus += 0.25

    kw_score = min(1.0, base_score * 0.75 + phrase_bonus)
    return kw_score, term_recall

async def retrieve_relevant_chunks(
    query: str,
    db: Session,
    top_k: int = settings.RAG_TOP_K,
    min_confidence_score: float = 0.15,
) -> Tuple[List[Dict[str, Any]], List[Citation], bool]:
    """
    Performs hybrid retrieval using keyword overlap and vector cosine similarity.
    Returns:
      - relevant_chunks: List of chunk data with content, metadata, and score
      - citations: List of formatted Citation objects
      - has_confident_evidence: True if top score exceeds confidence threshold
    """
    # Fetch only authoritative, indexed chunks and sources
    chunks_with_sources = (
        db.query(DocumentChunk, KnowledgeSource)
        .join(KnowledgeSource, DocumentChunk.source_id == KnowledgeSource.id)
        .filter(KnowledgeSource.status == "indexed")
        .filter(KnowledgeSource.is_authoritative == True)
        .all()
    )

    if not chunks_with_sources:
        logger.info("Knowledge base is empty or has no authoritative documents indexed.")
        return [], [], False

    # Generate query embedding
    query_embedding = await get_embedding(query)

    scored_items = []
    for chunk, source in chunks_with_sources:
        # Keyword score and term recall
        kw_score, term_recall = compute_keyword_score(query, chunk.content, source.title, source.author_or_guest or "")

        # Vector score
        vec_score = 0.0
        if chunk.embedding:
            try:
                emb_list = json.loads(chunk.embedding)
                vec_score = max(0.0, cosine_similarity(query_embedding, emb_list))
            except Exception as e:
                logger.warning(f"Error parsing embedding for chunk {chunk.id}: {e}")

        # Combined hybrid score (harmonic or weighted average)
        combined_score = 0.45 * kw_score + 0.55 * vec_score
        
        scored_items.append({
            "chunk": chunk,
            "source": source,
            "score": combined_score,
            "kw_score": kw_score,
            "term_recall": term_recall,
            "vec_score": vec_score,
        })

    # Sort descending by score
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    top_items = scored_items[:top_k]

    # Filter out items with virtually zero relevance
    filtered_items = [item for item in top_items if item["score"] > 0.08]

    # Check evidence threshold: Top item must meet minimum confidence threshold and adequate keyword recall
    threshold = getattr(settings, "MIN_EVIDENCE_THRESHOLD", 0.20)
    has_confident_evidence = bool(
        filtered_items and (
            filtered_items[0]["score"] >= threshold and
            filtered_items[0].get("term_recall", 0.0) >= 0.35
        )
    )

    if not has_confident_evidence:
        return [], [], False

    relevant_chunks = []
    citations = []

    for item in filtered_items:
        chunk = item["chunk"]
        source = item["source"]
        
        # Build clean snippet (first 250 characters of chunk)
        snippet = chunk.content[:240].strip()
        if len(chunk.content) > 240:
            snippet += "..."

        citation = Citation(
            source_id=source.id,
            source_title=source.title,
            chunk_id=chunk.id,
            url=source.url,
            author_or_guest=source.author_or_guest,
            provenance_file=source.provenance_file,
            snippet=snippet,
        )
        citations.append(citation)

        relevant_chunks.append({
            "chunk_id": chunk.id,
            "source_id": source.id,
            "source_title": source.title,
            "author_or_guest": source.author_or_guest,
            "provenance_file": source.provenance_file,
            "url": source.url,
            "content": chunk.content,
            "score": item["score"],
            "snippet": snippet,
        })

    return relevant_chunks, citations, has_confident_evidence

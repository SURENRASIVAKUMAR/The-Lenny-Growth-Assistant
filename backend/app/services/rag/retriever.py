import json
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk
from backend.app.schemas.message import Citation
from backend.app.services.rag.embedder import get_embedding, cosine_similarity

logger = logging.getLogger(__name__)

def compute_keyword_score(query: str, text: str, title: str) -> float:
    """Calculate term-overlap score normalized between 0 and 1."""
    query_tokens = set(re_tokenize(query))
    if not query_tokens:
        return 0.0

    text_tokens = set(re_tokenize(text))
    title_tokens = set(re_tokenize(title))

    # Weight title matches higher
    overlap_text = len(query_tokens.intersection(text_tokens))
    overlap_title = len(query_tokens.intersection(title_tokens))

    score = (overlap_text + overlap_title * 2) / (len(query_tokens) * 2)
    return min(1.0, score)

def re_tokenize(text: str) -> List[str]:
    import re
    tokens = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
    # Exclude common stop words
    stopwords = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "how", "what", "why"}
    return [t for t in tokens if t not in stopwords]

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
    # Fetch all chunks and sources
    chunks_with_sources = (
        db.query(DocumentChunk, KnowledgeSource)
        .join(KnowledgeSource, DocumentChunk.source_id == KnowledgeSource.id)
        .filter(KnowledgeSource.status == "indexed")
        .all()
    )

    if not chunks_with_sources:
        logger.info("Knowledge base is empty. No documents indexed.")
        return [], [], False

    # Generate query embedding
    query_embedding = await get_embedding(query)

    scored_items = []
    for chunk, source in chunks_with_sources:
        # Keyword score
        kw_score = compute_keyword_score(query, chunk.content, source.title)

        # Vector score
        vec_score = 0.0
        if chunk.embedding:
            try:
                emb_list = json.loads(chunk.embedding)
                vec_score = max(0.0, cosine_similarity(query_embedding, emb_list))
            except Exception as e:
                logger.warning(f"Error parsing embedding for chunk {chunk.id}: {e}")

        # Combined hybrid score (harmonic or weighted average)
        combined_score = 0.4 * kw_score + 0.6 * vec_score
        
        scored_items.append({
            "chunk": chunk,
            "source": source,
            "score": combined_score,
            "kw_score": kw_score,
            "vec_score": vec_score,
        })

    # Sort descending by score
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    top_items = scored_items[:top_k]

    # Filter out items with virtually zero relevance
    filtered_items = [item for item in top_items if item["score"] > 0.05]

    has_confident_evidence = bool(
        filtered_items and filtered_items[0]["score"] >= min_confidence_score
    )

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
            snippet=snippet,
        )
        citations.append(citation)

        relevant_chunks.append({
            "chunk_id": chunk.id,
            "source_id": source.id,
            "source_title": source.title,
            "author_or_guest": source.author_or_guest,
            "url": source.url,
            "content": chunk.content,
            "score": item["score"],
            "snippet": snippet,
        })

    return relevant_chunks, citations, has_confident_evidence

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.services.rag.retriever import retrieve_relevant_chunks
from backend.app.models.knowledge import KnowledgeSource

logger = logging.getLogger(__name__)

async def tool_search_knowledge_base(query: str, db: Session, top_k: int = 4) -> Dict[str, Any]:
    """Explicit agent tool: queries the knowledge base for relevant chunks and citations."""
    chunks, citations, has_evidence = await retrieve_relevant_chunks(query, db, top_k=top_k)
    return {
        "query": query,
        "chunks": chunks,
        "citations": [c.model_dump() for c in citations],
        "has_evidence": has_evidence,
        "count": len(chunks),
    }

def tool_get_source_metadata(source_id: str, db: Session) -> Optional[Dict[str, Any]]:
    """Explicit agent tool: returns source details and summary."""
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        return None
    return {
        "id": source.id,
        "title": source.title,
        "source_type": source.source_type,
        "url": source.url,
        "author_or_guest": source.author_or_guest,
        "summary": source.summary,
        "chunk_count": source.chunk_count,
        "status": source.status,
    }

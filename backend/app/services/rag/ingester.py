import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk
from backend.app.schemas.knowledge import IngestionResult
from backend.app.services.rag.chunker import chunk_text
from backend.app.services.rag.embedder import get_embedding

logger = logging.getLogger(__name__)

async def ingest_document(
    title: str,
    content: str,
    source_type: str = "podcast_transcript",
    url: Optional[str] = None,
    author_or_guest: Optional[str] = None,
    summary: Optional[str] = None,
    db: Session = None,
    overwrite: bool = True,
) -> IngestionResult:
    """
    Ingests a document into the knowledge base, splits into chunks,
    generates embeddings, and persists to the database.
    """
    if not title or not content.strip():
        raise ValueError("Title and non-empty content are required for ingestion.")

    # Duplicate detection by title
    existing = db.query(KnowledgeSource).filter(KnowledgeSource.title == title).first()
    if existing:
        if not overwrite:
            return IngestionResult(
                source_id=existing.id,
                title=existing.title,
                chunks_created=existing.chunk_count,
                status="skipped",
                message="Document with this title already exists in the knowledge base.",
            )
        # Update existing source
        source = existing
        source.source_type = source_type
        source.url = url
        source.author_or_guest = author_or_guest
        source.summary = summary
        source.raw_content = content
        # Remove old chunks
        db.query(DocumentChunk).filter(DocumentChunk.source_id == source.id).delete()
    else:
        source = KnowledgeSource(
            title=title,
            source_type=source_type,
            url=url,
            author_or_guest=author_or_guest,
            summary=summary,
            raw_content=content,
            status="indexed",
        )
        db.add(source)
        db.flush()

    # Split into chunks
    raw_chunks = chunk_text(content)
    chunk_records = []

    for item in raw_chunks:
        emb = await get_embedding(item["content"])
        chunk = DocumentChunk(
            source_id=source.id,
            chunk_index=item["chunk_index"],
            content=item["content"],
            token_count=item["token_count"],
            embedding=json.dumps(emb),
        )
        chunk_records.append(chunk)

    db.add_all(chunk_records)
    source.chunk_count = len(chunk_records)
    source.status = "indexed"
    db.commit()
    db.refresh(source)

    logger.info(f"Ingested '{title}' with {len(chunk_records)} chunks.")
    return IngestionResult(
        source_id=source.id,
        title=source.title,
        chunks_created=len(chunk_records),
        status="success",
        message=f"Successfully indexed '{title}' into {len(chunk_records)} chunks.",
    )

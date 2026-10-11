import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk
from backend.app.schemas.knowledge import (
    KnowledgeSourceResponse,
    IngestionRequest,
    IngestionBatchRequest,
    IngestionResult,
    ChunkResponse,
)
from backend.app.services.rag.ingester import ingest_document

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sources", response_model=List[KnowledgeSourceResponse])
def list_knowledge_sources(db: Session = Depends(get_db)):
    """List all knowledge sources in the database."""
    sources = db.query(KnowledgeSource).order_by(KnowledgeSource.created_at.desc()).all()
    return sources

@router.get("/sources/{source_id}/chunks", response_model=List[ChunkResponse])
def get_source_chunks(source_id: str, db: Session = Depends(get_db)):
    """Retrieve all document chunks for a specific source."""
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    chunks = db.query(DocumentChunk).filter(DocumentChunk.source_id == source_id).order_by(DocumentChunk.chunk_index.asc()).all()
    return chunks

@router.post("/ingest", response_model=IngestionResult, status_code=status.HTTP_201_CREATED)
async def ingest_single_document(request: IngestionRequest, db: Session = Depends(get_db)):
    """Ingest a single document/transcript into the knowledge base."""
    try:
        result = await ingest_document(
            title=request.title,
            content=request.content,
            source_type=request.source_type,
            url=request.url,
            author_or_guest=request.author_or_guest,
            summary=request.summary,
            db=db,
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error ingesting document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

@router.post("/batch", response_model=List[IngestionResult])
async def ingest_batch_documents(request: IngestionBatchRequest, db: Session = Depends(get_db)):
    """Ingest multiple documents in batch."""
    results = []
    for item in request.sources:
        try:
            res = await ingest_document(
                title=item.title,
                content=item.content,
                source_type=item.source_type,
                url=item.url,
                author_or_guest=item.author_or_guest,
                summary=item.summary,
                db=db,
            )
            results.append(res)
        except Exception as e:
            results.append(
                IngestionResult(
                    source_id="error",
                    title=item.title,
                    chunks_created=0,
                    status="failed",
                    message=str(e),
                )
            )
    return results

@router.post("/refresh", response_model=dict)
def refresh_knowledge_base(db: Session = Depends(get_db)):
    """Verify and refresh chunk counts across all indexed sources."""
    sources = db.query(KnowledgeSource).all()
    total_chunks = 0
    for s in sources:
        count = db.query(DocumentChunk).filter(DocumentChunk.source_id == s.id).count()
        s.chunk_count = count
        total_chunks += count
    db.commit()
    return {
        "status": "refreshed",
        "total_sources": len(sources),
        "total_chunks": total_chunks,
    }

@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_source(source_id: str, db: Session = Depends(get_db)):
    """Delete a knowledge source and all its associated chunks."""
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Knowledge source not found")
    db.delete(source)
    db.commit()
    return None

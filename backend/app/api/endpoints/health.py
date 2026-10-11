from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db, check_database_connection
from backend.app.schemas.config import HealthResponse, ConfigStatusResponse, DatabaseStatus, ProviderStatus
from backend.app.services.providers.factory import get_provider, check_all_providers
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    db_info = check_database_connection()
    provider = get_provider()
    provider_health = await provider.check_health()
    
    return HealthResponse(
        status="healthy" if db_info["status"] == "connected" else "degraded",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        database=DatabaseStatus(**db_info),
        active_provider=ProviderStatus(
            provider=provider_health.provider,
            model=provider_health.model,
            available=provider_health.available,
            configured=provider_health.configured,
            error=provider_health.error,
            details=provider_health.details,
        ),
    )

@router.get("/config/status", response_model=ConfigStatusResponse)
async def get_config_status(db: Session = Depends(get_db)):
    db_info = check_database_connection()
    ollama_provider = get_provider("ollama")
    ollama_health = await ollama_provider.check_health()
    
    source_count = 0
    chunk_count = 0
    if db_info["status"] == "connected":
        try:
            source_count = db.query(KnowledgeSource).filter(KnowledgeSource.is_authoritative == True).count()
            chunk_count = (
                db.query(DocumentChunk)
                .join(KnowledgeSource, DocumentChunk.source_id == KnowledgeSource.id)
                .filter(KnowledgeSource.is_authoritative == True)
                .count()
            )
        except Exception:
            pass

    return ConfigStatusResponse(
        active_provider=settings.AI_PROVIDER,
        active_model=settings.OPENAI_MODEL if settings.AI_PROVIDER == "openai" else settings.OLLAMA_MODEL,
        openai_configured=bool(settings.OPENAI_API_KEY),
        openai_model=settings.OPENAI_MODEL,
        ollama_base_url=settings.OLLAMA_BASE_URL,
        ollama_model=settings.OLLAMA_MODEL,
        ollama_available=ollama_health.available,
        database_status=db_info["status"],
        database_name=settings.DB_NAME,
        active_engine=db_info.get("active_engine", "mysql"),
        rag_sources_count=source_count,
        rag_chunks_count=chunk_count,
    )

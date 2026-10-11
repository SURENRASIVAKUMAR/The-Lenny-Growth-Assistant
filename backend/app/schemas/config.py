from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DatabaseStatus(BaseModel):
    status: str
    database_name: str
    host: str
    port: int
    driver: str
    active_engine: Optional[str] = None
    setup_required: Optional[bool] = False
    setup_instructions: Optional[str] = None
    error: Optional[str] = None

class ProviderStatus(BaseModel):
    provider: str
    model: str
    available: bool
    configured: bool
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: DatabaseStatus
    active_provider: ProviderStatus

class ConfigStatusResponse(BaseModel):
    active_provider: str
    active_model: str
    openai_configured: bool
    openai_model: str
    ollama_base_url: str
    ollama_model: str
    ollama_available: bool
    database_status: str
    database_name: str
    active_engine: Optional[str] = "mysql"
    rag_sources_count: int
    rag_chunks_count: int

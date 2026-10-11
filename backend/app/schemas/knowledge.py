from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    chunk_index: int
    content: str
    token_count: Optional[int] = None
    created_at: datetime

class KnowledgeSourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(default="podcast_transcript", max_length=50)
    url: Optional[str] = Field(default=None, max_length=512)
    author_or_guest: Optional[str] = Field(default=None, max_length=255)
    summary: Optional[str] = None

class IngestionRequest(KnowledgeSourceBase):
    content: str = Field(..., min_length=10)

class IngestionBatchRequest(BaseModel):
    sources: List[IngestionRequest]

class KnowledgeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    source_type: str
    url: Optional[str] = None
    author_or_guest: Optional[str] = None
    summary: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

class IngestionResult(BaseModel):
    source_id: str
    title: str
    chunks_created: int
    status: str
    message: str

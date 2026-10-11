from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Citation(BaseModel):
    source_id: str
    source_title: str
    chunk_id: str
    url: Optional[str] = None
    author_or_guest: Optional[str] = None
    snippet: str

class MessageCreate(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    model_used: Optional[str] = None
    provider_used: Optional[str] = None
    citations: Optional[List[Citation]] = None

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    model_used: Optional[str] = None
    provider_used: Optional[str] = None
    citations: Optional[List[Citation]] = None
    created_at: datetime

class Ship30Params(BaseModel):
    topic: Optional[str] = None
    audience: Optional[str] = "Product managers, founders, and growth leaders"
    tone: Optional[str] = "Authoritative yet accessible, analytical, actionable"
    target_length: Optional[int] = 1250

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1)
    mode: Optional[str] = "standard"  # "standard" | "ship30"
    ship30_params: Optional[Ship30Params] = None
    provider: Optional[str] = None    # "openai" | "ollama" | None
    model: Optional[str] = None

class GeneratedArtifactData(BaseModel):
    id: Optional[str] = None
    title: str
    artifact_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    message: MessageResponse
    citations: List[Citation] = []
    artifact: Optional[GeneratedArtifactData] = None
    provider_used: str
    model_used: str
    rag_used: bool = False
    warning: Optional[str] = None

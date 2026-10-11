from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ArtifactCreate(BaseModel):
    session_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    artifact_type: str = Field(..., pattern="^(markdown|html|essay|code)$")
    content: str = Field(..., min_length=1)
    metadata_json: Optional[str] = None

class ArtifactUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    artifact_type: Optional[str] = None
    metadata_json: Optional[str] = None

class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    title: str
    artifact_type: str
    content: str
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

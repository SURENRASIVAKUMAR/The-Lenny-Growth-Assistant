from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class SessionBase(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)

class SessionCreate(BaseModel):
    title: Optional[str] = Field(default="New Conversation", max_length=255)

class SessionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # "markdown", "html", "essay", "code"
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded metadata (word count, tags, skill: "ship30", etc.)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    session = relationship("ChatSession", back_populates="artifacts")

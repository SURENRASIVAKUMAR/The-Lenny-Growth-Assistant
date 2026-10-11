import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False, default="podcast_transcript")  # podcast_transcript, newsletter, essay, guide
    url = Column(String(512), nullable=True)
    author_or_guest = Column(String(255), nullable=True)
    provenance_file = Column(String(512), nullable=True)  # repository relative file path (e.g. episodes/elena-verna/transcript.md)
    publish_date = Column(String(50), nullable=True)     # publication date from YAML frontmatter
    episode_duration = Column(String(50), nullable=True) # human-readable duration from YAML frontmatter
    is_authoritative = Column(Boolean, default=True, nullable=False) # True = authoritative repo; False = synthetic/demo
    summary = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="indexed")  # indexed, pending, failed
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    chunks = relationship("DocumentChunk", back_populates="source", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded metadata (e.g. section, speaker, timestamps)
    embedding = Column(Text, nullable=True)      # JSON-encoded float array or vector representation
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    source = relationship("KnowledgeSource", back_populates="chunks")

    __table_args__ = (
        Index("idx_source_chunk_index", "source_id", "chunk_index"),
    )

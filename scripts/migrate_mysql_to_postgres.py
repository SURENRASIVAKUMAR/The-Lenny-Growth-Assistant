#!/usr/bin/env python3
"""
MySQL to PostgreSQL Safe Data Migration Script.
Transfers existing chat sessions, messages, knowledge sources, document chunks,
and artifacts from MySQL to PostgreSQL without modifying or dropping MySQL data.
"""

import os
import sys
import logging
from datetime import datetime

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.models import (
    Base,
    ChatSession,
    Message,
    KnowledgeSource,
    DocumentChunk,
    Artifact,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migration")

def run_migration():
    mysql_url = settings.MYSQL_DATABASE_URL or "mysql+pymysql://root:@localhost:3306/lenny_growth_assistant"
    pg_url = settings.get_database_url()

    logger.info("=== Starting Safe MySQL -> PostgreSQL Migration ===")
    logger.info(f"Source (MySQL): {mysql_url.split('@')[-1]}")
    logger.info(f"Target (PostgreSQL): {pg_url.split('@')[-1]}")

    # 1. Connect to MySQL (Source)
    try:
        mysql_engine = create_engine(mysql_url, pool_pre_ping=True)
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[✓] Successfully connected to source MySQL database.")
    except Exception as e:
        logger.error(f"[✗] Could not connect to source MySQL database: {e}")
        return False

    # 2. Connect to PostgreSQL (Target)
    try:
        pg_engine = create_engine(pg_url, pool_pre_ping=True)
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[✓] Successfully connected to target PostgreSQL database.")
    except Exception as e:
        logger.error(f"[✗] Could not connect to target PostgreSQL database: {e}")
        logger.info("\nAction Required:")
        logger.info("1. Ensure PostgreSQL is installed and running on port 5432.")
        logger.info("2. Create database 'lenny_growth_assistant':")
        logger.info("   psql -U postgres -c 'CREATE DATABASE lenny_growth_assistant;'")
        logger.info("3. Ensure credentials match .env (DB_USER=postgres, DB_PASSWORD=postgres).")
        return False

    # 3. Create tables in PostgreSQL
    logger.info("[...] Creating PostgreSQL schema and tables...")
    Base.metadata.create_all(pg_engine)
    logger.info("[✓] PostgreSQL schema verified.")

    MySQLSession = sessionmaker(bind=mysql_engine)
    PGSession = sessionmaker(bind=pg_engine)

    mysql_db = MySQLSession()
    pg_db = PGSession()

    try:
        # Table 1: Chat Sessions
        mysql_sessions = mysql_db.query(ChatSession).all()
        logger.info(f"Source chat_sessions found: {len(mysql_sessions)}")
        for s in mysql_sessions:
            existing = pg_db.query(ChatSession).filter_by(id=s.id).first()
            if not existing:
                pg_db.add(ChatSession(
                    id=s.id,
                    title=s.title,
                    created_at=s.created_at,
                    updated_at=s.updated_at
                ))
        pg_db.commit()

        # Table 2: Messages
        mysql_messages = mysql_db.query(Message).all()
        logger.info(f"Source messages found: {len(mysql_messages)}")
        for m in mysql_messages:
            existing = pg_db.query(Message).filter_by(id=m.id).first()
            if not existing:
                pg_db.add(Message(
                    id=m.id,
                    session_id=m.session_id,
                    role=m.role,
                    content=m.content,
                    model_used=m.model_used,
                    provider_used=m.provider_used,
                    citations=m.citations,
                    created_at=m.created_at
                ))
        pg_db.commit()

        # Table 3: Artifacts
        mysql_artifacts = mysql_db.query(Artifact).all()
        logger.info(f"Source artifacts found: {len(mysql_artifacts)}")
        for a in mysql_artifacts:
            existing = pg_db.query(Artifact).filter_by(id=a.id).first()
            if not existing:
                pg_db.add(Artifact(
                    id=a.id,
                    session_id=a.session_id,
                    title=a.title,
                    artifact_type=a.artifact_type,
                    content=a.content,
                    metadata_json=a.metadata_json,
                    created_at=a.created_at,
                    updated_at=a.updated_at
                ))
        pg_db.commit()

        # Table 4: Knowledge Sources
        mysql_sources = mysql_db.query(KnowledgeSource).all()
        logger.info(f"Source knowledge_sources found: {len(mysql_sources)}")
        for ks in mysql_sources:
            existing = pg_db.query(KnowledgeSource).filter_by(id=ks.id).first()
            if not existing:
                pg_db.add(KnowledgeSource(
                    id=ks.id,
                    title=ks.title,
                    source_type=ks.source_type,
                    url=ks.url,
                    author_or_guest=ks.author_or_guest,
                    summary=ks.summary,
                    raw_content=ks.raw_content,
                    status=ks.status,
                    error_message=ks.error_message,
                    chunk_count=ks.chunk_count,
                    is_authoritative=bool(getattr(ks, "is_authoritative", False)),
                    provenance_file=getattr(ks, "provenance_file", None) or "legacy_sample_data",
                    publish_date=getattr(ks, "publish_date", None),
                    episode_duration=getattr(ks, "episode_duration", None),
                    created_at=ks.created_at,
                    updated_at=ks.updated_at
                ))
        pg_db.commit()

        # Table 5: Document Chunks
        mysql_chunks = mysql_db.query(DocumentChunk).all()
        logger.info(f"Source document_chunks found: {len(mysql_chunks)}")
        for ch in mysql_chunks:
            existing = pg_db.query(DocumentChunk).filter_by(id=ch.id).first()
            if not existing:
                pg_db.add(DocumentChunk(
                    id=ch.id,
                    source_id=ch.source_id,
                    chunk_index=ch.chunk_index,
                    content=ch.content,
                    token_count=ch.token_count,
                    metadata_json=ch.metadata_json,
                    embedding=ch.embedding,
                    created_at=ch.created_at
                ))
        pg_db.commit()

        # Validation
        pg_session_count = pg_db.query(ChatSession).count()
        pg_msg_count = pg_db.query(Message).count()
        pg_art_count = pg_db.query(Artifact).count()
        pg_source_count = pg_db.query(KnowledgeSource).count()
        pg_chunk_count = pg_db.query(DocumentChunk).count()

        logger.info("\n=== Migration Validation Summary ===")
        logger.info(f"Chat Sessions:    MySQL={len(mysql_sessions)} | PostgreSQL={pg_session_count}")
        logger.info(f"Messages:         MySQL={len(mysql_messages)} | PostgreSQL={pg_msg_count}")
        logger.info(f"Artifacts:        MySQL={len(mysql_artifacts)} | PostgreSQL={pg_art_count}")
        logger.info(f"Knowledge Sources:MySQL={len(mysql_sources)} | PostgreSQL={pg_source_count}")
        logger.info(f"Document Chunks:  MySQL={len(mysql_chunks)} | PostgreSQL={pg_chunk_count}")

        logger.info("[✓] Safe migration completed successfully. MySQL data was preserved untouched.")
        return True

    except Exception as e:
        pg_db.rollback()
        logger.error(f"[✗] Error during migration: {e}")
        return False
    finally:
        mysql_db.close()
        pg_db.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

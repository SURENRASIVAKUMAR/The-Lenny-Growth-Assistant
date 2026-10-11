#!/usr/bin/env python3
"""
Authoritative Lenny Podcast Transcripts Ingestion Pipeline.
Reads real markdown transcripts from https://github.com/ChatPRD/lennys-podcast-transcripts,
extracts YAML frontmatter metadata, splits into overlapping chunks, computes embeddings,
and stores them in the database with strict provenance tracking.
Marks legacy sample documents as synthetic/demo material to exclude them from production retrieval.
"""

import os
import sys
import json
import yaml
import asyncio
import logging
import argparse
from typing import List, Dict, Any, Optional

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.core.database import resolve_active_engine
from backend.app.models.knowledge import KnowledgeSource, DocumentChunk
from backend.app.services.rag.chunker import chunk_text
from backend.app.services.rag.embedder import get_embedding

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingestion")

# Prominent curated episodes across growth, retention, activation, PMF, and SaaS
FEATURED_EPISODES = [
    "hila-qu",
    "elena-verna",
    "casey-winters",
    "brian-balfour",
    "sarah-tavel",
    "naomi-gleit",
    "kristen-berman",
    "ben-williams",
    "oji-udezue",
    "lauryn-isford",
    "patrick-campbell",
    "shreyas-doshi",
    "sean-ellis",
    "elena-verna-20",
    "adam-fishman",
    "albert-cheng",
    "brian-chesky",
    "nir-eyal",
    "fareed-mosavat",
    "april-dunford",
    "madhavan-ramanujam",
    "marily-nika",
    "dan-hockenmaier",
    "geoffrey-moore",
    "ada-chen-rekhi",
    "alex-komoroske",
]

def parse_transcript_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Parse a transcript.md file extracting YAML frontmatter and transcript text."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---")
        if len(parts) >= 3:
            raw_yaml = parts[1]
            body = "---".join(parts[2:]).strip()
            metadata = yaml.safe_load(raw_yaml) or {}
            return {
                "metadata": metadata,
                "body": body,
            }
        else:
            return {
                "metadata": {},
                "body": content.strip()
            }
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        return None

async def ingest_repository(repo_path: str, limit: Optional[int] = 12, all_episodes: bool = False, db_url_override: Optional[str] = None):
    episodes_dir = os.path.join(repo_path, "episodes")
    if not os.path.exists(episodes_dir):
        logger.info(f"Episodes directory not found at: {episodes_dir}. Attempting automatic clone from ChatPRD/lennys-podcast-transcripts...")
        import subprocess
        try:
            os.makedirs(os.path.dirname(os.path.abspath(repo_path)), exist_ok=True)
            subprocess.run(["git", "clone", "--depth", "1", "https://github.com/ChatPRD/lennys-podcast-transcripts.git", repo_path], check=True)
            logger.info("Successfully cloned ChatPRD/lennys-podcast-transcripts archive.")
        except Exception as e:
            logger.error(f"Failed to automatically clone archive: {e}. Please clone manually to {repo_path}")
            return

    # Database resolution
    if db_url_override:
        engine = create_engine(db_url_override, pool_pre_ping=True)
    else:
        engine, active_type = resolve_active_engine(force_refresh=True)
        logger.info(f"Connected to database engine ({active_type})")

    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Step 1: Mark legacy demo documents as synthetic/demo
        legacy_sources = db.query(KnowledgeSource).filter(
            KnowledgeSource.provenance_file.is_(None)
        ).all()
        for ls in legacy_sources:
            ls.is_authoritative = False
            ls.provenance_file = "legacy_sample_demo"
        db.commit()
        if legacy_sources:
            logger.info(f"Marked {len(legacy_sources)} legacy demonstration sources as is_authoritative=False.")

        # Step 2: Determine episode list
        all_dirs = [d for d in os.listdir(episodes_dir) if os.path.isdir(os.path.join(episodes_dir, d))]
        if all_episodes:
            selected_slugs = all_dirs
        else:
            # Prioritize featured episodes that exist, then fill up to limit
            selected_slugs = [slug for slug in FEATURED_EPISODES if slug in all_dirs]
            remaining = [d for d in all_dirs if d not in selected_slugs]
            if limit and len(selected_slugs) < limit:
                selected_slugs.extend(remaining[:limit - len(selected_slugs)])

        logger.info(f"Beginning ingestion of {len(selected_slugs)} authoritative episodes from ChatPRD repository...")

        ingested_count = 0
        total_chunks_created = 0

        for idx, slug in enumerate(selected_slugs, 1):
            file_path = os.path.join(episodes_dir, slug, "transcript.md")
            if not os.path.exists(file_path):
                logger.warning(f"[{idx}/{len(selected_slugs)}] Skipping {slug}: transcript.md not found")
                continue

            parsed = parse_transcript_file(file_path)
            if not parsed or not parsed["body"]:
                logger.warning(f"[{idx}/{len(selected_slugs)}] Skipping {slug}: empty or unparseable transcript")
                continue

            meta = parsed["metadata"]
            body = parsed["body"]

            rel_provenance = f"episodes/{slug}/transcript.md"
            title = meta.get("title") or f"Lenny's Podcast: {slug.replace('-', ' ').title()}"
            guest = meta.get("guest") or slug.replace('-', ' ').title()
            url = meta.get("youtube_url") or f"https://www.youtube.com/watch?v={meta.get('video_id', '')}"
            pub_date = str(meta.get("publish_date", ""))
            duration = str(meta.get("duration", ""))
            summary = meta.get("description", "")[:1000] if meta.get("description") else None

            # Check if source already exists
            existing_source = db.query(KnowledgeSource).filter(
                (KnowledgeSource.provenance_file == rel_provenance) | (KnowledgeSource.title == title)
            ).first()

            if existing_source:
                source = existing_source
                source.title = title
                source.author_or_guest = guest
                source.url = url
                source.provenance_file = rel_provenance
                source.publish_date = pub_date
                source.episode_duration = duration
                source.summary = summary
                source.is_authoritative = True
                source.status = "indexed"
                # Remove old chunks to re-index cleanly
                db.query(DocumentChunk).filter(DocumentChunk.source_id == source.id).delete()
            else:
                source = KnowledgeSource(
                    title=title,
                    source_type="podcast_transcript",
                    url=url,
                    author_or_guest=guest,
                    provenance_file=rel_provenance,
                    publish_date=pub_date,
                    episode_duration=duration,
                    summary=summary,
                    status="indexed",
                    is_authoritative=True,
                )
                db.add(source)

            db.commit()
            db.refresh(source)

            # Chunk the transcript (index up to 140 chunks per episode to capture complete frameworks and deep dialogue)
            raw_chunks = chunk_text(body, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
            chunks_to_index = raw_chunks[:140]

            for chunk_dict in chunks_to_index:
                emb = await get_embedding(chunk_dict["content"])
                db_chunk = DocumentChunk(
                    source_id=source.id,
                    chunk_index=chunk_dict["chunk_index"],
                    content=chunk_dict["content"],
                    token_count=chunk_dict["token_count"],
                    metadata_json=json.dumps({
                        "episode_slug": slug,
                        "guest": guest,
                        "provenance": rel_provenance,
                    }),
                    embedding=json.dumps(emb),
                )
                db.add(db_chunk)

            source.chunk_count = len(chunks_to_index)
            db.commit()

            ingested_count += 1
            total_chunks_created += len(chunks_to_index)
            logger.info(f"[{idx}/{len(selected_slugs)}] Ingested '{guest}': {len(chunks_to_index)} chunks (Provenance: {rel_provenance})")

        # Summary
        authoritative_sources = db.query(KnowledgeSource).filter(KnowledgeSource.is_authoritative == True).count()
        authoritative_chunks = (
            db.query(DocumentChunk)
            .join(KnowledgeSource, DocumentChunk.source_id == KnowledgeSource.id)
            .filter(KnowledgeSource.is_authoritative == True)
            .count()
        )

        logger.info("\n=== Ingestion Complete ===")
        logger.info(f"New Episodes Ingested:    {ingested_count}")
        logger.info(f"Total Authoritative Sources: {authoritative_sources}")
        logger.info(f"Total Authoritative Chunks:  {authoritative_chunks}")
        logger.info("All indexed records are strictly traced to ChatPRD/lennys-podcast-transcripts.")

    except Exception as e:
        logger.error(f"Error during repository ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest authoritative Lenny Podcast transcripts")
    parser.add_argument("--repo-path", default="data/lennys-podcast-transcripts", help="Path to cloned repository")
    parser.add_argument("--limit", type=int, default=12, help="Max episodes to ingest")
    parser.add_argument("--all", action="store_true", help="Ingest all available episodes")
    parser.add_argument("--db-url", default=None, help="Database URL override")
    args = parser.parse_args()

    asyncio.run(ingest_repository(
        repo_path=args.repo_path,
        limit=args.limit,
        all_episodes=args.all,
        db_url_override=args.db_url
    ))

import os
import sys
import glob
import re
import asyncio
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, check_database_connection
from backend.app.services.rag.ingester import ingest_document

def parse_markdown_metadata(content: str, filename: str) -> dict:
    """Extract metadata from markdown headers."""
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    author_match = re.search(r"\*\*Author / Guest Reference\*\*:\s*(.+)$", content, re.MULTILINE)
    url_match = re.search(r"\*\*URL\*\*:\s*(.+)$", content, re.MULTILINE)
    source_type_match = re.search(r"\*\*Source Type\*\*:\s*(.+)$", content, re.MULTILINE)

    title = title_match.group(1).strip() if title_match else Path(filename).stem.replace("_", " ").title()
    author = author_match.group(1).strip() if author_match else "Lenny's Growth Knowledge Base"
    url = url_match.group(1).strip() if url_match else None
    source_type = source_type_match.group(1).strip() if source_type_match else "document"

    return {
        "title": title,
        "author_or_guest": author,
        "url": url,
        "source_type": source_type,
    }

async def main():
    print("==================================================")
    print(" The Lenny Growth Assistant - Ingestion Engine    ")
    print("==================================================")

    db_check = check_database_connection()
    if db_check["status"] != "connected":
        print(f"ERROR: Cannot connect to MySQL database at {db_check['host']}:{db_check['port']}")
        print(f"Error details: {db_check.get('error')}")
        print("Please make sure XAMPP MySQL is running.")
        sys.exit(1)

    print(f"Database connection verified: {db_check['database_name']}")
    
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample_data")
    md_files = glob.glob(os.path.join(sample_dir, "*.md"))

    if not md_files:
        print(f"No markdown documents found in {sample_dir}")
        return

    print(f"Found {len(md_files)} sample document(s) to index.")

    db = SessionLocal()
    total_chunks = 0
    try:
        for fpath in md_files:
            fname = os.path.basename(fpath)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            meta = parse_markdown_metadata(content, fname)
            print(f"\nIndexing: '{meta['title']}'...")
            
            result = await ingest_document(
                title=meta["title"],
                content=content,
                source_type=meta["source_type"],
                url=meta["url"],
                author_or_guest=meta["author_or_guest"],
                summary=f"Indexed from {fname}",
                db=db,
                overwrite=True,
            )
            print(f"-> {result.message} (Chunks: {result.chunks_created})")
            total_chunks += result.chunks_created

        print("\n==================================================")
        print(f"Ingestion Complete! Total Chunks Indexed: {total_chunks}")
        print("==================================================")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())

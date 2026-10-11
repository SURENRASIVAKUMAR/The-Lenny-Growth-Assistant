import re
from typing import List, Dict, Any
from backend.app.core.config import settings

def clean_text(text: str) -> str:
    """Normalize whitespace and clean unwanted artifacts."""
    if not text:
        return ""
    # Normalize carriage returns and line feeds
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    return text.strip()

def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Split text into overlapping chunks, respecting paragraph and sentence boundaries.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []

    # If text is shorter than chunk size, return single chunk
    if len(cleaned) <= chunk_size:
        return [{
            "chunk_index": 0,
            "content": cleaned,
            "token_count": len(cleaned.split()),
        }]

    # Split by paragraphs first
    paragraphs = cleaned.split("\n\n")
    chunks = []
    current_chunk = ""
    chunk_idx = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If a single paragraph is larger than chunk_size, split by sentences
        if len(para) > chunk_size:
            sentences = re.split(r"(?<=[.?!])\s+", para)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(current_chunk) + len(sentence) + 1 <= chunk_size:
                    current_chunk = f"{current_chunk} {sentence}".strip()
                else:
                    if current_chunk:
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "content": current_chunk,
                            "token_count": len(current_chunk.split()),
                        })
                        chunk_idx += 1
                        # Overlap: keep the last portion of current_chunk
                        overlap_start = max(0, len(current_chunk) - chunk_overlap)
                        overlap_text = current_chunk[overlap_start:]
                        current_chunk = f"{overlap_text} {sentence}".strip()
                    else:
                        # Sentence itself is longer than chunk_size
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "content": sentence[:chunk_size],
                            "token_count": len(sentence[:chunk_size].split()),
                        })
                        chunk_idx += 1
                        current_chunk = sentence[chunk_size - chunk_overlap:]
        else:
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": current_chunk,
                        "token_count": len(current_chunk.split()),
                    })
                    chunk_idx += 1
                    overlap_start = max(0, len(current_chunk) - chunk_overlap)
                    overlap_text = current_chunk[overlap_start:]
                    current_chunk = f"{overlap_text}\n\n{para}".strip()
                else:
                    current_chunk = para

    if current_chunk.strip():
        chunks.append({
            "chunk_index": chunk_idx,
            "content": current_chunk.strip(),
            "token_count": len(current_chunk.strip().split()),
        })

    return chunks

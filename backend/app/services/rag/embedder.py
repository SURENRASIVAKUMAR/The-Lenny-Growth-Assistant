import math
import json
import hashlib
import logging
from typing import List, Optional
import numpy as np
from openai import AsyncOpenAI
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def generate_local_embedding(text: str, dim: int = 128) -> List[float]:
    """
    Generates a deterministic n-dimensional normalized vector for a piece of text
    using n-gram hashing and term weighting.
    Zero external dependencies, fast, and works 100% offline.
    """
    if not text:
        return [0.0] * dim

    vector = np.zeros(dim, dtype=np.float32)
    tokens = text.lower().split()
    
    # Unigrams and bigrams
    ngrams = tokens + [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]

    for token in ngrams:
        # Stable hash bucket
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        index = h % dim
        sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
        # Weight longer tokens slightly higher
        weight = min(len(token), 8) / 4.0
        vector[index] += sign * weight

    # Normalize vector to unit length
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector.tolist()

async def get_embedding(text: str) -> List[float]:
    """
    Fetches embedding from OpenAI if configured, otherwise uses local deterministic vector.
    """
    if settings.OPENAI_API_KEY:
        try:
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            resp = await client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text[:8000],  # stay within token limits
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.warning(f"OpenAI embedding generation failed, using local embedding fallback: {e}")
            return generate_local_embedding(text)
    
    return generate_local_embedding(text)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two vector lists."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    arr1 = np.array(v1, dtype=np.float32)
    arr2 = np.array(v2, dtype=np.float32)
    dot = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))

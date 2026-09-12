import logging
import math
from typing import List, Optional
import numpy as np
from app.core.config import settings

logger = logging.getLogger(__name__)

_model_instance = None


def get_embedding_model():
    """
    Lazy-loads and caches the singleton lightweight sentence-transformer model.
    Uses FastEmbed (ONNX Runtime, CPU-optimized, lightweight, zero GPU requirement).
    """
    global _model_instance
    if _model_instance is None:
        try:
            from fastembed import TextEmbedding
            model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
            logger.info(f"Loading local embedding model: {model_name}")
            _model_instance = TextEmbedding(model_name=model_name)
        except Exception as e:
            logger.warning(f"FastEmbed model loading failed: {e}. Falling back to internal vectorizer.")
            _model_instance = False
    return _model_instance


def _fallback_term_vector(text: str, dim: int = 384) -> List[float]:
    """
    Deterministic fallback embedding generator based on character and word n-gram hashing
    when local neural model download is unavailable.
    """
    tokens = text.lower().split()
    vec = [0.0] * dim
    if not tokens:
        return vec

    for i, token in enumerate(tokens):
        # Hash token into vector dimension
        h = hash(token) % dim
        vec[h] += 1.0 / (1.0 + math.log(1.0 + i))

    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def generate_embedding(text: str) -> List[float]:
    """
    Generates a normalized float vector for the provided text.
    """
    if not text or not text.strip():
        return [0.0] * 384

    model = get_embedding_model()
    if model:
        try:
            embeddings_generator = model.embed([text])
            arr = next(embeddings_generator)
            # Ensure float list
            return [float(x) for x in arr]
        except Exception as e:
            logger.warning(f"Embedding inference failed: {e}. Using deterministic fallback.")

    return _fallback_term_vector(text)


def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculates cosine similarity between two float vectors.
    Returns float clamped in range [0.0, 1.0].
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    cos_sim = float(np.dot(a, b) / (norm_a * norm_b))
    # Normalized range [0.0, 1.0] (embeddings from sentence transformers are usually > 0, but clamp securely)
    return max(0.0, min(1.0, cos_sim))

import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.ml.embeddings import generate_embedding
from app.ml.representation import build_opportunity_representation
from app.models.opportunity import Opportunity
from app.models.opportunity_embedding import OpportunityEmbedding

logger = logging.getLogger(__name__)

# Process-level in-memory cache for ultra-low latency: (opp_id, content_hash) -> embedding
_MEMORY_CACHE: Dict[str, List[float]] = {}


def get_or_compute_opportunity_embedding(
    db: Session,
    opportunity: Opportunity,
    opp_rep: Optional[Dict[str, Any]] = None,
) -> List[float]:
    """
    Returns the opportunity's embedding vector from cache or computes and stores it.
    
    1. Checks in-memory fast cache (opp_id + hash).
    2. Checks database `opportunity_embeddings` table.
    3. If content hash matches, returns cached embedding (zero recomputation).
    4. If hash changed or missing, recomputes embedding, updates DB, and updates in-memory cache.
    """
    if opp_rep is None:
        opp_rep = build_opportunity_representation(opportunity)

    current_hash = opp_rep["content_hash"]
    memory_key = f"{opportunity.id}:{current_hash}"

    # Fast Tier 1: Process Memory
    if memory_key in _MEMORY_CACHE:
        return _MEMORY_CACHE[memory_key]

    # Persistent Tier 2: Database Table
    model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    cached_record = (
        db.query(OpportunityEmbedding)
        .filter(OpportunityEmbedding.opportunity_id == opportunity.id)
        .first()
    )

    if cached_record and cached_record.content_hash == current_hash and cached_record.embedding:
        # Cache hit!
        _MEMORY_CACHE[memory_key] = cached_record.embedding
        return cached_record.embedding

    # Cache miss or invalidated: compute new embedding
    logger.info(f"Computing and caching embedding for opportunity: {opportunity.id} ({opportunity.title})")
    new_embedding = generate_embedding(opp_rep["semantic_text"])

    if cached_record:
        # Update existing record
        cached_record.content_hash = current_hash
        cached_record.embedding = new_embedding
        cached_record.model_name = model_name
    else:
        # Create new record
        new_record = OpportunityEmbedding(
            opportunity_id=opportunity.id,
            content_hash=current_hash,
            embedding=new_embedding,
            model_name=model_name,
        )
        db.add(new_record)

    try:
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to commit opportunity embedding to DB: {e}")
        db.rollback()

    _MEMORY_CACHE[memory_key] = new_embedding
    return new_embedding


def invalidate_opportunity_cache(opportunity_id: str):
    """
    Purges process memory cache for this opportunity ID.
    """
    keys_to_delete = [k for k in _MEMORY_CACHE if k.startswith(f"{opportunity_id}:")]
    for k in keys_to_delete:
        del _MEMORY_CACHE[k]

from app.ml.embeddings import compute_cosine_similarity, generate_embedding
from app.ml.representation import build_opportunity_representation, build_student_representation
from app.ml.skill_matcher import calculate_skill_match
from app.ml.eligibility import evaluate_eligibility
from app.ml.scorer import compute_hybrid_score
from app.ml.matcher import match_student_and_opportunity, rank_opportunities_for_student
from app.ml.cache import get_or_compute_opportunity_embedding

__all__ = [
    "generate_embedding",
    "compute_cosine_similarity",
    "build_student_representation",
    "build_opportunity_representation",
    "calculate_skill_match",
    "evaluate_eligibility",
    "compute_hybrid_score",
    "match_student_and_opportunity",
    "rank_opportunities_for_student",
    "get_or_compute_opportunity_embedding",
]

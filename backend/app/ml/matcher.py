import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.ml.cache import get_or_compute_opportunity_embedding
from app.ml.eligibility import evaluate_eligibility
from app.ml.embeddings import compute_cosine_similarity, generate_embedding
from app.ml.representation import (
    build_opportunity_representation,
    build_student_representation,
)
from app.ml.scorer import (
    calculate_education_score,
    calculate_experience_score,
    calculate_interest_score,
    calculate_preference_score,
    compute_hybrid_score,
)
from app.ml.skill_matcher import calculate_skill_match
from app.models.enums import EligibilityStatus
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile

logger = logging.getLogger(__name__)


def generate_explanation(
    overall_score: int,
    skill_result: Dict[str, Any],
    eligibility_result: Dict[str, Any],
    opportunity: Opportunity,
) -> Dict[str, Any]:
    """
    Synthesizes human-readable, transparent explainable AI feedback
    describing why the opportunity matches the student and what gaps exist.
    """
    # Headline
    if overall_score >= 85:
        compatibility_label = "Exceptional Compatibility"
    elif overall_score >= 70:
        compatibility_label = "Strong Fit with High Potential"
    elif overall_score >= 55:
        compatibility_label = "Moderate Fit with Growth Areas"
    else:
        compatibility_label = "Exploratory Match"

    # Key bullet points
    reasons = []
    matched_skills = skill_result.get("matched_skills", [])
    missing_skills = skill_result.get("missing_skills", [])
    partial_skills = skill_result.get("partial_skills", [])

    if matched_skills:
        reasons.append(
            f"You possess {len(matched_skills)} core technical competencies: {', '.join(matched_skills[:4])}."
        )
    if partial_skills:
        notes = [f"{p['required_skill']} (via {p['student_skill']})" for p in partial_skills[:2]]
        reasons.append(f"Transferable skills identified: {', '.join(notes)}.")

    reasons.append(eligibility_result.get("summary_note", "Eligibility criteria assessed."))

    # Strong matches list for Stitch UI
    strong_matches = []
    for item in skill_result.get("verified_matched", []):
        ver_text = "Verified from profile & assessment"
        if item.get("verified"):
            ver_text = f"Verified via {item.get('verified_via', 'portfolio')}"
        strong_matches.append({
            "skill": item["name"],
            "verification_note": ver_text,
            "proficiency": item.get("proficiency", "Proficient"),
        })

    # Recommended action for closing missing skill gap
    recommended_action = None
    if missing_skills:
        primary_gap = missing_skills[0]
        recommended_action = {
            "title": f"Upskill in {primary_gap}",
            "description": f"Complete a targeted module or project on {primary_gap} to increase your match confidence by +8-12%.",
            "skill_gap": primary_gap,
        }

    return {
        "compatibility_label": compatibility_label,
        "summary": (
            f"Your background satisfies {len(matched_skills)} required skill benchmarks and aligns "
            f"closely with {opportunity.organization}'s {opportunity.domain} focus."
        ),
        "reasons": reasons,
        "strong_matches": strong_matches,
        "missing_skills": missing_skills,
        "recommended_action": recommended_action,
    }


def match_student_and_opportunity(
    db: Session,
    student_profile: StudentProfile,
    opportunity: Opportunity,
) -> Dict[str, Any]:
    """
    Executes the complete AIML Matching Pipeline for a single student profile
    and a specific opportunity.
    """
    # 1. Student Representation
    student_rep = build_student_representation(student_profile)

    # 2. Student Embedding
    student_vector = generate_embedding(student_rep["semantic_text"])

    # 3. Opportunity Representation
    opp_rep = build_opportunity_representation(opportunity)

    # 4. Opportunity Embedding (via persistent DB-backed cache)
    opp_vector = get_or_compute_opportunity_embedding(db, opportunity, opp_rep)

    # 5. Semantic Cosine Similarity
    semantic_sim = compute_cosine_similarity(student_vector, opp_vector)

    # 6. Skill Matching (exact, missing, partial, verified)
    skill_result = calculate_skill_match(
        student_skills=student_rep["skills"],
        required_skills=opp_rep["required_skills"],
        preferred_skills=opp_rep["preferred_skills"],
        skills_detail=student_rep.get("skills_detail"),
    )

    # 7. Eligibility Evaluation (4-tier)
    eligibility_result = evaluate_eligibility(student_rep, opp_rep)

    # 8. Component Scores
    education_score = calculate_education_score(
        student_rep,
        eligibility_result["criteria"],
    )
    interest_score = calculate_interest_score(
        student_rep["preferred_domains"],
        opp_rep["domain"],
        opp_rep["title"],
    )
    experience_score = calculate_experience_score(
        student_rep["experience"],
        opp_rep["experience_requirements"],
        len(student_rep["skills"]),
    )
    preference_score = calculate_preference_score(
        student_rep["preferred_locations"],
        student_rep["preferred_work_mode"],
        opp_rep["location"],
        opp_rep["mode"],
    )

    # 9. Hybrid Scoring
    hybrid = compute_hybrid_score(
        skill_match_percentage=skill_result["skill_match_percentage"],
        semantic_similarity=semantic_sim,
        education_score=education_score,
        interest_score=interest_score,
        experience_score=experience_score,
        preference_score=preference_score,
    )

    # 10. Explainable Recommendation
    explanation = generate_explanation(
        overall_score=hybrid["overall_match_score"],
        skill_result=skill_result,
        eligibility_result=eligibility_result,
        opportunity=opportunity,
    )

    return {
        "opportunity_id": opportunity.id,
        "overall_match_score": hybrid["overall_match_score"],
        "skill_score": hybrid["skill_score"],
        "semantic_similarity": hybrid["semantic_similarity"],
        "education_score": hybrid["education_score"],
        "interest_score": hybrid["interest_score"],
        "experience_score": hybrid["experience_score"],
        "preference_score": hybrid["preference_score"],
        "matched_skills": skill_result["matched_skills"],
        "missing_skills": skill_result["missing_skills"],
        "partial_skills": skill_result["partial_skills"],
        "eligibility_status": eligibility_result["status"],
        "eligibility_note": eligibility_result["summary_note"],
        "eligibility_criteria": eligibility_result["criteria"],
        "match_breakdown": hybrid["match_breakdown"],
        "explanation": explanation,
    }


def rank_opportunities_for_student(
    db: Session,
    student_profile: StudentProfile,
    opportunities: List[Opportunity],
) -> List[Dict[str, Any]]:
    """
    Ranks a list of opportunities for a given student based on real hybrid computation
    and eligibility tiering.
    """
    if not opportunities:
        return []

    # Status ranking order
    status_priority = {
        EligibilityStatus.ELIGIBLE: 3,
        EligibilityStatus.PARTIALLY_ELIGIBLE: 2,
        EligibilityStatus.UNKNOWN: 1,
        EligibilityStatus.NOT_ELIGIBLE: 0,
    }

    scored_items = []
    for opp in opportunities:
        match_data = match_student_and_opportunity(db, student_profile, opp)
        scored_items.append({
            "opportunity": opp,
            "match": match_data,
        })

    # Sort descending by eligibility priority first, then overall score
    scored_items.sort(
        key=lambda x: (
            status_priority.get(x["match"]["eligibility_status"], 0),
            x["match"]["overall_match_score"],
            x["match"]["skill_score"],
        ),
        reverse=True,
    )

    return scored_items

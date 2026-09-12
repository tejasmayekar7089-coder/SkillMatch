import re
from typing import Any, Dict, List, Optional
from app.core.config import settings


def _text_overlap(list1: List[str], target_str: str) -> float:
    """Helper to detect overlap between a list of terms and a target text."""
    if not list1 or not target_str:
        return 0.0
    norm_target = re.sub(r"[^\w\s]", "", target_str.lower())
    matched = 0
    for item in list1:
        norm_item = re.sub(r"[^\w\s]", "", item.lower())
        if norm_item in norm_target or norm_target in norm_item:
            matched += 1
    return min(1.0, matched / max(1, len(list1)))


def calculate_education_score(student: Dict[str, Any], eligibility_criteria: List[Dict[str, Any]]) -> float:
    """Calculates education score out of 100."""
    score = 0.0
    for crit in eligibility_criteria:
        name = crit.get("criterion", "")
        st = crit.get("status", "")
        if name == "Degree":
            score += 50.0 if st == "PASSED" else (35.0 if st == "UNKNOWN" else 10.0)
        elif name == "Major / Branch":
            score += 30.0 if st == "PASSED" else (20.0 if st == "UNKNOWN" else 0.0)
        elif name == "Academic Year":
            score += 20.0 if st == "PASSED" else (15.0 if st == "UNKNOWN" else 0.0)
    return max(10.0, min(100.0, score))


def calculate_interest_score(student_domains: List[str], opp_domain: str, opp_title: str) -> float:
    """Calculates interest fit score out of 100."""
    if not student_domains:
        return 65.0  # Neutral default

    combined_target = f"{opp_domain} {opp_title}".lower()
    for d in student_domains:
        d_lower = d.lower()
        if d_lower in combined_target or any(word in combined_target for word in d_lower.split() if len(word) > 2):
            return 95.0

    return 35.0


def calculate_experience_score(student_exp: str, opp_exp_req: str, skills_count: int) -> float:
    """Calculates practical experience score out of 100."""
    score = 50.0
    if student_exp and len(student_exp.strip()) > 30:
        score += 35.0
    if skills_count >= 5:
        score += 15.0
    elif skills_count >= 3:
        score += 10.0
    return min(100.0, score)


def calculate_preference_score(
    student_locs: List[str],
    student_mode: str,
    opp_loc: str,
    opp_mode: str,
) -> float:
    """Calculates preference fit score out of 100."""
    if "remote" in opp_mode.lower() or "flexible" in opp_mode.lower():
        return 100.0
    if not student_locs and not student_mode:
        return 75.0  # Neutral

    if _text_overlap(student_locs, opp_loc) > 0:
        return 100.0
    if student_mode and student_mode.lower() == opp_mode.lower():
        return 90.0
    return 40.0


def compute_hybrid_score(
    skill_match_percentage: float,
    semantic_similarity: float,  # 0.0 to 1.0
    education_score: float,      # 0 to 100
    interest_score: float,       # 0 to 100
    experience_score: float,     # 0 to 100
    preference_score: float,     # 0 to 100
) -> Dict[str, Any]:
    """
    Computes weighted hybrid score using configurable settings:
    - Skill Match = 40%
    - Semantic Similarity = 25%
    - Education = 15%
    - Interests = 10%
    - Experience = 5%
    - Preferences = 5%
    Total = 100%
    """
    w_skill = getattr(settings, "MATCH_WEIGHT_SKILL", 0.40)
    w_sem = getattr(settings, "MATCH_WEIGHT_SEMANTIC", 0.25)
    w_edu = getattr(settings, "MATCH_WEIGHT_EDUCATION", 0.15)
    w_int = getattr(settings, "MATCH_WEIGHT_INTERESTS", 0.10)
    w_exp = getattr(settings, "MATCH_WEIGHT_EXPERIENCE", 0.05)
    w_pref = getattr(settings, "MATCH_WEIGHT_PREFERENCES", 0.05)

    semantic_pct = max(0.0, min(100.0, semantic_similarity * 100.0))

    overall = (
        (w_skill * skill_match_percentage) +
        (w_sem * semantic_pct) +
        (w_edu * education_score) +
        (w_int * interest_score) +
        (w_exp * experience_score) +
        (w_pref * preference_score)
    )

    overall_score = max(5, min(100, int(round(overall))))

    # Format breakdown tailored to existing Stitch UI representation
    skills_stitch = int(round((skill_match_percentage / 100.0) * 40.0))
    education_stitch = int(round((education_score / 100.0) * 20.0))
    interests_stitch = int(round((interest_score / 100.0) * 20.0))
    experience_stitch = int(round((experience_score / 100.0) * 20.0))

    match_breakdown = {
        "skillsScore": min(40, skills_stitch),
        "skillsTotal": 40,
        "educationScore": min(20, education_stitch),
        "educationTotal": 20,
        "interestsScore": min(20, interests_stitch),
        "interestsTotal": 20,
        "experienceScore": min(20, experience_stitch),
        "experienceTotal": 20,
        "skillsFitPercent": int(round(skill_match_percentage)),
        "academicCriteriaPercent": int(round(education_score)),
        "experienceLevelPercent": int(round(experience_score)),
    }

    return {
        "overall_match_score": overall_score,
        "skill_score": round(skill_match_percentage, 1),
        "semantic_similarity": round(semantic_pct, 1),
        "education_score": round(education_score, 1),
        "interest_score": round(interest_score, 1),
        "experience_score": round(experience_score, 1),
        "preference_score": round(preference_score, 1),
        "match_breakdown": match_breakdown,
    }

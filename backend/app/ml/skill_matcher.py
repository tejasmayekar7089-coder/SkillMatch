from typing import Any, Dict, List, Optional, Set
from app.services.skill_normalizer import CANONICAL_SKILLS, SkillNormalizationService

# Related skills clusters for partial credit
RELATED_SKILL_CLUSTERS: List[Set[str]] = [
    # Deep Learning / ML Frameworks
    {"PyTorch", "TensorFlow", "Keras", "JAX", "Deep Learning", "Machine Learning"},
    # Web / Frontend Frameworks
    {"React", "Next.js", "Vue.js", "Angular", "JavaScript", "TypeScript"},
    # Python Backend Frameworks
    {"FastAPI", "Flask", "Django", "REST APIs"},
    # Node / JS Backend
    {"Node.js", "Express.js", "Next.js", "REST APIs"},
    # Relational Databases
    {"PostgreSQL", "MySQL", "SQLite", "SQL"},
    # Container & Cloud Ops
    {"Docker", "Kubernetes", "CI/CD", "GitHub Actions", "Linux"},
    # Cloud Platforms
    {"AWS", "Google Cloud", "Azure"},
    # Core Languages
    {"C++", "C", "Rust", "Go"},
    {"Java", "Kotlin", "Scala", "Spring Boot"},
    # Data Science & Analytics
    {"Pandas", "NumPy", "Data Analysis", "Data Science", "Python"},
    {"Tableau", "Power BI", "Data Analysis", "SQL"},
]


def find_related_skills(missing_skill: str, student_skills: List[str]) -> Optional[str]:
    """
    Checks if student possesses a related skill in the same canonical cluster.
    """
    student_skills_set = set(student_skills)
    for cluster in RELATED_SKILL_CLUSTERS:
        if missing_skill in cluster:
            for s in student_skills:
                if s in cluster and s != missing_skill:
                    return s
    return None


def calculate_skill_match(
    student_skills: List[str],
    required_skills: List[str],
    preferred_skills: Optional[List[str]] = None,
    skills_detail: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Computes deterministic skill match metrics:
    - matched_skills: normalized exact matches
    - missing_skills: unmet required skills
    - partial_skills: related skills student has that offer partial proficiency
    - matched_preferred_skills: bonus preferred skills
    - skill_match_percentage: 0 to 100 percentage
    """
    pref_list = preferred_skills or []
    detail_map = {}
    if skills_detail:
        for item in skills_detail:
            detail_map[item["name"].lower()] = item

    # 1. Normalize all skill inputs via canonical normalizer
    norm_student = SkillNormalizationService.normalize_list(student_skills)
    norm_required = SkillNormalizationService.normalize_list(required_skills)
    norm_preferred = SkillNormalizationService.normalize_list(pref_list)

    student_lower = {s.lower() for s in norm_student}

    # 2. Identify exact matched skills
    matched_skills: List[str] = []
    missing_candidates: List[str] = []

    for req in norm_required:
        if req.lower() in student_lower:
            matched_skills.append(req)
        else:
            missing_candidates.append(req)

    # 3. Identify partial / related skills
    partial_skills: List[Dict[str, str]] = []
    missing_skills: List[str] = []

    for missing in missing_candidates:
        related = find_related_skills(missing, norm_student)
        if related:
            partial_skills.append({
                "required_skill": missing,
                "student_skill": related,
                "note": f"Partial match via {related}",
            })
        else:
            missing_skills.append(missing)

    # 4. Matched preferred skills
    matched_preferred: List[str] = [p for p in norm_preferred if p.lower() in student_lower]

    # 5. Calculate skill score percentage
    total_req_count = len(norm_required)
    if total_req_count == 0:
        # If no strict skills required, evaluate preferred skills
        if norm_preferred:
            pref_ratio = len(matched_preferred) / len(norm_preferred)
            percentage = 70.0 + (pref_ratio * 30.0)
        else:
            percentage = 100.0
    else:
        # Full credit (1.0) for exact match, half credit (0.5) for related/partial match
        exact_points = float(len(matched_skills))
        partial_points = float(len(partial_skills)) * 0.5
        
        # Preferred skills bonus (up to 10% bonus if any preferred skills matched)
        pref_bonus = 0.0
        if norm_preferred and matched_preferred:
            pref_bonus = min(10.0, (len(matched_preferred) / len(norm_preferred)) * 10.0)

        base_ratio = (exact_points + partial_points) / float(total_req_count)
        percentage = min(100.0, (base_ratio * 100.0) + pref_bonus)

    # Build verified metadata for matched skills
    verified_matched = []
    for s in matched_skills:
        info = detail_map.get(s.lower(), {})
        verified_matched.append({
            "name": s,
            "verified": info.get("verified", False),
            "verified_via": info.get("verified_via") or "Profile skill assessment",
            "proficiency": info.get("proficiency", "Intermediate"),
        })

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "partial_skills": partial_skills,
        "matched_preferred_skills": matched_preferred,
        "verified_matched": verified_matched,
        "skill_match_percentage": round(percentage, 2),
        "total_required": total_req_count,
        "matched_count": len(matched_skills),
    }

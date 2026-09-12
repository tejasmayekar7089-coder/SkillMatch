import hashlib
import json
from typing import Any, Dict, List, Optional
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile
from app.services.skill_normalizer import SkillNormalizationService


def build_student_representation(profile: StudentProfile) -> Dict[str, Any]:
    """
    Builds both a structured dictionary and a semantic textual representation
    for a student profile.
    """
    # 1. Normalized skills
    skills_data = []
    normalized_skill_names = []
    if profile.skills:
        for ss in profile.skills:
            raw_name = ss.skill.name if ss.skill else ""
            canon = SkillNormalizationService.normalize(raw_name)
            if canon:
                normalized_skill_names.append(canon)
                skills_data.append({
                    "name": canon,
                    "proficiency": ss.proficiency or "Intermediate",
                    "verified": bool(ss.verified),
                    "verified_via": ss.verified_via,
                })
    # Deduplicate normalized skill names preserving order
    normalized_skill_names = list(dict.fromkeys(normalized_skill_names))

    # 2. Extract projects
    projects_summary = []
    if profile.projects:
        for p in profile.projects:
            techs = p.technologies if isinstance(p.technologies, list) else []
            tech_str = f" ({', '.join(techs)})" if techs else ""
            desc = f": {p.description}" if p.description else ""
            projects_summary.append(f"{p.name}{tech_str}{desc}")

    # 3. Extract certifications
    certs_summary = []
    if profile.certifications:
        for c in profile.certifications:
            issuer = f" ({c.issuer})" if c.issuer else ""
            certs_summary.append(f"{c.name}{issuer}")

    # 4. Synthesize textual representation for semantic embedding
    text_parts = []
    if profile.target_role:
        text_parts.append(f"Target Role: {profile.target_role}.")
    
    edu_parts = []
    if profile.degree:
        edu_parts.append(profile.degree)
    if profile.branch or profile.major:
        edu_parts.append(f"in {profile.branch or profile.major}")
    if profile.academic_year or profile.year:
        edu_parts.append(f"({profile.academic_year or profile.year})")
    if profile.college or profile.university:
        edu_parts.append(f"at {profile.college or profile.university}")
    if profile.gpa:
        edu_parts.append(f"with GPA {profile.gpa:.2f}")
    if edu_parts:
        text_parts.append(f"Education: {' '.join(edu_parts)}.")

    if normalized_skill_names:
        skills_str = ", ".join(
            [f"{s['name']} ({s['proficiency']})" for s in skills_data]
            if skills_data
            else normalized_skill_names
        )
        text_parts.append(f"Technical Competencies: {skills_str}.")

    pref_domains = profile.preferred_domains if isinstance(profile.preferred_domains, list) else []
    if pref_domains:
        text_parts.append(f"Preferred Domains: {', '.join(pref_domains)}.")

    pref_locations = profile.preferred_locations if isinstance(profile.preferred_locations, list) else []
    if pref_locations:
        text_parts.append(f"Preferred Locations: {', '.join(pref_locations)}.")
    if profile.preferred_work_mode:
        text_parts.append(f"Preferred Work Mode: {profile.preferred_work_mode}.")

    if projects_summary:
        text_parts.append(f"Projects: {' | '.join(projects_summary[:3])}.")

    if certs_summary:
        text_parts.append(f"Certifications: {', '.join(certs_summary[:3])}.")

    if profile.summary:
        text_parts.append(f"Summary: {profile.summary}")
    elif profile.bio:
        text_parts.append(f"Bio: {profile.bio}")

    semantic_text = " ".join(text_parts).strip()
    if not semantic_text:
        semantic_text = "Student profile seeking career and skill opportunities."

    return {
        "profile_id": profile.id,
        "user_id": profile.user_id,
        "semantic_text": semantic_text,
        "skills": normalized_skill_names,
        "skills_detail": skills_data,
        "degree": profile.degree or "",
        "branch": profile.branch or profile.major or "",
        "academic_year": profile.academic_year or profile.year or "",
        "graduation_year": profile.graduation_year or "",
        "gpa": profile.gpa,
        "preferred_domains": pref_domains,
        "preferred_locations": pref_locations,
        "preferred_work_mode": profile.preferred_work_mode or "",
        "experience": profile.experience or "",
        "target_role": profile.target_role or "",
    }


def compute_opportunity_hash(opportunity: Opportunity) -> str:
    """
    Computes a deterministic SHA-256 hash of an opportunity's meaningful content.
    Used for cache invalidation: if this hash matches the cached hash,
    the embedding does NOT need to be recomputed.
    """
    req_skills = sorted(opportunity.required_skills or [])
    pref_skills = sorted(opportunity.preferred_skills or [])
    deg_req = sorted(opportunity.degree_requirements or [])
    branch_req = sorted(opportunity.branch_requirements or [])
    year_req = sorted(opportunity.academic_year_requirements or [])

    payload = {
        "title": (opportunity.title or "").strip(),
        "organization": (opportunity.organization or "").strip(),
        "category": str(opportunity.category.value if hasattr(opportunity.category, "value") else opportunity.category),
        "domain": (opportunity.domain or "").strip(),
        "location": (opportunity.location or "").strip(),
        "mode": str(opportunity.mode.value if hasattr(opportunity.mode, "value") else opportunity.mode),
        "description": (opportunity.description or "").strip(),
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "degree_requirements": deg_req,
        "branch_requirements": branch_req,
        "academic_year_requirements": year_req,
        "experience_requirements": (opportunity.experience_requirements or "").strip(),
        "eligibility_requirements": (opportunity.eligibility_requirements or "").strip(),
        "key_responsibilities": sorted(opportunity.key_responsibilities or []),
    }
    dumped = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


def build_opportunity_representation(opportunity: Opportunity) -> Dict[str, Any]:
    """
    Builds structured features, deterministic content hash, and semantic
    textual representation for an opportunity.
    """
    # 1. Normalize required and preferred skills
    raw_req = opportunity.required_skills or []
    norm_req = SkillNormalizationService.normalize_list(raw_req)

    raw_pref = opportunity.preferred_skills or []
    norm_pref = SkillNormalizationService.normalize_list(raw_pref)

    # 2. Textual representation for embedding
    cat_val = opportunity.category_label or (
        opportunity.category.value if hasattr(opportunity.category, "value") else str(opportunity.category)
    )
    mode_val = opportunity.mode.value if hasattr(opportunity.mode, "value") else str(opportunity.mode)

    text_parts = [
        f"Opportunity: {opportunity.title} at {opportunity.organization}.",
        f"Category: {cat_val} in domain {opportunity.domain}.",
        f"Location: {opportunity.location} ({mode_val}).",
    ]

    if norm_req:
        text_parts.append(f"Required Skills: {', '.join(norm_req)}.")
    if norm_pref:
        text_parts.append(f"Preferred Skills: {', '.join(norm_pref)}.")

    if opportunity.description:
        text_parts.append(f"Description: {opportunity.description}")

    if opportunity.key_responsibilities:
        text_parts.append(f"Responsibilities: {' | '.join(opportunity.key_responsibilities[:4])}.")

    elig_parts = []
    if opportunity.degree_requirements:
        elig_parts.append(f"Degrees: {', '.join(opportunity.degree_requirements)}")
    if opportunity.branch_requirements:
        elig_parts.append(f"Branches: {', '.join(opportunity.branch_requirements)}")
    if opportunity.academic_year_requirements:
        elig_parts.append(f"Academic Years: {', '.join(opportunity.academic_year_requirements)}")
    if opportunity.experience_requirements:
        elig_parts.append(f"Experience: {opportunity.experience_requirements}")
    if opportunity.eligibility_requirements:
        elig_parts.append(f"Criteria: {opportunity.eligibility_requirements}")
    if elig_parts:
        text_parts.append(f"Eligibility: {'; '.join(elig_parts)}.")

    semantic_text = " ".join(text_parts).strip()
    content_hash = compute_opportunity_hash(opportunity)

    return {
        "opportunity_id": opportunity.id,
        "content_hash": content_hash,
        "semantic_text": semantic_text,
        "required_skills": norm_req,
        "preferred_skills": norm_pref,
        "degree_requirements": opportunity.degree_requirements or [],
        "branch_requirements": opportunity.branch_requirements or [],
        "academic_year_requirements": opportunity.academic_year_requirements or [],
        "experience_requirements": opportunity.experience_requirements or "",
        "eligibility_requirements": opportunity.eligibility_requirements or "",
        "domain": opportunity.domain or "",
        "location": opportunity.location or "",
        "mode": mode_val,
        "category": cat_val,
        "title": opportunity.title or "",
        "organization": opportunity.organization or "",
    }

import re
from typing import Any, Dict, List, Optional, Tuple
from app.models.enums import EligibilityStatus


def _normalize_str(s: str) -> str:
    return re.sub(r"[^\w\s]", "", (s or "").lower()).strip()


def check_degree_match(student_degree: str, degree_requirements: List[str]) -> Tuple[str, str]:
    """
    Returns (status: 'PASSED' | 'FAILED' | 'UNKNOWN', reason: str)
    """
    if not degree_requirements:
        return "PASSED", "No specific degree required."

    # Check for open/all terms
    for req in degree_requirements:
        norm_r = _normalize_str(req)
        if any(term in norm_r for term in ["all", "open to all", "any degree"]):
            return "PASSED", "Open to all university degrees."

    if not student_degree or not student_degree.strip():
        return "UNKNOWN", "Degree not specified in student profile."

    norm_s = _normalize_str(student_degree)
    
    # Degree equivalence groups
    bachelor_terms = ["btech", "be", "bs", "bachelor", "btech be", "undergraduate"]
    master_terms = ["ms", "mtech", "master", "postgraduate", "graduate", "msc"]
    phd_terms = ["phd", "doctorate"]

    is_student_bachelor = any(t in norm_s for t in bachelor_terms)
    is_student_master = any(t in norm_s for t in master_terms)
    is_student_phd = any(t in norm_s for t in phd_terms)

    for req in degree_requirements:
        norm_r = _normalize_str(req)
        # Direct substring
        if norm_s in norm_r or norm_r in norm_s:
            return "PASSED", f"Degree {student_degree} satisfies {req}."
        if is_student_bachelor and any(t in norm_r for t in bachelor_terms):
            return "PASSED", f"Bachelor qualification {student_degree} satisfies requirement {req}."
        if is_student_master and any(t in norm_r for t in master_terms):
            return "PASSED", f"Master qualification {student_degree} satisfies requirement {req}."
        if is_student_phd and any(t in norm_r for t in phd_terms):
            return "PASSED", f"Doctorate qualification satisfies requirement {req}."

    return "FAILED", f"Degree {student_degree} does not match required: {', '.join(degree_requirements)}."


def check_branch_match(student_branch: str, branch_requirements: List[str]) -> Tuple[str, str]:
    """
    Returns (status: 'PASSED' | 'FAILED' | 'UNKNOWN', reason: str)
    """
    if not branch_requirements:
        return "PASSED", "No specific major/branch required."

    for req in branch_requirements:
        norm_r = _normalize_str(req)
        if any(term in norm_r for term in ["all", "open", "any branch", "any major"]):
            return "PASSED", "Open to all academic branches/majors."

    if not student_branch or not student_branch.strip():
        return "UNKNOWN", "Major/branch not specified in student profile."

    norm_s = _normalize_str(student_branch)

    # CS/IT synonyms
    cs_synonyms = ["computer science", "cs", "cse", "software engineering", "information technology", "computing"]
    is_cs = any(t in norm_s for t in cs_synonyms)

    # AI/Data synonyms
    ai_synonyms = ["artificial intelligence", "ai", "machine learning", "data science", "analytics"]
    is_ai = any(t in norm_s for t in ai_synonyms)

    for req in branch_requirements:
        norm_r = _normalize_str(req)
        if norm_s in norm_r or norm_r in norm_s:
            return "PASSED", f"Major {student_branch} matches {req}."
        if is_cs and any(t in norm_r for t in cs_synonyms):
            return "PASSED", f"Computing background matches {req}."
        if is_ai and any(t in norm_r for t in ai_synonyms):
            return "PASSED", f"AI/Data background matches {req}."

    return "FAILED", f"Major {student_branch} does not match required: {', '.join(branch_requirements)}."


def check_academic_year_match(student_year: str, year_requirements: List[str]) -> Tuple[str, str]:
    """
    Returns (status: 'PASSED' | 'FAILED' | 'UNKNOWN', reason: str)
    """
    if not year_requirements:
        return "PASSED", "No academic year constraint."

    for req in year_requirements:
        norm_r = _normalize_str(req)
        if any(term in norm_r for term in ["all", "any year", "all academic years"]):
            return "PASSED", "Open to all academic years."

    if not student_year or not student_year.strip():
        return "UNKNOWN", "Academic year not specified in student profile."

    norm_s = _normalize_str(student_year)

    for req in year_requirements:
        norm_r = _normalize_str(req)
        if norm_s in norm_r or norm_r in norm_s:
            return "PASSED", f"Year {student_year} meets criteria {req}."

    # Digits matching
    s_digits = re.findall(r"\d+", norm_s)
    if s_digits:
        for req in year_requirements:
            r_digits = re.findall(r"\d+", _normalize_str(req))
            if s_digits[0] in r_digits:
                return "PASSED", f"Year {student_year} meets criteria {req}."

    return "FAILED", f"Year {student_year} does not match {', '.join(year_requirements)}."


def check_location_and_mode(
    student_locations: List[str],
    student_mode: str,
    opp_location: str,
    opp_mode: str,
) -> Tuple[str, str]:
    """
    Checks location and work mode compatibility.
    """
    norm_opp_mode = _normalize_str(opp_mode)
    if "remote" in norm_opp_mode or "online" in norm_opp_mode or "flexible" in norm_opp_mode:
        return "PASSED", f"Remote/flexible work mode ({opp_mode}) is universally accessible."

    if not student_locations and not student_mode:
        return "UNKNOWN", "Location preferences not specified in student profile."

    norm_opp_loc = _normalize_str(opp_location)
    
    # Check student locations
    for loc in student_locations:
        norm_loc = _normalize_str(loc)
        if "remote" in norm_loc:
            continue
        if norm_loc in norm_opp_loc or norm_opp_loc in norm_loc:
            return "PASSED", f"Student preferred location '{loc}' matches {opp_location}."

    if student_mode and _normalize_str(student_mode) == norm_opp_mode:
        return "PASSED", f"Work mode preference {student_mode} matches opportunity mode."

    return "FAILED", f"On-site location {opp_location} does not match preferred locations: {', '.join(student_locations)}."


def evaluate_eligibility(
    student: Dict[str, Any],
    opportunity: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Comprehensive 4-tier eligibility evaluation:
    - ELIGIBLE
    - PARTIALLY_ELIGIBLE
    - NOT_ELIGIBLE
    - UNKNOWN
    
    Ensures missing profile attributes NEVER automatically cause ineligibility.
    """
    criteria_checks = []

    # 1. Degree
    deg_status, deg_reason = check_degree_match(
        student.get("degree", ""),
        opportunity.get("degree_requirements", []),
    )
    criteria_checks.append({"criterion": "Degree", "status": deg_status, "note": deg_reason})

    # 2. Branch / Major
    branch_status, branch_reason = check_branch_match(
        student.get("branch", ""),
        opportunity.get("branch_requirements", []),
    )
    criteria_checks.append({"criterion": "Major / Branch", "status": branch_status, "note": branch_reason})

    # 3. Academic Year
    year_status, year_reason = check_academic_year_match(
        student.get("academic_year", ""),
        opportunity.get("academic_year_requirements", []),
    )
    criteria_checks.append({"criterion": "Academic Year", "status": year_status, "note": year_reason})

    # 4. Location & Work Mode
    loc_status, loc_reason = check_location_and_mode(
        student.get("preferred_locations", []),
        student.get("preferred_work_mode", ""),
        opportunity.get("location", ""),
        opportunity.get("mode", ""),
    )
    criteria_checks.append({"criterion": "Location & Mode", "status": loc_status, "note": loc_reason})

    # Synthesize counts
    passed_count = sum(1 for c in criteria_checks if c["status"] == "PASSED")
    unknown_count = sum(1 for c in criteria_checks if c["status"] == "UNKNOWN")
    failed_count = sum(1 for c in criteria_checks if c["status"] == "FAILED")

    # Determine 4-tier status
    if failed_count >= 2:
        final_status = EligibilityStatus.NOT_ELIGIBLE
        summary_note = "Does not meet multiple stated eligibility benchmarks."
    elif failed_count == 1:
        # If only 1 criterion failed but others passed/unknown
        if passed_count >= 2:
            final_status = EligibilityStatus.PARTIALLY_ELIGIBLE
            failed_crit = next(c for c in criteria_checks if c["status"] == "FAILED")
            summary_note = f"Partially eligible: fails {failed_crit['criterion']} ({failed_crit['note']}), but satisfies other benchmarks."
        else:
            final_status = EligibilityStatus.NOT_ELIGIBLE
            failed_crit = next(c for c in criteria_checks if c["status"] == "FAILED")
            summary_note = f"Not eligible: {failed_crit['note']}"
    else:
        # Zero failed criteria
        if unknown_count >= 3:
            final_status = EligibilityStatus.UNKNOWN
            summary_note = "Profile information insufficient to determine complete eligibility."
        elif unknown_count > 0:
            final_status = EligibilityStatus.ELIGIBLE
            summary_note = f"Eligible: satisfies {passed_count} primary criteria (with {unknown_count} unconfirmed)."
        else:
            final_status = EligibilityStatus.ELIGIBLE
            summary_note = f"Fully eligible: satisfies all {passed_count} stated qualification benchmarks."

    return {
        "status": final_status,
        "summary_note": summary_note,
        "criteria": criteria_checks,
        "passed_count": passed_count,
        "unknown_count": unknown_count,
        "failed_count": failed_count,
    }

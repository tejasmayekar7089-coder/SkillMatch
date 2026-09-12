import math
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, func, or_
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_optional, require_admin
from app.database.database import get_db
from app.models.enums import EligibilityStatus, OpportunityCategory, UserRole, WorkMode
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.opportunity import (
    MatchExplanationResponse,
    MatchResultResponse,
    OpportunityCreate,
    OpportunityResponse,
    OpportunityUpdate,
    PaginatedOpportunityResponse,
)
from app.models.student_profile import StudentProfile
from app.ml.matcher import match_student_and_opportunity

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

CATEGORY_MAP = {
    "internships": OpportunityCategory.INTERNSHIP,
    "internship": OpportunityCategory.INTERNSHIP,
    "hackathons": OpportunityCategory.HACKATHON,
    "hackathon": OpportunityCategory.HACKATHON,
    "scholarships": OpportunityCategory.SCHOLARSHIP,
    "scholarship": OpportunityCategory.SCHOLARSHIP,
    "courses": OpportunityCategory.COURSE,
    "course": OpportunityCategory.COURSE,
    "projects": OpportunityCategory.PROJECT,
    "project": OpportunityCategory.PROJECT,
    "jobs": OpportunityCategory.JOB,
    "job": OpportunityCategory.JOB,
    "skill-opportunities": OpportunityCategory.SKILL_OPPORTUNITY,
    "skill_opportunities": OpportunityCategory.SKILL_OPPORTUNITY,
    "skill-opportunity": OpportunityCategory.SKILL_OPPORTUNITY,
    "skill_opportunity": OpportunityCategory.SKILL_OPPORTUNITY,
}

CATEGORY_LABELS = {
    OpportunityCategory.INTERNSHIP: "Internship",
    OpportunityCategory.HACKATHON: "Hackathon",
    OpportunityCategory.SCHOLARSHIP: "Scholarship",
    OpportunityCategory.COURSE: "Course",
    OpportunityCategory.PROJECT: "Project",
    OpportunityCategory.JOB: "Job",
    OpportunityCategory.SKILL_OPPORTUNITY: "Skill Opportunity",
}


def serialize_opportunity(opp: Opportunity) -> OpportunityResponse:
    # Derive work mode
    mode_val = opp.mode if opp.mode else WorkMode.REMOTE

    return OpportunityResponse(
        id=opp.id,
        title=opp.title,
        organization=opp.organization,
        organizationLogoText=opp.organization_logo_text or opp.organization[:2].upper(),
        organizationSubtext=opp.organization_subtext,
        category=opp.category,
        categoryLabel=opp.category_label or CATEGORY_LABELS.get(opp.category, "Opportunity"),
        domain=opp.domain,
        location=opp.location,
        mode=mode_val,
        work_mode=str(mode_val.value) if hasattr(mode_val, "value") else str(mode_val),
        compensation=opp.compensation,
        deadline=opp.deadline,
        deadlineDaysRemaining=opp.deadline_days_remaining,
        postedAgo=opp.posted_ago or "Recently",
        duration=opp.duration,
        cohortSize=opp.cohort_size,
        description=opp.description,
        required_skills=opp.required_skills or [],
        requiredSkills=opp.required_skills or [],
        preferred_skills=opp.preferred_skills or [],
        preferredSkills=opp.preferred_skills or [],
        eligibility_requirements=opp.eligibility_requirements,
        eligibilityRequirements=opp.eligibility_requirements,
        degree_requirements=opp.degree_requirements or [],
        degreeRequirements=opp.degree_requirements or [],
        branch_requirements=opp.branch_requirements or [],
        branchRequirements=opp.branch_requirements or [],
        academic_year_requirements=opp.academic_year_requirements or [],
        academicYearRequirements=opp.academic_year_requirements or [],
        experience_requirements=opp.experience_requirements,
        experienceRequirements=opp.experience_requirements,
        application_url=opp.application_url,
        applicationUrl=opp.application_url,
        keyResponsibilities=opp.key_responsibilities or [],
        requirements=opp.requirements or {},
        stages=opp.stages,
        matchScore=opp.match_score or 0,
        matchBreakdown=opp.match_breakdown,
        matchedSkills=opp.matched_skills or [],
        missingSkills=opp.missing_skills or [],
        verified=opp.verified,
        verified_status=opp.verified,
        eligibilityStatus=opp.eligibility_status or EligibilityStatus.ELIGIBLE,
        eligibilityNote=opp.eligibility_note or "",
        featured=opp.featured or False,
        imageBanner=opp.image_banner,
        status=opp.status,
        created_at=opp.created_at,
        updated_at=opp.updated_at,
    )


@router.get("", response_model=PaginatedOpportunityResponse)
def get_opportunities(
    category: Optional[str] = None,
    query: Optional[str] = None,
    q: Optional[str] = None,
    domain: Optional[str] = None,
    location: Optional[str] = None,
    work_mode: Optional[str] = None,
    mode: Optional[str] = None,
    skills: Optional[str] = None,
    skill: Optional[str] = None,
    eligible_only: Optional[bool] = None,
    eligibleOnly: Optional[bool] = None,
    min_match_score: Optional[int] = None,
    minMatchScore: Optional[int] = None,
    deadline: Optional[str] = None,
    verified: Optional[bool] = None,
    sort_by: Optional[str] = "match-desc",
    sortBy: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    query_text = query or q
    work_mode_filter = work_mode or mode
    skills_filter = skills or skill
    is_eligible_only = eligible_only if eligible_only is not None else eligibleOnly
    min_score = min_match_score if min_match_score is not None else minMatchScore
    sort_order = sortBy or sort_by or "match-desc"

    db_query = db.query(Opportunity)

    # 1. Role-based verification constraint
    is_admin = current_user and current_user.role == UserRole.ADMIN
    if not is_admin:
        # Students / Public visitors can ONLY see verified opportunities
        db_query = db_query.filter(Opportunity.verified == True)
    else:
        # Admins can optionally filter by verified state, or view all
        if verified is not None:
            db_query = db_query.filter(Opportunity.verified == verified)

    # 2. Category filtering (supports both enum name and URL slug)
    if category and category.lower() != "all":
        cat_lower = category.lower().strip()
        matched_cat = CATEGORY_MAP.get(cat_lower)
        if not matched_cat:
            try:
                matched_cat = OpportunityCategory(category.upper().strip())
            except ValueError:
                matched_cat = None
        if matched_cat:
            db_query = db_query.filter(Opportunity.category == matched_cat)

    # 3. Domain filtering
    if domain and domain.lower() not in ["all", "domain: all"]:
        clean_domain = domain.replace("Domain:", "").strip()
        if clean_domain and clean_domain.lower() != "all":
            db_query = db_query.filter(Opportunity.domain.ilike(f"%{clean_domain}%"))

    # 4. Location filtering
    if location and location.lower() not in ["all", "any", "location: any"]:
        clean_loc = location.replace("Location:", "").strip()
        if clean_loc and clean_loc.lower() not in ["all", "any"]:
            db_query = db_query.filter(Opportunity.location.ilike(f"%{clean_loc}%"))

    # 5. Work Mode filtering
    if work_mode_filter and work_mode_filter.lower() not in ["all", "mode: all"]:
        db_query = db_query.filter(
            or_(
                Opportunity.mode.ilike(f"%{work_mode_filter}%"),
                Opportunity.location.ilike(f"%{work_mode_filter}%"),
            )
        )

    # 6. Search query (Search across title, organization, skills, domain, location, description)
    if query_text:
        term = query_text.strip()
        search_clauses = [
            Opportunity.title.ilike(f"%{term}%"),
            Opportunity.organization.ilike(f"%{term}%"),
            Opportunity.domain.ilike(f"%{term}%"),
            Opportunity.location.ilike(f"%{term}%"),
            Opportunity.description.ilike(f"%{term}%"),
            func.cast(Opportunity.required_skills, String).ilike(f"%{term}%"),
            func.cast(Opportunity.preferred_skills, String).ilike(f"%{term}%"),
            func.cast(Opportunity.matched_skills, String).ilike(f"%{term}%"),
        ]
        db_query = db_query.filter(or_(*search_clauses))

    # 7. Skills filter
    if skills_filter:
        skill_list = [s.strip() for s in skills_filter.split(",") if s.strip()]
        for s in skill_list:
            db_query = db_query.filter(
                or_(
                    func.cast(Opportunity.required_skills, String).ilike(f"%{s}%"),
                    func.cast(Opportunity.preferred_skills, String).ilike(f"%{s}%"),
                    func.cast(Opportunity.matched_skills, String).ilike(f"%{s}%"),
                )
            )

    # 8. Eligibility filter
    if is_eligible_only:
        db_query = db_query.filter(Opportunity.eligibility_status == EligibilityStatus.ELIGIBLE)

    # 9. Minimum match score filter
    if min_score is not None:
        db_query = db_query.filter(Opportunity.match_score >= min_score)

    # 10. Deadline filter
    if deadline:
        db_query = db_query.filter(Opportunity.deadline.ilike(f"%{deadline.strip()}%"))

    # 11. Sorting
    if sort_order in ["newest", "created_desc"]:
        db_query = db_query.order_by(Opportunity.created_at.desc())
    elif sort_order in ["deadline", "deadline-asc", "deadline_asc"]:
        db_query = db_query.order_by(Opportunity.deadline.asc())
    elif sort_order in ["compensation"]:
        db_query = db_query.order_by(Opportunity.compensation.desc())
    else:  # default / relevance / match-desc
        db_query = db_query.order_by(Opportunity.match_score.desc(), Opportunity.created_at.desc())

    # 12. Pagination
    total = db_query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    opps = db_query.offset(offset).limit(page_size).all()

    items = [serialize_opportunity(opp) for opp in opps]

    return PaginatedOpportunityResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def _resolve_student_profile(db: Session, current_user: Optional[User]) -> Optional[StudentProfile]:
    if current_user and getattr(current_user, "student_profile", None):
        return current_user.student_profile
    if current_user:
        prof = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if prof:
            return prof
    return db.query(StudentProfile).first()


@router.get("/categories")
def get_opportunity_categories(db: Session = Depends(get_db)):
    """Returns counts of verified opportunities across all 7 pillars."""
    categories_data = []
    total_verified = db.query(Opportunity).filter(Opportunity.verified == True).count()
    categories_data.append({"id": "all", "label": "All Opportunities", "count": total_verified})

    slug_map = [
        (OpportunityCategory.INTERNSHIP, "internships", "Internships"),
        (OpportunityCategory.HACKATHON, "hackathons", "Hackathons"),
        (OpportunityCategory.SCHOLARSHIP, "scholarships", "Scholarships"),
        (OpportunityCategory.COURSE, "courses", "Courses"),
        (OpportunityCategory.PROJECT, "projects", "Projects"),
        (OpportunityCategory.JOB, "jobs", "Jobs"),
        (OpportunityCategory.SKILL_OPPORTUNITY, "skill-opportunities", "Skill Opportunities"),
    ]

    for cat, slug, label in slug_map:
        cnt = db.query(Opportunity).filter(Opportunity.category == cat, Opportunity.verified == True).count()
        categories_data.append({
            "id": slug,
            "label": label,
            "count": cnt,
        })
    return categories_data


@router.get("/{id}", response_model=OpportunityResponse)
def get_opportunity(
    id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    is_admin = current_user and current_user.role == UserRole.ADMIN
    if not is_admin and not opp.verified:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    # Compute real match if student profile exists
    student_profile = _resolve_student_profile(db, current_user)
    resp = serialize_opportunity(opp)
    if student_profile:
        try:
            match_data = match_student_and_opportunity(db, student_profile, opp)
            resp.matchScore = match_data["overall_match_score"]
            resp.matchBreakdown = match_data["match_breakdown"]
            resp.matchedSkills = match_data["matched_skills"]
            resp.missingSkills = match_data["missing_skills"]
            resp.eligibilityStatus = match_data["eligibility_status"]
            resp.eligibilityNote = match_data["eligibility_note"]
        except Exception:
            pass

    return resp


@router.get("/{id}/match", response_model=MatchResultResponse)
def get_opportunity_match(
    id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Returns the real calculated AIML match results between the authenticated
    student and this opportunity.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please log in or create a student profile.",
        )

    match_data = match_student_and_opportunity(db, student_profile, opp)

    return MatchResultResponse(
        opportunityId=opp.id,
        opportunity_id=opp.id,
        overallMatchScore=match_data["overall_match_score"],
        overall_match_score=match_data["overall_match_score"],
        skillScore=match_data["skill_score"],
        skill_score=match_data["skill_score"],
        semanticSimilarity=match_data["semantic_similarity"],
        semantic_similarity=match_data["semantic_similarity"],
        educationScore=match_data["education_score"],
        education_score=match_data["education_score"],
        interestScore=match_data["interest_score"],
        interest_score=match_data["interest_score"],
        experienceScore=match_data["experience_score"],
        experience_score=match_data["experience_score"],
        preferenceScore=match_data["preference_score"],
        preference_score=match_data["preference_score"],
        matchedSkills=match_data["matched_skills"],
        matched_skills=match_data["matched_skills"],
        missingSkills=match_data["missing_skills"],
        missing_skills=match_data["missing_skills"],
        partialSkills=match_data["partial_skills"],
        partial_skills=match_data["partial_skills"],
        eligibilityStatus=match_data["eligibility_status"],
        eligibility_status=match_data["eligibility_status"],
        eligibilityNote=match_data["eligibility_note"],
        eligibility_note=match_data["eligibility_note"],
        matchBreakdown=match_data["match_breakdown"],
        match_breakdown=match_data["match_breakdown"],
    )


@router.get("/{id}/match-explanation", response_model=MatchExplanationResponse)
def get_opportunity_match_explanation(
    id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Returns explainable AI match feedback, identifying specific verified skill
    matches, missing requirements, and recommended actions.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please log in or create a student profile.",
        )

    match_data = match_student_and_opportunity(db, student_profile, opp)
    expl = match_data["explanation"]

    return MatchExplanationResponse(
        opportunityId=opp.id,
        opportunity_id=opp.id,
        compatibilityLabel=expl["compatibility_label"],
        compatibility_label=expl["compatibility_label"],
        summary=expl["summary"],
        reasons=expl["reasons"],
        strongMatches=expl["strong_matches"],
        strong_matches=expl["strong_matches"],
        missingSkills=expl["missing_skills"],
        missing_skills=expl["missing_skills"],
        recommendedAction=expl["recommended_action"],
        recommended_action=expl["recommended_action"],
        matchScore=match_data["overall_match_score"],
        match_score=match_data["overall_match_score"],
        matchBreakdown=match_data["match_breakdown"],
        match_breakdown=match_data["match_breakdown"],
    )


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opp_in: OpportunityCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    # Resolve work mode
    resolved_mode = opp_in.mode
    if not resolved_mode and opp_in.work_mode:
        try:
            resolved_mode = WorkMode(opp_in.work_mode)
        except ValueError:
            resolved_mode = WorkMode.REMOTE
    if not resolved_mode:
        resolved_mode = WorkMode.REMOTE

    category_label = opp_in.categoryLabel or CATEGORY_LABELS.get(opp_in.category, "Opportunity")

    req_skills = opp_in.required_skills if opp_in.required_skills is not None else (opp_in.requiredSkills or [])
    pref_skills = opp_in.preferred_skills if opp_in.preferred_skills is not None else (opp_in.preferredSkills or [])
    elig_req = opp_in.eligibility_requirements if opp_in.eligibility_requirements is not None else opp_in.eligibilityRequirements
    deg_req = opp_in.degree_requirements if opp_in.degree_requirements is not None else (opp_in.degreeRequirements or [])
    branch_req = opp_in.branch_requirements if opp_in.branch_requirements is not None else (opp_in.branchRequirements or [])
    year_req = opp_in.academic_year_requirements if opp_in.academic_year_requirements is not None else (opp_in.academicYearRequirements or [])
    exp_req = opp_in.experience_requirements if opp_in.experience_requirements is not None else opp_in.experienceRequirements
    app_url = opp_in.application_url if opp_in.application_url is not None else opp_in.applicationUrl
    key_resp = opp_in.key_responsibilities if opp_in.key_responsibilities is not None else (opp_in.keyResponsibilities or [])
    m_score = opp_in.match_score if opp_in.match_score is not None else (opp_in.matchScore or 0)
    m_breakdown = opp_in.match_breakdown or opp_in.matchBreakdown or {}
    matched_s = opp_in.matched_skills if opp_in.matched_skills is not None else (opp_in.matchedSkills or [])
    missing_s = opp_in.missing_skills if opp_in.missing_skills is not None else (opp_in.missingSkills or [])
    e_status = opp_in.eligibility_status or opp_in.eligibilityStatus or EligibilityStatus.ELIGIBLE
    e_note = opp_in.eligibility_note or opp_in.eligibilityNote or ""
    v_by = opp_in.verified_by or opp_in.verifiedBy
    banner = opp_in.image_banner or opp_in.imageBanner

    opp = Opportunity(
        title=opp_in.title,
        organization=opp_in.organization,
        organization_logo_text=opp_in.organizationLogoText or opp_in.organization[:2].upper(),
        organization_subtext=opp_in.organizationSubtext,
        category=opp_in.category,
        category_label=category_label,
        domain=opp_in.domain,
        location=opp_in.location,
        mode=resolved_mode,
        compensation=opp_in.compensation,
        deadline=opp_in.deadline,
        deadline_days_remaining=opp_in.deadlineDaysRemaining,
        posted_ago=opp_in.postedAgo or "Just now",
        duration=opp_in.duration,
        cohort_size=opp_in.cohortSize,
        description=opp_in.description,
        required_skills=req_skills,
        preferred_skills=pref_skills,
        eligibility_requirements=elig_req,
        degree_requirements=deg_req,
        branch_requirements=branch_req,
        academic_year_requirements=year_req,
        experience_requirements=exp_req,
        application_url=app_url,
        key_responsibilities=key_resp,
        requirements=opp_in.requirements or {},
        stages=opp_in.stages,
        match_score=m_score,
        match_breakdown=m_breakdown,
        matched_skills=matched_s,
        missing_skills=missing_s,
        verified=bool(opp_in.verified),
        eligibility_status=e_status,
        eligibility_note=e_note,
        verified_by=v_by or (current_user.full_name if opp_in.verified else None),
        featured=bool(opp_in.featured),
        image_banner=banner,
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)

    return serialize_opportunity(opp)


@router.put("/{id}", response_model=OpportunityResponse)
def update_opportunity(
    id: str,
    opp_in: OpportunityUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    update_data = opp_in.model_dump(exclude_unset=True)

    field_mapping = {
        "title": "title",
        "organization": "organization",
        "organizationLogoText": "organization_logo_text",
        "organizationSubtext": "organization_subtext",
        "category": "category",
        "categoryLabel": "category_label",
        "domain": "domain",
        "location": "location",
        "mode": "mode",
        "compensation": "compensation",
        "deadline": "deadline",
        "deadlineDaysRemaining": "deadline_days_remaining",
        "postedAgo": "posted_ago",
        "duration": "duration",
        "cohortSize": "cohort_size",
        "description": "description",
        "required_skills": "required_skills",
        "requiredSkills": "required_skills",
        "preferred_skills": "preferred_skills",
        "preferredSkills": "preferred_skills",
        "eligibility_requirements": "eligibility_requirements",
        "eligibilityRequirements": "eligibility_requirements",
        "degree_requirements": "degree_requirements",
        "degreeRequirements": "degree_requirements",
        "branch_requirements": "branch_requirements",
        "branchRequirements": "branch_requirements",
        "academic_year_requirements": "academic_year_requirements",
        "academicYearRequirements": "academic_year_requirements",
        "experience_requirements": "experience_requirements",
        "experienceRequirements": "experience_requirements",
        "application_url": "application_url",
        "applicationUrl": "application_url",
        "keyResponsibilities": "key_responsibilities",
        "key_responsibilities": "key_responsibilities",
        "requirements": "requirements",
        "stages": "stages",
        "matchScore": "match_score",
        "match_score": "match_score",
        "matchBreakdown": "match_breakdown",
        "match_breakdown": "match_breakdown",
        "matchedSkills": "matched_skills",
        "matched_skills": "matched_skills",
        "missingSkills": "missing_skills",
        "missing_skills": "missing_skills",
        "verified": "verified",
        "eligibilityStatus": "eligibility_status",
        "eligibility_status": "eligibility_status",
        "eligibilityNote": "eligibility_note",
        "eligibility_note": "eligibility_note",
        "verifiedBy": "verified_by",
        "verified_by": "verified_by",
        "featured": "featured",
        "imageBanner": "image_banner",
        "image_banner": "image_banner",
    }

    for schema_field, model_field in field_mapping.items():
        if schema_field in update_data:
            setattr(opp, model_field, update_data[schema_field])

    if opp_in.work_mode and not opp_in.mode:
        try:
            opp.mode = WorkMode(opp_in.work_mode)
        except ValueError:
            pass

    if opp_in.category and not opp_in.categoryLabel:
        opp.category_label = CATEGORY_LABELS.get(opp_in.category, "Opportunity")

    db.commit()
    db.refresh(opp)
    return serialize_opportunity(opp)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_opportunity(
    id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    db.delete(opp)
    db.commit()
    return {"message": "Opportunity deleted successfully", "id": id}


@router.patch("/{id}/verify", response_model=OpportunityResponse)
def verify_opportunity(
    id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    opp.verified = True
    opp.verified_by = current_user.full_name or "SkillMatch Admin Team"
    opp.eligibility_note = "Verified for active candidate matching"
    db.commit()
    db.refresh(opp)
    return serialize_opportunity(opp)


@router.patch("/{id}/reject", response_model=OpportunityResponse)
def reject_opportunity(
    id: str,
    reason: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    opp = db.query(Opportunity).filter(Opportunity.id == id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    opp.verified = False
    opp.eligibility_note = reason or "Listing unverified / rejected by administrative review"
    db.commit()
    db.refresh(opp)
    return serialize_opportunity(opp)

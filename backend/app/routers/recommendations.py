from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_optional, get_db
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.opportunity import OpportunityResponse
from app.ml.matcher import rank_opportunities_for_student

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _resolve_student_profile(db: Session, current_user: Optional[User]) -> Optional[StudentProfile]:
    if current_user and getattr(current_user, "student_profile", None):
        return current_user.student_profile
    if current_user:
        prof = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if prof:
            return prof
    return db.query(StudentProfile).first()


@router.get("", response_model=List[OpportunityResponse])
def get_recommendations(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Returns personalized opportunity recommendations for the user
    calculated via the real AIML hybrid matching engine.
    """
    # 1. Fetch verified opportunities only
    opps = db.query(Opportunity).filter(Opportunity.verified == True).all()

    student_profile = _resolve_student_profile(db, current_user)

    if student_profile and opps:
        try:
            ranked_items = rank_opportunities_for_student(db, student_profile, opps)
            results = []
            for item in ranked_items[:20]:
                opp = item["opportunity"]
                m = item["match"]
                results.append(
                    OpportunityResponse(
                        id=opp.id,
                        title=opp.title,
                        organization=opp.organization,
                        organizationLogoText=opp.organization_logo_text,
                        organizationSubtext=opp.organization_subtext,
                        category=opp.category,
                        categoryLabel=opp.category_label,
                        domain=opp.domain,
                        location=opp.location,
                        mode=opp.mode,
                        work_mode=str(opp.mode.value if hasattr(opp.mode, "value") else opp.mode),
                        compensation=opp.compensation,
                        deadline=opp.deadline,
                        deadlineDaysRemaining=opp.deadline_days_remaining,
                        postedAgo=opp.posted_ago,
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
                        matchScore=m["overall_match_score"],
                        matchBreakdown=m["match_breakdown"],
                        matchedSkills=m["matched_skills"],
                        missingSkills=m["missing_skills"],
                        verified=opp.verified,
                        verified_status=opp.verified,
                        eligibilityStatus=m["eligibility_status"],
                        eligibilityNote=m["eligibility_note"],
                        verifiedBy=opp.verified_by,
                        featured=opp.featured,
                        imageBanner=opp.image_banner,
                        created_at=opp.created_at,
                        updated_at=opp.updated_at,
                    )
                )
            return results
        except Exception:
            pass

    # Baseline fallback
    return [
        OpportunityResponse(
            id=opp.id,
            title=opp.title,
            organization=opp.organization,
            organizationLogoText=opp.organization_logo_text,
            organizationSubtext=opp.organization_subtext,
            category=opp.category,
            categoryLabel=opp.category_label,
            domain=opp.domain,
            location=opp.location,
            mode=opp.mode,
            work_mode=str(opp.mode.value if hasattr(opp.mode, "value") else opp.mode),
            compensation=opp.compensation,
            deadline=opp.deadline,
            deadlineDaysRemaining=opp.deadline_days_remaining,
            postedAgo=opp.posted_ago,
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
            matchScore=opp.match_score,
            matchBreakdown=opp.match_breakdown,
            matchedSkills=opp.matched_skills or [],
            missingSkills=opp.missing_skills or [],
            verified=opp.verified,
            verified_status=opp.verified,
            eligibilityStatus=opp.eligibility_status,
            eligibilityNote=opp.eligibility_note,
            verifiedBy=opp.verified_by,
            featured=opp.featured,
            imageBanner=opp.image_banner,
            created_at=opp.created_at,
            updated_at=opp.updated_at,
        )
        for opp in opps[:10]
    ]

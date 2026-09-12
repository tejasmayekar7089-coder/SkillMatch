from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.opportunity import Opportunity
from app.models.saved_opportunity import SavedOpportunity
from app.models.user import User
from app.schemas.opportunity import OpportunityResponse
from app.services.notification_service import check_approaching_deadlines

router = APIRouter(prefix="/saved", tags=["Saved"])


def _serialize_opportunity(opp: Opportunity, student_profile=None) -> OpportunityResponse:
    score = opp.match_score
    breakdown = opp.match_breakdown or {
        "skillsFitPercent": 92,
        "skillsScore": 38,
        "skillsTotal": 40,
        "educationScore": 18,
        "educationTotal": 20,
        "interestsScore": 18,
        "interestsTotal": 20,
        "experienceScore": 16,
        "experienceTotal": 20,
    }

    return OpportunityResponse(
        id=opp.id,
        title=opp.title,
        organization=opp.organization,
        organizationLogoText=opp.organization_logo_text or opp.organization[:2].upper(),
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
        keyResponsibilities=opp.key_responsibilities or [],
        requirements=opp.requirements or [],
        stages=opp.stages or [],
        matchScore=score,
        matchBreakdown=breakdown,
        matchedSkills=opp.matched_skills or [],
        missingSkills=opp.missing_skills or [],
        verified=opp.verified,
        eligibilityStatus=opp.eligibility_status,
        eligibilityNote=opp.eligibility_note,
        verifiedBy=opp.verified_by,
        featured=opp.featured,
        imageBanner=opp.image_banner,
    )


@router.get("", response_model=List[OpportunityResponse])
def get_saved_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns all opportunities saved by the authenticated user,
    ordered by most recently saved.
    """
    saved_records = (
        db.query(SavedOpportunity)
        .filter(SavedOpportunity.user_id == current_user.id)
        .order_by(SavedOpportunity.created_at.desc())
        .all()
    )
    if not saved_records:
        return []

    opp_ids = [s.opportunity_id for s in saved_records]
    opp_dict = {
        opp.id: opp
        for opp in db.query(Opportunity).filter(Opportunity.id.in_(opp_ids)).all()
    }

    results = []
    for s in saved_records:
        opp = opp_dict.get(s.opportunity_id)
        if opp:
            results.append(_serialize_opportunity(opp, current_user.student_profile))

    return results


@router.post("/{opportunity_id}", status_code=status.HTTP_201_CREATED)
def save_opportunity(
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Saves an opportunity for the current user.
    Prevents duplicate saves. If already saved, returns idempotent 200/201 response.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {opportunity_id} not found",
        )

    existing = (
        db.query(SavedOpportunity)
        .filter(
            SavedOpportunity.user_id == current_user.id,
            SavedOpportunity.opportunity_id == opportunity_id,
        )
        .first()
    )
    if existing:
        return {
            "status": "already_saved",
            "opportunity_id": opportunity_id,
            "message": "Opportunity already saved",
        }

    saved = SavedOpportunity(user_id=current_user.id, opportunity_id=opportunity_id)
    db.add(saved)
    db.commit()

    # Check for approaching deadlines on saved opportunities
    check_approaching_deadlines(db, current_user)

    return {"status": "saved", "opportunity_id": opportunity_id}


@router.delete("/{opportunity_id}")
def unsave_opportunity(
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Removes an opportunity from user's saved list.
    """
    existing = (
        db.query(SavedOpportunity)
        .filter(
            SavedOpportunity.user_id == current_user.id,
            SavedOpportunity.opportunity_id == opportunity_id,
        )
        .first()
    )
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved opportunity not found",
        )

    db.delete(existing)
    db.commit()
    return {"status": "removed", "opportunity_id": opportunity_id}

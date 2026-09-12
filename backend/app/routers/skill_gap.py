from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_optional, get_db
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.ml.skill_gap_engine import (
    analyze_skill_gap_for_opportunity,
    analyze_skill_gap_for_role,
    recommend_learning_resources_for_gap,
)

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap"])


def _resolve_student_profile(db: Session, current_user: Optional[User]) -> StudentProfile:
    if current_user and getattr(current_user, "student_profile", None):
        return current_user.student_profile
    if current_user:
        prof = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if prof:
            return prof
    existing = db.query(StudentProfile).first()
    if existing:
        return existing
    return StudentProfile(
        id="default-profile",
        user_id="default-user",
        degree="B.Tech / B.E.",
        branch="Computer Science",
        academic_year="3rd Year",
        target_role="Machine Learning Engineer",
        preferred_domains=["AI / Machine Learning", "Web Technologies"],
        preferred_locations=["Remote"],
        preferred_work_mode="Remote",
    )


@router.get("")
def get_skill_gap_analysis(
    role: Optional[str] = Query(None),
    role_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Skill gap analysis for a target career role.
    Computes real readiness percentage, mastered vs developing vs critical gaps,
    and actual employer benchmarks.
    """
    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    target_role = role or role_id or student_profile.target_role or "Machine Learning Engineer"
    return analyze_skill_gap_for_role(db, student_profile, target_role)


@router.get("/learning")
def get_general_learning_recommendations(
    role: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Recommends actual database courses and projects targeting missing skills
    for the student's target career role.
    """
    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return recommend_learning_resources_for_gap(db, student_profile, role_title=role)


@router.get("/{opportunity_id}")
def get_opportunity_skill_gap(
    opportunity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Skill gap analysis for a specific opportunity.
    Compares current skills vs required skills, classifies as MATCHED, MISSING, PARTIAL,
    and returns priority ranked skills.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return analyze_skill_gap_for_opportunity(db, student_profile, opp)


@router.get("/{opportunity_id}/learning")
def get_opportunity_learning_recommendations(
    opportunity_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Recommends actual database courses and projects targeting the specific missing skills
    identified for this opportunity.
    """
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    return recommend_learning_resources_for_gap(db, student_profile, opportunity_id=opportunity_id)

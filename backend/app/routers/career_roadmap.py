from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user_optional, get_db
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.ml.skill_gap_engine import generate_career_roadmap

router = APIRouter(prefix="/career-roadmap", tags=["Career Roadmap"])


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
def get_career_roadmap(
    role: Optional[str] = Query(None),
    target_career: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Generates a personalized, step-by-step career trajectory:
    Current Profile -> Target Career -> Required Skills -> Missing Skills -> Learning -> Projects -> Opportunities.
    Driven by actual database opportunities and courses.
    """
    student_profile = _resolve_student_profile(db, current_user)
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    career = target_career or role or student_profile.target_role or "Machine Learning Engineer"
    return generate_career_roadmap(db, student_profile, career)

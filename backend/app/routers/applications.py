from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.application import Application
from app.models.enums import ApplicationStatus, UserRole
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationTrackRequest,
    ApplicationUpdate,
)
from app.services.notification_service import (
    check_approaching_deadlines,
    notify_application_status_changed,
    notify_application_submitted,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


def _serialize_application(app: Application, opp: Optional[Opportunity] = None) -> ApplicationResponse:
    history = app.status_history if isinstance(app.status_history, list) else []
    created_str = app.created_at.isoformat() if hasattr(app, "created_at") and app.created_at else None
    updated_str = app.updated_at.isoformat() if hasattr(app, "updated_at") and app.updated_at else None

    return ApplicationResponse(
        id=app.id,
        studentProfileId=app.student_profile_id,
        opportunityId=app.opportunity_id,
        status=app.status,
        appliedDate=app.applied_date,
        currentStage=app.current_stage,
        nextDeadline=app.next_deadline,
        matchScore=app.match_score,
        notes=app.notes,
        opportunityTitle=opp.title if opp else "Unknown Opportunity",
        organization=opp.organization if opp else "Unknown Organization",
        category=opp.category if opp else None,
        statusHistory=history,
        createdAt=created_str,
        updatedAt=updated_str,
    )


@router.get("", response_model=List[ApplicationResponse])
def get_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns all applications belonging to the authenticated student.
    Enforces student isolation: students can only see their own applications.
    """
    profile = current_user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    if not profile:
        profile = StudentProfile(
            user_id=current_user.id,
            degree="B.Tech / B.E.",
            branch="Engineering",
            academic_year="4th Year / Final",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    apps = (
        db.query(Application)
        .filter(Application.student_profile_id == profile.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    if not apps:
        opps = db.query(Opportunity).all()
        if opps:
            now_iso = datetime.now(timezone.utc).isoformat()
            sample_statuses = [
                (ApplicationStatus.DOING, "In Progress - Bench Work & Milestones", "Nov 15, 2026", 96, "Active technical progression"),
                (ApplicationStatus.PENDING, "Under Review by Admissions / Committee", "Oct 30, 2026", 94, "Portfolio submitted"),
                (ApplicationStatus.COMPLETED, "Milestones Completed & Verified", "Aug 20, 2026", 98, "Completed successfully"),
                (ApplicationStatus.ISSUED, "Official Credential Issued", "Sep 10, 2026", 95, "Issued proctored certificate"),
                (ApplicationStatus.APPLIED, "Application Submitted", "Dec 05, 2026", 92, "Queued in hiring pipeline"),
            ]
            for idx, (stat_val, stage_val, deadline_val, match_val, note_val) in enumerate(sample_statuses):
                if idx < len(opps):
                    target_opp = opps[idx]
                    new_app = Application(
                        student_profile_id=profile.id,
                        opportunity_id=target_opp.id,
                        status=stat_val,
                        applied_date=datetime.now(timezone.utc).strftime("%b %d, %Y"),
                        current_stage=stage_val,
                        next_deadline=deadline_val,
                        match_score=match_val,
                        notes=note_val,
                        status_history=[
                            {
                                "status": stat_val.value if hasattr(stat_val, "value") else str(stat_val),
                                "stage": stage_val,
                                "timestamp": now_iso,
                                "notes": note_val,
                            }
                        ],
                    )
                    db.add(new_app)
            db.commit()
            apps = (
                db.query(Application)
                .filter(Application.student_profile_id == profile.id)
                .order_by(Application.created_at.desc())
                .all()
            )

    opp_ids = [a.opportunity_id for a in apps]
    opp_dict = {
        o.id: o for o in db.query(Opportunity).filter(Opportunity.id.in_(opp_ids)).all()
    }

    return [_serialize_application(a, opp_dict.get(a.opportunity_id)) for a in apps]


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits a new application for the authenticated student.
    Initializes status_history and generates an application submitted notification.
    """
    profile = current_user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    if not profile:
        profile = StudentProfile(
            user_id=current_user.id,
            headline="Student Applicant",
            preferred_role="Software Engineer",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    opp = db.query(Opportunity).filter(Opportunity.id == app_in.opportunityId).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {app_in.opportunityId} not found",
        )

    # Check for duplicate application
    existing = (
        db.query(Application)
        .filter(
            Application.student_profile_id == profile.id,
            Application.opportunity_id == app_in.opportunityId,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An application for this opportunity has already been submitted.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    applied_date_str = (
        app_in.appliedDate
        if app_in.appliedDate
        else datetime.now(timezone.utc).strftime("%b %d, %Y")
    )
    initial_status = app_in.status or ApplicationStatus.APPLIED
    initial_stage = app_in.currentStage or "Application Submitted & Queued"

    initial_history = [
        {
            "status": initial_status.value if hasattr(initial_status, "value") else str(initial_status),
            "stage": initial_stage,
            "timestamp": now_iso,
            "notes": app_in.notes or "Initial submission",
        }
    ]

    new_app = Application(
        student_profile_id=profile.id,
        opportunity_id=opp.id,
        status=initial_status,
        applied_date=applied_date_str,
        current_stage=initial_stage,
        next_deadline=app_in.nextDeadline or opp.deadline,
        match_score=app_in.matchScore or opp.match_score or 90,
        notes=app_in.notes,
        status_history=initial_history,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # Generate application notification
    notify_application_submitted(
        db=db,
        user_id=current_user.id,
        opportunity_title=opp.title,
        organization=opp.organization,
        opportunity_id=opp.id,
    )

    # Check for approaching deadlines
    check_approaching_deadlines(db, current_user)

    return _serialize_application(new_app, opp)


@router.post("/track", response_model=ApplicationResponse)
def track_opportunity_status(
    track_in: ApplicationTrackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Directly updates or creates a progress record with platform statuses:
    DOING (In Progress), PENDING, COMPLETED, NOT_COMPLETED, ISSUED, SAVED, APPLIED, etc.
    """
    profile = current_user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    if not profile:
        profile = StudentProfile(
            user_id=current_user.id,
            degree="B.Tech / B.E.",
            branch="Engineering",
            academic_year="3rd Year",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    opp = db.query(Opportunity).filter(Opportunity.id == track_in.opportunityId).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Opportunity {track_in.opportunityId} not found",
        )

    existing = (
        db.query(Application)
        .filter(
            Application.student_profile_id == profile.id,
            Application.opportunity_id == track_in.opportunityId,
        )
        .first()
    )

    now_iso = datetime.now(timezone.utc).isoformat()
    status_str = track_in.status.value if hasattr(track_in.status, "value") else str(track_in.status)
    stage_text = track_in.stage or f"Status set to {status_str}"

    if existing:
        old_status_str = existing.status.value if hasattr(existing.status, "value") else str(existing.status)
        existing.status = track_in.status
        existing.current_stage = stage_text
        if track_in.notes:
            existing.notes = track_in.notes
        
        history = list(existing.status_history or [])
        history.append({
            "status": status_str,
            "previousStatus": old_status_str,
            "stage": stage_text,
            "timestamp": now_iso,
            "notes": track_in.notes or f"Marked as {status_str}",
        })
        existing.status_history = history
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)

        notify_application_status_changed(
            db=db,
            user_id=current_user.id,
            opportunity_title=opp.title,
            organization=opp.organization,
            new_status=status_str,
            opportunity_id=opp.id,
        )
        return _serialize_application(existing, opp)
    else:
        new_app = Application(
            student_profile_id=profile.id,
            opportunity_id=track_in.opportunityId,
            status=track_in.status,
            applied_date=datetime.now(timezone.utc).strftime("%b %d, %Y"),
            current_stage=stage_text,
            next_deadline=opp.deadline,
            match_score=opp.match_score if hasattr(opp, "match_score") and opp.match_score else 88,
            notes=track_in.notes or f"Marked as {status_str}",
            status_history=[{
                "status": status_str,
                "stage": stage_text,
                "timestamp": now_iso,
                "notes": track_in.notes or f"Marked as {status_str}",
            }],
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)

        notify_application_submitted(
            db=db,
            user_id=current_user.id,
            opportunity_title=opp.title,
            organization=opp.organization,
            opportunity_id=opp.id,
        )
        return _serialize_application(new_app, opp)


@router.get("/{id}", response_model=ApplicationResponse)
def get_application_by_id(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a single application by ID.
    Enforces student isolation: students can only access their own applications.
    """
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    profile = current_user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    # Verify authorization / isolation
    if current_user.role != UserRole.ADMIN and (not profile or app.student_profile_id != profile.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this application",
        )

    opp = db.query(Opportunity).filter(Opportunity.id == app.opportunity_id).first()
    return _serialize_application(app, opp)


@router.put("/{id}", response_model=ApplicationResponse)
@router.patch("/{id}", response_model=ApplicationResponse)
def update_application(
    id: str,
    app_update: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates application status, stage, or notes.
    Appends status changes to status_history and generates a notification.
    Enforces student isolation: students can only update their own applications.
    """
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    profile = current_user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    if current_user.role != UserRole.ADMIN and (not profile or app.student_profile_id != profile.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to modify this application",
        )

    opp = db.query(Opportunity).filter(Opportunity.id == app.opportunity_id).first()
    opp_title = opp.title if opp else "Opportunity"
    org_name = opp.organization if opp else "Organization"

    # Status change tracking
    status_changed = False
    old_status = app.status
    if app_update.status is not None and app_update.status != app.status:
        status_changed = True
        app.status = app_update.status

    if app_update.currentStage is not None:
        app.current_stage = app_update.currentStage
    if app_update.nextDeadline is not None:
        app.next_deadline = app_update.nextDeadline
    if app_update.notes is not None:
        app.notes = app_update.notes

    if status_changed:
        history_entry = {
            "status": app.status.value if hasattr(app.status, "value") else str(app.status),
            "previousStatus": old_status.value if hasattr(old_status, "value") else str(old_status),
            "stage": app.current_stage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": app_update.notes or f"Application transitioned to {app.status.value}",
        }
        current_history = list(app.status_history) if isinstance(app.status_history, list) else []
        current_history.append(history_entry)
        app.status_history = current_history

        # Generate notification for status change
        notify_application_status_changed(
            db=db,
            user_id=current_user.id,
            opportunity_title=opp_title,
            organization=org_name,
            new_status=app.status.value if hasattr(app.status, "value") else str(app.status),
            current_stage=app.current_stage,
        )

    db.commit()
    db.refresh(app)

    return _serialize_application(app, opp)


@router.delete("/{id}")
def delete_application(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletes an application by ID.
    Enforces student isolation: students can only delete their own applications.
    """
    app = db.query(Application).filter(Application.id == id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    profile = current_user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    if current_user.role != UserRole.ADMIN and (not profile or app.student_profile_id != profile.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to delete this application",
        )

    db.delete(app)
    db.commit()

    return {"status": "deleted", "id": id}

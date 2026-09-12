from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.application import Application
from app.models.enums import ApplicationStatus, NotificationType
from app.models.notification import Notification
from app.models.opportunity import Opportunity
from app.models.saved_opportunity import SavedOpportunity
from app.models.user import User


def format_time_ago(dt: Optional[datetime]) -> str:
    if not dt:
        return "Recently"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = max(1, seconds // 60)
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = max(1, seconds // 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = max(1, seconds // 86400)
        return f"{days}d ago"
    else:
        weeks = max(1, seconds // 604800)
        return f"{weeks}w ago"


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    description: str,
    notif_type: NotificationType = NotificationType.SYSTEM,
    link: Optional[str] = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        title=title,
        description=description,
        type=notif_type,
        link=link,
        is_read=False,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def check_approaching_deadlines(db: Session, user: User) -> List[Notification]:
    """
    Checks saved opportunities and active applications for approaching deadlines
    (deadline_days_remaining <= 5).
    Guarantees no duplicate notifications are sent to the user for the same opportunity.
    """
    new_notifs: List[Notification] = []

    # 1. Collect opportunity IDs from saved opportunities
    saved_records = (
        db.query(SavedOpportunity).filter(SavedOpportunity.user_id == user.id).all()
    )
    saved_opp_ids = {s.opportunity_id for s in saved_records}

    # 2. Collect opportunity IDs from active applications (if user has student profile)
    app_opp_ids = set()
    if user.student_profile:
        active_apps = (
            db.query(Application)
            .filter(
                Application.student_profile_id == user.student_profile.id,
                Application.status.in_([
                    ApplicationStatus.SAVED,
                    ApplicationStatus.PLANNING,
                    ApplicationStatus.APPLIED,
                    ApplicationStatus.SHORTLISTED,
                    ApplicationStatus.INTERVIEW,
                ]),
            )
            .all()
        )
        app_opp_ids = {a.opportunity_id for a in active_apps}

    all_relevant_opp_ids = saved_opp_ids.union(app_opp_ids)
    if not all_relevant_opp_ids:
        return new_notifs

    opps = db.query(Opportunity).filter(Opportunity.id.in_(all_relevant_opp_ids)).all()

    for opp in opps:
        # Check approaching deadline (between 0 and 5 days remaining)
        days_rem = opp.deadline_days_remaining
        if days_rem is not None and 0 <= days_rem <= 5:
            # Check if user has already received a deadline notification for this opportunity
            existing_notif = (
                db.query(Notification)
                .filter(
                    Notification.user_id == user.id,
                    Notification.type == NotificationType.DEADLINE,
                    Notification.link == f"/opportunity/{opp.id}",
                )
                .first()
            )
            if existing_notif:
                continue

            day_str = f"{days_rem} day{'s' if days_rem != 1 else ''}"
            deadline_date = opp.deadline or "soon"
            title = f"Approaching Deadline: {opp.title}"
            desc = (
                f"Application deadline for {opp.title} at {opp.organization} closes in {day_str} "
                f"({deadline_date}). Finalize your application now!"
            )
            link = f"/opportunity/{opp.id}"

            created = create_notification(
                db=db,
                user_id=user.id,
                title=title,
                description=desc,
                notif_type=NotificationType.DEADLINE,
                link=link,
            )
            new_notifs.append(created)

    return new_notifs


def notify_application_submitted(
    db: Session,
    user_id: str,
    opportunity_title: str,
    organization: str,
    opportunity_id: str,
) -> Notification:
    return create_notification(
        db=db,
        user_id=user_id,
        title=f"Application Submitted: {opportunity_title}",
        description=f"Your application for {opportunity_title} at {organization} was received and is under review.",
        notif_type=NotificationType.APPLICATION,
        link="/applications",
    )


def notify_application_status_changed(
    db: Session,
    user_id: str,
    opportunity_title: str,
    organization: str,
    new_status: str,
    current_stage: Optional[str] = None,
) -> Notification:
    stage_text = f" Current stage: {current_stage}." if current_stage else ""
    return create_notification(
        db=db,
        user_id=user_id,
        title=f"Status Update: {opportunity_title}",
        description=f"Your application at {organization} transitioned to {new_status}.{stage_text}",
        notif_type=NotificationType.APPLICATION,
        link="/applications",
    )


def notify_new_match(
    db: Session,
    user_id: str,
    opportunity_title: str,
    organization: str,
    match_score: int,
    opportunity_id: str,
) -> Optional[Notification]:
    link = f"/opportunity/{opportunity_id}"
    existing = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.type == NotificationType.MATCH,
            Notification.link == link,
        )
        .first()
    )
    if existing:
        return None

    return create_notification(
        db=db,
        user_id=user_id,
        title=f"New High Match ({match_score}%): {opportunity_title}",
        description=f"{organization} has a listing with a {match_score}% skill alignment for your profile.",
        notif_type=NotificationType.MATCH,
        link=link,
    )


def notify_recommendation_update(
    db: Session,
    user_id: str,
    title: str,
    description: str,
    link: Optional[str] = "/recommendations",
) -> Notification:
    return create_notification(
        db=db,
        user_id=user_id,
        title=title,
        description=description,
        notif_type=NotificationType.MATCH,
        link=link,
    )

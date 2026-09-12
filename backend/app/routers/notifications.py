from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import check_approaching_deadlines, format_time_ago

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns all notifications for the authenticated user,
    automatically scanning for approaching deadlines without generating duplicates.
    """
    # 1. Run deadline detection for approaching deadlines
    check_approaching_deadlines(db, current_user)

    # 2. Fetch all user notifications
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return [
        NotificationResponse(
            id=n.id,
            userId=n.user_id,
            title=n.title,
            description=n.description,
            type=n.type,
            read=n.is_read,
            link=n.link,
            timeAgo=format_time_ago(n.created_at),
            createdAt=n.created_at.isoformat() if n.created_at else None,
        )
        for n in notifs
    ]


@router.put("/read-all")
@router.patch("/read-all")
@router.post("/read-all")
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marks all notifications for the authenticated user as read.
    """
    unread = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .all()
    )
    count = len(unread)
    for n in unread:
        n.is_read = True

    db.commit()
    return {"status": "ok", "marked_read": count}


@router.put("/{id}/read")
@router.patch("/{id}/read")
def mark_notification_read(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Marks a specific notification as read.
    Enforces authorization: users can only mark their own notifications as read.
    """
    notif = (
        db.query(Notification)
        .filter(Notification.id == id, Notification.user_id == current_user.id)
        .first()
    )
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notif.is_read = True
    db.commit()
    return {"status": "ok", "id": id}

from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import NotificationType


class NotificationBase(BaseModel):
    title: str
    description: str
    type: NotificationType = NotificationType.SYSTEM
    link: Optional[str] = None


class NotificationCreate(NotificationBase):
    userId: str


class NotificationResponse(NotificationBase):
    id: str
    userId: str
    read: bool
    timeAgo: Optional[str] = "Just now"
    createdAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

from app.schemas.common import HealthResponse, MessageResponse, PaginatedResponse
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.schemas.profile import StudentProfileResponse, StudentProfileCreate, StudentProfileUpdate
from app.schemas.opportunity import OpportunityResponse, OpportunityCreate, OpportunityUpdate
from app.schemas.application import ApplicationResponse, ApplicationCreate, ApplicationUpdate
from app.schemas.notification import NotificationResponse, NotificationCreate
from app.schemas.skill_gap import TargetRoleGapDataResponse

__all__ = [
    "HealthResponse",
    "MessageResponse",
    "PaginatedResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "StudentProfileResponse",
    "StudentProfileCreate",
    "StudentProfileUpdate",
    "OpportunityResponse",
    "OpportunityCreate",
    "OpportunityUpdate",
    "ApplicationResponse",
    "ApplicationCreate",
    "ApplicationUpdate",
    "NotificationResponse",
    "NotificationCreate",
    "TargetRoleGapDataResponse",
]

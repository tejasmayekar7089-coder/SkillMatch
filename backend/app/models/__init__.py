from app.database.base import Base
from app.models.enums import (
    ApplicationStatus,
    EligibilityStatus,
    NotificationType,
    OpportunityCategory,
    SkillLevel,
    UserRole,
    WorkMode,
)
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.skill import Skill, StudentSkill
from app.models.interest import Interest, StudentInterest
from app.models.project import Project
from app.models.certification import Certification
from app.models.opportunity import Opportunity, OpportunitySkill
from app.models.saved_opportunity import SavedOpportunity
from app.models.application import Application
from app.models.notification import Notification
from app.models.recommendation import Recommendation
from app.models.skill_gap import SkillGap
from app.models.opportunity_embedding import OpportunityEmbedding

__all__ = [
    "Base",
    "UserRole",
    "OpportunityCategory",
    "ApplicationStatus",
    "WorkMode",
    "EligibilityStatus",
    "SkillLevel",
    "NotificationType",
    "User",
    "StudentProfile",
    "Skill",
    "StudentSkill",
    "Interest",
    "StudentInterest",
    "Project",
    "Certification",
    "Opportunity",
    "OpportunitySkill",
    "OpportunityEmbedding",
    "SavedOpportunity",
    "Application",
    "Notification",
    "Recommendation",
    "SkillGap",
]

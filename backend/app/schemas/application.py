from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import ApplicationStatus, OpportunityCategory


class StatusHistoryEntry(BaseModel):
    status: str
    stage: Optional[str] = None
    timestamp: str
    notes: Optional[str] = None


class ApplicationBase(BaseModel):
    opportunityId: str
    status: ApplicationStatus = ApplicationStatus.APPLIED
    appliedDate: Optional[str] = None
    currentStage: str = "Applied"
    nextDeadline: Optional[str] = None
    matchScore: int = 0
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationTrackRequest(BaseModel):
    opportunityId: str
    status: ApplicationStatus = ApplicationStatus.DOING
    notes: Optional[str] = None
    stage: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    currentStage: Optional[str] = None
    nextDeadline: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: str
    studentProfileId: str
    opportunityTitle: Optional[str] = None
    organization: Optional[str] = None
    category: Optional[OpportunityCategory] = None
    statusHistory: List[Dict[str, Any]] = []
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

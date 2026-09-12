from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.opportunity import OpportunityResponse


class UpcomingDeadlineItem(BaseModel):
    id: str
    title: str
    organization: str
    category: str
    categoryLabel: str
    deadline: str
    deadlineDaysRemaining: Optional[int] = None
    isSaved: bool = False
    isApplied: bool = False
    link: str


class DashboardRecommendedItem(BaseModel):
    opportunity: OpportunityResponse
    matchScore: int
    eligibilityStatus: str
    eligibilityNote: str
    matchedSkills: List[str]
    missingSkills: List[str]


class DashboardSkillGapSummary(BaseModel):
    targetRole: str
    readinessScore: int
    competenciesMet: int
    competenciesTotal: int
    criticalGaps: List[Dict[str, Any]]
    masteredSkills: List[Dict[str, Any]]


class DashboardResponse(BaseModel):
    studentName: str
    profileCompletion: int
    totalSaved: int
    totalApplications: int
    applicationStatusCounts: Dict[str, int]
    recommendedOpportunities: List[DashboardRecommendedItem]
    upcomingDeadlines: List[UpcomingDeadlineItem]
    skillGaps: DashboardSkillGapSummary
    learningRecommendations: List[Dict[str, Any]]
    recentNotifications: List[Dict[str, Any]]
    categoryCounts: Dict[str, int]
    matchRateAvg: int
    readinessScore: int

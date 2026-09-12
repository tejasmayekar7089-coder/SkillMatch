from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AdminDashboardStats(BaseModel):
    totalStudents: int
    totalOpportunities: int
    opportunitiesByCategory: Dict[str, int]
    verifiedOpportunities: int
    pendingOpportunities: int
    applicationCounts: int
    applicationsByStatus: Dict[str, int]
    activeUsers: int
    recentActivity: List[Dict[str, Any]]
    verificationRate: float
    avgMatchFit: float


class AdminStudentSummary(BaseModel):
    id: str
    userId: str
    name: str
    email: str
    university: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    targetRole: Optional[str] = None
    verifiedSkillsCount: int = 0
    profileStrength: int = 0
    verifiedProfilePercent: int = 0
    isActive: bool = True
    applicationsCount: int = 0
    status: str = "Active"


class AdminStudentDetail(BaseModel):
    id: str
    userId: str
    name: str
    email: str
    university: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    major: Optional[str] = None
    academicYear: Optional[str] = None
    graduationYear: Optional[str] = None
    gpa: Optional[float] = None
    targetRole: Optional[str] = None
    isActive: bool = True
    profileStrength: int = 0
    verifiedProfilePercent: int = 0
    skills: List[Dict[str, Any]] = []
    interests: List[str] = []
    projects: List[Dict[str, Any]] = []
    applications: List[Dict[str, Any]] = []
    createdAt: Optional[str] = None


class AdminUserStatusUpdate(BaseModel):
    isActive: bool


class AdminOpportunityAction(BaseModel):
    reason: Optional[str] = None


class AdminAnalyticsResponse(BaseModel):
    opportunityDistribution: Dict[str, int]
    modeDistribution: Dict[str, int]
    categoryPopularity: List[Dict[str, Any]]
    applicationsTotal: int
    applicationsByStatus: Dict[str, int]
    applicationOutcomes: Dict[str, Any]
    studentSkillTrends: Dict[str, Any]
    matchPrecision: Dict[str, Any]

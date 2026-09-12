from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import EligibilityStatus, OpportunityCategory, WorkMode, OpportunityStatus


class MatchBreakdownSchema(BaseModel):
    skillsScore: int = 0
    skillsTotal: int = 40
    educationScore: int = 0
    educationTotal: int = 20
    interestsScore: int = 0
    interestsTotal: int = 20
    experienceScore: int = 0
    experienceTotal: int = 20
    skillsFitPercent: Optional[int] = None
    academicCriteriaPercent: Optional[int] = None
    experienceLevelPercent: Optional[int] = None


class OpportunityBase(BaseModel):
    title: str
    organization: str
    organizationLogoText: str = "ORG"
    organizationSubtext: Optional[str] = None
    category: OpportunityCategory
    categoryLabel: str = ""
    domain: str
    location: str
    mode: WorkMode = WorkMode.REMOTE
    work_mode: Optional[str] = None
    compensation: Optional[str] = None
    deadline: str
    deadlineDaysRemaining: Optional[int] = None
    postedAgo: str = "Recently"
    duration: Optional[str] = None
    cohortSize: Optional[str] = None
    description: str

    # 19 Required Fields - snake_case
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    eligibility_requirements: Optional[str] = None
    degree_requirements: List[str] = []
    branch_requirements: List[str] = []
    academic_year_requirements: List[str] = []
    experience_requirements: Optional[str] = None
    application_url: Optional[str] = None
    verified_status: Optional[bool] = None

    # camelCase versions for frontend
    requiredSkills: List[str] = []
    preferredSkills: List[str] = []
    eligibilityRequirements: Optional[str] = None
    degreeRequirements: List[str] = []
    branchRequirements: List[str] = []
    academicYearRequirements: List[str] = []
    experienceRequirements: Optional[str] = None
    applicationUrl: Optional[str] = None

    # Stitch UI fields
    keyResponsibilities: List[str] = []
    requirements: Optional[Any] = None
    stages: Optional[List[Any]] = None
    matchScore: int = 0
    matchBreakdown: Optional[Dict[str, Any]] = None
    matchedSkills: List[str] = []
    missingSkills: List[str] = []
    verified: bool = False
    eligibilityStatus: EligibilityStatus = EligibilityStatus.ELIGIBLE
    eligibilityNote: str = ""
    verifiedBy: Optional[str] = None
    featured: bool = False
    imageBanner: Optional[str] = None
    status: OpportunityStatus = OpportunityStatus.UNMARKED


class OpportunityCreate(BaseModel):
    title: str
    organization: str
    organizationLogoText: Optional[str] = None
    organizationSubtext: Optional[str] = None
    category: OpportunityCategory
    categoryLabel: Optional[str] = None
    domain: str = "General"
    location: str = "Remote"
    mode: Optional[WorkMode] = None
    work_mode: Optional[str] = None
    compensation: Optional[str] = None
    deadline: str
    deadlineDaysRemaining: Optional[int] = None
    postedAgo: Optional[str] = None
    duration: Optional[str] = None
    cohortSize: Optional[str] = None
    description: str

    # Accept either camelCase or snake_case
    required_skills: Optional[List[str]] = None
    requiredSkills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    eligibility_requirements: Optional[str] = None
    eligibilityRequirements: Optional[str] = None
    degree_requirements: Optional[List[str]] = None
    degreeRequirements: Optional[List[str]] = None
    branch_requirements: Optional[List[str]] = None
    branchRequirements: Optional[List[str]] = None
    academic_year_requirements: Optional[List[str]] = None
    academicYearRequirements: Optional[List[str]] = None
    experience_requirements: Optional[str] = None
    experienceRequirements: Optional[str] = None
    application_url: Optional[str] = None
    applicationUrl: Optional[str] = None

    keyResponsibilities: Optional[List[str]] = None
    key_responsibilities: Optional[List[str]] = None
    requirements: Optional[Any] = None
    stages: Optional[List[Any]] = None
    matchScore: Optional[int] = None
    match_score: Optional[int] = None
    matchBreakdown: Optional[Dict[str, Any]] = None
    match_breakdown: Optional[Dict[str, Any]] = None
    matchedSkills: Optional[List[str]] = None
    matched_skills: Optional[List[str]] = None
    missingSkills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    verified: Optional[bool] = False
    eligibilityStatus: Optional[EligibilityStatus] = None
    eligibility_status: Optional[EligibilityStatus] = None
    eligibilityNote: Optional[str] = None
    eligibility_note: Optional[str] = None
    verifiedBy: Optional[str] = None
    verified_by: Optional[str] = None
    featured: Optional[bool] = False
    imageBanner: Optional[str] = None
    image_banner: Optional[str] = None
    status: Optional[OpportunityStatus] = None


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    organizationLogoText: Optional[str] = None
    organizationSubtext: Optional[str] = None
    category: Optional[OpportunityCategory] = None
    categoryLabel: Optional[str] = None
    domain: Optional[str] = None
    location: Optional[str] = None
    mode: Optional[WorkMode] = None
    work_mode: Optional[str] = None
    compensation: Optional[str] = None
    deadline: Optional[str] = None
    deadlineDaysRemaining: Optional[int] = None
    postedAgo: Optional[str] = None
    duration: Optional[str] = None
    cohortSize: Optional[str] = None
    description: Optional[str] = None

    required_skills: Optional[List[str]] = None
    requiredSkills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    eligibility_requirements: Optional[str] = None
    eligibilityRequirements: Optional[str] = None
    degree_requirements: Optional[List[str]] = None
    degreeRequirements: Optional[List[str]] = None
    branch_requirements: Optional[List[str]] = None
    branchRequirements: Optional[List[str]] = None
    academic_year_requirements: Optional[List[str]] = None
    academicYearRequirements: Optional[List[str]] = None
    experience_requirements: Optional[str] = None
    experienceRequirements: Optional[str] = None
    application_url: Optional[str] = None
    applicationUrl: Optional[str] = None

    keyResponsibilities: Optional[List[str]] = None
    key_responsibilities: Optional[List[str]] = None
    requirements: Optional[Dict[str, Any]] = None
    stages: Optional[List[Dict[str, Any]]] = None
    matchScore: Optional[int] = None
    match_score: Optional[int] = None
    matchBreakdown: Optional[Dict[str, Any]] = None
    match_breakdown: Optional[Dict[str, Any]] = None
    matchedSkills: Optional[List[str]] = None
    matched_skills: Optional[List[str]] = None
    missingSkills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    verified: Optional[bool] = None
    eligibilityStatus: Optional[EligibilityStatus] = None
    eligibility_status: Optional[EligibilityStatus] = None
    eligibilityNote: Optional[str] = None
    eligibility_note: Optional[str] = None
    verifiedBy: Optional[str] = None
    verified_by: Optional[str] = None
    featured: Optional[bool] = None
    imageBanner: Optional[str] = None
    image_banner: Optional[str] = None
    status: Optional[OpportunityStatus] = None


class OpportunityResponse(OpportunityBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedOpportunityResponse(BaseModel):
    items: List[OpportunityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MatchResultResponse(BaseModel):
    opportunityId: str
    opportunity_id: Optional[str] = None
    overallMatchScore: int
    overall_match_score: Optional[int] = None
    skillScore: float
    skill_score: Optional[float] = None
    semanticSimilarity: float
    semantic_similarity: Optional[float] = None
    educationScore: float
    education_score: Optional[float] = None
    interestScore: float
    interest_score: Optional[float] = None
    experienceScore: float
    experience_score: Optional[float] = None
    preferenceScore: float
    preference_score: Optional[float] = None
    matchedSkills: List[str] = []
    matched_skills: Optional[List[str]] = None
    missingSkills: List[str] = []
    missing_skills: Optional[List[str]] = None
    partialSkills: List[Dict[str, Any]] = []
    partial_skills: Optional[List[Dict[str, Any]]] = None
    eligibilityStatus: EligibilityStatus
    eligibility_status: Optional[EligibilityStatus] = None
    eligibilityNote: str = ""
    eligibility_note: Optional[str] = None
    matchBreakdown: Dict[str, Any] = {}
    match_breakdown: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class MatchExplanationResponse(BaseModel):
    opportunityId: str
    opportunity_id: Optional[str] = None
    compatibilityLabel: str
    compatibility_label: Optional[str] = None
    summary: str
    reasons: List[str] = []
    strongMatches: List[Dict[str, Any]] = []
    strong_matches: Optional[List[Dict[str, Any]]] = None
    missingSkills: List[str] = []
    missing_skills: Optional[List[str]] = None
    recommendedAction: Optional[Dict[str, Any]] = None
    recommended_action: Optional[Dict[str, Any]] = None
    matchScore: int = 0
    match_score: Optional[int] = None
    matchBreakdown: Dict[str, Any] = {}
    match_breakdown: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

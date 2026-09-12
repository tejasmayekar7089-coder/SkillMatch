from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- SKILL SCHEMAS ---
class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Skill name")
    proficiency: str = Field(default="Beginner", description="Proficiency level (e.g. Beginner, Intermediate, Advanced, Essential)")
    category: Optional[str] = None
    experience_level: Optional[str] = None


class SkillUpdate(BaseModel):
    proficiency: Optional[str] = None
    experience_level: Optional[str] = None
    progress_percent: Optional[int] = None


class SkillResponse(BaseModel):
    id: str
    skill_id: str
    name: str
    normalized_name: str
    proficiency: str
    level: str
    category: Optional[str] = None
    experience_level: Optional[str] = None
    verified: bool = False
    verifiedVia: Optional[str] = None
    progress_percent: int = 0

    model_config = ConfigDict(from_attributes=True)


# --- INTEREST SCHEMAS ---
class InterestCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Interest name")
    category: Optional[str] = None


class InterestResponse(BaseModel):
    id: str
    interest_id: str
    name: str
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- PROJECT SCHEMAS ---
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    technologies: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    project_url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    title: str
    name: str
    description: str
    technologies: List[str] = []
    skills: List[str] = []
    project_url: Optional[str] = None
    link: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    verified: bool = False

    model_config = ConfigDict(from_attributes=True)


# --- CERTIFICATION SCHEMAS ---
class CertificationCreate(BaseModel):
    name: str = Field(..., min_length=1)
    issuing_organization: str = Field(..., min_length=1)
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationUpdate(BaseModel):
    name: Optional[str] = None
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class CertificationResponse(BaseModel):
    id: str
    name: str
    issuing_organization: str
    issuer: str
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    verified: bool = False

    model_config = ConfigDict(from_attributes=True)


# --- STUDENT PROFILE SCHEMAS ---
class StudentProfileBase(BaseModel):
    college: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    major: Optional[str] = None
    academic_year: Optional[str] = None
    year: Optional[str] = None
    graduation_year: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[float] = None
    preferred_domains: List[str] = []
    preferred_locations: List[str] = []
    preferred_work_mode: Optional[str] = None
    experience: Optional[str] = None
    bio: Optional[str] = None
    summary: Optional[str] = None
    target_role: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    college: Optional[str] = None
    university: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    major: Optional[str] = None
    academic_year: Optional[str] = None
    year: Optional[str] = None
    graduation_year: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[float] = None
    preferred_domains: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_work_mode: Optional[str] = None
    experience: Optional[str] = None
    bio: Optional[str] = None
    summary: Optional[str] = None
    target_role: Optional[str] = None


class StudentProfileResponse(StudentProfileBase):
    id: str
    user_id: str
    full_name: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    avatarUrl: Optional[str] = None
    verified_profile_percent: int = 0
    profile_strength: int = 0
    match_confidence: int = 0
    skills: List[SkillResponse] = []
    interests: List[InterestResponse] = []
    projects: List[ProjectResponse] = []
    certifications: List[CertificationResponse] = []

    model_config = ConfigDict(from_attributes=True)

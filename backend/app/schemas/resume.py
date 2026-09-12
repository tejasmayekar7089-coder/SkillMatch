from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ResumeExtractedData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    academic_year: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[float] = None
    summary: Optional[str] = None
    skills: List[str] = []
    projects: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []


class ResumeUploadResponse(BaseModel):
    success: bool = True
    filename: str
    extracted_data: ResumeExtractedData
    raw_text_preview: str = ""


class ProjectConfirmItem(BaseModel):
    title: str
    description: Optional[str] = ""
    technologies: List[str] = []
    skills: List[str] = []
    project_url: Optional[str] = None
    github_url: Optional[str] = None


class CertificationConfirmItem(BaseModel):
    name: str
    issuing_organization: Optional[str] = "Verified Issuer"
    issue_date: Optional[str] = "Verified"
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None


class ResumeConfirmRequest(BaseModel):
    name: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    academic_year: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[float] = None
    summary: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[ProjectConfirmItem]] = None
    certifications: Optional[List[CertificationConfirmItem]] = None


class ResumeConfirmResponse(BaseModel):
    success: bool = True
    message: str
    updated_fields: List[str] = []
    skills_added: int = 0
    projects_added: int = 0
    certifications_added: int = 0

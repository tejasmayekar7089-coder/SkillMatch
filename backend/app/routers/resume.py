from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.certification import Certification
from app.models.project import Project
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.resume import (
    ResumeConfirmRequest,
    ResumeConfirmResponse,
    ResumeExtractedData,
    ResumeUploadResponse,
)
from app.services.resume_parser import ResumeParserService
from app.services.skill_normalizer import SkillNormalizationService

router = APIRouter(prefix="/resume", tags=["Resume Intelligence"])


@router.get("/status")
def get_resume_service_status():
    """Health and readiness check for resume processing service."""
    return {"status": "available", "supported_formats": ["pdf"], "intelligence": "active"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
):
    """
    Uploads and analyzes a PDF resume.
    Extracts text and structured information (name, email, education, degree, branch, skills, projects, experience, certifications).
    NOTE: Extracted data is returned for user preview and DOES NOT overwrite the student's profile.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF resumes are supported.",
        )

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not read uploaded file: {str(e)}",
        )

    if not content or len(content) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF file is empty or corrupted.",
        )

    try:
        parsed_data = ResumeParserService.parse_resume_bytes(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to extract structured resume content: {str(e)}",
        )

    extracted_model = ResumeExtractedData(
        name=parsed_data.get("name"),
        email=parsed_data.get("email"),
        phone=parsed_data.get("phone"),
        college=parsed_data.get("college"),
        degree=parsed_data.get("degree"),
        branch=parsed_data.get("branch"),
        academic_year=parsed_data.get("academic_year"),
        graduation_year=parsed_data.get("graduation_year"),
        gpa=parsed_data.get("gpa"),
        summary=parsed_data.get("summary"),
        skills=parsed_data.get("skills", []),
        projects=parsed_data.get("projects", []),
        experience=parsed_data.get("experience", []),
        certifications=parsed_data.get("certifications", []),
    )

    return ResumeUploadResponse(
        success=True,
        filename=file.filename,
        extracted_data=extracted_model,
        raw_text_preview=parsed_data.get("raw_text_preview", ""),
    )


@router.post("/confirm", response_model=ResumeConfirmResponse)
def confirm_resume(
    request: ResumeConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Applies only user-confirmed resume fields to the authenticated student's profile.
    Prevents duplicate skills and normalizes all skill inputs.
    """
    updated_fields: List[str] = []

    # 1. Update User Full Name if confirmed
    if request.name and request.name.strip():
        current_user.full_name = request.name.strip()
        updated_fields.append("name")

    # 2. Retrieve or create linked StudentProfile
    profile = current_user.student_profile
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()

    # 3. Update confirmed Profile Fields
    if request.college and request.college.strip():
        profile.college = request.college.strip()
        updated_fields.append("college")
    if request.degree and request.degree.strip():
        profile.degree = request.degree.strip()
        updated_fields.append("degree")
    if request.branch and request.branch.strip():
        profile.branch = request.branch.strip()
        updated_fields.append("branch")
    if request.academic_year and request.academic_year.strip():
        profile.academic_year = request.academic_year.strip()
        updated_fields.append("academic_year")
    if request.graduation_year and request.graduation_year.strip():
        profile.graduation_year = request.graduation_year.strip()
        updated_fields.append("graduation_year")
    if request.gpa is not None and request.gpa > 0:
        profile.gpa = request.gpa
        updated_fields.append("gpa")
    if request.summary and request.summary.strip():
        profile.summary = request.summary.strip()
        profile.bio = request.summary.strip()
        updated_fields.append("summary")
    if request.experience and request.experience.strip():
        profile.experience = request.experience.strip()
        updated_fields.append("experience")

    # 4. Add Confirmed Skills (Normalized, duplicate prevention enforced)
    skills_added = 0
    if request.skills:
        for raw_skill in request.skills:
            if not raw_skill or not raw_skill.strip():
                continue
            student_skill, is_new = SkillNormalizationService.add_skill_to_student(
                db=db,
                student_profile_id=profile.id,
                raw_name=raw_skill.strip(),
                proficiency="Intermediate",
                verified=True,
                verified_via="Resume Intelligence Audit",
            )
            if is_new:
                skills_added += 1

    # 5. Add Confirmed Projects
    projects_added = 0
    if request.projects:
        for proj in request.projects:
            if not proj.title or not proj.title.strip():
                continue
            # Avoid duplicate project names for this student
            existing_proj = (
                db.query(Project)
                .filter(Project.student_profile_id == profile.id, Project.name.ilike(proj.title.strip()))
                .first()
            )
            if not existing_proj:
                new_project = Project(
                    student_profile_id=profile.id,
                    name=proj.title.strip(),
                    title=proj.title.strip(),
                    description=proj.description or f"Project developed by {current_user.full_name}.",
                    technologies=proj.technologies or proj.skills or [],
                    skills=proj.skills or proj.technologies or [],
                    project_url=proj.project_url,
                    github_url=proj.github_url,
                    verified=True,
                )
                db.add(new_project)
                projects_added += 1

    # 6. Add Confirmed Certifications
    certs_added = 0
    if request.certifications:
        for cert in request.certifications:
            if not cert.name or not cert.name.strip():
                continue
            existing_cert = (
                db.query(Certification)
                .filter(Certification.student_profile_id == profile.id, Certification.name.ilike(cert.name.strip()))
                .first()
            )
            if not existing_cert:
                new_cert = Certification(
                    student_profile_id=profile.id,
                    name=cert.name.strip(),
                    issuer=cert.issuing_organization or "Verified Issuer",
                    issuing_organization=cert.issuing_organization or "Verified Issuer",
                    issue_date=cert.issue_date or "Verified",
                    credential_id=cert.credential_id,
                    credential_url=cert.credential_url,
                    verified=True,
                )
                db.add(new_cert)
                certs_added += 1

    db.commit()

    return ResumeConfirmResponse(
        success=True,
        message="Resume data successfully confirmed and applied to student profile.",
        updated_fields=updated_fields,
        skills_added=skills_added,
        projects_added=projects_added,
        certifications_added=certs_added,
    )

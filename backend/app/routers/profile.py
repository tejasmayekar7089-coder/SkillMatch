from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.models.certification import Certification
from app.models.interest import Interest, StudentInterest
from app.models.project import Project
from app.models.skill import Skill, StudentSkill
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.profile import (
    CertificationCreate,
    CertificationResponse,
    CertificationUpdate,
    InterestCreate,
    InterestResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    StudentProfileResponse,
    StudentProfileUpdate,
)

router = APIRouter(prefix="/profile", tags=["Profile"])


def get_or_create_student_profile(user: User, db: Session) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=user.id,
            degree="B.Tech / B.E.",
            major="Computer Science",
            branch="Computer Science",
            year="3rd Year",
            academic_year="3rd Year",
            verified_profile_percent=85,
            profile_strength=80,
            match_confidence=88,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def serialize_profile(profile: StudentProfile, user: User) -> StudentProfileResponse:
    skills_resp = [
        SkillResponse(
            id=ss.id,
            skill_id=ss.skill_id,
            name=ss.skill.name,
            normalized_name=ss.skill.normalized_name,
            proficiency=ss.proficiency,
            level=str(ss.level.value if hasattr(ss.level, "value") else ss.level),
            category=ss.skill.category,
            experience_level=ss.experience_level,
            verified=ss.verified,
            verifiedVia=ss.verified_via,
            progress_percent=ss.progress_percent,
        )
        for ss in profile.skills
    ]

    interests_resp = [
        InterestResponse(
            id=si.id,
            interest_id=si.interest_id,
            name=si.interest.name,
            category=si.interest.category,
        )
        for si in profile.interests
    ]

    projects_resp = [
        ProjectResponse(
            id=p.id,
            title=p.title,
            name=p.name or p.title,
            description=p.description,
            technologies=p.technologies or [],
            skills=p.skills or [],
            project_url=p.project_url or p.link,
            link=p.link or p.project_url,
            github_url=p.github_url,
            start_date=p.start_date,
            end_date=p.end_date,
            verified=p.verified,
        )
        for p in profile.projects
    ]

    certs_resp = [
        CertificationResponse(
            id=c.id,
            name=c.name,
            issuing_organization=c.issuing_organization or c.issuer,
            issuer=c.issuer or c.issuing_organization,
            issue_date=c.issue_date,
            credential_id=c.credential_id,
            credential_url=c.credential_url,
            verified=c.verified,
        )
        for c in profile.certifications
    ]

    from urllib.parse import quote_plus
    avatar = user.avatar_url
    if not avatar or "aida-public/AB6AXuDJbu" in avatar:
        safe_name = quote_plus(user.full_name.strip()) if user.full_name else "User"
        avatar = f"https://ui-avatars.com/api/?name={safe_name}&background=0284c7&color=fff&size=128&bold=true"

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=user.full_name,
        name=user.full_name,
        email=user.email,
        avatar_url=avatar,
        avatarUrl=avatar,
        college=profile.college or profile.university,
        university=profile.university or profile.college,
        degree=profile.degree,
        branch=profile.branch or profile.major,
        major=profile.major or profile.branch,
        academic_year=profile.academic_year or profile.year,
        year=profile.year or profile.academic_year,
        graduation_year=profile.graduation_year or profile.graduation_date,
        graduation_date=profile.graduation_date or profile.graduation_year,
        gpa=profile.gpa,
        preferred_domains=profile.preferred_domains or [],
        preferred_locations=profile.preferred_locations or [],
        preferred_work_mode=profile.preferred_work_mode,
        experience=profile.experience,
        bio=profile.bio or profile.summary,
        summary=profile.summary or profile.bio,
        target_role=profile.target_role,
        verified_profile_percent=profile.verified_profile_percent,
        profile_strength=profile.profile_strength,
        match_confidence=profile.match_confidence,
        skills=skills_resp,
        interests=interests_resp,
        projects=projects_resp,
        certifications=certs_resp,
    )


# ==========================================
# 1. PROFILE ENDPOINTS
# ==========================================
@router.get("", response_model=StudentProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    return serialize_profile(profile, current_user)


@router.put("", response_model=StudentProfileResponse)
def update_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    update_data = profile_in.model_dump(exclude_unset=True)

    # Sync user fields if provided
    if "full_name" in update_data and update_data["full_name"]:
        current_user.full_name = update_data.pop("full_name")
    if "avatar_url" in update_data and update_data["avatar_url"]:
        current_user.avatar_url = update_data.pop("avatar_url")
    if "email" in update_data and update_data["email"]:
        new_email = update_data.pop("email").lower()
        if new_email != current_user.email:
            existing = db.query(User).filter(User.email == new_email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email is already in use")
            current_user.email = new_email

    # Keep aliases synchronized
    if "college" in update_data and not update_data.get("university"):
        update_data["university"] = update_data["college"]
    if "university" in update_data and not update_data.get("college"):
        update_data["college"] = update_data["university"]

    if "branch" in update_data and not update_data.get("major"):
        update_data["major"] = update_data["branch"]
    if "major" in update_data and not update_data.get("branch"):
        update_data["branch"] = update_data["major"]

    if "academic_year" in update_data and not update_data.get("year"):
        update_data["year"] = update_data["academic_year"]
    if "year" in update_data and not update_data.get("academic_year"):
        update_data["academic_year"] = update_data["year"]

    if "graduation_year" in update_data and not update_data.get("graduation_date"):
        update_data["graduation_date"] = update_data["graduation_year"]
    if "graduation_date" in update_data and not update_data.get("graduation_year"):
        update_data["graduation_year"] = update_data["graduation_date"]

    if "bio" in update_data and not update_data.get("summary"):
        update_data["summary"] = update_data["bio"]
    if "summary" in update_data and not update_data.get("bio"):
        update_data["bio"] = update_data["summary"]

    for key, value in update_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)
    return serialize_profile(profile, current_user)


# ==========================================
# 2. SKILLS ENDPOINTS
# ==========================================
@router.get("/skills", response_model=List[SkillResponse])
def get_student_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    return [
        SkillResponse(
            id=ss.id,
            skill_id=ss.skill_id,
            name=ss.skill.name,
            normalized_name=ss.skill.normalized_name,
            proficiency=ss.proficiency,
            level=str(ss.level.value if hasattr(ss.level, "value") else ss.level),
            category=ss.skill.category,
            experience_level=ss.experience_level,
            verified=ss.verified,
            verifiedVia=ss.verified_via,
            progress_percent=ss.progress_percent,
        )
        for ss in profile.skills
    ]


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def add_student_skill(
    skill_in: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    name_clean = skill_in.name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Skill name cannot be empty")

    norm_name = name_clean.lower()

    # Find or create skill in master dictionary
    master_skill = db.query(Skill).filter(Skill.normalized_name == norm_name).first()
    if not master_skill:
        master_skill = Skill(
            name=name_clean,
            normalized_name=norm_name,
            category=skill_in.category or "General",
        )
        db.add(master_skill)
        db.flush()

    # Check if student already has this skill (prevent duplicate)
    existing_ss = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_profile_id == profile.id,
            StudentSkill.skill_id == master_skill.id,
        )
        .first()
    )
    if existing_ss:
        # Update existing proficiency instead of duplicating
        existing_ss.proficiency = skill_in.proficiency
        if skill_in.experience_level:
            existing_ss.experience_level = skill_in.experience_level
        db.commit()
        db.refresh(existing_ss)
        return SkillResponse(
            id=existing_ss.id,
            skill_id=master_skill.id,
            name=master_skill.name,
            normalized_name=master_skill.normalized_name,
            proficiency=existing_ss.proficiency,
            level=str(existing_ss.level.value if hasattr(existing_ss.level, "value") else existing_ss.level),
            category=master_skill.category,
            experience_level=existing_ss.experience_level,
            verified=existing_ss.verified,
            verifiedVia=existing_ss.verified_via,
            progress_percent=existing_ss.progress_percent,
        )

    # Create new student skill
    student_skill = StudentSkill(
        student_profile_id=profile.id,
        skill_id=master_skill.id,
        proficiency=skill_in.proficiency,
        experience_level=skill_in.experience_level,
        progress_percent=75,
    )
    db.add(student_skill)
    db.commit()
    db.refresh(student_skill)

    return SkillResponse(
        id=student_skill.id,
        skill_id=master_skill.id,
        name=master_skill.name,
        normalized_name=master_skill.normalized_name,
        proficiency=student_skill.proficiency,
        level=str(student_skill.level.value if hasattr(student_skill.level, "value") else student_skill.level),
        category=master_skill.category,
        experience_level=student_skill.experience_level,
        verified=student_skill.verified,
        verifiedVia=student_skill.verified_via,
        progress_percent=student_skill.progress_percent,
    )


@router.put("/skills/{skill_id}", response_model=SkillResponse)
def update_student_skill(
    skill_id: str,
    skill_in: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    # Search by either student_skill.id or student_skill.skill_id
    student_skill = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_profile_id == profile.id,
            (StudentSkill.id == skill_id) | (StudentSkill.skill_id == skill_id),
        )
        .first()
    )
    if not student_skill:
        raise HTTPException(status_code=404, detail="Skill not found in your profile")

    if skill_in.proficiency:
        student_skill.proficiency = skill_in.proficiency
    if skill_in.experience_level is not None:
        student_skill.experience_level = skill_in.experience_level
    if skill_in.progress_percent is not None:
        student_skill.progress_percent = skill_in.progress_percent

    db.commit()
    db.refresh(student_skill)

    return SkillResponse(
        id=student_skill.id,
        skill_id=student_skill.skill_id,
        name=student_skill.skill.name,
        normalized_name=student_skill.skill.normalized_name,
        proficiency=student_skill.proficiency,
        level=str(student_skill.level.value if hasattr(student_skill.level, "value") else student_skill.level),
        category=student_skill.skill.category,
        experience_level=student_skill.experience_level,
        verified=student_skill.verified,
        verifiedVia=student_skill.verified_via,
        progress_percent=student_skill.progress_percent,
    )


@router.delete("/skills/{skill_id}")
def delete_student_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    student_skill = (
        db.query(StudentSkill)
        .filter(
            StudentSkill.student_profile_id == profile.id,
            (StudentSkill.id == skill_id) | (StudentSkill.skill_id == skill_id),
        )
        .first()
    )
    if not student_skill:
        raise HTTPException(status_code=404, detail="Skill not found in your profile")

    db.delete(student_skill)
    db.commit()
    return {"status": "ok", "message": "Skill removed from profile"}


# ==========================================
# 3. INTERESTS ENDPOINTS
# ==========================================
@router.get("/interests", response_model=List[InterestResponse])
def get_student_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    return [
        InterestResponse(
            id=si.id,
            interest_id=si.interest_id,
            name=si.interest.name,
            category=si.interest.category,
        )
        for si in profile.interests
    ]


@router.post("/interests", response_model=InterestResponse, status_code=status.HTTP_201_CREATED)
def add_student_interest(
    interest_in: InterestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    name_clean = interest_in.name.strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Interest name cannot be empty")

    master_interest = db.query(Interest).filter(Interest.name.ilike(name_clean)).first()
    if not master_interest:
        master_interest = Interest(name=name_clean, category=interest_in.category or "General")
        db.add(master_interest)
        db.flush()

    existing_si = (
        db.query(StudentInterest)
        .filter(
            StudentInterest.student_profile_id == profile.id,
            StudentInterest.interest_id == master_interest.id,
        )
        .first()
    )
    if existing_si:
        return InterestResponse(
            id=existing_si.id,
            interest_id=master_interest.id,
            name=master_interest.name,
            category=master_interest.category,
        )

    student_interest = StudentInterest(
        student_profile_id=profile.id,
        interest_id=master_interest.id,
    )
    db.add(student_interest)
    db.commit()
    db.refresh(student_interest)

    return InterestResponse(
        id=student_interest.id,
        interest_id=master_interest.id,
        name=master_interest.name,
        category=master_interest.category,
    )


@router.delete("/interests/{interest_id}")
def delete_student_interest(
    interest_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    student_interest = (
        db.query(StudentInterest)
        .filter(
            StudentInterest.student_profile_id == profile.id,
            (StudentInterest.id == interest_id) | (StudentInterest.interest_id == interest_id),
        )
        .first()
    )
    if not student_interest:
        raise HTTPException(status_code=404, detail="Interest not found in your profile")

    db.delete(student_interest)
    db.commit()
    return {"status": "ok", "message": "Interest removed from profile"}


# ==========================================
# 4. PROJECTS ENDPOINTS
# ==========================================
@router.get("/projects", response_model=List[ProjectResponse])
def get_student_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    return [
        ProjectResponse(
            id=p.id,
            title=p.title,
            name=p.name or p.title,
            description=p.description,
            technologies=p.technologies or [],
            skills=p.skills or [],
            project_url=p.project_url or p.link,
            link=p.link or p.project_url,
            github_url=p.github_url,
            start_date=p.start_date,
            end_date=p.end_date,
            verified=p.verified,
        )
        for p in profile.projects
    ]


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_student_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    project = Project(
        student_profile_id=profile.id,
        title=project_in.title,
        name=project_in.title,
        description=project_in.description,
        technologies=project_in.technologies,
        skills=project_in.skills or project_in.technologies,
        project_url=project_in.project_url,
        link=project_in.project_url,
        github_url=project_in.github_url,
        start_date=project_in.start_date,
        end_date=project_in.end_date,
        verified=False,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        name=project.name,
        description=project.description,
        technologies=project.technologies,
        skills=project.skills,
        project_url=project.project_url,
        link=project.link,
        github_url=project.github_url,
        start_date=project.start_date,
        end_date=project.end_date,
        verified=project.verified,
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project_by_id(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.student_profile_id == profile.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=project.id,
        title=project.title,
        name=project.name,
        description=project.description,
        technologies=project.technologies,
        skills=project.skills,
        project_url=project.project_url,
        link=project.link,
        github_url=project.github_url,
        start_date=project.start_date,
        end_date=project.end_date,
        verified=project.verified,
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_student_project(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.student_profile_id == profile.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_in.model_dump(exclude_unset=True)
    if "title" in update_data:
        update_data["name"] = update_data["title"]
    if "project_url" in update_data:
        update_data["link"] = update_data["project_url"]

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        title=project.title,
        name=project.name,
        description=project.description,
        technologies=project.technologies,
        skills=project.skills,
        project_url=project.project_url,
        link=project.link,
        github_url=project.github_url,
        start_date=project.start_date,
        end_date=project.end_date,
        verified=project.verified,
    )


@router.delete("/projects/{project_id}")
def delete_student_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.student_profile_id == profile.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"status": "ok", "message": "Project removed from profile"}


# ==========================================
# 5. CERTIFICATIONS ENDPOINTS
# ==========================================
@router.get("/certifications", response_model=List[CertificationResponse])
def get_student_certifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    return [
        CertificationResponse(
            id=c.id,
            name=c.name,
            issuing_organization=c.issuing_organization or c.issuer,
            issuer=c.issuer or c.issuing_organization,
            issue_date=c.issue_date,
            credential_id=c.credential_id,
            credential_url=c.credential_url,
            verified=c.verified,
        )
        for c in profile.certifications
    ]


@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def add_student_certification(
    cert_in: CertificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    cert = Certification(
        student_profile_id=profile.id,
        name=cert_in.name,
        issuing_organization=cert_in.issuing_organization,
        issuer=cert_in.issuing_organization,
        issue_date=cert_in.issue_date,
        credential_id=cert_in.credential_id,
        credential_url=cert_in.credential_url,
        verified=False,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return CertificationResponse(
        id=cert.id,
        name=cert.name,
        issuing_organization=cert.issuing_organization,
        issuer=cert.issuer,
        issue_date=cert.issue_date,
        credential_id=cert.credential_id,
        credential_url=cert.credential_url,
        verified=cert.verified,
    )


@router.get("/certifications/{certification_id}", response_model=CertificationResponse)
def get_certification_by_id(
    certification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    cert = (
        db.query(Certification)
        .filter(Certification.id == certification_id, Certification.student_profile_id == profile.id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    return CertificationResponse(
        id=cert.id,
        name=cert.name,
        issuing_organization=cert.issuing_organization,
        issuer=cert.issuer,
        issue_date=cert.issue_date,
        credential_id=cert.credential_id,
        credential_url=cert.credential_url,
        verified=cert.verified,
    )


@router.put("/certifications/{certification_id}", response_model=CertificationResponse)
def update_student_certification(
    certification_id: str,
    cert_in: CertificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    cert = (
        db.query(Certification)
        .filter(Certification.id == certification_id, Certification.student_profile_id == profile.id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    update_data = cert_in.model_dump(exclude_unset=True)
    if "issuing_organization" in update_data:
        update_data["issuer"] = update_data["issuing_organization"]

    for key, value in update_data.items():
        setattr(cert, key, value)

    db.commit()
    db.refresh(cert)

    return CertificationResponse(
        id=cert.id,
        name=cert.name,
        issuing_organization=cert.issuing_organization,
        issuer=cert.issuer,
        issue_date=cert.issue_date,
        credential_id=cert.credential_id,
        credential_url=cert.credential_url,
        verified=cert.verified,
    )


@router.delete("/certifications/{certification_id}")
def delete_student_certification(
    certification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_student_profile(current_user, db)
    cert = (
        db.query(Certification)
        .filter(Certification.id == certification_id, Certification.student_profile_id == profile.id)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    db.delete(cert)
    db.commit()
    return {"status": "ok", "message": "Certification removed from profile"}

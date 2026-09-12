from app.models import (
    Application,
    ApplicationStatus,
    Certification,
    EligibilityStatus,
    Interest,
    Notification,
    NotificationType,
    Opportunity,
    OpportunityCategory,
    OpportunitySkill,
    Project,
    Recommendation,
    SavedOpportunity,
    Skill,
    SkillGap,
    SkillLevel,
    StudentInterest,
    StudentProfile,
    StudentSkill,
    User,
    UserRole,
    WorkMode,
)


def test_model_imports():
    """Verify all 15 core models and key enums are importable and registered on Base."""
    assert User.__tablename__ == "users"
    assert StudentProfile.__tablename__ == "student_profiles"
    assert Skill.__tablename__ == "skills"
    assert StudentSkill.__tablename__ == "student_skills"
    assert Interest.__tablename__ == "interests"
    assert StudentInterest.__tablename__ == "student_interests"
    assert Project.__tablename__ == "projects"
    assert Certification.__tablename__ == "certifications"
    assert Opportunity.__tablename__ == "opportunities"
    assert OpportunitySkill.__tablename__ == "opportunity_skills"
    assert SavedOpportunity.__tablename__ == "saved_opportunities"
    assert Application.__tablename__ == "applications"
    assert Notification.__tablename__ == "notifications"
    assert Recommendation.__tablename__ == "recommendations"
    assert SkillGap.__tablename__ == "skill_gaps"


def test_opportunity_categories_supported():
    """Verify strictly all 7 required Opportunity categories exist."""
    required = {
        "INTERNSHIP",
        "HACKATHON",
        "SCHOLARSHIP",
        "COURSE",
        "PROJECT",
        "JOB",
        "SKILL_OPPORTUNITY",
    }
    actual = {c.value for c in OpportunityCategory}
    assert required == actual


def test_application_statuses_supported():
    """Verify strictly all required Application statuses exist."""
    required = {
        "SAVED",
        "PLANNING",
        "DOING",
        "PENDING",
        "APPLIED",
        "SHORTLISTED",
        "INTERVIEW",
        "SELECTED",
        "COMPLETED",
        "NOT_COMPLETED",
        "ISSUED",
        "REJECTED",
    }
    actual = {s.value for s in ApplicationStatus}
    assert required == actual


def test_user_roles_supported():
    """Verify user roles support STUDENT and ADMIN."""
    assert UserRole.STUDENT.value == "STUDENT"
    assert UserRole.ADMIN.value == "ADMIN"


def test_basic_database_relationships(db_session):
    """Verify creating records and testing primary/foreign key relationships across the system."""
    # 1. User
    user = User(
        email="alex.chen@university.edu",
        hashed_password="securehashedpassword",
        full_name="Alex Chen",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.flush()
    assert user.id is not None

    # 2. StudentProfile (1:1 with User)
    profile = StudentProfile(
        user_id=user.id,
        degree="B.S. in Computer Science",
        major="Artificial Intelligence",
        university="State Tech University",
        gpa=3.85,
        target_role="AI / ML Engineer",
    )
    db_session.add(profile)
    db_session.flush()
    assert profile.id is not None
    assert user.student_profile.id == profile.id

    # 3. Skill & StudentSkill
    skill = Skill(name="Python", category="Languages", description="Core language")
    db_session.add(skill)
    db_session.flush()

    student_skill = StudentSkill(
        student_profile_id=profile.id,
        skill_id=skill.id,
        level=SkillLevel.ADVANCED,
        verified=True,
        progress_percent=95,
    )
    db_session.add(student_skill)
    db_session.flush()
    assert len(profile.skills) == 1
    assert profile.skills[0].skill.name == "Python"

    # 4. Project
    project = Project(
        student_profile_id=profile.id,
        name="Neural Style Transfer",
        description="Deep learning project using PyTorch",
        technologies=["Python", "PyTorch", "OpenCV"],
        verified=True,
    )
    db_session.add(project)
    db_session.flush()
    assert len(profile.projects) == 1

    # 5. Certification
    cert = Certification(
        student_profile_id=profile.id,
        name="AWS Certified Developer",
        issuer="Amazon Web Services",
        verified=True,
    )
    db_session.add(cert)
    db_session.flush()
    assert len(profile.certifications) == 1

    # 6. Opportunity & OpportunitySkill (using category INTERNSHIP)
    opp = Opportunity(
        title="AI Research Intern",
        organization="OpenAI",
        category=OpportunityCategory.INTERNSHIP,
        category_label="Internship",
        domain="Artificial Intelligence",
        location="San Francisco, CA",
        mode=WorkMode.HYBRID,
        compensation="$55/hr",
        deadline="2026-04-15",
        description="Work on next-generation generative AI models.",
        key_responsibilities=["Model evaluation", "Benchmarking"],
        requirements={"technicalSkills": []},
        match_score=92,
        eligibility_status=EligibilityStatus.ELIGIBLE,
        eligibility_note="Meets all core criteria",
        verified=True,
    )
    db_session.add(opp)
    db_session.flush()
    assert opp.id is not None

    opp_skill = OpportunitySkill(
        opportunity_id=opp.id,
        skill_id=skill.id,
        level=SkillLevel.ADVANCED,
        is_required=True,
    )
    db_session.add(opp_skill)
    db_session.flush()
    assert len(opp.opportunity_skills) == 1

    # 7. SavedOpportunity
    saved = SavedOpportunity(user_id=user.id, opportunity_id=opp.id)
    db_session.add(saved)
    db_session.flush()
    assert len(user.saved_opportunities) == 1

    # 8. Application (using status APPLIED)
    application = Application(
        student_profile_id=profile.id,
        opportunity_id=opp.id,
        status=ApplicationStatus.APPLIED,
        applied_date="2026-03-01",
        current_stage="Resume Review",
        match_score=92,
    )
    db_session.add(application)
    db_session.flush()
    assert len(profile.applications) == 1
    assert profile.applications[0].opportunity.title == "AI Research Intern"

    # 9. Notification
    notif = Notification(
        user_id=user.id,
        title="Application Received",
        description="Your application to OpenAI was submitted.",
        type=NotificationType.APPLICATION,
        is_read=False,
    )
    db_session.add(notif)
    db_session.flush()
    assert len(user.notifications) == 1

    # 10. Recommendation
    rec = Recommendation(
        student_profile_id=profile.id,
        opportunity_id=opp.id,
        match_score=92,
        match_reasons=["High Python match", "Target role alignment"],
        rank=1,
    )
    db_session.add(rec)
    db_session.flush()
    assert len(profile.recommendations) == 1

    # 11. SkillGap
    gap = SkillGap(
        student_profile_id=profile.id,
        target_role="AI / ML Engineer",
        readiness_score=78,
        estimated_weeks="4-6 weeks",
        competencies_met=14,
        competencies_total=18,
    )
    db_session.add(gap)
    db_session.flush()
    assert len(profile.skill_gaps) == 1

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.application import Application
from app.models.enums import ApplicationStatus, OpportunityCategory, UserRole, WorkMode
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.services.skill_normalizer import SkillNormalizationService


def _create_users_for_admin_tests(client: TestClient, db: Session):
    # 1. Admin user
    admin_user = db.query(User).filter(User.email == "platform.admin@skillmatch.edu").first()
    if not admin_user:
        admin_user = User(
            email="platform.admin@skillmatch.edu",
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Platform Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    # 2. Student user
    student_user = db.query(User).filter(User.email == "student.rbac@test.edu").first()
    if not student_user:
        student_user = User(
            email="student.rbac@test.edu",
            hashed_password=get_password_hash("StudentPass123!"),
            full_name="RBAC Student",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

        prof = StudentProfile(
            user_id=student_user.id,
            university="National Institute of Technology",
            degree="B.Tech",
            major="Computer Science",
            gpa=3.85,
            target_role="Machine Learning Engineer",
            verified_profile_percent=85,
            profile_strength=90,
        )
        db.add(prof)
        db.commit()
        db.refresh(prof)
        SkillNormalizationService.add_skill_to_student(db, prof.id, "Python", "advanced", True, "coursework")
        SkillNormalizationService.add_skill_to_student(db, prof.id, "PyTorch", "intermediate", True, "assessment")

    # Log in both
    res_admin = client.post("/api/auth/login", json={"email": "platform.admin@skillmatch.edu", "password": "AdminPass123!"})
    assert res_admin.status_code == 200, f"Admin login failed: {res_admin.text}"
    admin_token = res_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    res_student = client.post("/api/auth/login", json={"email": "student.rbac@test.edu", "password": "StudentPass123!"})
    assert res_student.status_code == 200, f"Student login failed: {res_student.text}"
    student_token = res_student.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    return admin_headers, student_headers, admin_user, student_user


def test_rbac_authorization_enforcement(client: TestClient, db_session: Session):
    admin_headers, student_headers, admin_user, student_user = _create_users_for_admin_tests(client, db_session)

    admin_endpoints = [
        ("GET", "/api/admin/dashboard"),
        ("GET", "/api/admin/stats"),
        ("GET", "/api/admin/opportunities"),
        ("GET", "/api/admin/students"),
        ("GET", "/api/admin/analytics"),
    ]

    # 1. Unauthenticated request -> 401 Unauthorized
    for method, path in admin_endpoints:
        res = client.get(path)
        assert res.status_code == 401, f"Unauthenticated request to {path} should return 401, got {res.status_code}"

    # 2. Student request -> 403 Forbidden
    for method, path in admin_endpoints:
        res = client.get(path, headers=student_headers)
        assert res.status_code == 403, f"Student request to {path} should return 403, got {res.status_code}"
        assert "Admin privileges required" in res.json()["detail"]

    # 3. Admin request -> 200 OK
    for method, path in admin_endpoints:
        res = client.get(path, headers=admin_headers)
        assert res.status_code == 200, f"Admin request to {path} should return 200, got {res.status_code}"


def test_admin_dashboard_real_aggregated_statistics(client: TestClient, db_session: Session):
    admin_headers, student_headers, admin_user, student_user = _create_users_for_admin_tests(client, db_session)

    res = client.get("/api/admin/dashboard", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()

    # Compare values against database records directly
    expected_students = db_session.query(StudentProfile).count()
    expected_opportunities = db_session.query(Opportunity).count()
    expected_verified = db_session.query(Opportunity).filter(Opportunity.verified == True).count()
    expected_applications = db_session.query(Application).count()

    assert data["totalStudents"] == expected_students
    assert data["totalOpportunities"] == expected_opportunities
    assert data["verifiedOpportunities"] == expected_verified
    assert data["pendingOpportunities"] == (expected_opportunities - expected_verified)
    assert data["applicationCounts"] == expected_applications
    assert isinstance(data["opportunitiesByCategory"], dict)
    assert isinstance(data["applicationsByStatus"], dict)
    assert isinstance(data["recentActivity"], list)
    assert data["activeUsers"] >= 1


def test_opportunity_management_and_verification_lifecycle(client: TestClient, db_session: Session):
    admin_headers, student_headers, admin_user, student_user = _create_users_for_admin_tests(client, db_session)

    # 1. Admin creates unverified opportunity
    payload = {
        "title": "Quantum Algorithm Research Fellow",
        "organization": "Quantum AI Labs",
        "category": "INTERNSHIP",
        "domain": "Quantum Computing",
        "location": "Boston, MA",
        "workMode": "Hybrid",
        "deadline": "30 Dec 2026",
        "description": "Research fellowship in NISQ algorithms and error mitigation.",
        "requiredSkills": ["Python", "Quantum Computing", "Linear Algebra"],
        "verified": False,
    }

    res_create = client.post("/api/admin/opportunities", json=payload, headers=admin_headers)
    assert res_create.status_code == 201
    created_opp = res_create.json()
    opp_id = created_opp["id"]
    assert created_opp["verified"] is False

    # 2. Student queries opportunities -> Should NOT be visible to student
    res_student_disc = client.get("/api/opportunities", headers=student_headers)
    assert res_student_disc.status_code == 200
    student_opps = res_student_disc.json()["items"]
    assert not any(o["id"] == opp_id for o in student_opps), "Unverified opportunity should NOT be visible to student!"

    # 3. Admin queries pending opportunities -> Should be visible to admin
    res_admin_pending = client.get("/api/admin/opportunities?verified=false", headers=admin_headers)
    assert res_admin_pending.status_code == 200
    pending_list = res_admin_pending.json()
    assert any(o["id"] == opp_id for o in pending_list), "Unverified opportunity must be visible in admin queue"

    # 4. Admin verifies opportunity
    res_verify = client.patch(f"/api/admin/opportunities/{opp_id}/verify", headers=admin_headers)
    assert res_verify.status_code == 200
    assert res_verify.json()["verified"] is True

    # 5. Student queries opportunities -> Should now be VISIBLE to student!
    res_student_disc2 = client.get("/api/opportunities", headers=student_headers)
    assert res_student_disc2.status_code == 200
    student_opps2 = res_student_disc2.json()["items"]
    assert any(o["id"] == opp_id for o in student_opps2), "Verified opportunity MUST be visible to students!"

    # 6. Admin rejects opportunity
    res_reject = client.patch(f"/api/admin/opportunities/{opp_id}/reject?reason=Expired", headers=admin_headers)
    assert res_reject.status_code == 200
    assert res_reject.json()["verified"] is False

    # 7. Student queries opportunities again -> Should be REMOVED from student view!
    res_student_disc3 = client.get("/api/opportunities", headers=student_headers)
    student_opps3 = res_student_disc3.json()["items"]
    assert not any(o["id"] == opp_id for o in student_opps3), "Rejected opportunity must not be visible to students!"

    # 8. Admin deletes opportunity
    res_delete = client.delete(f"/api/admin/opportunities/{opp_id}", headers=admin_headers)
    assert res_delete.status_code == 200


def test_student_management_and_deactivation(client: TestClient, db_session: Session):
    admin_headers, student_headers, admin_user, student_user = _create_users_for_admin_tests(client, db_session)

    # 1. Admin lists students with search
    res_list = client.get("/api/admin/students?search=RBAC", headers=admin_headers)
    assert res_list.status_code == 200
    students = res_list.json()
    assert len(students) >= 1
    found_student = next(s for s in students if s["email"] == "student.rbac@test.edu")
    assert found_student["name"] == "RBAC Student"
    assert found_student["university"] == "National Institute of Technology"
    prof_id = found_student["id"]

    # 2. Admin views student detail
    res_detail = client.get(f"/api/admin/students/{prof_id}", headers=admin_headers)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["email"] == "student.rbac@test.edu"
    assert len(detail["skills"]) >= 1

    # 3. Admin views student skills
    res_skills = client.get(f"/api/admin/students/{prof_id}/skills", headers=admin_headers)
    assert res_skills.status_code == 200
    skills = res_skills.json()
    assert any(s["name"] == "Python" for s in skills)

    # 4. Admin deactivates student
    res_deactivate = client.patch(
        f"/api/admin/students/{prof_id}/status",
        json={"isActive": False},
        headers=admin_headers,
    )
    assert res_deactivate.status_code == 200
    assert res_deactivate.json()["isActive"] is False

    # Check in DB
    db_session.refresh(student_user)
    assert student_user.is_active is False

    # 5. Reactivate student
    res_reactivate = client.patch(
        f"/api/admin/students/{prof_id}/status",
        json={"isActive": True},
        headers=admin_headers,
    )
    assert res_reactivate.status_code == 200
    assert res_reactivate.json()["isActive"] is True
    db_session.refresh(student_user)
    assert student_user.is_active is True


def test_admin_analytics_endpoint(client: TestClient, db_session: Session):
    admin_headers, student_headers, admin_user, student_user = _create_users_for_admin_tests(client, db_session)

    res = client.get("/api/admin/analytics", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()

    assert "opportunityDistribution" in data
    assert "modeDistribution" in data
    assert "categoryPopularity" in data
    assert "applicationOutcomes" in data
    assert "studentSkillTrends" in data
    assert "matchPrecision" in data
    assert len(data["categoryPopularity"]) >= 1

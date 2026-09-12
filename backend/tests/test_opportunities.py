import pytest
from app.core.security import create_access_token, get_password_hash
from app.models.enums import EligibilityStatus, OpportunityCategory, UserRole, WorkMode
from app.models.opportunity import Opportunity
from app.models.user import User


@pytest.fixture
def admin_token(db_session):
    admin = User(
        email="admin_test@skillmatch.edu",
        hashed_password=get_password_hash("AdminPass123!"),
        full_name="Admin Test",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return create_access_token(admin.id)


@pytest.fixture
def student_token(db_session):
    student = User(
        email="student_test@skillmatch.edu",
        hashed_password=get_password_hash("StudentPass123!"),
        full_name="Student Test",
        role=UserRole.STUDENT,
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return create_access_token(student.id)


def test_admin_create_opportunity(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "title": "Quantum Algorithm Research Intern",
        "organization": "IBM Quantum",
        "category": "INTERNSHIP",
        "description": "Develop and benchmark quantum variational algorithms using Qiskit.",
        "domain": "Quantum Computing",
        "location": "Yorktown Heights, NY",
        "mode": "Hybrid",
        "deadline": "30 Nov 2026",
        "requiredSkills": ["Python", "Qiskit", "Linear Algebra"],
        "preferredSkills": ["C++", "Quantum Mechanics"],
        "eligibilityRequirements": "Undergraduate enrolled in Physics or CS with GPA >= 3.5",
        "degreeRequirements": ["B.Tech / B.E.", "B.S."],
        "branchRequirements": ["Physics", "Computer Science"],
        "academicYearRequirements": ["3rd Year", "4th Year"],
        "experienceRequirements": "Prior quantum simulation project",
        "applicationUrl": "https://ibm.com/quantum/careers",
        "compensation": "$5,000 / month",
        "verified": True,
    }

    res = client.post("/api/opportunities", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == payload["title"]
    assert data["organization"] == payload["organization"]
    assert data["category"] == "INTERNSHIP"
    assert "Python" in data["required_skills"]
    assert "Qiskit" in data["required_skills"]
    assert data["application_url"] == payload["applicationUrl"]
    assert data["verified"] is True
    assert data["id"] is not None


def test_student_cannot_create_opportunity(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "title": "Unauthorized Opportunity",
        "organization": "Rogue Org",
        "category": "INTERNSHIP",
        "description": "Should fail",
        "domain": "General",
        "location": "Remote",
        "deadline": "31 Dec 2026",
    }
    res = client.post("/api/opportunities", json=payload, headers=headers)
    assert res.status_code == 403
    assert "Admin" in res.json()["detail"]


def test_unauthenticated_cannot_create_opportunity(client):
    payload = {
        "title": "Unauthorized Opportunity",
        "organization": "Rogue Org",
        "category": "INTERNSHIP",
        "description": "Should fail",
        "domain": "General",
        "location": "Remote",
        "deadline": "31 Dec 2026",
    }
    res = client.post("/api/opportunities", json=payload)
    assert res.status_code == 401


def test_admin_update_opportunity(client, admin_token, db_session):
    opp = Opportunity(
        title="Original Title",
        organization="Test Org",
        category=OpportunityCategory.PROJECT,
        category_label="Project",
        domain="Systems",
        location="Remote",
        mode=WorkMode.REMOTE,
        deadline="15 Oct 2026",
        description="Original description",
        verified=True,
    )
    db_session.add(opp)
    db_session.commit()
    db_session.refresh(opp)

    headers = {"Authorization": f"Bearer {admin_token}"}
    update_payload = {
        "title": "Updated Title",
        "compensation": "$2,000 Stipend",
        "requiredSkills": ["Rust", "Systems"],
    }
    res = client.put(f"/api/opportunities/{opp.id}", json=update_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Updated Title"
    assert data["compensation"] == "$2,000 Stipend"
    assert "Rust" in data["required_skills"]


def test_admin_verify_and_reject(client, admin_token, student_token, db_session):
    opp = Opportunity(
        title="Pending Audit Opportunity",
        organization="Startup Alpha",
        category=OpportunityCategory.HACKATHON,
        category_label="Hackathon",
        domain="Web3",
        location="Remote",
        mode=WorkMode.ONLINE,
        deadline="20 Dec 2026",
        description="Awaiting audit",
        verified=False,
    )
    db_session.add(opp)
    db_session.commit()
    db_session.refresh(opp)

    student_headers = {"Authorization": f"Bearer {student_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Student cannot verify
    res = client.patch(f"/api/opportunities/{opp.id}/verify", headers=student_headers)
    assert res.status_code == 403

    # Admin verifies
    res = client.patch(f"/api/opportunities/{opp.id}/verify", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["verified"] is True

    # Admin rejects
    res = client.patch(
        f"/api/opportunities/{opp.id}/reject?reason=Missing+credentials", headers=admin_headers
    )
    assert res.status_code == 200
    assert res.json()["verified"] is False
    assert "Missing credentials" in res.json()["eligibilityNote"]


def test_student_visibility_only_verified(client, student_token, admin_token, db_session):
    opp_verified = Opportunity(
        title="Public Verified Opportunity",
        organization="Verified Org",
        category=OpportunityCategory.SCHOLARSHIP,
        category_label="Scholarship",
        domain="AI",
        location="Remote",
        mode=WorkMode.ONLINE,
        deadline="15 Nov 2026",
        description="Visible to all",
        verified=True,
    )
    opp_unverified = Opportunity(
        title="Private Unverified Listing",
        organization="Hidden Org",
        category=OpportunityCategory.JOB,
        category_label="Job",
        domain="Finance",
        location="New York",
        mode=WorkMode.ONSITE,
        deadline="15 Nov 2026",
        description="Not visible to student",
        verified=False,
    )
    db_session.add_all([opp_verified, opp_unverified])
    db_session.commit()

    # 1. Unauthenticated or Student caller
    res = client.get("/api/opportunities")
    assert res.status_code == 200
    data = res.json()
    titles = [item["title"] for item in data["items"]]
    assert "Public Verified Opportunity" in titles
    assert "Private Unverified Listing" not in titles

    # 2. Direct lookup of unverified by student -> 404
    res_direct = client.get(f"/api/opportunities/{opp_unverified.id}")
    assert res_direct.status_code == 404

    # 3. Direct lookup of unverified by admin -> 200
    res_admin = client.get(
        f"/api/opportunities/{opp_unverified.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 200
    assert res_admin.json()["title"] == "Private Unverified Listing"


def test_search_and_filters(client, db_session):
    opp1 = Opportunity(
        title="Senior Deep Learning Engineer",
        organization="NeuroTech",
        category=OpportunityCategory.JOB,
        category_label="Job",
        domain="Neuroscience",
        location="Boston, MA",
        mode=WorkMode.ONSITE,
        deadline="10 Nov 2026",
        description="Brain-computer interface models",
        required_skills=["Python", "PyTorch", "Signal Processing"],
        verified=True,
        match_score=95,
    )
    opp2 = Opportunity(
        title="Frontend React Contributor",
        organization="OpenWeb",
        category=OpportunityCategory.PROJECT,
        category_label="Project",
        domain="Web Development",
        location="Remote",
        mode=WorkMode.REMOTE,
        deadline="05 Dec 2026",
        description="Building dashboard components",
        required_skills=["TypeScript", "React", "TailwindCSS"],
        verified=True,
        match_score=75,
    )
    db_session.add_all([opp1, opp2])
    db_session.commit()

    # Search by title keyword
    res = client.get("/api/opportunities?q=NeuroTech")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Senior Deep Learning Engineer"

    # Search by skill
    res = client.get("/api/opportunities?skills=React")
    assert res.status_code == 200
    items = res.json()["items"]
    assert any(i["title"] == "Frontend React Contributor" for i in items)
    assert not any(i["title"] == "Senior Deep Learning Engineer" for i in items)

    # Filter by category (slug format)
    res = client.get("/api/opportunities?category=projects")
    assert res.status_code == 200
    items = res.json()["items"]
    assert all(i["category"] == "PROJECT" for i in items)

    # Filter by location
    res = client.get("/api/opportunities?location=Boston")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 1
    assert items[0]["location"] == "Boston, MA"


def test_sorting_and_pagination(client, db_session):
    for i in range(1, 6):
        opp = Opportunity(
            title=f"Opportunity #{i}",
            organization=f"Org {i}",
            category=OpportunityCategory.COURSE,
            category_label="Course",
            domain="Computer Science",
            location="Remote",
            mode=WorkMode.ONLINE,
            deadline=f"2026-11-0{i}",
            description=f"Description {i}",
            verified=True,
            match_score=70 + i * 5,
        )
        db_session.add(opp)
    db_session.commit()

    # Pagination: page_size = 2
    res = client.get("/api/opportunities?category=courses&page=1&page_size=2&sortBy=match-desc")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 5
    assert data["total_pages"] >= 3

    # Sorting verify: highest match score first
    assert data["items"][0]["matchScore"] >= data["items"][1]["matchScore"]


def test_admin_delete_opportunity(client, admin_token, student_token, db_session):
    opp = Opportunity(
        title="Opportunity to Delete",
        organization="Delete Me Corp",
        category=OpportunityCategory.SKILL_OPPORTUNITY,
        category_label="Skill Opportunity",
        domain="DevOps",
        location="Remote",
        mode=WorkMode.FLEXIBLE,
        deadline="15 Nov 2026",
        description="Will be removed",
        verified=True,
    )
    db_session.add(opp)
    db_session.commit()
    db_session.refresh(opp)

    # Student cannot delete -> 403
    res_student = client.delete(
        f"/api/opportunities/{opp.id}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student.status_code == 403

    # Admin deletes -> 200
    res_admin = client.delete(
        f"/api/opportunities/{opp.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 200

    # Ensure deleted
    res_check = client.get(f"/api/opportunities/{opp.id}")
    assert res_check.status_code == 404

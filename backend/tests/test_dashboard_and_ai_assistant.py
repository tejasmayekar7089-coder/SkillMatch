import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.enums import ApplicationStatus, OpportunityCategory, WorkMode
from app.models.opportunity import Opportunity
from app.models.saved_opportunity import SavedOpportunity
from app.models.application import Application
from app.models.student_profile import StudentProfile
from app.models.user import User


def _create_auth_student_with_skills(client: TestClient, db_session: Session, email: str, name: str):
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": name,
            "role": "STUDENT",
            "college": "National Institute of Technology",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    token = reg_resp.json()["access_token"]
    user_id = reg_resp.json()["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add profile details
    prof = db_session.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    assert prof is not None
    prof.degree = "B.Tech"
    prof.branch = "Computer Science"
    prof.academic_year = "3rd Year"
    prof.gpa = 3.82
    prof.target_role = "Machine Learning Engineer"

    from app.services.skill_normalizer import SkillNormalizationService
    for skill_name, level in [("Python", "Advanced"), ("PyTorch", "Intermediate"), ("FastAPI", "Intermediate")]:
        SkillNormalizationService.add_skill_to_student(
            db=db_session,
            student_profile_id=prof.id,
            raw_name=skill_name,
            proficiency=level,
            verified=True,
            verified_via="Coursework CS301",
        )

    db_session.commit()
    db_session.refresh(prof)
    return token, user_id, headers, prof


def _create_sample_opportunities(db_session: Session):
    opps_to_create = [
        Opportunity(
            id="opp-dash-1",
            title="DeepMind Research Internship",
            organization="Google DeepMind",
            category=OpportunityCategory.INTERNSHIP,
            category_label="Internship",
            domain="Artificial Intelligence",
            location="London / Remote",
            mode=WorkMode.REMOTE,
            compensation="$6,500/mo",
            deadline="Nov 15, 2026",
            deadline_days_remaining=4,
            posted_ago="2d ago",
            duration="12 weeks",
            cohort_size="5 interns",
            description="Frontier research in deep reinforcement learning and transformers.",
            required_skills=["Python", "PyTorch", "Transformers", "Distributed Systems"],
            preferred_skills=["JAX", "CUDA"],
            match_score=94,
            verified=True,
        ),
        Opportunity(
            id="opp-dash-2",
            title="Climate AI Global Hackathon",
            organization="UN Climate Tech",
            category=OpportunityCategory.HACKATHON,
            category_label="Hackathon",
            domain="Climate Tech",
            location="Remote",
            mode=WorkMode.ONLINE,
            compensation="$50,000 Prize Pool",
            deadline="Oct 20, 2026",
            deadline_days_remaining=2,
            posted_ago="1w ago",
            duration="48 hours",
            cohort_size="500 hackers",
            description="Build predictive climate models using satellite imagery.",
            required_skills=["Python", "Satellite Data", "Computer Vision"],
            match_score=88,
            verified=True,
        ),
        Opportunity(
            id="opp-dash-3",
            title="Cloud Infrastructure Fellow",
            organization="Apex Cloud",
            category=OpportunityCategory.SCHOLARSHIP,
            category_label="Scholarship",
            domain="Cloud Computing",
            location="San Francisco, CA",
            mode=WorkMode.HYBRID,
            compensation="$10,000 Fellowship",
            deadline="Dec 01, 2026",
            deadline_days_remaining=45,
            posted_ago="3d ago",
            duration="6 months",
            cohort_size="10 fellows",
            description="Open source infrastructure fellowship.",
            required_skills=["Go", "Kubernetes", "Linux"],
            match_score=52,
            verified=True,
        ),
    ]
    for o in opps_to_create:
        if not db_session.query(Opportunity).filter(Opportunity.id == o.id).first():
            db_session.add(o)
    db_session.commit()


def test_dashboard_endpoint_real_aggregated_metrics(client: TestClient, db_session: Session):
    _create_sample_opportunities(db_session)
    token, user_id, headers, prof = _create_auth_student_with_skills(
        client, db_session, "dash.student@test.edu", "Dash Student"
    )

    # 1. Save an opportunity
    save_resp = client.post("/api/saved/opp-dash-1", headers=headers)
    assert save_resp.status_code in [200, 201]

    # 2. Submit an application
    apply_resp = client.post(
        "/api/applications",
        json={
            "opportunityId": "opp-dash-2",
            "status": "APPLIED",
            "currentStage": "Application Submitted & Queued",
        },
        headers=headers,
    )
    assert apply_resp.status_code == 201

    # 3. GET /api/dashboard
    dash_resp = client.get("/api/dashboard", headers=headers)
    assert dash_resp.status_code == 200, dash_resp.text
    data = dash_resp.json()

    # Verify real aggregated data
    assert data["studentName"] == "Dash Student"
    assert data["profileCompletion"] > 50
    assert data["totalSaved"] == 1
    assert data["totalApplications"] == 1
    assert data["applicationStatusCounts"]["APPLIED"] == 1
    assert data["applicationStatusCounts"]["INTERVIEW"] == 0

    # Recommended opportunities
    assert len(data["recommendedOpportunities"]) > 0
    top_rec = data["recommendedOpportunities"][0]
    assert "opportunity" in top_rec
    assert "matchScore" in top_rec
    assert "eligibilityStatus" in top_rec
    assert "matchedSkills" in top_rec
    assert "missingSkills" in top_rec

    # Upcoming deadlines
    assert len(data["upcomingDeadlines"]) > 0
    # Must be sorted by deadline_days_remaining ascending
    days_list = [d["deadlineDaysRemaining"] for d in data["upcomingDeadlines"] if d["deadlineDaysRemaining"] is not None]
    assert days_list == sorted(days_list)

    # Skill gaps summary
    assert data["skillGaps"]["targetRole"] == "Machine Learning Engineer"
    assert data["skillGaps"]["readinessScore"] > 0
    assert len(data["skillGaps"]["masteredSkills"]) >= 3


def test_ai_assistant_grounded_responses(client: TestClient, db_session: Session):
    _create_sample_opportunities(db_session)
    token, user_id, headers, prof = _create_auth_student_with_skills(
        client, db_session, "ai.student@test.edu", "AI Student"
    )

    # Save opp-dash-1
    client.post("/api/saved/opp-dash-1", headers=headers)

    # 1. Query: "Show me my saved opportunities."
    res1 = client.post("/api/ai/chat", json={"message": "Show me my saved opportunities."}, headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert "DeepMind Research Internship" in data1["reply"]
    assert any(s["title"] == "DeepMind Research Internship" for s in data1["sources"])

    # 2. Query: "Which opportunities match my profile?"
    res2 = client.post("/api/ai/chat", json={"message": "Which opportunities match my profile?"}, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert "% Match" in data2["reply"]
    assert len(data2["sources"]) > 0

    # 3. Query: "What skills am I missing for this internship?"
    res3 = client.post(
        "/api/ai/chat",
        json={"message": "What skills am I missing for DeepMind Research Internship?", "opportunityId": "opp-dash-1"},
        headers=headers,
    )
    assert res3.status_code == 200
    data3 = res3.json()
    assert "Missing Skills" in data3["reply"]
    assert "Readiness Score" in data3["reply"]
    # Python & PyTorch are mastered by student, so Transformers or Distributed Systems must be in missing skills!
    assert "Transformers" in data3["reply"] or "Distributed Systems" in data3["reply"]

    # 4. Query: "What should I learn next?"
    res4 = client.post("/api/ai/chat", json={"message": "What should I learn next?"}, headers=headers)
    assert res4.status_code == 200
    data4 = res4.json()
    assert len(data4["recommendedActions"]) > 0

    # 5. Query: "How can I improve my match score?"
    res5 = client.post("/api/ai/chat", json={"message": "How can I improve my match score?"}, headers=headers)
    assert res5.status_code == 200
    data5 = res5.json()
    assert "Skill Gaps" in data5["reply"]
    assert "hybrid scoring" in data5["reply"].lower()

    # 6. Important Rule: Grounded anti-hallucination test
    # Asking for a non-existent company
    res6 = client.post(
        "/api/ai/chat",
        json={"message": "Tell me about the internship at QuantumCyberUnicornX"},
        headers=headers,
    )
    assert res6.status_code == 200
    data6 = res6.json()
    # Assistant must explicitly state information is unavailable and NOT invent fake data
    assert "unavailable in the SkillMatch" in data6["reply"] or "currently unavailable" in data6["reply"]

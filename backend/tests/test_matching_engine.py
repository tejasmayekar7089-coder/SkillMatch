import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database.database import SessionLocal
from app.models.enums import EligibilityStatus, OpportunityCategory, WorkMode
from app.models.opportunity import Opportunity
from app.models.opportunity_embedding import OpportunityEmbedding
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.ml.matcher import match_student_and_opportunity, rank_opportunities_for_student
from app.ml.cache import get_or_compute_opportunity_embedding
from app.ml.eligibility import evaluate_eligibility
from app.ml.skill_gap_engine import (
    analyze_skill_gap_for_opportunity,
    analyze_skill_gap_for_role,
    generate_career_roadmap,
    recommend_learning_resources_for_gap,
)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


def test_three_profiles_produce_different_scores_and_logical_rankings(db_session: Session):
    """
    Verify that Alex Morgan (AI/ML), Maya Chen (Fullstack), and David Kumar (Analytics)
    receive genuinely computed, distinct match scores and logical rankings.
    """
    alex_user = db_session.query(User).filter(User.email == "student@skillmatch.edu").first()
    maya_user = db_session.query(User).filter(User.email == "maya.chen@skillmatch.edu").first()
    david_user = db_session.query(User).filter(User.email == "david.kumar@skillmatch.edu").first()

    assert alex_user is not None and alex_user.student_profile is not None
    assert maya_user is not None and maya_user.student_profile is not None
    assert david_user is not None and david_user.student_profile is not None

    alex_prof = alex_user.student_profile
    maya_prof = maya_user.student_profile
    david_prof = david_user.student_profile

    # Fetch opportunities
    ml_opp = db_session.query(Opportunity).filter(Opportunity.id == "opp-intern-1").first()
    assert ml_opp is not None

    # Compute matches for all 3 against the ML Research Intern
    alex_match = match_student_and_opportunity(db_session, alex_prof, ml_opp)
    maya_match = match_student_and_opportunity(db_session, maya_prof, ml_opp)
    david_match = match_student_and_opportunity(db_session, david_prof, ml_opp)

    # 1. Scores must be different and not hardcoded
    assert alex_match["overall_match_score"] != maya_match["overall_match_score"]
    assert alex_match["overall_match_score"] != david_match["overall_match_score"]

    # 2. Alex Morgan (specialist in PyTorch, ML, Python) MUST score highest for ML Research Intern
    assert alex_match["overall_match_score"] > maya_match["overall_match_score"]
    assert alex_match["overall_match_score"] > david_match["overall_match_score"]

    # 3. Matched skills must reflect actual candidate skills
    # ML Opp requires: Python, PyTorch, Machine Learning, FastAPI
    assert "Python" in alex_match["matched_skills"]
    assert "PyTorch" in alex_match["matched_skills"]
    assert "Machine Learning" in alex_match["matched_skills"]
    assert len(alex_match["matched_skills"]) >= 3

    # Maya has JavaScript, TypeScript, React etc. - PyTorch must be in her missing skills
    assert "PyTorch" in maya_match["missing_skills"]
    assert "Machine Learning" in maya_match["missing_skills"]

    # 4. Multi-opportunity ranking test
    all_opps = db_session.query(Opportunity).filter(Opportunity.verified == True).all()
    alex_ranked = rank_opportunities_for_student(db_session, alex_prof, all_opps)
    maya_ranked = rank_opportunities_for_student(db_session, maya_prof, all_opps)

    # Alex top match should be an ML / Research / AI opportunity
    alex_top_opp = alex_ranked[0]["opportunity"]
    assert any(term in alex_top_opp.title.lower() or term in alex_top_opp.domain.lower() for term in ["machine learning", "ai", "intelligence", "models"])

    # Rankings between Alex and Maya must not be identical
    alex_order = [item["opportunity"].id for item in alex_ranked[:5]]
    maya_order = [item["opportunity"].id for item in maya_ranked[:5]]
    assert alex_order != maya_order


def test_four_tier_eligibility_logic():
    """
    Test ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE, and UNKNOWN.
    Verify missing profile info does NOT automatically make candidate ineligible.
    """
    # 1. Complete fit -> ELIGIBLE
    student_eligible = {
        "degree": "B.Tech / B.E.",
        "branch": "Computer Science",
        "academic_year": "3rd Year",
        "preferred_locations": ["San Francisco, CA"],
        "preferred_work_mode": "Remote",
    }
    opp_criteria = {
        "degree_requirements": ["B.Tech / B.E.", "B.S."],
        "branch_requirements": ["Computer Science", "Information Technology"],
        "academic_year_requirements": ["3rd Year", "4th Year"],
        "location": "San Francisco, CA",
        "mode": "Remote",
    }
    res_el = evaluate_eligibility(student_eligible, opp_criteria)
    assert res_el["status"] == EligibilityStatus.ELIGIBLE
    assert res_el["passed_count"] == 4

    # 2. Missing info (no degree, no branch, no year) -> UNKNOWN, NOT ineligible!
    student_sparse = {
        "degree": "",
        "branch": "",
        "academic_year": "",
        "preferred_locations": [],
        "preferred_work_mode": "",
    }
    res_un = evaluate_eligibility(student_sparse, opp_criteria)
    assert res_un["status"] == EligibilityStatus.UNKNOWN
    assert res_un["failed_count"] == 0

    # 3. Only 1 criteria mismatch (e.g. 2nd year instead of 3rd year) -> PARTIALLY_ELIGIBLE
    student_partial = {
        "degree": "B.Tech / B.E.",
        "branch": "Computer Science",
        "academic_year": "1st Year",
        "preferred_locations": ["San Francisco, CA"],
        "preferred_work_mode": "Remote",
    }
    res_part = evaluate_eligibility(student_partial, opp_criteria)
    assert res_part["status"] == EligibilityStatus.PARTIALLY_ELIGIBLE
    assert res_part["failed_count"] == 1

    # 4. Multiple failures -> NOT_ELIGIBLE
    student_not = {
        "degree": "B.A. Literature",
        "branch": "English",
        "academic_year": "1st Year",
        "preferred_locations": ["Tokyo, Japan"],
        "preferred_work_mode": "On-site",
    }
    opp_onsite = {
        "degree_requirements": ["B.Tech / B.E."],
        "branch_requirements": ["Computer Science"],
        "academic_year_requirements": ["3rd Year"],
        "location": "San Francisco, CA",
        "mode": "On-site",
    }
    res_not = evaluate_eligibility(student_not, opp_onsite)
    assert res_not["status"] == EligibilityStatus.NOT_ELIGIBLE
    assert res_not["failed_count"] >= 2


def test_database_embedding_cache(db_session: Session):
    """
    Test persistent opportunity embedding cache:
    - 1st call computes and persists in OpportunityEmbedding table.
    - 2nd call hits cache without model recalculation.
    """
    opp = db_session.query(Opportunity).first()
    assert opp is not None

    # Compute embedding
    emb1 = get_or_compute_opportunity_embedding(db_session, opp)
    assert isinstance(emb1, list)
    assert len(emb1) == 384

    # Verify stored in DB
    cached = db_session.query(OpportunityEmbedding).filter(OpportunityEmbedding.opportunity_id == opp.id).first()
    assert cached is not None
    assert cached.embedding == emb1

    # Second call must retrieve exact same cached embedding
    emb2 = get_or_compute_opportunity_embedding(db_session, opp)
    assert emb2 == emb1


def test_skill_gap_analysis_and_priority_ranking(db_session: Session):
    """
    Test skill gap analysis for an opportunity and career role.
    Verifies classification into MATCHED, MISSING, PARTIAL and priority ranking.
    """
    alex_user = db_session.query(User).filter(User.email == "student@skillmatch.edu").first()
    alex_prof = alex_user.student_profile

    # Test for opportunity
    ml_opp = db_session.query(Opportunity).filter(Opportunity.id == "opp-intern-1").first()
    gap_opp = analyze_skill_gap_for_opportunity(db_session, alex_prof, ml_opp)

    assert "readiness_percentage" in gap_opp
    assert "matched_skills" in gap_opp
    assert "missing_skills" in gap_opp
    assert "priority_skills" in gap_opp
    assert isinstance(gap_opp["priority_skills"], list)

    # Test for target role
    gap_role = analyze_skill_gap_for_role(db_session, alex_prof, "Machine Learning Engineer")
    assert gap_role["roleTitle"] == "Machine Learning Engineer"
    assert gap_role["readinessScore"] > 0
    assert len(gap_role["mastered"]) > 0
    assert "criticalGaps" in gap_role

    # Verify priority order: critical gaps are ordered by dependency / demand
    if len(gap_role["criticalGaps"]) > 1:
        deps = [g.get("dependency", 2) for g in gap_role["criticalGaps"]]
        assert deps == sorted(deps)


def test_learning_recommendations_and_career_roadmap(db_session: Session):
    """
    Test learning recommendations from actual database opportunities
    and structured career roadmap milestones.
    """
    alex_user = db_session.query(User).filter(User.email == "student@skillmatch.edu").first()
    alex_prof = alex_user.student_profile

    ml_opp = db_session.query(Opportunity).filter(Opportunity.id == "opp-intern-1").first()

    # 1. Learning recommendations for opportunity
    recs = recommend_learning_resources_for_gap(db_session, alex_prof, opportunity_id=ml_opp.id)
    assert len(recs) > 0
    for r in recs:
        assert "id" in r
        assert "title" in r
        assert "provider" in r
        assert "type" in r
        assert "addressesGap" in r

    # 2. Career Roadmap sequence
    steps = generate_career_roadmap(db_session, alex_prof, "Machine Learning Engineer")
    assert len(steps) >= 5
    assert steps[0]["status"] == "completed"
    assert any(s["status"] == "current" for s in steps)
    assert steps[-1]["tag"] == "Placement"


def test_api_endpoints(client: TestClient, db_session: Session):
    """
    Verify all API endpoints:
    - GET /api/recommendations
    - GET /api/opportunities/{id}/match
    - GET /api/opportunities/{id}/match-explanation
    - GET /api/skill-gap
    - GET /api/skill-gap/{id}
    - GET /api/skill-gap/{id}/learning
    - GET /api/career-roadmap
    """
    opp = db_session.query(Opportunity).first()
    assert opp is not None

    # 1. Recommendations
    r_rec = client.get("/api/recommendations")
    assert r_rec.status_code == 200
    rec_data = r_rec.json()
    assert isinstance(rec_data, list)
    assert len(rec_data) > 0
    assert "matchScore" in rec_data[0]

    # 2. Opportunity Match
    r_match = client.get(f"/api/opportunities/{opp.id}/match")
    assert r_match.status_code == 200
    m_data = r_match.json()
    assert "overallMatchScore" in m_data
    assert "skillScore" in m_data
    assert "semanticSimilarity" in m_data
    assert "matchedSkills" in m_data
    assert "eligibilityStatus" in m_data

    # 3. Match Explanation
    r_expl = client.get(f"/api/opportunities/{opp.id}/match-explanation")
    assert r_expl.status_code == 200
    expl_data = r_expl.json()
    assert "compatibilityLabel" in expl_data
    assert "summary" in expl_data
    assert "reasons" in expl_data
    assert "strongMatches" in expl_data

    # 4. Skill Gap by Role
    r_gap = client.get("/api/skill-gap?role=Full-Stack+Developer")
    assert r_gap.status_code == 200
    gap_data = r_gap.json()
    assert gap_data["roleTitle"] == "Full-Stack Developer"
    assert "readinessScore" in gap_data

    # 5. Skill Gap by Opportunity
    r_opp_gap = client.get(f"/api/skill-gap/{opp.id}")
    assert r_opp_gap.status_code == 200
    opp_gap_data = r_opp_gap.json()
    assert "readiness_percentage" in opp_gap_data
    assert "priority_skills" in opp_gap_data

    # 6. Learning for Opportunity
    r_opp_learn = client.get(f"/api/skill-gap/{opp.id}/learning")
    assert r_opp_learn.status_code == 200
    learn_data = r_opp_learn.json()
    assert isinstance(learn_data, list)

    # 7. Career Roadmap
    r_road = client.get("/api/career-roadmap?role=Data+Scientist")
    assert r_road.status_code == 200
    road_data = r_road.json()
    assert isinstance(road_data, list)
    assert len(road_data) >= 5

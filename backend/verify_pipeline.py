from app.database.database import SessionLocal
from app.models.user import User
from app.models.opportunity import Opportunity
from app.ml.matcher import match_student_and_opportunity
from app.ml.skill_gap_engine import (
    analyze_skill_gap_for_role,
    recommend_learning_resources_for_gap,
    generate_career_roadmap,
)

def run_demo():
    db = SessionLocal()
    users = db.query(User).filter(User.role == "STUDENT").all()
    opps = db.query(Opportunity).filter(Opportunity.verified == True).all()

    print("=================================================================")
    print("      SKILLMATCH REAL DATABASE COMPUTATION VERIFICATION          ")
    print("=================================================================")

    ml_opp = next((o for o in opps if "Machine Learning Research" in o.title), opps[0])
    web_opp = next((o for o in opps if "HackMIT" in o.title or "Web" in o.title), opps[1])

    for u in users:
        p = u.student_profile
        if not p or not p.skills:
            continue

        skills = [s.skill.name for s in p.skills]
        print(f"\n>> STUDENT: {u.full_name} ({u.email})")
        print(f"   Degree: {p.degree} in {p.branch} (Year: {p.academic_year}, GPA: {p.gpa})")
        print(f"   Target Role: {p.target_role}")
        print(f"   Indexed Skills ({len(skills)}): {', '.join(skills)}")

        # Match 1: ML Intern
        m1 = match_student_and_opportunity(db, p, ml_opp)
        print(f"\n   [Match 1: {ml_opp.title}]")
        print(f"   - Overall Score:      {m1['overall_match_score']}%")
        print(f"   - Skill Score:        {m1['skill_score']}%")
        print(f"   - Semantic Sim:       {m1['semantic_similarity']}%")
        print(f"   - Education Score:    {m1['education_score']}%")
        print(f"   - Matched Skills:     {m1['matched_skills']}")
        print(f"   - Missing Skills:     {m1['missing_skills']}")
        print(f"   - Eligibility:        {m1['eligibility_status'].value} ({m1['eligibility_note']})")

        # Match 2: Web Opp
        m2 = match_student_and_opportunity(db, p, web_opp)
        print(f"\n   [Match 2: {web_opp.title}]")
        print(f"   - Overall Score:      {m2['overall_match_score']}%")
        print(f"   - Skill Score:        {m2['skill_score']}%")
        print(f"   - Matched Skills:     {m2['matched_skills']}")
        print(f"   - Missing Skills:     {m2['missing_skills']}")

        # Skill Gap Analysis
        gap = analyze_skill_gap_for_role(db, p, p.target_role)
        print(f"\n   [Skill Gap for Target: {gap['roleTitle']}]")
        print(f"   - Readiness:          {gap['readinessScore']}% ({gap['competenciesMet']}/{gap['competenciesTotal']} competencies)")
        print(f"   - Mastered:           {[m['name'] for m in gap['mastered']]}")
        print(f"   - Critical Gaps:      {[c['name'] for c in gap['criticalGaps']]}")

        # Learning Recommendations
        learning = recommend_learning_resources_for_gap(db, p, role_title=p.target_role)
        print(f"\n   [Learning Recommendations from DB ({len(learning)} found)]")
        for rec in learning[:2]:
            print(f"   - {rec['title']} ({rec['provider']}) -> Addresses: {rec['addressesGap']} | {rec['impactScore']}")

        # Career Roadmap
        roadmap = generate_career_roadmap(db, p, p.target_role)
        print(f"\n   [Career Roadmap Steps ({len(roadmap)} steps)]")
        for step in roadmap[:4]:
            print(f"   - Step {step['stepNumber']} [{step['status']}]: {step['title']}")

    db.close()

if __name__ == "__main__":
    run_demo()

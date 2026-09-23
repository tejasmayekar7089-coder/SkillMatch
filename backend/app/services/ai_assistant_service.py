import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.application import Application
from app.models.enums import ApplicationStatus
from app.models.opportunity import Opportunity
from app.models.saved_opportunity import SavedOpportunity
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.ml.matcher import rank_opportunities_for_student, match_student_and_opportunity
from app.ml.skill_gap_engine import (
    analyze_skill_gap_for_opportunity,
    analyze_skill_gap_for_role,
    recommend_learning_resources_for_gap,
)
from app.schemas.ai_assistant import AIChatResponse, AIChatSource

logger = logging.getLogger(__name__)

GENERIC_STOP_WORDS = {
    "internship", "intern", "research", "fellowship", "scholarship", "challenge",
    "project", "program", "course", "bootcamp", "developer", "engineer", "engineering",
    "scientist", "analyst", "opportunity", "training", "position", "associate", "role",
    "skills", "campus", "student", "about", "which", "where", "there", "summer", "winter"
}


def _find_mentioned_opportunity(db: Session, query: str, explicit_id: Optional[str] = None) -> Optional[Opportunity]:
    if explicit_id:
        opp = db.query(Opportunity).filter(Opportunity.id == explicit_id).first()
        if opp:
            return opp

    q_lower = query.lower()
    opps = db.query(Opportunity).all()

    # 1. Exact ID in query
    for opp in opps:
        if opp.id.lower() in q_lower:
            return opp

    # 2. Exact Title in query
    for opp in opps:
        if opp.title.lower() in q_lower:
            return opp

    # 3. Exact Organization in query
    for opp in opps:
        if opp.organization.lower() in q_lower:
            return opp

    # 4. Distinctive title token
    for opp in opps:
        distinctive_tokens = [
            w for w in re.findall(r'\b[a-zA-Z0-9]+\b', opp.title.lower())
            if len(w) >= 4 and w not in GENERIC_STOP_WORDS
        ]
        for token in distinctive_tokens:
            if re.search(rf'\b{re.escape(token)}\b', q_lower):
                return opp

    return None


def _call_external_llm(
    system_prompt: str,
    user_query: str,
) -> Optional[str]:
    """
    Optional integration with real external LLM providers (Gemini, OpenAI, Groq, OpenRouter)
    if API keys are provided via environment variables.
    """
    gemini_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    openai_key = os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    groq_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
    openrouter_key = os.environ.get("OPENROUTER_API_KEY") or settings.OPENROUTER_API_KEY

    # 1. Gemini API Call
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"{system_prompt}\n\nStudent Query: {user_query}"}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1024,
                }
            }
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
        except Exception as e:
            logger.warning("Gemini LLM call failed or timed out: %s", e)

    # 2. OpenAI / Groq / OpenRouter Compatible Call
    api_key = openai_key or groq_key or openrouter_key
    if api_key:
        try:
            base_url = "https://api.openai.com/v1/chat/completions"
            model_name = "gpt-4o-mini"
            if groq_key:
                base_url = "https://api.groq.com/openai/v1/chat/completions"
                model_name = "llama-3.1-70b-versatile"
            elif openrouter_key:
                base_url = "https://openrouter.ai/api/v1/chat/completions"
                model_name = "google/gemini-flash-1.5"

            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                "temperature": 0.2,
                "max_tokens": 1024,
            }
            headers = {"Authorization": f"Bearer {api_key}"}
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(base_url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0]["message"]["content"].strip()
        except Exception as e:
            logger.warning("External OpenAI/Groq call failed: %s", e)

    return None


def process_student_query(
    db: Session,
    user: User,
    message: str,
    opportunity_id: Optional[str] = None,
) -> AIChatResponse:
    """
    Accurate, Grounded, Multi-Disciplinary AI Career Advisor service.
    Answers student questions using authenticated student data, machine learning match scoring,
    and official university platform database records.
    """
    profile = user.student_profile
    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    now_iso = datetime.now(timezone.utc).isoformat()
    q_lower = message.lower().strip()
    sources: List[AIChatSource] = []
    actions: List[Dict[str, Any]] = []

    # Assemble Student Context
    student_name = user.full_name or "Student"
    degree_info = f"{profile.degree} in {profile.major} (Year {profile.year})" if profile else "Undergraduate Student"
    gpa_info = f"{profile.gpa} / 4.00" if profile and profile.gpa else "N/A"
    target_role = profile.target_role if profile and profile.target_role else "Software Engineer / Data Scientist"
    
    verified_skills = []
    if profile and profile.skills:
        for ps in profile.skills:
            if ps.skill:
                prof_val = getattr(ps, "proficiency", None) or getattr(ps, "proficiency_level", None) or "Proficient"
                verified_skills.append(f"{ps.skill.name} ({prof_val})")

    all_opportunities = db.query(Opportunity).filter(Opportunity.verified == True).all()
    if not all_opportunities:
        all_opportunities = db.query(Opportunity).all()

    # Check if external LLM should be consulted with grounded context
    gemini_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    openai_key = os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    groq_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
    openrouter_key = os.environ.get("OPENROUTER_API_KEY") or settings.OPENROUTER_API_KEY

    if gemini_key or openai_key or groq_key or openrouter_key:
        opps_summary = [
            f"- [{o.id}] {o.title} at {o.organization} ({o.category_label}, {o.domain}, {o.mode.value}, Deadline: {o.deadline}, Req: {', '.join(o.required_skills or [])})"
            for o in all_opportunities[:15]
        ]
        
        system_grounding_prompt = f"""
You are the SkillMatch AI Career Advisor, a highly intelligent, empathetic, and professional university career advisor.
You have authenticated access to the student's real profile and database listings:

STUDENT PROFILE:
- Name: {student_name}
- Academic Program: {degree_info}
- GPA: {gpa_info}
- Target Career Role: {target_role}
- Verified Skills: {', '.join(verified_skills) if verified_skills else 'None registered'}

VERIFIED DATABASE OPPORTUNITIES:
{chr(10).join(opps_summary)}

INSTRUCTIONS:
1. Give accurate, realistic, highly structured responses in Markdown with clear headings, bullet points, and practical action items.
2. Ground all advice strictly in the student's actual branch, skills, and the opportunities listed above.
3. If the student asks for interview preparation, provide exact technical questions, coding concepts, and behavioral strategies tailored to the company's tech stack.
4. If the student asks for a study plan or skill gap, provide a realistic 4-week breakdown.
5. If the student asks for a cover letter or application pitch, draft an elevator pitch highlighting their verified GPA, projects, and skills.
6. If the student asks about an entity not in the database, clearly state it is not in the verified campus database.
"""
        llm_reply = _call_external_llm(system_grounding_prompt, message)
        if llm_reply:
            # Detect any mentioned opportunities to attach clickable sources
            for opp in all_opportunities:
                if opp.title.lower() in llm_reply.lower() or opp.organization.lower() in llm_reply.lower():
                    sources.append(AIChatSource(title=f"{opp.title} ({opp.organization})", type="opportunity", link=f"/opportunity/{opp.id}"))
                    actions.append({"label": f"View {opp.title}", "link": f"/opportunity/{opp.id}"})

            if not sources:
                sources.append(AIChatSource(title="Student Profile", type="profile", link="/profile"))
                actions.append({"label": "Explore Opportunities", "link": "/discover"})

            return AIChatResponse(
                reply=llm_reply,
                sources=sources[:3],
                recommendedActions=actions[:3],
                timestamp=now_iso,
            )

    # =========================================================================
    # ADVANCED DETERMINISTIC GROUNDED REASONING ENGINE (Failsafe & Offline Mode)
    # =========================================================================

    # 1. Interview Preparation & Technical Challenge Guide
    if any(k in q_lower for k in ["interview", "prepare for interview", "interview questions", "technical round", "assessment tips", "interview prep"]):
        target_opp = _find_mentioned_opportunity(db, message, opportunity_id)
        if not target_opp and all_opportunities:
            target_opp = all_opportunities[0]

        if target_opp:
            sources.append(AIChatSource(title=target_opp.title, type="opportunity", link=f"/opportunity/{target_opp.id}"))
            actions.append({"label": f"View {target_opp.title}", "link": f"/opportunity/{target_opp.id}"})
            actions.append({"label": "Practice Technical Skills", "link": "/skill-gap-analysis"})

            req_skills = target_opp.required_skills or ["Core Engineering", "Problem Solving"]
            skills_preview = ", ".join(req_skills[:4])

            reply = (
                f"### 🎯 Comprehensive Interview & Assessment Strategy for **{target_opp.title}** at **{target_opp.organization}**\n\n"
                f"**Domain Focus**: {target_opp.domain} • **Core Stack**: {skills_preview}\n\n"
                "#### 1. Technical Screening Round (Expected Focus Areas)\n"
                f"• **Domain Fundamentals**: Be ready to explain fundamental algorithms and architectures related to **{req_skills[0] if req_skills else 'Data Structures'}**.\n"
                f"• **Practical Implementation**: Prepare for live coding/debugging in `{req_skills[1] if len(req_skills) > 1 else 'Python'}`. Practice memory optimization and modular clean code.\n"
                "• **System / Architecture Scenario**: You will be asked how you scale, test, or validate systems under real-world constraints.\n\n"
                "#### 2. Three High-Yield Questions to Practice:\n"
                f"1. *'Can you walk through a complex project where you utilized {req_skills[0] if req_skills else 'your core skills'} to solve an edge case or latency bottleneck?'*\n"
                f"2. *'How would you design an end-to-end pipeline or simulation model for {target_opp.organization}\'s core use cases?'*\n"
                "3. *'Explain a scenario where your initial approach failed and how you debugged and validated the fix.'*\n\n"
                "#### 3. Tailored Candidate Tip:\n"
                f"Highlight your verified academic GPA ({gpa_info}) and anchor your answers in measurable metrics (e.g. latency reduced, accuracy improved, simulation convergence time)."
            )
            return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 2. Application Pitch & Cover Letter Generator
    if any(k in q_lower for k in ["cover letter", "pitch", "elevator pitch", "draft application", "application note", "write an application"]):
        target_opp = _find_mentioned_opportunity(db, message, opportunity_id)
        if not target_opp and all_opportunities:
            target_opp = all_opportunities[0]

        if target_opp:
            sources.append(AIChatSource(title=target_opp.title, type="opportunity", link=f"/opportunity/{target_opp.id}"))
            actions.append({"label": f"Apply to {target_opp.organization}", "link": f"/opportunity/{target_opp.id}"})

            top_skills_str = ", ".join(verified_skills[:3]) if verified_skills else "software engineering and quantitative analysis"
            reply = (
                f"### 📝 Tailored Application Note for **{target_opp.title}** at **{target_opp.organization}**\n\n"
                "Here is a professional, high-impact candidate pitch tailored to this listing:\n\n"
                "---\n\n"
                f"*Dear {target_opp.organization} Hiring Committee,*\n\n"
                f"I am writing to express my strong interest in the **{target_opp.title}** position. As a {degree_info} student with a verified GPA of **{gpa_info}**, my background aligns directly with your team's focus on {target_opp.domain}.\n\n"
                f"Through rigorous coursework and hands-on projects, I have developed verified competencies in **{top_skills_str}**. I am particularly drawn to {target_opp.organization} because of your leadership in scalable engineering, and I am eager to contribute immediately to your active projects.\n\n"
                "I welcome the opportunity to discuss how my technical foundation and rapid problem-solving abilities can support your goals.\n\n"
                f"*Sincerely,*\n"
                f"**{student_name}**\n"
                f"Verified SkillMatch Candidate ID • {target_role}\n\n"
                "---\n\n"
                "💡 *Tip: You can paste this directly into the candidate note section when submitting your application!*"
            )
            return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 3. Department Specific Inquiries (Mechanical, Electrical, Finance, CS)
    dept_keywords = {
        "mechanical": ["mechanical", "cad", "solidworks", "ansys", "fea", "cfd", "thermal", "robotics", "automotive"],
        "electrical": ["electrical", "embedded", "firmware", "iot", "rtos", "vlsi", "fpga", "microcontroller", "verilog", "arm"],
        "finance": ["finance", "financial", "quantitative", "quant", "dcf", "valuation", "fintech", "arbitrage", "portfolio", "trading"],
        "ai_cs": ["ai", "machine learning", "ml", "python", "full stack", "react", "fastapi", "deep learning", "pytorch", "nlp"]
    }

    matched_dept = None
    for dept, terms in dept_keywords.items():
        if any(re.search(r"\b" + re.escape(t) + r"\b", q_lower) for t in terms):
            matched_dept = dept
            break

    if matched_dept and any(re.search(r"\b" + re.escape(k) + r"\b", q_lower) for k in ["opportunity", "opportunities", "internship", "internships", "jobs", "hackathon", "project", "courses", "find", "show me"]):
        dept_opps = [
            o for o in all_opportunities
            if any(t in (o.title + " " + o.domain + " " + (o.description or "")).lower() for t in dept_keywords[matched_dept])
        ]
        if not dept_opps:
            dept_opps = all_opportunities[:4]

        pick_lines = []
        for o in dept_opps[:4]:
            match_data = match_student_and_opportunity(db, profile, o) if profile else None
            score_badge = f"**{match_data['overall_match_score']}% Match**" if match_data else "Open for matching"
            deadline_str = f"• Deadline: {o.deadline}" if o.deadline else ""
            pick_lines.append(
                f"• **{o.title}** at **{o.organization}** ({o.category_label})\n"
                f"  {score_badge} • Mode: {o.mode.value} {deadline_str}\n"
                f"  *Required Skills:* {', '.join(o.required_skills[:3]) if o.required_skills else 'Domain alignment'}"
            )
            sources.append(AIChatSource(title=o.title, type="opportunity", link=f"/opportunity/{o.id}"))
            actions.append({"label": f"View {o.title}", "link": f"/opportunity/{o.id}"})

        reply = (
            f"### 🔍 Top Verified Listings for **{matched_dept.replace('_', ' / ').upper()}**\n\n"
            f"Here are the active partner opportunities in our verified database:\n\n"
            + "\n\n".join(pick_lines)
            + "\n\nWould you like a step-by-step skill gap breakdown or interview strategy for any of these?"
        )
        return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 4. Multi-Week Detailed Skill Roadmap & Learning Plan
    if any(k in q_lower for k in ["roadmap", "learning plan", "step by step", "how to learn", "curriculum", "study plan", "how to become"]):
        target = target_role
        role_gap = analyze_skill_gap_for_role(db, profile, target) if profile else {}
        critical_gaps = role_gap.get("criticalGaps", [])
        gap_names = [s["name"] if isinstance(s, dict) else getattr(s, "name", str(s)) for s in critical_gaps]
        primary_gap = gap_names[0] if gap_names else "Distributed Systems & Cloud Deployment"
        secondary_gap = gap_names[1] if len(gap_names) > 1 else "Performance Optimization & CI/CD"

        reply = (
            f"### 🚀 4-Week Career Acceleration Roadmap for **{target}**\n\n"
            f"**Target Role Focus**: {target} • **Priority Competency**: `{primary_gap}`\n\n"
            "#### 📅 Week 1: Core Fundamentals & Theory\n"
            f"• Master the foundational principles of **{primary_gap}**.\n"
            "• Complete proctored quizzes and review canonical documentation (2 hours daily).\n\n"
            "#### 📅 Week 2: Practical Exercises & Implementations\n"
            f"• Build 2 isolated mini-projects utilizing `{primary_gap}`.\n"
            "• Benchmark latency, computational efficiency, and edge cases.\n\n"
            "#### 📅 Week 3: Multi-Component Capstone Integration\n"
            f"• Integrate **{primary_gap}** with **{secondary_gap}** into a production-ready repository.\n"
            "• Write unit tests, Docker containerization scripts, and clear documentation.\n\n"
            "#### 📅 Week 4: Portfolio Verification & Application Submission\n"
            "• Connect your GitHub repo to SkillMatch for automatic verification.\n"
            "• Target top partner listings in the Discover feed with your enhanced **+15% match readiness index**."
        )
        sources.append(AIChatSource(title="Career Roadmap Hub", type="profile", link="/career-roadmap"))
        sources.append(AIChatSource(title="Skill Gap Diagnostics", type="skill", link="/skill-gap-analysis"))
        actions.append({"label": "Open Career Roadmap", "link": "/career-roadmap"})
        actions.append({"label": "Verify New Skills", "link": "/profile"})
        return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 5. Saved Opportunities Inquiry
    if any(k in q_lower for k in ["saved", "bookmark", "bookmarked", "save list"]):
        saved_records = (
            db.query(SavedOpportunity)
            .filter(SavedOpportunity.user_id == user.id)
            .all()
        )
        if not saved_records:
            return AIChatResponse(
                reply="You currently have no saved opportunities. You can bookmark any listing from your Discover or Category feeds to track them here.",
                sources=[],
                recommendedActions=[{"label": "Explore Opportunities", "link": "/discover"}],
                timestamp=now_iso,
            )

        opp_ids = [s.opportunity_id for s in saved_records]
        opps = db.query(Opportunity).filter(Opportunity.id.in_(opp_ids)).all()
        
        opp_bullets = []
        for opp in opps:
            deadline_str = f"Deadline: {opp.deadline}" if opp.deadline else ""
            comp_str = f"• {opp.compensation}" if opp.compensation else ""
            opp_bullets.append(f"• **{opp.title}** at {opp.organization} ({opp.category_label}) {comp_str} {deadline_str}")
            sources.append(AIChatSource(title=opp.title, type="opportunity", link=f"/opportunity/{opp.id}"))
            actions.append({"label": f"View {opp.title}", "link": f"/opportunity/{opp.id}"})

        reply = (
            f"### 📌 Saved Opportunities in Your Pipeline ({len(opps)})\n\n"
            + "\n".join(opp_bullets)
            + "\n\nWould you like to review the required skills or start an application for any of these?"
        )
        return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 6. Application Pipeline / Status Inquiry
    if any(k in q_lower for k in ["my application", "application status", "applied", "application tracker", "where do i stand", "tracking"]):
        if not profile:
            return AIChatResponse(
                reply="You haven't submitted any applications yet because your student profile is not initialized.",
                sources=[],
                recommendedActions=[{"label": "Complete Profile", "link": "/profile"}],
                timestamp=now_iso,
            )

        apps = db.query(Application).filter(Application.student_profile_id == profile.id).all()
        if not apps:
            return AIChatResponse(
                reply="You currently have no active applications. Explore your AI recommended matches to submit your first application!",
                sources=[],
                recommendedActions=[{"label": "Find Opportunities", "link": "/discover"}],
                timestamp=now_iso,
            )

        app_opp_ids = [a.opportunity_id for a in apps]
        opp_dict = {o.id: o for o in db.query(Opportunity).filter(Opportunity.id.in_(app_opp_ids)).all()}

        app_lines = []
        for app in apps:
            opp = opp_dict.get(app.opportunity_id)
            opp_title = opp.title if opp else "Opportunity"
            org_name = opp.organization if opp else "Organization"
            app_lines.append(
                f"• **{opp_title}** ({org_name})\n"
                f"  Status: **{app.status.value}** • Current stage: *{app.current_stage}*"
            )
            sources.append(AIChatSource(title=opp_title, type="application", link="/applications"))

        reply = (
            f"### 📋 Active Application Pipeline ({len(apps)})\n\n"
            + "\n\n".join(app_lines)
            + "\n\nCheck your Application Tracker to review deadline updates or status transition history."
        )
        return AIChatResponse(
            reply=reply,
            sources=sources,
            recommendedActions=[{"label": "Open Application Tracker", "link": "/applications"}],
            timestamp=now_iso,
        )

    # 7. Missing Skills / Gap Analysis Inquiry
    if any(k in q_lower for k in ["missing", "skill gap", "skills needed", "skills am i missing", "what skills do i need", "requirements for"]):
        target_opp = _find_mentioned_opportunity(db, message, opportunity_id)
        if not target_opp and all_opportunities and profile:
            ranked = rank_opportunities_for_student(db, profile, all_opportunities)
            if ranked:
                target_opp = ranked[0]["opportunity"]

        if target_opp and profile:
            gap = analyze_skill_gap_for_opportunity(db, profile, target_opp)
            sources.append(AIChatSource(title=target_opp.title, type="opportunity", link=f"/opportunity/{target_opp.id}"))
            sources.append(AIChatSource(title="Skill Gap Analysis", type="skill", link="/skill-gap-analysis"))

            matched_str = ", ".join(gap["matched_skills"]) if gap["matched_skills"] else "None yet verified"
            missing_str = ", ".join(gap["missing_skills"]) if gap["missing_skills"] else "None! You satisfy all required skills."

            readiness_pct = gap.get("readiness_percentage", 0)
            matched_count = len(gap.get("matched_skills", []))
            missing_count = len(gap.get("missing_skills", []))

            reply = (
                f"### 📊 Skill Diagnostics for **{target_opp.title}** at **{target_opp.organization}**\n\n"
                f"• **Candidate Readiness Score**: **{readiness_pct}%**\n"
                f"• **Verified Matched Skills ({matched_count})**: `{matched_str}`\n"
                f"• **Identified Skill Gaps / Missing Skills ({missing_count})**: `{missing_str}`\n\n"
            )

            if gap.get("missing_skills"):
                top_missing = gap["missing_skills"][0]
                reply += f"💡 **Recommended Action**: Focus on **{top_missing}** first. Acquiring this competency will provide an estimated **+8-12% match boost** for this position."
                actions.append({"label": f"Learn {top_missing}", "link": "/skill-gap-analysis"})
            else:
                reply += "🎉 Your verified skills completely satisfy all technical requirements for this role!"

            return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 8. Top Matches & Recommendations
    if any(k in q_lower for k in ["which opportunities", "match my profile", "recommend", "best fit", "what opportunities", "what jobs", "top matches"]):
        if not profile:
            return AIChatResponse(
                reply="Please complete your student profile so I can compute accurate AI recommendations based on your verified skills.",
                sources=[],
                recommendedActions=[{"label": "Complete Profile", "link": "/profile"}],
                timestamp=now_iso,
            )

        ranked = rank_opportunities_for_student(db, profile, all_opportunities)
        top_picks = ranked[:3]

        pick_lines = []
        for item in top_picks:
            o = item["opportunity"]
            m = item["match"]
            pick_lines.append(
                f"• **{o.title}** at **{o.organization}** — **{m['overall_match_score']}% Match** ({m['eligibility_status']})\n"
                f"  *Key skills matched:* {', '.join(m['matched_skills'][:3]) if m['matched_skills'] else 'Profile alignment'}"
            )
            sources.append(AIChatSource(title=o.title, type="opportunity", link=f"/opportunity/{o.id}"))
            actions.append({"label": f"View {o.title}", "link": f"/opportunity/{o.id}"})

        skills_names = [s.skill.name for s in profile.skills[:4] if s.skill] if profile and profile.skills else []
        skills_disp = ", ".join(skills_names) if skills_names else "coursework"
        reply = (
            f"### 🎯 Top AI-Ranked Matches for **{student_name}**\n\n"
            f"Based on your verified competencies (**{skills_disp}**), academic branch (**{profile.major}**), and GPA (**{profile.gpa or 'N/A'}**):\n\n"
            + "\n\n".join(pick_lines)
            + "\n\nWould you like me to explain the match breakdown or show how to close any remaining gaps?"
        )
        return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    # 9. Improve Match Score
    if any(k in q_lower for k in ["improve my match", "increase match", "reach 100", "higher score", "boost score"]):
        reply = (
            "### 📈 How to Systematically Maximize Your SkillMatch Index\n\n"
            "Our hybrid scoring engine evaluates 6 core dimensions:\n\n"
            "1. **Close Identified Skill Gaps (40% Weight)**: Verified technical skills carry the highest weight. Complete proctored assessments or upload verified certifications.\n"
            "2. **Semantic Experience Alignment (25% Weight)**: Ensure your resume narrative, project descriptions, and coursework descriptions use canonical engineering terminology.\n"
            "3. **Academic Benchmarks (15% Weight)**: Keep your verified GPA, graduation window, and department records up to date.\n"
            "4. **Domain & Career Preferences (10% Weight)**: Align your target roles and preferred working modes in your profile.\n"
            "5. **Project Portfolios (5% Weight)**: Link active GitHub repositories with unit tests and clear documentation."
        )
        return AIChatResponse(
            reply=reply,
            sources=[
                AIChatSource(title="Profile Settings", type="profile", link="/profile"),
                AIChatSource(title="Skill Gap Diagnostics", type="skill", link="/skill-gap-analysis"),
            ],
            recommendedActions=[
                {"label": "Diagnose Skill Gaps", "link": "/skill-gap-analysis"},
                {"label": "Update Profile & Projects", "link": "/profile"},
            ],
            timestamp=now_iso,
        )

    # 10. Specific Opportunity Lookups
    mentioned_opp = _find_mentioned_opportunity(db, message, opportunity_id)
    if mentioned_opp:
        match_info = match_student_and_opportunity(db, profile, mentioned_opp) if profile else None
        score_text = f"Your personal match score is **{match_info['overall_match_score']}%** ({match_info['eligibility_status']})." if match_info else "Log in to compute your personalized match score."
        
        reply = (
            f"### 📋 Details for **{mentioned_opp.title}** at **{mentioned_opp.organization}**\n\n"
            f"• **Category**: {mentioned_opp.category_label} • **Domain**: {mentioned_opp.domain}\n"
            f"• **Location / Mode**: {mentioned_opp.location} ({mentioned_opp.mode.value})\n"
            f"• **Compensation**: {mentioned_opp.compensation or 'Disclosed upon match'}\n"
            f"• **Deadline**: {mentioned_opp.deadline} ({mentioned_opp.deadline_days_remaining} days remaining)\n"
            f"• **Match Index**: {score_text}\n\n"
            f"**Required Technical Skills**: `{', '.join(mentioned_opp.required_skills or [])}`\n\n"
            f"**Overview**: {mentioned_opp.description}"
        )
        sources.append(AIChatSource(title=mentioned_opp.title, type="opportunity", link=f"/opportunity/{mentioned_opp.id}"))
        actions.append({"label": "View Opportunity Details", "link": f"/opportunity/{mentioned_opp.id}"})
        actions.append({"label": "Prepare for Interview", "link": f"/opportunity/{mentioned_opp.id}"})
        return AIChatResponse(reply=reply, sources=sources, recommendedActions=actions, timestamp=now_iso)

    if any(k in q_lower for k in ["tell me about", "details for", "information on", "about the internship", "about the job", "internship at", "job at", "role at"]):
        return AIChatResponse(
            reply="The requested opportunity or employer is currently unavailable in the SkillMatch verified partner database. Please explore our active partner opportunities on the Discover page.",
            sources=[],
            recommendedActions=[{"label": "Explore Discover", "link": "/discover"}],
            timestamp=now_iso,
        )

    # 11. General Grounded Assistant Welcome & Capabilities
    skills_list = [s.skill.name for s in profile.skills if s.skill] if profile and profile.skills else []
    skills_str = ", ".join(skills_list[:6]) if skills_list else "No skills listed yet"
    target = profile.target_role if profile and profile.target_role else "Software Engineering"
    gpa_str = str(profile.gpa) if profile and profile.gpa else "unavailable"

    reply = (
        f"Hello **{student_name}**! I am your SkillMatch AI Career Advisor.\n\n"
        f"**Your Active Profile Summary**:\n"
        f"• **Academic Program**: {degree_info}\n"
        f"• **Target Career Role**: {target}\n"
        f"• **Verified Skills**: {skills_str}\n"
        f"• **Academic GPA**: {gpa_str}\n\n"
        "Here are some high-impact questions you can ask me:\n"
        "• *'Which opportunities match my profile?'*\n"
        "• *'Give me an interview preparation plan for TechNova Labs'* (or any company)\n"
        "• *'Draft a cover letter pitch for my target internship'*\n"
        "• *'Show me top Mechanical / Electrical / Finance opportunities'*\n"
        "• *'Create a 4-week learning roadmap for my skill gaps'*\n"
        "• *'How can I improve my match score to 95%?'*"
    )
    return AIChatResponse(
        reply=reply,
        sources=[AIChatSource(title="Student Profile", type="profile", link="/profile")],
        recommendedActions=[
            {"label": "View Recommendations", "link": "/discover"},
            {"label": "Check Skill Gaps", "link": "/skill-gap-analysis"},
        ],
        timestamp=now_iso,
    )

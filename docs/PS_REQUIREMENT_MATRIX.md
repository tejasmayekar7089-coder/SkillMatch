# SkillMatch - Problem Statement Requirement Matrix

This document provides a comprehensive traceability matrix mapping every single requirement of the approved SkillMatch Problem Statement to its architectural implementation, backend service, REST API endpoint, database model, frontend page, and automated verification test.

---

## Traceability Matrix

| # | Requirement Domain | Feature / Specification | Backend Service / Module | REST API Endpoint | Database Model(s) | Frontend Page / Component | Verification / Test Case |
|---|---|---|---|---|---|---|---|
| **1** | **Authentication & Security** | Student Registration & Password Hashing | `app.core.security`, `app.routers.auth` | `POST /api/auth/register` | `User`, `StudentProfile` | `RegisterPage.tsx` | `test_auth_and_profile.py` |
| **2** | **Authentication & Security** | JWT Authentication & Session Token Issuance | `app.core.security`, `app.core.dependencies` | `POST /api/auth/login` | `User` | `LoginPage.tsx` | `test_auth_and_profile.py` |
| **3** | **Authentication & Security** | Authenticated User Identity (`/me`) | `app.core.dependencies` | `GET /api/auth/me` | `User`, `StudentProfile` | `Header.tsx`, `Sidebar.tsx` | `test_auth_and_profile.py` |
| **4** | **Authentication & Security** | Role-Based Authorization (Admin vs Student) | `app.core.dependencies.require_admin` | All `/api/admin/*` | `User.role` | Admin Pages | `test_admin.py::test_rbac_authorization_enforcement` |
| **5** | **Student Profile** | Student Academic Details (Degree, Major, GPA) | `app.routers.profile` | `GET /api/profile`, `PUT /api/profile` | `StudentProfile` | `ProfilePage.tsx`, `OnboardingPage.tsx` | `test_auth_and_profile.py` |
| **6** | **Skill Taxonomy** | Skill Normalization & Alias Deduplication | `SkillNormalizationService` | `POST /api/profile/skills` | `Skill`, `StudentSkill` | `ProfilePage.tsx` | `test_resume_and_skills.py::test_skill_normalization_aliases` |
| **7** | **Skill Taxonomy** | Proctored & Coursework Skill Verification | `SkillNormalizationService` | `PUT /api/profile/skills/{id}` | `StudentSkill.verified` | `ProfilePage.tsx` | `test_resume_and_skills.py::test_canonical_skills_in_database` |
| **8** | **Resume Intelligence** | Resume Upload & Non-Destructive Extraction | `ResumeParserService`, `SkillExtractorService` | `POST /api/resume/upload` | `StudentProfile` | `ProfilePage.tsx` (Resume Modal) | `test_resume_and_skills.py::test_resume_upload_non_destructive` |
| **9** | **Resume Intelligence** | Extracted Data Confirmation & Profile Update | `ResumeParserService` | `POST /api/resume/confirm` | `StudentProfile`, `StudentSkill`, `Project` | `ProfilePage.tsx` (Confirmation Step) | `test_resume_and_skills.py::test_resume_confirm_updates_profile` |
| **10** | **Opportunity Engine** | 7-Pillar Opportunities (Internships, Hackathons, etc.) | `app.routers.opportunities` | `GET /api/opportunities`, `GET /api/opportunities/categories` | `Opportunity` | `DiscoverPage.tsx`, `CategoryOpportunitiesPage.tsx` | `test_opportunities.py::test_sorting_and_pagination` |
| **11** | **Opportunity Engine** | Opportunity Verification State Isolation | `app.routers.opportunities` | `GET /api/opportunities?verified=true` | `Opportunity.verified` | `DiscoverPage.tsx` | `test_opportunities.py::test_student_visibility_only_verified` |
| **12** | **Opportunity Engine** | Multi-Factor Search & Attribute Filtering | `app.routers.opportunities` | `GET /api/opportunities?q=...&category=...` | `Opportunity` | `DiscoverPage.tsx` | `test_opportunities.py::test_search_and_filters` |
| **13** | **AIML Matching Engine** | Semantic Embeddings & Representation | `RepresentationBuilder`, `LocalEmbeddingModel` | Internal Pipeline | `OpportunityEmbedding` | `OpportunityCard.tsx` | `test_matching_engine.py::test_database_embedding_cache` |
| **14** | **AIML Matching Engine** | Hybrid Scoring (Skills + Semantic + Academic + Domain) | `app.ml.matcher.match_student_and_opportunity` | `GET /api/opportunities/{id}/match` | `StudentProfile`, `Opportunity` | `OpportunityDetailPage.tsx` | `test_matching_engine.py::test_three_profiles_produce_different_scores_and_logical_rankings` |
| **15** | **AIML Matching Engine** | 4-Tier Eligibility Evaluation & Explainable Decisions | `app.ml.eligibility.evaluate_eligibility` | `GET /api/opportunities/{id}/match` | `Opportunity.requirements` | `OpportunityDetailPage.tsx` | `test_matching_engine.py::test_four_tier_eligibility_logic` |
| **16** | **AIML Matching Engine** | Ranked Personalized Recommendations | `app.ml.matcher.rank_opportunities_for_student` | `GET /api/recommendations` | `StudentProfile`, `Opportunity` | `DiscoverPage.tsx`, `DashboardPage.tsx` | `test_matching_engine.py::test_api_endpoints` |
| **17** | **Skill Gap Analysis** | Competency Comparison (Matched, Missing, Partial) | `app.ml.skill_gap_engine.analyze_skill_gap_for_role` | `GET /api/skill-gap?role=...` | `StudentSkill`, `CareerBenchmarks` | `SkillGapPage.tsx` | `test_matching_engine.py::test_skill_gap_analysis_and_priority_ranking` |
| **18** | **Skill Gap Analysis** | Priority Ranking of Missing Competencies | `app.ml.skill_gap_engine.rank_priority_skills` | `GET /api/skill-gap` | `CareerBenchmarks` | `SkillGapPage.tsx` | `test_matching_engine.py::test_skill_gap_analysis_and_priority_ranking` |
| **19** | **Learning & Roadmap** | Database-Grounded Learning Recommendations | `recommend_learning_resources_for_gap` | `GET /api/skill-gap/learning` | `Opportunity` (Course, Project) | `SkillGapPage.tsx` | `test_matching_engine.py::test_learning_recommendations_and_career_roadmap` |
| **20** | **Learning & Roadmap** | Personalized Multi-Step Career Roadmap | `generate_career_roadmap` | `GET /api/career-roadmap?role=...` | `StudentProfile`, `CareerBenchmarks` | `CareerRoadmapPage.tsx` | `test_matching_engine.py::test_learning_recommendations_and_career_roadmap` |
| **21** | **Saved Opportunities** | Save / Bookmark Listings & Prevent Duplicates | `app.routers.saved` | `POST /api/saved/{id}`, `DELETE /api/saved/{id}`, `GET /api/saved` | `SavedOpportunity` | `SavedOpportunitiesPage.tsx`, `OpportunityDetailPage.tsx` | `test_saved_and_applications.py::test_saved_opportunities_lifecycle_and_duplicate_prevention` |
| **22** | **Application Tracker** | 7-Status Application Submissions & Transitions | `app.routers.applications` | `POST /api/applications`, `PUT /api/applications/{id}`, `GET /api/applications` | `Application` | `ApplicationTrackerPage.tsx`, `OpportunityDetailPage.tsx` | `test_saved_and_applications.py::test_application_tracker_lifecycle_history_and_student_isolation` |
| **23** | **Application Tracker** | Timestamped Transition History Audit Trail | `app.routers.applications` | `GET /api/applications/{id}` | `Application.status_history` | `ApplicationTrackerPage.tsx` (Timeline Modal) | `test_saved_and_applications.py::test_application_tracker_lifecycle_history_and_student_isolation` |
| **24** | **Notifications** | Dynamic Deadline Alerts & Status Change Stream | `NotificationService`, `app.routers.notifications` | `GET /api/notifications`, `PUT /api/notifications/{id}/read` | `Notification` | `Header.tsx` (Notification Bell) | `test_saved_and_applications.py::test_approaching_deadline_notification_and_duplicate_prevention` |
| **25** | **Student Dashboard** | Live Aggregation (Zero Hardcoding) | `app.routers.dashboard` | `GET /api/dashboard` | `StudentProfile`, `Application`, `SavedOpportunity` | `DashboardPage.tsx` | `test_dashboard_and_ai_assistant.py::test_dashboard_endpoint_real_aggregated_metrics` |
| **26** | **AI Assistant** | Grounded Career Assistant (Strict Anti-Hallucination) | `app.services.ai_assistant_service` | `POST /api/ai/chat` | `Opportunity`, `StudentProfile` | `AIAssistantPage.tsx` | `test_dashboard_and_ai_assistant.py::test_ai_assistant_grounded_responses` |
| **27** | **Admin Operations** | Real Statistical Dashboard Aggregation | `app.routers.admin` | `GET /api/admin/dashboard` | `User`, `StudentProfile`, `Opportunity`, `Application` | `AdminDashboardPage.tsx` | `test_admin.py::test_admin_dashboard_real_aggregated_statistics` |
| **28** | **Admin Operations** | Opportunity CRUD & Verification Review | `app.routers.admin` | `POST /api/admin/opportunities`, `PATCH /verify`, `PATCH /reject` | `Opportunity` | `AdminOpportunitiesPage.tsx`, `AdminVerificationPage.tsx` | `test_admin.py::test_opportunity_management_and_verification_lifecycle` |
| **29** | **Admin Operations** | Student Talent Directory & Account Deactivation | `app.routers.admin` | `GET /api/admin/students`, `PATCH /students/{id}/status` | `StudentProfile`, `User.is_active` | `AdminStudentsPage.tsx` | `test_admin.py::test_student_management_and_deactivation` |
| **30** | **Admin Operations** | System Telemetry & Match Accuracy Analytics | `app.routers.admin` | `GET /api/admin/analytics` | `Opportunity`, `Application`, `Skill` | `AdminAnalyticsPage.tsx` | `test_admin.py::test_admin_analytics_endpoint` |

---

## Detailed Requirement Implementation Verification

### 1. Zero Random Numbers Verification
- All match scores are computed using the formula:
  $$\text{Overall Score} = 0.40 \cdot \text{SkillScore} + 0.25 \cdot \text{SemanticSimilarity} + 0.15 \cdot \text{EducationScore} + 0.10 \cdot \text{DomainAlignment} + 0.10 \cdot \text{ExperienceScore}$$
- Proven by `verify_pipeline.py` and `tests/test_matching_engine.py`: 3 diverse student profiles obtain distinct, explainable scores that accurately reflect their indexed coursework and GPA.

### 2. Student Data Isolation Verification
- Tested in `tests/test_saved_and_applications.py`:
  - Attempts by Student B to view, edit, or delete Student A's application return `403 Forbidden`.
  - Saved opportunities and application lists are strictly filtered by authenticated user ID.

### 3. Verification State Privacy Verification
- Tested in `tests/test_admin.py`:
  - Unverified opportunities (`verified == False`) are strictly hidden from students in `/api/opportunities` and `/api/recommendations`.
  - Once approved by an Admin via `PATCH /api/admin/opportunities/{id}/verify`, the listing becomes discoverable immediately.
  - If rejected via `PATCH /api/admin/opportunities/{id}/reject`, it is withdrawn from student feeds.

### 4. Grounded AI Assistant Verification
- Tested in `tests/test_dashboard_and_ai_assistant.py`:
  - Grounded answers to *"What skills am I missing for this internship?"*, *"Which opportunities match my profile?"*, *"What should I learn next?"*, and *"Show me my saved opportunities."*
  - Anti-hallucination verified: When asked about non-existent organizations (e.g. `QuantumCyberUnicornX`), the assistant explicitly states that the listing is currently unavailable in the verified database.

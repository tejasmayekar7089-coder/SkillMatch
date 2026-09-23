# SkillMatch - Intelligent Student Opportunity Engine

SkillMatch is an AI-powered student career matching platform that maps verified student competencies, coursework, and GitHub project portfolios to curated opportunities across 7 pillars: **Internships**, **Hackathons**, **Scholarships**, **Courses**, **Projects**, **Jobs**, and **Skill Opportunities**.

The system features real AIML hybrid scoring (combining skill set overlap, local semantic sentence-transformers, academic criteria, and domain alignment), explainable match breakdowns, 4-tier eligibility evaluations, career roadmapping, non-destructive resume parsing, an application tracker with status history timelines, and an administrative governance portal.

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Stitch Frontend (React + Vite)                  │
│   Tailwind CSS • Material Symbols • TypeScript • Dynamic State Hubs    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST APIs (/api/*) + JWT Bearer
┌───────────────────────────────────▼────────────────────────────────────┐
│                        FastAPI Application Gateway                     │
│  Lifespan Hooks • CORS • Dependencies • Auth Guard • Routers (/api)   │
└──────────┬────────────────────────┬────────────────────────┬───────────┘
           │                        │                        │
┌──────────▼──────────┐  ┌──────────▼──────────┐  ┌──────────▼───────────┐
│     Core Routers    │  │    AIML Engine      │  │   Administrative     │
│  Auth, Profile,     │  │  Skill Normalizer   │  │   Governance Portal  │
│  Opportunities,     │  │  Semantic Embedder  │  │   Verification Queue │
│  Applications,      │  │  Hybrid Matcher     │  │   Student Directory  │
│  Saved, Dashboard,  │  │  Skill Gap Engine   │  │   Telemetry Analytics│
│  AI Assistant       │  │  Career Roadmap     │  │   Account Status     │
└──────────┬──────────┘  └──────────┬──────────┘  └──────────┬───────────┘
           │                        │                        │
┌──────────▼────────────────────────▼────────────────────────▼───────────┐
│                    SQLAlchemy 2.0 ORM + Alembic                        │
│                 SQLite Database (skillmatch.db)                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **Database ORM**: SQLAlchemy 2.0 with SQLite / PostgreSQL support
- **Migrations**: Alembic
- **Machine Learning & NLP**: Local `sentence-transformers` (`all-MiniLM-L6-v2`) with deterministic fallback caching
- **Authentication**: JWT (JSON Web Tokens) with `pyjwt` and `passlib[bcrypt]`
- **Testing**: Pytest with `TestClient` (Starlette / HTTPX)

### Frontend
- **Framework**: React 18 with TypeScript
- **Bundler & Dev Server**: Vite 6
- **Styling**: Tailwind CSS v3 with Stitch custom design tokens
- **Routing**: React Router v6

---

## 3. Pre-Seeded Accounts & Credentials

| Role | Email | Password | Full Name | Academic Background |
|---|---|---|---|---|
| **Student (ML Specialist)** | `student@skillmatch.edu` | `StudentPass123!` | Alex Morgan | 3rd Year B.Tech, CS (GPA: 3.82) |
| **Student (Full-Stack)** | `maya.chen@skillmatch.edu` | `StudentPass123!` | Maya Chen | 4th Year B.S., Software Eng (GPA: 3.65) |
| **Student (Analytics)** | `david.kumar@skillmatch.edu` | `StudentPass123!` | David Kumar | 2nd Year B.B.A., Info Systems (GPA: 3.40) |
| **Admin** | `admin@skillmatch.edu` | `AdminPass123!` | Campus Administrator | University Career Placement Center |

---

## 4. Getting Started & Local Setup

### Prerequisites
- Python 3.12+ (or `uv` package manager)
- Node.js 18+ and `npm`

### Step 1: Backend Setup
From the repository root:
```bash
# Navigate to backend directory
cd backend

# Using uv (recommended)
uv sync

# Alternatively, using standard virtualenv:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Database Initialization & Seeding
```bash
# Create database tables and seed verified opportunities, users, and benchmarks
uv run python app/seed.py
```

### Step 3: Frontend Setup
From the repository root:
```bash
# Install dependencies
npm install

# Verify production TypeScript build
npm run build
```

---

## 5. Running the Application

### Start the Backend API Server
```bash
# In the backend directory:
uv run uvicorn app.main:app --reload --port 8000
```
- **Backend Root**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`
- **Health Check**: `http://127.0.0.1:8000/api/health`

### Start the Frontend Dev Server
```bash
# In the repository root:
npm run dev
```
- **Stitch Frontend**: `http://localhost:5173`

---

## 6. AIML Matching Pipeline

SkillMatch employs a real multi-factor hybrid scoring model. **Zero random numbers are generated.**

$$\text{Overall Score} = 0.40 \cdot \text{SkillScore} + 0.25 \cdot \text{SemanticSimilarity} + 0.15 \cdot \text{EducationScore} + 0.10 \cdot \text{DomainAlignment} + 0.10 \cdot \text{ExperienceScore}$$

1. **Skill Extraction & Normalization**: Canonical alias mapping (`ml` $\rightarrow$ `Machine Learning`, `reactjs` $\rightarrow$ `React`).
2. **Student & Opportunity Representations**: Rich textual representations summarizing degree, competencies, and expectations.
3. **Local Semantic Embedding**: Pretrained sentence embeddings with database caching in `opportunity_embeddings` table.
4. **4-Tier Eligibility Evaluation**: `ELIGIBLE`, `PARTIALLY_ELIGIBLE`, `NOT_ELIGIBLE`, and `UNKNOWN`.
5. **Skill Gap Diagnostics**: Analyzes readiness percentage, classifies competencies into `MATCHED`, `MISSING`, and `PARTIAL`, and ranks missing skills by industry demand.
6. **Curriculum Recommendations**: Maps identified gaps to verified database courses, hackathons, and projects.

To verify the mathematical computation across three diverse profiles:
```bash
uv run --directory backend python verify_pipeline.py
```

---

## 7. Automated Test Suite

SkillMatch includes 45+ comprehensive automated tests covering authentication, RBAC, opportunity lifecycles, matching math, skill gaps, application tracker timelines, notifications, and administrative controls.

```bash
# Run all backend tests
uv run --directory backend pytest -v

# Run specific domain test suites
uv run --directory backend pytest tests/test_matching_engine.py -v
uv run --directory backend pytest tests/test_saved_and_applications.py -v
uv run --directory backend pytest tests/test_dashboard_and_ai_assistant.py -v
uv run --directory backend pytest tests/test_admin.py -v
uv run --directory backend pytest tests/test_resume_and_skills.py -v
```

---

## 8. Complete REST API Directory

| Domain | Method | Endpoint | Description | Auth Required |
|---|---|---|---|---|
| **Health** | `GET` | `/api/health` | Database and service health check | No |
| **Auth** | `POST` | `/api/auth/register` | Register new student or administrator | No |
| **Auth** | `POST` | `/api/auth/login` | Authenticate and issue JWT access token | No |
| **Auth** | `GET` | `/api/auth/me` | Retrieve authenticated identity | Yes |
| **Profile** | `GET` | `/api/profile` | Retrieve student profile and skills | Yes |
| **Profile** | `PUT` | `/api/profile` | Update profile fields | Yes |
| **Profile** | `POST` | `/api/profile/skills` | Add normalized skill to student | Yes |
| **Resume** | `POST` | `/api/resume/upload` | Parse PDF/DOCX/TXT resume non-destructively | Yes |
| **Resume** | `POST` | `/api/resume/confirm` | Confirm parsed data and update profile | Yes |
| **Opportunities** | `GET` | `/api/opportunities` | Search, filter, and paginate opportunities | Optional |
| **Opportunities** | `GET` | `/api/opportunities/categories` | Counts of verified listings by category | No |
| **Opportunities** | `GET` | `/api/opportunities/{id}` | Detailed opportunity view with personal match score | Optional |
| **Opportunities** | `GET` | `/api/opportunities/{id}/match`| Computed match breakdown and eligibility | Yes |
| **Recommendations** | `GET` | `/api/recommendations` | Ranked recommendations via AIML engine | Optional |
| **Skill Gap** | `GET` | `/api/skill-gap` | Skill gap analysis for target career or opportunity | Optional |
| **Skill Gap** | `GET` | `/api/skill-gap/learning` | Curated database resources closing skill gaps | Optional |
| **Roadmap** | `GET` | `/api/career-roadmap` | Step-by-step career readiness roadmap | Optional |
| **Saved** | `POST` | `/api/saved/{opportunity_id}` | Save listing and schedule deadline alerts | Yes |
| **Saved** | `DELETE` | `/api/saved/{opportunity_id}` | Unsave listing | Yes |
| **Saved** | `GET` | `/api/saved` | List all saved opportunities for student | Yes |
| **Applications** | `POST` | `/api/applications` | Submit application (7 statuses supported) | Yes |
| **Applications** | `GET` | `/api/applications` | List student's own applications (isolated) | Yes |
| **Applications** | `GET` | `/api/applications/{id}` | View application details and transition history | Yes |
| **Applications** | `PUT` | `/api/applications/{id}` | Transition status and append history entry | Yes |
| **Applications** | `DELETE` | `/api/applications/{id}` | Withdraw application | Yes |
| **Notifications** | `GET` | `/api/notifications` | Live notification stream with deadline alerts | Yes |
| **Notifications** | `PUT` | `/api/notifications/{id}/read` | Mark individual notification read | Yes |
| **Notifications** | `PUT` | `/api/notifications/read-all` | Mark all notifications read | Yes |
| **Dashboard** | `GET` | `/api/dashboard` | Real aggregated statistics for student | Yes |
| **AI Assistant** | `POST` | `/api/ai/chat` | Grounded AI assistant (anti-hallucination) | Yes |
| **Admin** | `GET` | `/api/admin/dashboard` | University-wide operational metrics | Admin Only |
| **Admin** | `GET` | `/api/admin/opportunities` | Manage verified and pending listings | Admin Only |
| **Admin** | `POST` | `/api/admin/opportunities` | Admin opportunity creation | Admin Only |
| **Admin** | `PATCH` | `/api/admin/opportunities/{id}/verify` | Verify opportunity listing | Admin Only |
| **Admin** | `PATCH` | `/api/admin/opportunities/{id}/reject` | Reject/unverify opportunity listing | Admin Only |
| **Admin** | `GET` | `/api/admin/students` | Student talent directory with search | Admin Only |
| **Admin** | `GET` | `/api/admin/students/{id}` | Detailed student profile oversight | Admin Only |
| **Admin** | `PATCH` | `/api/admin/students/{id}/status` | Activate/deactivate student account | Admin Only |
| **Admin** | `GET` | `/api/admin/analytics` | Match precision and category telemetry | Admin Only |

---

## 9. Production Deployment

SkillMatch uses a decoupled, high-performance production architecture:
- **Frontend**: React 18 + Vite SPA deployed on **Vercel** with client-side routing rewrites (`vercel.json`).
- **Backend**: FastAPI + Uvicorn deployed on a managed Python container host (**Render**, **Railway**, or **Docker/VPS**) running CPU-optimized ONNX FastEmbed neural embeddings.
- **Database**: **PostgreSQL** (Neon, Supabase, Railway Postgres, or Render Postgres).

### 9.1 Frontend Deployment (Vercel)
1. Import your GitHub repository into [Vercel](https://vercel.com).
2. Set the framework preset to **Vite**.
3. Set the Root Directory to `./` (repository root).
4. Configure Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com/api` (or your backend domain)
5. Deploy. The included `vercel.json` ensures all deep SPA routes (`/discover`, `/dashboard`, `/opportunity/:id`, etc.) resolve to `index.html`.

### 9.2 Backend Deployment (Render / Railway / Docker)

#### Option A: 1-Click Render Blueprint
1. In [Render](https://render.com), select **New +** -> **Blueprint**.
2. Connect your repository. Render automatically reads `backend/render.yaml` to provision the PostgreSQL database and the FastAPI Web Service.
3. Set `CORS_ORIGINS` to include your Vercel frontend URL (e.g. `https://skillmatch.vercel.app`).

#### Option B: Railway / PaaS
1. Create a new project in [Railway](https://railway.app) from your GitHub repo.
2. Set Root Directory to `backend/`.
3. Add a PostgreSQL plugin database.
4. Set Environment Variables:
   - `DATABASE_URL`: `${{Postgres.DATABASE_URL}}`
   - `SECRET_KEY`: `your-secure-random-32-char-key`
   - `ENVIRONMENT`: `production`
   - `CORS_ORIGINS`: `https://your-frontend.vercel.app`
5. Railway uses the included `backend/Procfile` (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`).

#### Option C: Docker Container
```bash
cd backend
docker build -t skillmatch-backend .
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" \
  -e SECRET_KEY="your-secret-key" \
  -e CORS_ORIGINS="https://your-frontend.vercel.app" \
  skillmatch-backend
```

### 9.3 Production Database Migration
When connecting to a fresh PostgreSQL database:
```bash
cd backend
# Run database migrations
uv run alembic upgrade head

# Seed initial opportunities and benchmarks
uv run python migrate_db.py
```

### 9.4 Health & Monitoring
- Backend Root Health: `GET https://your-backend.com/health`
- Backend API Health: `GET https://your-backend.com/api/health`
- Swagger Documentation: `GET https://your-backend.com/docs`

---

## 10. PS Requirement Matrix Reference

The complete requirement traceability matrix mapping every problem statement specification to code and tests is available in [docs/PS_REQUIREMENT_MATRIX.md](docs/PS_REQUIREMENT_MATRIX.md).

# SkillMatch Backend Foundation

FastAPI + SQLAlchemy + Alembic backend foundation for SkillMatch.

## Technology Stack

- **Python 3.12+**
- **FastAPI**: Modern, high-performance async web framework
- **SQLAlchemy 2.0**: Declarative ORM supporting SQLite & PostgreSQL
- **Alembic**: Database schema migration management
- **Pydantic v2**: Request/response schema validation and settings management
- **Uvicorn**: ASGI web server
- **Pytest**: Automated testing framework

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI application setup, CORS, lifespan, router mounting
│   ├── core/
│   │   ├── config.py               # Settings loaded from environment (.env)
│   │   ├── security.py             # Password hashing (bcrypt) & JWT helpers
│   │   └── dependencies.py         # DB session dependency & auth dependencies
│   ├── database/
│   │   ├── base.py                 # Declarative Base & TimestampMixin
│   │   └── database.py             # Engine, SessionLocal, get_db, DB health checker
│   ├── models/
│   │   ├── enums.py                # Enums (UserRole, OpportunityCategory [7], ApplicationStatus [7], etc.)
│   │   ├── user.py                 # User model (STUDENT, ADMIN)
│   │   ├── student_profile.py      # StudentProfile model
│   │   ├── skill.py                # Skill & StudentSkill models
│   │   ├── interest.py             # Interest & StudentInterest models
│   │   ├── project.py              # Project model
│   │   ├── certification.py        # Certification model
│   │   ├── opportunity.py          # Opportunity (7 categories) & OpportunitySkill models
│   │   ├── saved_opportunity.py    # SavedOpportunity model
│   │   ├── application.py          # Application model (7 statuses)
│   │   ├── notification.py         # Notification model
│   │   ├── recommendation.py       # Recommendation model
│   │   └── skill_gap.py            # SkillGap model
│   ├── schemas/
│   │   ├── common.py               # HealthResponse, MessageResponse, PaginatedResponse
│   │   ├── auth.py                 # UserCreate, UserLogin, Token, UserResponse
│   │   ├── profile.py              # StudentProfile schemas
│   │   ├── opportunity.py          # Opportunity schemas
│   │   ├── application.py          # Application schemas
│   │   ├── notification.py         # Notification schemas
│   │   └── skill_gap.py            # SkillGap schemas
│   ├── routers/
│   │   ├── health.py               # GET /api/health (DB connectivity check)
│   │   ├── auth.py                 # /api/auth routes
│   │   ├── profile.py              # /api/profile routes
│   │   ├── opportunities.py        # /api/opportunities routes
│   │   ├── recommendations.py      # /api/recommendations routes
│   │   ├── skill_gap.py            # /api/skill-gap routes
│   │   ├── resume.py               # /api/resume routes
│   │   ├── saved.py                # /api/saved routes
│   │   ├── applications.py         # /api/applications routes
│   │   ├── notifications.py        # /api/notifications routes
│   │   ├── dashboard.py            # /api/dashboard routes
│   │   └── admin.py                # /api/admin routes
│   ├── services/                   # Business logic layer
│   ├── ml/                         # AI / ML engines (reserved for future phases)
│   └── utils/                      # Helper utilities
│
├── alembic/
│   ├── env.py                      # Alembic configuration importing Base.metadata
│   └── versions/                   # Migration versions
├── tests/
│   ├── conftest.py                 # Pytest fixtures & isolated in-memory DB client
│   ├── test_startup.py             # App startup & /docs verification
│   ├── test_health.py              # /api/health and DB connectivity check
│   ├── test_models.py              # Model imports, categories, statuses, relationships
│   └── test_routes.py              # Verifies all mounted /api/* endpoints
├── alembic.ini                     # Alembic configuration file
├── .env.example                    # Sample environment variables
├── requirements.txt                # Pinned dependencies
└── README.md
```

---

## Setup Instructions

### 1. Create Virtual Environment and Install Dependencies

```bash
cd backend
uv venv .venv --python 3.12
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

To switch to PostgreSQL in production:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/skillmatch
```

### 3. Database Migrations

Apply existing Alembic migrations:
```bash
alembic upgrade head
```

To generate new migrations after updating models:
```bash
alembic revision --autogenerate -m "describe_changes"
alembic upgrade head
```

---

## Running the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## Running Tests

Execute the automated test suite with Pytest:
```bash
pytest -v
```

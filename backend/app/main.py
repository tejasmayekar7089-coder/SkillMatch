from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.database import engine
from app.routers import api_router


import logging
import app.models  # Ensure all SQLAlchemy models are registered before create_all

logger = logging.getLogger("skillmatch")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist across SQLite and PostgreSQL
    try:
        Base.metadata.create_all(bind=engine)
        from app.database.database import SessionLocal
        from app.models.user import User
        from app.seed import seed_database

        with SessionLocal() as db:
            admin_user = db.query(User).filter(User.email == "admin@skillmatch.edu").first()
            if not admin_user:
                logger.info("Initializing fresh database with seed data...")
                seed_database()
    except Exception as e:
        logger.warning(f"Lifespan database startup check/seed warning: {e}")
    yield
    # Shutdown logic if any
    pass


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="SkillMatch Backend API - Powering verified career matches, skill gap analysis, and student opportunities.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS for frontend (React/Vite/Stitch)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount /api routes
    app.include_router(api_router)

    @app.get("/health", tags=["Health"])
    def health():
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "Welcome to the SkillMatch API",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_application()

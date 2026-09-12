from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.base import Base
from app.database.database import engine
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist in development if not migrated yet
    Base.metadata.create_all(bind=engine)
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

    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": "Welcome to the SkillMatch API",
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


app = create_application()

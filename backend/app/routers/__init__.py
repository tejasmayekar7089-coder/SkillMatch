from fastapi import APIRouter
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.opportunities import router as opportunities_router
from app.routers.recommendations import router as recommendations_router
from app.routers.skill_gap import router as skill_gap_router
from app.routers.resume import router as resume_router
from app.routers.saved import router as saved_router
from app.routers.applications import router as applications_router
from app.routers.notifications import router as notifications_router
from app.routers.dashboard import router as dashboard_router
from app.routers.admin import router as admin_router
from app.routers.career_roadmap import router as career_roadmap_router
from app.routers.ai_assistant import router as ai_router

api_router = APIRouter(prefix="/api")

# Mount health check directly under /api/health
api_router.include_router(health_router)

# Mount feature routers under /api/*
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(opportunities_router)
api_router.include_router(recommendations_router)
api_router.include_router(skill_gap_router)
api_router.include_router(career_roadmap_router)
api_router.include_router(resume_router)
api_router.include_router(saved_router)
api_router.include_router(applications_router)
api_router.include_router(notifications_router)
api_router.include_router(dashboard_router)
api_router.include_router(admin_router)
api_router.include_router(ai_router)

__all__ = ["api_router"]

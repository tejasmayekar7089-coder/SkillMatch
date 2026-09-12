from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def check_health(db: Session = Depends(get_db)):
    """
    Health check endpoint verifying backend service and database connectivity.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "error", "database": f"disconnected: {str(exc)}"},
        )

    return HealthResponse(status="ok", database=db_status)

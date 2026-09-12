from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.ai_assistant import AIChatRequest, AIChatResponse
from app.services.ai_assistant_service import process_student_query

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=AIChatResponse)
@router.post("/query", response_model=AIChatResponse)
def chat_with_ai_assistant(
    req: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Direct endpoint for SkillMatch AI Career Advisor.
    Grounded strictly on actual student profile data and database opportunity records.
    Never invents fictitious opportunities. Explicitly states when data is unavailable.
    """
    return process_student_query(
        db=db,
        user=current_user,
        message=req.message,
        opportunity_id=req.opportunityId,
    )

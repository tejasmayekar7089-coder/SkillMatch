from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AIChatRequest(BaseModel):
    message: str
    opportunityId: Optional[str] = None
    roleId: Optional[str] = None


class AIChatSource(BaseModel):
    title: str
    type: str  # 'opportunity', 'skill', 'application', 'profile'
    link: Optional[str] = None
    detail: Optional[str] = None


class AIChatResponse(BaseModel):
    reply: str
    sources: List[AIChatSource] = []
    recommendedActions: List[Dict[str, Any]] = []
    timestamp: Optional[str] = None

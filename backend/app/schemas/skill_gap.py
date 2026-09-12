from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class SkillDetailSchema(BaseModel):
    name: str
    level: str
    description: str
    verificationNote: str
    progressPercent: Optional[int] = None
    rolesDemandPercent: Optional[int] = None
    priority: Optional[str] = None
    learningUrl: Optional[str] = None


class TargetRoleGapDataResponse(BaseModel):
    id: str
    roleId: str
    roleTitle: str
    readinessScore: int
    estimatedWeeksToClose: str
    competenciesMet: int
    competenciesTotal: int
    mastered: List[Dict[str, Any]] = []
    developing: List[Dict[str, Any]] = []
    criticalGaps: List[Dict[str, Any]] = []
    employerBenchmarks: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

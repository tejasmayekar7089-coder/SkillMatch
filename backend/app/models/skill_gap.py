from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile


class SkillGap(Base, TimestampMixin):
    __tablename__ = "skill_gaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    target_role: Mapped[str] = mapped_column(String(150), nullable=False)
    readiness_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 - 100
    estimated_weeks: Mapped[str] = mapped_column(String(50), default="4-6 weeks", nullable=False)
    competencies_met: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    competencies_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    mastered_skills: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    developing_skills: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    critical_gaps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    employer_benchmarks: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    roadmap_steps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    gap_closing_resources: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="skill_gaps")

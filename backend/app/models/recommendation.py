from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile
    from app.models.opportunity import Opportunity


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"
    __table_args__ = (
        UniqueConstraint("student_profile_id", "opportunity_id", name="uq_student_opportunity_recommendation"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    match_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    match_reasons: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="recommendations")
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="recommendations")

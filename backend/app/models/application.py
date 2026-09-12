from typing import TYPE_CHECKING, Optional
from sqlalchemy import Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid
from app.models.enums import ApplicationStatus

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile
    from app.models.opportunity import Opportunity


class Application(Base, TimestampMixin):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("student_profile_id", "opportunity_id", name="uq_student_opportunity_application"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # 7 Application statuses
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status", create_type=False),
        default=ApplicationStatus.APPLIED,
        index=True,
        nullable=False,
    )
    applied_date: Mapped[str] = mapped_column(String(50), nullable=False)
    current_stage: Mapped[str] = mapped_column(String(100), default="Applied", nullable=False)
    next_deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status_history: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="applications")
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="applications")

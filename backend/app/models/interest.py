from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile


class Interest(Base, TimestampMixin):
    __tablename__ = "interests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    student_interests: Mapped[List["StudentInterest"]] = relationship(
        "StudentInterest", back_populates="interest", cascade="all, delete-orphan"
    )


class StudentInterest(Base, TimestampMixin):
    __tablename__ = "student_interests"
    __table_args__ = (
        UniqueConstraint("student_profile_id", "interest_id", name="uq_student_interest"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    interest_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("interests.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="interests")
    interest: Mapped["Interest"] = relationship("Interest", back_populates="student_interests")

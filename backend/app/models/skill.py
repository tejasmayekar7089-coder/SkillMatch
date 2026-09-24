from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid
from app.models.enums import SkillLevel

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile
    from app.models.opportunity import OpportunitySkill


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __init__(self, **kwargs):
        if "normalized_name" not in kwargs and "name" in kwargs and kwargs["name"]:
            kwargs["normalized_name"] = kwargs["name"].strip().lower()
        super().__init__(**kwargs)

    # Relationships
    student_skills: Mapped[List["StudentSkill"]] = relationship(
        "StudentSkill", back_populates="skill", cascade="all, delete-orphan"
    )
    opportunity_skills: Mapped[List["OpportunitySkill"]] = relationship(
        "OpportunitySkill", back_populates="skill", cascade="all, delete-orphan"
    )


class StudentSkill(Base, TimestampMixin):
    __tablename__ = "student_skills"
    __table_args__ = (
        UniqueConstraint("student_profile_id", "skill_id", name="uq_student_skill"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    proficiency: Mapped[str] = mapped_column(String(50), default="Beginner", nullable=False)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    level: Mapped[SkillLevel] = mapped_column(
        Enum(SkillLevel, native_enum=False, length=50),
        default=SkillLevel.BEGINNER,
        nullable=False,
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_via: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="student_skills")

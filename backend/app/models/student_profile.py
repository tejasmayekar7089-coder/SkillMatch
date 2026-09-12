from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.skill import StudentSkill
    from app.models.interest import StudentInterest
    from app.models.project import Project
    from app.models.certification import Certification
    from app.models.application import Application
    from app.models.recommendation import Recommendation
    from app.models.skill_gap import SkillGap


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    # Academic details
    college: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    university: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    degree: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    academic_year: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    year: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    graduation_year: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    graduation_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gpa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Preferences & Background
    preferred_domains: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_locations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_work_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metrics
    verified_profile_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profile_strength: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    match_confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    target_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student_profile")
    skills: Mapped[List["StudentSkill"]] = relationship(
        "StudentSkill", back_populates="student_profile", cascade="all, delete-orphan"
    )
    interests: Mapped[List["StudentInterest"]] = relationship(
        "StudentInterest", back_populates="student_profile", cascade="all, delete-orphan"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="student_profile", cascade="all, delete-orphan"
    )
    certifications: Mapped[List["Certification"]] = relationship(
        "Certification", back_populates="student_profile", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="student_profile", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="student_profile", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[List["SkillGap"]] = relationship(
        "SkillGap", back_populates="student_profile", cascade="all, delete-orphan"
    )

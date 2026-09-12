from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid
from app.models.enums import EligibilityStatus, OpportunityCategory, SkillLevel, WorkMode, OpportunityStatus

if TYPE_CHECKING:
    from app.models.skill import Skill
    from app.models.saved_opportunity import SavedOpportunity
    from app.models.application import Application
    from app.models.recommendation import Recommendation


class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    organization: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    organization_logo_text: Mapped[str] = mapped_column(String(10), default="ORG", nullable=False)
    organization_subtext: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # 7 Required Categories strictly mapped to Enum
    category: Mapped[OpportunityCategory] = mapped_column(
        Enum(OpportunityCategory, name="opportunity_category", create_type=False),
        index=True,
        nullable=False,
    )
    category_label: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    mode: Mapped[WorkMode] = mapped_column(
        Enum(WorkMode, name="work_mode", create_type=False),
        default=WorkMode.REMOTE,
        nullable=False,
    )
    compensation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    deadline: Mapped[str] = mapped_column(String(50), nullable=False)
    deadline_days_remaining: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    posted_ago: Mapped[str] = mapped_column(String(50), default="Recently", nullable=False)
    duration: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cohort_size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    preferred_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    eligibility_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    degree_requirements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    branch_requirements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    academic_year_requirements: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    experience_requirements: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    application_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    key_responsibilities: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    requirements: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    stages: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    match_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    match_breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    matched_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)

    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    eligibility_status: Mapped[EligibilityStatus] = mapped_column(
        Enum(EligibilityStatus, name="eligibility_status", create_type=False),
        default=EligibilityStatus.ELIGIBLE,
        nullable=False,
    )
    eligibility_note: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    verified_by: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    image_banner: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # New status field for opportunity lifecycle
    status: Mapped[OpportunityStatus] = mapped_column(
        Enum(OpportunityStatus, name="opportunity_status", create_type=False),
        default=OpportunityStatus.UNMARKED,
        nullable=False,
    )

    # Relationships
    opportunity_skills: Mapped[List["OpportunitySkill"]] = relationship(
        "OpportunitySkill", back_populates="opportunity", cascade="all, delete-orphan"
    )
    saved_by: Mapped[List["SavedOpportunity"]] = relationship(
        "SavedOpportunity", back_populates="opportunity", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="opportunity", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="opportunity", cascade="all, delete-orphan"
    )


class OpportunitySkill(Base, TimestampMixin):
    __tablename__ = "opportunity_skills"
    __table_args__ = (
        UniqueConstraint("opportunity_id", "skill_id", name="uq_opportunity_skill"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False
    )
    level: Mapped[SkillLevel] = mapped_column(
        Enum(SkillLevel, name="skill_level", create_type=False),
        default=SkillLevel.BEGINNER,
        nullable=False,
    )
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verification_source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="opportunity_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="opportunity_skills")

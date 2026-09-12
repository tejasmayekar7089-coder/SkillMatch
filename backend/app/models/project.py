from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    project_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def __init__(self, **kwargs):
        if "title" not in kwargs and "name" in kwargs:
            kwargs["title"] = kwargs["name"]
        elif "name" not in kwargs and "title" in kwargs:
            kwargs["name"] = kwargs["title"]
        if "project_url" not in kwargs and "link" in kwargs:
            kwargs["project_url"] = kwargs["link"]
        elif "link" not in kwargs and "project_url" in kwargs:
            kwargs["link"] = kwargs["project_url"]
        if "skills" not in kwargs and "technologies" in kwargs:
            kwargs["skills"] = list(kwargs["technologies"])
        super().__init__(**kwargs)

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="projects")

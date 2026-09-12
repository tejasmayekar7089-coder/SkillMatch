from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.student_profile import StudentProfile


class Certification(Base, TimestampMixin):
    __tablename__ = "certifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuing_organization: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    credential_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    credential_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __init__(self, **kwargs):
        if "issuing_organization" not in kwargs and "issuer" in kwargs:
            kwargs["issuing_organization"] = kwargs["issuer"]
        elif "issuer" not in kwargs and "issuing_organization" in kwargs:
            kwargs["issuer"] = kwargs["issuing_organization"]
        super().__init__(**kwargs)

    # Relationships
    student_profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="certifications")

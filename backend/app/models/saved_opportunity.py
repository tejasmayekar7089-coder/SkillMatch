from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.opportunity import Opportunity


class SavedOpportunity(Base, TimestampMixin):
    __tablename__ = "saved_opportunities"
    __table_args__ = (
        UniqueConstraint("user_id", "opportunity_id", name="uq_user_saved_opportunity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_opportunities")
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="saved_by")

from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity


class OpportunityEmbedding(Base, TimestampMixin):
    __tablename__ = "opportunity_embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("opportunities.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    embedding: Mapped[List[float]] = mapped_column(JSON, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), default="BAAI/bge-small-en-v1.5", nullable=False)

    # Relationship
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", backref="embedding_record")

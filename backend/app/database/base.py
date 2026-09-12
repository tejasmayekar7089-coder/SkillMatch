import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Generate tablename automatically in snake_case
        name = cls.__name__
        chars = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                chars.append("_")
            chars.append(char.lower())
        return "".join(chars)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

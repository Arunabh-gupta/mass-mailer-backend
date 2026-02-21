from datetime import datetime
import uuid
from sqlalchemy import DateTime, String
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class Contact(Base):
    """Email recipients: recruiters, hiring managers, or any other contact."""
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

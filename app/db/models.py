import uuid
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    input_type: Mapped[str] = mapped_column(String(16), nullable=False)

    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("status IN ('queued','processing','completed','failed')", name="ck_jobs_status"),
        CheckConstraint("input_type IN ('url','text')", name="ck_jobs_input_type"),
        CheckConstraint(
            "(url IS NOT NULL AND text IS NULL) OR (url IS NULL AND text IS NOT NULL)",
            name="ck_jobs_exactly_one_input",
        ),
    )


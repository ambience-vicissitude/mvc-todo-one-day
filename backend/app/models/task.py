import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import TASK_TITLE_MAX_LENGTH
from app.models.base import Base


class TaskStatus(enum.StrEnum):
    """Allowed lifecycle states for a task."""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Task(Base):
    """SQLAlchemy model for a task owned by one and only one user."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(TASK_TITLE_MAX_LENGTH))
    description: Mapped[str] = mapped_column(Text, default="")
    # Stored as VARCHAR (not a native PG enum) so adding a status needs no ALTER TYPE.
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            native_enum=False,
            length=20,
            values_callable=lambda e: [member.value for member in e],
        ),
        default=TaskStatus.TODO,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

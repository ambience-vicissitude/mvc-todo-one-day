"""Request and response schemas for task API data."""

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.core.constants import TASK_DESCRIPTION_MAX_LENGTH, TASK_TITLE_MAX_LENGTH
from app.models.task import TaskStatus

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=TASK_TITLE_MAX_LENGTH)]


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: Title
    description: str = Field(default="", max_length=TASK_DESCRIPTION_MAX_LENGTH)
    status: TaskStatus = TaskStatus.TODO
    due_date: date | None = None


class TaskUpdate(BaseModel):
    """PATCH schema; omitted values stay unchanged and only due_date can be cleared with null."""

    title: Title | None = None
    description: str | None = Field(default=None, max_length=TASK_DESCRIPTION_MAX_LENGTH)
    status: TaskStatus | None = None
    due_date: date | None = None


class TaskRead(BaseModel):
    """Response schema built from a SQLAlchemy Task model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    updated_at: datetime


# Unused schema follows... breaks YAGNI, but this is an assignment
# TRIM: Hard deletion vs soft deletion


class TaskDelete(BaseModel):
    """Schema for deleting task data."""

    model_config = ConfigDict(from_attributes=True)

    id: int

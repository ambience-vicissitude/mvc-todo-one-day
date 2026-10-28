"""Composition root: wires controllers -> services -> repositories (dependency injection).

This module defines dependency injection for this FastAPI app,
providing services and repositories to controllers,
and handling the current user context.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.events import EventPublisher, LoggingEventPublisher
from app.core.exceptions import NotFoundError
from app.core.security import get_current_user_id
from app.db.session import get_db
from app.models.user import User
from app.repositories.task_repo import TaskRepository
from app.repositories.user_repo import UserRepository
from app.services.task_service import TaskService
from app.services.user_service import UserService

DbSession = Annotated[Session, Depends(get_db)]


@lru_cache
def get_event_publisher() -> EventPublisher:
    """Get the event publisher instance.

    Cached as a process-wide singleton.

    Returns:
        EventPublisher: The event publisher instance.
    """
    # TRIM: Swap in an MQ adapter here (see app/core/events.py).
    return LoggingEventPublisher()


def get_user_service(db: DbSession) -> UserService:
    """Get the user service instance.

    Args:
        db (DbSession): The database session.

    Returns:
        UserService: The user service instance.
    """
    return UserService(UserRepository(db))


def get_task_service(db: DbSession, events: Annotated[EventPublisher, Depends(get_event_publisher)]) -> TaskService:
    """Get the task service instance.

    Args:
        db (DbSession): The database session.
        events (EventPublisher): The event publisher instance.

    Returns:
        TaskService: The task service instance.
    """
    return TaskService(TaskRepository(db), events)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_current_user(user_id: Annotated[int, Depends(get_current_user_id)], users: UserServiceDep) -> User:
    """Get the current user instance.

    Args:
        user_id (int): The ID of the current user.
        users (UserService): The user service instance.

    Returns:
        User: The current user instance.

    Raises:
        HTTPException: If the user is not found.
    """
    try:
        return users.get(user_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown user") from exc


CurrentUser = Annotated[User, Depends(get_current_user)]

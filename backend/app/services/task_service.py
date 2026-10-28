"""Business logic for task operations."""

import logging
from datetime import date

from app.core.events import DomainEvent, EventPublisher
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.task import Task, TaskStatus
from app.repositories.task_repo import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger("app.services.task")

# Fields a client may explicitly clear by sending null.
_NULLABLE_FIELDS = {"due_date"}


class TaskService:
    """Business rules: ownership, due-date validity, and event publication.

    Knows nothing about HTTP or SQL (those live in controllers and repositories).
    """

    def __init__(self, repo: TaskRepository, events: EventPublisher) -> None:
        """Initialize with task persistence and event-publishing dependencies."""
        self._repo = repo
        self._events = events

    def create(self, user_id: int, data: TaskCreate) -> Task:
        """Create a task for the user and publish its creation event.

        Raises:
            BusinessRuleError: If the due date is in the past.
        """
        self._check_due_date(data.due_date)
        task = self._repo.save(Task(user_id=user_id, **data.model_dump()))
        logger.info("task created id=%s user=%s", task.id, user_id)
        self._events.publish(DomainEvent("task.created", {"task_id": task.id, "user_id": user_id}))
        return task

    def list_for_user(self, user_id: int, status: TaskStatus | None = None) -> list[Task]:
        """List a user's tasks, optionally filtered by status.

        Args:
            user_id: Owner of the tasks to list.
            status: Optional status filter.

        Returns:
            The user's matching tasks, ordered by the repository.
        """
        return self._repo.list_for_user(user_id, status)

    def get(self, user_id: int, task_id: int) -> Task:
        """Get a user's task or raise NotFoundError for missing and foreign-owned tasks.

        Raises:
            NotFoundError: If the task is missing or belongs to another user.
        """
        task = self._repo.get_for_user(user_id, task_id)
        if task is None:
            # Same error for "missing" and "someone else's" so ids cannot be probed.
            raise NotFoundError(f"Task {task_id} not found")
        return task

    def update(self, user_id: int, task_id: int, data: TaskUpdate) -> Task:
        """Apply changes and publish an event only when status changes.

        Raises:
            NotFoundError: If the task is missing or belongs to another user.
            BusinessRuleError: If the updated due date is in the past.
        """
        task = self.get(user_id, task_id)
        changes = {
            key: value
            for key, value in data.model_dump(exclude_unset=True).items()
            if value is not None or key in _NULLABLE_FIELDS
        }
        if "due_date" in changes and changes["due_date"] != task.due_date:
            self._check_due_date(changes["due_date"])

        previous_status = task.status
        for key, value in changes.items():
            setattr(task, key, value)
        task = self._repo.save(task)
        logger.info("task updated id=%s user=%s", task.id, user_id)

        if task.status != previous_status:
            # Publish a status change event
            self._events.publish(
                DomainEvent(
                    "task.status_changed",
                    {"task_id": task.id, "from": previous_status, "to": task.status},
                )
            )
        return task

    def delete(self, user_id: int, task_id: int) -> None:
        """Delete a user's task and publish its deletion event.

        Raises:
            NotFoundError: If the task is missing or belongs to another user.
        """
        task = self.get(user_id, task_id)
        self._repo.delete(task)
        logger.info("task deleted id=%s user=%s", task_id, user_id)
        self._events.publish(DomainEvent("task.deleted", {"task_id": task_id, "user_id": user_id}))

    @staticmethod
    def _check_due_date(due_date: date | None) -> None:
        """Reject due dates earlier than today.

        Raises:
            BusinessRuleError: If the due date is in the past.
        """

        if due_date is not None and due_date < date.today():
            raise BusinessRuleError("Due date cannot be in the past")

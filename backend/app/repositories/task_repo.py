"""SQLAlchemy data access for user-scoped tasks."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus


class TaskRepository:
    """Data access only. Every query is scoped by user_id, so ownership cannot be bypassed."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, task: Task) -> Task:
        """Persist and return a task, committing the current transaction.

        Args:
            task: The task to persist.

        Returns:
            The persisted task with updated fields (e.g., ID, timestamps).
        """

        # Note: add-commit is best, violations will be caught at commit time
        self._session.add(task)
        self._session.commit()
        self._session.refresh(task)
        return task

    def get_for_user(self, user_id: int, task_id: int) -> Task | None:
        """Return a task only when it belongs to the given user; otherwise return None.

        Args:
            user_id: Owner of the task.
            task_id: ID of the task to retrieve.

        Returns:
            The task if it exists and belongs to the user, else None.
        """

        return self._session.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))

    def list_for_user(self, user_id: int, status: TaskStatus | None = None) -> list[Task]:
        """List a user's tasks, optionally filtered by status.

        Args:
            user_id: Owner of the tasks to list.
            status: Optional status filter.

        Returns:
            The user's matching tasks, ordered by the repository.
        """

        # TRIM: Eager-load future relationships to avoid N+1 queries; paginate if this list grows.
        # If the relationship becomes more complex, and lazy loading causes N+1 queries,
        # consider using joinedload or selectinload.
        stmt = select(Task).where(Task.user_id == user_id).order_by(Task.id.desc())
        if status is not None:
            stmt = stmt.where(Task.status == status)
        return list(self._session.scalars(stmt))

    def delete(self, task: Task) -> None:
        """Delete a task and commit the current transaction.

        Args:
            task: The task to delete.
        """

        self._session.delete(task)
        self._session.commit()

"""Repository for accessing user data.

Note: Repositories keep a data-access layer for SQLAlchemy models, separating it from
business logic.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data access only: no business rules."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, name: str) -> User:
        """Add a new user with the given name.

        Args:
            name (str): The name of the user to add.

        Returns:
            User: The newly created user instance.
        """

        user = User(name=name)

        self._session.add(user)
        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise

        return user

    def get(self, user_id: int) -> User | None:
        """Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user instance if found, else None.
        """

        return self._session.get(User, user_id)

    def list_all(self) -> list[User]:
        """List all users ordered by name.

        Returns:
            list[User]: A list of all user instances.
        """

        # TRIM: Could add pagination, filtering, etc. if the user list grows large
        # TRIM: Could also add sorting options, e.g., by creation date or ID if needed
        return list(self._session.scalars(select(User).order_by(User.name)))

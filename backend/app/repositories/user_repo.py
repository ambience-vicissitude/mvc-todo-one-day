"""Repository for accessing user data.

Note: Repositories keep a data-access layer for SQLAlchemy models, separating it from business logic.
"""

from sqlalchemy import select
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

        # pre-check for existing user with the same name
        if self.get_by_name(name) is not None:
            raise ValueError(f"User with name '{name}' already exists.")

        user = User(name=name)

        # Note: add-commit is best, violations will be caught at commit time
        self._session.add(user)
        self._session.commit()

        return user

    def get(self, user_id: int) -> User | None:
        """Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user instance if found, else None.
        """

        return self._session.get(User, user_id)

    def get_by_name(self, name: str) -> User | None:
        """Get a user by their name.

        Args:
            name (str): The name of the user to retrieve.

        Returns:
            User | None: The user instance if found, else None.
        """

        # TRIM: Would that duplicate names be a data-integrity problem, use `scalars(query).one_or_none()`
        # Or use `scalars(query).first()` if duplicates is not a problem and you just want the first match.
        # but for a username, it is reasonable to say that this is bad in general,
        # and `one_or_none()` is appropriate, alongside a db constraint
        # `one()` is also possible, but not my recommendation
        return self._session.scalars(select(User).where(User.name == name)).one_or_none()

    def list_all(self) -> list[User]:
        """List all users ordered by name.

        Returns:
            list[User]: A list of all user instances.
        """

        # TRIM: Could add pagination, filtering, etc. if the user list grows large
        # TRIM: Could also add sorting options, e.g., by creation date or ID if needed
        return list(self._session.scalars(select(User).order_by(User.name)))

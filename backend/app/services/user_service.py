"""Service layer for user-related business logic."""

import logging

from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.repositories.user_repo import UserRepository

logger = logging.getLogger("app.services.user")


class UserService:
    """Business logic for user management."""

    def __init__(self, repo: UserRepository) -> None:
        """Initialize the user service with a repository.

        Args:
            repo (UserRepository): The repository for accessing user data.
        """
        self._repo = repo

    def create(self, name: str) -> User:
        """Create a new user with the given name.

        Args:
            name (str): The name of the user to create.

        Returns:
            User: The newly created user instance.

        Raises:
            ConflictError: If a user with the given name already exists.
        """
        if self._repo.get_by_name(name) is not None:
            raise ConflictError(f"User '{name}' already exists")
        user = self._repo.add(name)
        logger.info("user created id=%s", user.id)
        return user

    def get(self, user_id: int) -> User:
        """Get a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User: The user instance if found.

        Raises:
            NotFoundError: If the user with the given ID does not exist.
        """
        user = self._repo.get(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    def list_all(self) -> list[User]:
        """List all users.

        Returns:
            list[User]: A list of all user instances.
        """
        return self._repo.list_all()

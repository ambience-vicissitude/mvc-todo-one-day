"""Domain errors. Services raise these; the controller layer maps them to HTTP (see main.py)."""


class DomainError(Exception):
    """Base class for domain errors."""

    def __init__(self, message: str) -> None:
        """Initialize the domain error with a message.

        Args:
            message (str): The error message.
        """

        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """Raised when a requested entity is not found."""



class ConflictError(DomainError):
    """Raised when a conflict occurs, such as a duplicate entry."""



class BusinessRuleError(DomainError):
    """Raised when a business rule is violated."""


"""Application-level errors. Every one of these is safe to show to an end user."""


class AppError(Exception):
    """Base class for errors that should be surfaced as a friendly message."""


class ValidationError(AppError):
    """Raised when input data fails validation (bad amount, missing field, ...)."""


class NotFoundError(AppError):
    """Raised when a referenced record (member, expense, income, budget) doesn't exist."""


class DatabaseError(AppError):
    """Raised when a database operation fails unexpectedly."""

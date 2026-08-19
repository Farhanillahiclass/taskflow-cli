"""
Custom exception hierarchy for TaskFlow CLI.

Using dedicated exception types (instead of generic Exception/ValueError
everywhere) keeps error handling in main.py precise and makes intent
explicit when reading the code.
"""


class TaskFlowError(Exception):
    """Base class for all application-specific errors."""


class InvalidTaskDataError(TaskFlowError):
    """Raised when task data fails validation (empty title, bad date, etc.)."""


class TaskNotFoundError(TaskFlowError):
    """Raised when a task ID does not exist in the manager."""


class StorageError(TaskFlowError):
    """Raised when reading from or writing to the JSON storage file fails."""

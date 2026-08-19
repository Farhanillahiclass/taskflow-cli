"""
Task domain model.

A Task is a plain data-holding object with validation built into its
constructor / setters so that an invalid Task can never exist once
constructed successfully (fail-fast principle).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from taskflow.exceptions import InvalidTaskDataError

VALID_PRIORITIES = ("Low", "Medium", "High")
VALID_STATUSES = ("Pending", "In Progress", "Completed")
DATE_FORMAT = "%Y-%m-%d"


@dataclass
class Task:
    """Represents a single task in the task management console."""

    task_id: int
    title: str
    description: str = ""
    priority: str = "Medium"
    due_date: Optional[str] = None  # stored as "YYYY-MM-DD" string or None
    status: str = "Pending"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self) -> None:
        self.title = self._validate_title(self.title)
        self.priority = self._validate_priority(self.priority)
        self.status = self._validate_status(self.status)
        self.due_date = self._validate_due_date(self.due_date)

    # ---------- validation helpers ----------

    @staticmethod
    def _validate_title(title: str) -> str:
        if not isinstance(title, str) or not title.strip():
            raise InvalidTaskDataError("Task title cannot be empty.")
        return title.strip()

    @staticmethod
    def _validate_priority(priority: str) -> str:
        priority = (priority or "Medium").strip().title()
        if priority not in VALID_PRIORITIES:
            raise InvalidTaskDataError(
                f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}."
            )
        return priority

    @staticmethod
    def _validate_status(status: str) -> str:
        status = (status or "Pending").strip().title()
        if status not in VALID_STATUSES:
            raise InvalidTaskDataError(
                f"Invalid status '{status}'. Must be one of {VALID_STATUSES}."
            )
        return status

    @staticmethod
    def _validate_due_date(due_date: Optional[str]) -> Optional[str]:
        if due_date in (None, ""):
            return None
        try:
            datetime.strptime(due_date, DATE_FORMAT)
        except ValueError as exc:
            raise InvalidTaskDataError(
                f"Invalid due date '{due_date}'. Expected format YYYY-MM-DD."
            ) from exc
        return due_date

    # ---------- behaviour ----------

    def is_overdue(self) -> bool:
        """A task is overdue if it has a due date in the past and isn't completed."""
        if self.due_date is None or self.status == "Completed":
            return False
        due = datetime.strptime(self.due_date, DATE_FORMAT).date()
        return due < date.today()

    def mark_completed(self) -> None:
        self.status = "Completed"

    # ---------- serialization ----------

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        try:
            return cls(
                task_id=data["task_id"],
                title=data["title"],
                description=data.get("description", ""),
                priority=data.get("priority", "Medium"),
                due_date=data.get("due_date"),
                status=data.get("status", "Pending"),
                created_at=data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
        except KeyError as exc:
            raise InvalidTaskDataError(f"Task record missing required field: {exc}") from exc

    def __str__(self) -> str:
        overdue_flag = " [OVERDUE]" if self.is_overdue() else ""
        due = self.due_date or "—"
        return (
            f"[{self.task_id:03}] {self.title} | Priority: {self.priority} | "
            f"Status: {self.status} | Due: {due}{overdue_flag}"
        )

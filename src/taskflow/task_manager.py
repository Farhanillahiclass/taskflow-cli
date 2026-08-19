"""
TaskManager: the central service class that owns the in-memory task
collection and coordinates persistence, validation, search, filtering
and sorting.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from taskflow.exceptions import InvalidTaskDataError, StorageError, TaskNotFoundError
from taskflow.storage import JSONStorage
from taskflow.task import Task

SORT_FIELDS = ("due_date", "priority", "status", "title", "task_id")
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}


class TaskManager:
    """CRUD + search/filter/sort + persistence for Task objects."""

    def __init__(self, storage: JSONStorage) -> None:
        self._storage = storage
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1
        self.load()

    # ---------- persistence ----------

    def load(self) -> None:
        records = self._storage.load()
        self._tasks = {}
        max_id = 0
        for record in records:
            try:
                task = Task.from_dict(record)
            except InvalidTaskDataError:
                # Skip corrupted individual records rather than crashing the app.
                continue
            self._tasks[task.task_id] = task
            max_id = max(max_id, task.task_id)
        self._next_id = max_id + 1

    def save(self) -> None:
        records = [t.to_dict() for t in self._tasks.values()]
        self._storage.save(records)

    # ---------- CRUD ----------

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "Medium",
        due_date: Optional[str] = None,
    ) -> Task:
        task = Task(
            task_id=self._next_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        self._tasks[task.task_id] = task
        self._next_id += 1
        self.save()
        return task

    def get_task(self, task_id: int) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise TaskNotFoundError(f"No task found with ID {task_id}.") from exc

    def update_task(self, task_id: int, **fields) -> Task:
        existing = self.get_task(task_id)
        data = existing.to_dict()
        data.update({k: v for k, v in fields.items() if v is not None})
        updated = Task.from_dict(data)  # re-validates
        self._tasks[task_id] = updated
        self.save()
        return updated

    def delete_task(self, task_id: int) -> None:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"No task found with ID {task_id}.")
        del self._tasks[task_id]
        self.save()

    def mark_completed(self, task_id: int) -> Task:
        task = self.get_task(task_id)
        task.mark_completed()
        self.save()
        return task

    # ---------- query ----------

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def search(self, keyword: str) -> List[Task]:
        keyword = keyword.strip().lower()
        return [
            t for t in self._tasks.values()
            if keyword in t.title.lower() or keyword in t.description.lower()
        ]

    def filter_by_priority(self, priority: str) -> List[Task]:
        priority = priority.strip().title()
        return [t for t in self._tasks.values() if t.priority == priority]

    def filter_by_status(self, status: str) -> List[Task]:
        status = status.strip().title()
        return [t for t in self._tasks.values() if t.status == status]

    def filter_overdue(self) -> List[Task]:
        return [t for t in self._tasks.values() if t.is_overdue()]

    def sort_tasks(self, field: str = "due_date", reverse: bool = False) -> List[Task]:
        if field not in SORT_FIELDS:
            raise InvalidTaskDataError(f"Cannot sort by '{field}'. Choose from {SORT_FIELDS}.")

        def sort_key(t: Task):
            if field == "due_date":
                return t.due_date or "9999-99-99"  # tasks with no due date sort last
            if field == "priority":
                return PRIORITY_RANK.get(t.priority, 99)
            return getattr(t, field)

        return sorted(self._tasks.values(), key=sort_key, reverse=reverse)

    # ---------- reporting ----------

    def status_summary(self) -> Dict[str, int]:
        summary = {status: 0 for status in ("Pending", "In Progress", "Completed")}
        for t in self._tasks.values():
            summary[t.status] = summary.get(t.status, 0) + 1
        summary["Overdue"] = len(self.filter_overdue())
        summary["Total"] = len(self._tasks)
        return summary

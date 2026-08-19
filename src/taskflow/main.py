"""
TaskFlow CLI — a menu-driven Task Management Console.

Author: Muhammad Farhan
Run with:  python -m taskflow.main
(from the project's src/ directory, or via the run.py launcher in the
project root — see README.md)
"""

from __future__ import annotations

import os

from taskflow.exceptions import InvalidTaskDataError, StorageError, TaskFlowError, TaskNotFoundError
from taskflow.task_manager import TaskManager
from taskflow.storage import JSONStorage

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tasks.json")

MENU = """
==================== TaskFlow CLI ====================
 1. Add Task
 2. View All Tasks
 3. Search Tasks (by keyword)
 4. Filter Tasks (by priority / status / overdue)
 5. Sort Tasks
 6. Update Task
 7. Mark Task as Completed
 8. Delete Task
 9. Summary Report
 0. Exit
========================================================
"""


def prompt(msg: str) -> str:
    return input(msg).strip()


def print_tasks(tasks) -> None:
    if not tasks:
        print("  (no tasks to show)")
        return
    for t in tasks:
        print(" ", t)


def handle_add(manager: TaskManager) -> None:
    title = prompt("Title: ")
    description = prompt("Description (optional): ")
    priority = prompt("Priority [Low/Medium/High] (default Medium): ") or "Medium"
    due_date = prompt("Due date YYYY-MM-DD (optional, press Enter to skip): ") or None
    task = manager.add_task(title, description, priority, due_date)
    print(f"Task added successfully -> {task}")


def handle_view(manager: TaskManager) -> None:
    print_tasks(manager.list_tasks())


def handle_search(manager: TaskManager) -> None:
    keyword = prompt("Enter keyword: ")
    print_tasks(manager.search(keyword))


def handle_filter(manager: TaskManager) -> None:
    print(" a) By priority   b) By status   c) Overdue only")
    choice = prompt("Choose filter type: ").lower()
    if choice == "a":
        value = prompt("Priority [Low/Medium/High]: ")
        print_tasks(manager.filter_by_priority(value))
    elif choice == "b":
        value = prompt("Status [Pending/In Progress/Completed]: ")
        print_tasks(manager.filter_by_status(value))
    elif choice == "c":
        print_tasks(manager.filter_overdue())
    else:
        print("Invalid filter option.")


def handle_sort(manager: TaskManager) -> None:
    field = prompt("Sort by [due_date/priority/status/title/task_id]: ") or "due_date"
    reverse = prompt("Descending? (y/N): ").lower() == "y"
    print_tasks(manager.sort_tasks(field, reverse))


def handle_update(manager: TaskManager) -> None:
    task_id = int(prompt("Task ID to update: "))
    print("Leave a field blank to keep its current value.")
    title = prompt("New title: ") or None
    description = prompt("New description: ") or None
    priority = prompt("New priority: ") or None
    due_date = prompt("New due date (YYYY-MM-DD): ") or None
    status = prompt("New status [Pending/In Progress/Completed]: ") or None
    task = manager.update_task(
        task_id, title=title, description=description,
        priority=priority, due_date=due_date, status=status,
    )
    print(f"Task updated -> {task}")


def handle_complete(manager: TaskManager) -> None:
    task_id = int(prompt("Task ID to mark completed: "))
    task = manager.mark_completed(task_id)
    print(f"Marked completed -> {task}")


def handle_delete(manager: TaskManager) -> None:
    task_id = int(prompt("Task ID to delete: "))
    manager.delete_task(task_id)
    print(f"Task {task_id} deleted.")


def handle_summary(manager: TaskManager) -> None:
    summary = manager.status_summary()
    print("\n---- Summary Report ----")
    for key, value in summary.items():
        print(f"  {key:12}: {value}")


def main() -> None:
    storage = JSONStorage(os.path.normpath(DATA_FILE))
    manager = TaskManager(storage)

    actions = {
        "1": handle_add,
        "2": handle_view,
        "3": handle_search,
        "4": handle_filter,
        "5": handle_sort,
        "6": handle_update,
        "7": handle_complete,
        "8": handle_delete,
        "9": handle_summary,
    }

    print("Welcome to TaskFlow CLI — Task Management Console")
    print(f"Data file: {os.path.normpath(DATA_FILE)}")

    while True:
        print(MENU)
        choice = prompt("Select an option: ")

        if choice == "0":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid option. Please choose a number from the menu.")
            continue

        try:
            action(manager)
        except ValueError:
            print("Error: Please enter a valid number for Task ID.")
        except TaskNotFoundError as exc:
            print(f"Error: {exc}")
        except InvalidTaskDataError as exc:
            print(f"Validation error: {exc}")
        except StorageError as exc:
            print(f"Storage error: {exc}")
        except TaskFlowError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()

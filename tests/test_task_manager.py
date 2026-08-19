"""
Unit tests for TaskFlow CLI.

Run with:  python -m unittest discover -s tests -v
(from the project root, after running the setup in README.md)

Covers: normal operation, invalid input, boundary/edge cases,
duplicate-like updates, and missing-record handling.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from taskflow.exceptions import InvalidTaskDataError, TaskNotFoundError
from taskflow.storage import JSONStorage
from taskflow.task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # Use a temporary file per test so tests never touch real data/tasks.json
        self.tmp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.tmp_dir, "tasks.json")
        self.storage = JSONStorage(self.data_file)
        self.manager = TaskManager(self.storage)

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        os.rmdir(self.tmp_dir)

    # ---- Test Case 1: Normal add ----
    def test_add_task_normal(self):
        task = self.manager.add_task("Write report", "Q3 summary", "High", "2026-12-01")
        self.assertEqual(task.task_id, 1)
        self.assertEqual(task.title, "Write report")
        self.assertEqual(len(self.manager.list_tasks()), 1)

    # ---- Test Case 2: Invalid input - empty title ----
    def test_add_task_empty_title_raises(self):
        with self.assertRaises(InvalidTaskDataError):
            self.manager.add_task("   ", "no title", "Low", None)

    # ---- Test Case 3: Invalid input - bad date format ----
    def test_add_task_invalid_date_raises(self):
        with self.assertRaises(InvalidTaskDataError):
            self.manager.add_task("Fix bug", priority="High", due_date="19-08-2026")

    # ---- Test Case 4: Boundary - overdue detection at exact past date ----
    def test_overdue_task_detected(self):
        task = self.manager.add_task("Old task", due_date="2020-01-01")
        self.assertTrue(task.is_overdue())
        overdue_list = self.manager.filter_overdue()
        self.assertIn(task.task_id, [t.task_id for t in overdue_list])

    # ---- Test Case 5: Completed tasks are never overdue (boundary rule) ----
    def test_completed_task_not_overdue(self):
        task = self.manager.add_task("Old but done", due_date="2020-01-01")
        self.manager.mark_completed(task.task_id)
        self.assertFalse(self.manager.get_task(task.task_id).is_overdue())

    # ---- Test Case 6: Missing data - operate on non-existent task ID ----
    def test_get_missing_task_raises(self):
        with self.assertRaises(TaskNotFoundError):
            self.manager.get_task(999)

    # ---- Test Case 7: Duplicate-like scenario - two tasks with identical titles are both allowed with unique IDs ----
    def test_duplicate_titles_get_unique_ids(self):
        t1 = self.manager.add_task("Daily standup")
        t2 = self.manager.add_task("Daily standup")
        self.assertNotEqual(t1.task_id, t2.task_id)
        self.assertEqual(len(self.manager.search("standup")), 2)

    # ---- Test Case 8: Persistence - data survives reload from disk ----
    def test_persistence_across_reload(self):
        self.manager.add_task("Persisted task", priority="Low")
        reloaded_manager = TaskManager(JSONStorage(self.data_file))
        self.assertEqual(len(reloaded_manager.list_tasks()), 1)
        self.assertEqual(reloaded_manager.list_tasks()[0].title, "Persisted task")

    # ---- Test Case 9: Sorting by priority orders High before Low ----
    def test_sort_by_priority(self):
        self.manager.add_task("Low task", priority="Low")
        self.manager.add_task("High task", priority="High")
        sorted_tasks = self.manager.sort_tasks("priority")
        self.assertEqual(sorted_tasks[0].priority, "High")

    # ---- Test Case 10: Deleting a task removes it and further access raises ----
    def test_delete_task(self):
        task = self.manager.add_task("Temp task")
        self.manager.delete_task(task.task_id)
        with self.assertRaises(TaskNotFoundError):
            self.manager.get_task(task.task_id)


if __name__ == "__main__":
    unittest.main()

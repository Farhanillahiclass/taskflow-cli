# TaskFlow CLI — Task Management Console

A menu-driven, JSON-persisted task management application built in pure
Python for the **Learn Depth Machine Learning Internship — Track 1,
Level-4 Python Project Challenge** (Project #8: Task Management Console).

**Author:** Muhammad Farhan
**LinkedIn:** https://www.linkedin.com/in/muhammadfarhanmrs
**Repository:** https://github.com/Farhanillahiclass/taskflow-cli

---

## Problem Statement

Manage tasks with priorities, due dates, status, search and persistence.
The application must produce an overdue-aware task manager: a task list
plus a status report, driven entirely from the command line.

## Objective

Build a functional, well-structured Python console application that
demonstrates functions, OOP, data structures, validation, exception
handling, and JSON-based data persistence — while remaining simple
enough to fully understand and defend in a technical discussion.

## Features

- **Add** tasks with title, description, priority, and due date
- **View** all tasks in a readable, aligned format
- **Search** tasks by keyword (title or description)
- **Filter** tasks by priority, by status, or overdue-only
- **Sort** tasks by due date, priority, status, title, or ID (ascending/descending)
- **Update** any task field without losing existing data
- **Mark tasks completed**
- **Delete** tasks
- **Summary report**: counts by status + overdue count
- **Automatic overdue detection** (due date in the past, not completed)
- **JSON persistence** — data survives between runs, saved atomically
- **Input validation** on every field (title, priority, status, date format)
- **Custom exception hierarchy** for precise, user-friendly error messages
- Corrupted individual records in the data file are skipped safely rather
  than crashing the whole app

## Technologies Used

- Python 3.9+ (standard library only — **zero cost**, no external
  dependencies required)
- `dataclasses`, `json`, `os`, `datetime`, `unittest` (all built-in)

## Project Structure

```
taskflow-cli/
├── run.py                       # Launcher — run this file
├── src/
│   └── taskflow/
│       ├── __init__.py
│       ├── main.py              # CLI menu and input handling
│       ├── task.py              # Task model (validation + serialization)
│       ├── task_manager.py      # CRUD, search, filter, sort, reporting
│       ├── storage.py           # JSON read/write (atomic save)
│       └── exceptions.py        # Custom exception hierarchy
├── data/
│   └── tasks.json               # Persisted task data (auto-created)
├── tests/
│   └── test_task_manager.py     # 10 unit tests (unittest)
├── screenshots/                 # Demonstration evidence
├── README.md
└── report.md                    # Project report
```

## Installation / Setup Instructions

No external packages are required.

1. Ensure Python 3.9 or later is installed:
   ```bash
   python3 --version
   ```
2. Clone the repository:
   ```bash
   git clone https://github.com/Farhanillahiclass/taskflow-cli.git
   cd taskflow-cli
   ```

That's it — no `pip install` needed.

## How to Run the Project

From the project root:

```bash
python run.py
```

or, if `python3` is the correct alias on your system:

```bash
python3 run.py
```

Then follow the on-screen numbered menu (1–9, 0 to exit).

### Example session

```
Select an option: 1
Title: Finish internship project
Description (optional): Submit before deadline
Priority [Low/Medium/High] (default Medium): High
Due date YYYY-MM-DD (optional, press Enter to skip): 2026-08-25
Task added successfully -> [001] Finish internship project | Priority: High | Status: Pending | Due: 2026-08-25
```

## Testing

Run the full test suite (10 test cases) from the project root:

```bash
python -m unittest discover -s tests -v
```

Expected result: `Ran 10 tests ... OK`

**Test coverage includes:**

| # | Test | Type |
|---|------|------|
| 1 | Add a valid task | Normal |
| 2 | Reject empty title | Invalid input |
| 3 | Reject malformed due date | Invalid input |
| 4 | Detect an overdue task | Boundary |
| 5 | Completed task is never overdue | Boundary rule |
| 6 | Access a non-existent task ID | Missing data |
| 7 | Two tasks with identical titles get unique IDs | Duplicate-like |
| 8 | Data persists correctly after reload from disk | Persistence |
| 9 | Sorting by priority orders High before Low | Normal |
| 10 | Deleting a task removes it permanently | Normal |

## Screenshots / Demonstration Evidence

See the `screenshots/` folder. `sample_run_transcript.txt` documents an
example session; replace it with actual terminal screenshots (PNG) showing:
- Adding a task
- Viewing/filtering/sorting tasks
- The summary report
- An error case (e.g. invalid date) being handled gracefully

## Limitations

- Single-user, local, single-file JSON storage (no concurrent multi-user access)
- No due-time (time-of-day) tracking, only due dates
- No recurring/repeating tasks
- Terminal-only interface (no GUI/web front-end)

## Future Improvements

- Add a `--export csv` option for reports
- Add reminder/notification support for tasks due soon
- Add tagging/categories in addition to priority
- Optional colorized terminal output for priority/status
- Migrate storage to SQLite for larger task volumes while keeping the same `TaskManager` interface

## Use of AI Tools

AI assistance (Claude) was used to help scaffold the project structure,
review code organization, and speed up boilerplate (CLI menu wiring,
test skeletons). The design decisions, logic, and final code are fully
understood by the author and can be explained/defended during evaluation.

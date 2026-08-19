# Project Report — TaskFlow CLI (Task Management Console)

**Author:** Muhammad Farhan
**LinkedIn:** https://www.linkedin.com/in/muhammadfarhanmrs
**Internship:** Learn Depth Machine Learning Internship — Track 1
**Project selected:** #8 — Task Management Console

---

## 1. Problem Understanding

The task required building a console application to manage tasks with
priorities, due dates, and status, along with search and persistence
support, producing an "overdue-aware" task manager. The core challenge
was not the individual features in isolation, but designing a clean
separation between the task **data model**, the **business logic**
(CRUD, search, filter, sort), and the **persistence layer**, so that
each piece stays simple, testable, and independently understandable.

## 2. Proposed Approach

I split the application into four layers, each with a single
responsibility:

1. **`Task`** — a `dataclass` representing one task, with all field
   validation happening in `__post_init__` so an invalid `Task` object
   can never exist once constructed.
2. **`TaskManager`** — owns the in-memory collection of tasks (a
   `dict` keyed by `task_id` for O(1) lookups) and exposes CRUD,
   search, filter, sort, and reporting methods.
3. **`JSONStorage`** — handles reading/writing the JSON file on disk,
   including atomic writes (write to a temp file, then `os.replace`)
   to avoid corrupting data if the program is interrupted mid-save.
4. **`main.py`** — a thin CLI layer that only handles user I/O
   (prompts, printing) and delegates all logic to `TaskManager`,
   catching custom exceptions to show friendly error messages.

This layering means the CLI could be replaced with a web front-end
later without touching the business logic at all.

## 3. Implementation

- **Data structures:** a `dict[int, Task]` for O(1) task lookup by ID;
  lists returned from query methods (`search`, `filter_*`, `sort_tasks`)
  for easy iteration/display.
- **OOP:** `Task` and `TaskManager` are classes with clear single
  responsibilities; a custom exception hierarchy (`TaskFlowError` and
  three subclasses) replaces generic exceptions for precise handling.
- **Validation:** title non-empty, priority restricted to
  Low/Medium/High, status restricted to a fixed set, and due dates
  parsed strictly against `YYYY-MM-DD` — all enforced at the model
  level (`Task.__post_init__`), not scattered across the CLI.
- **Exception handling:** every CLI action is wrapped in a `try/except`
  block in `main.py` catching specific `TaskFlowError` subtypes
  (`TaskNotFoundError`, `InvalidTaskDataError`, `StorageError`) plus
  `ValueError` for bad numeric input, so the app never crashes on bad
  user input.
- **Persistence:** tasks are serialized to/from dictionaries
  (`to_dict`/`from_dict`) and saved as a JSON array after every
  mutating operation. Corrupted individual records are skipped on load
  rather than crashing the whole application.
- **Search/filter/sort:** keyword search across title+description;
  filters by priority, status, or overdue status; sorting by five
  different fields with ascending/descending order, using a
  `PRIORITY_RANK` mapping so priority sorts logically (High → Low)
  rather than alphabetically.

## 4. Important Technical Decisions

- **`dataclass` over a plain class:** reduces boilerplate for
  `__init__`/equality while still allowing custom validation via
  `__post_init__`.
- **Dict-based storage instead of a list:** task lookup/update/delete
  by ID is O(1) instead of O(n) linear search.
- **Atomic file writes:** writing to a `.tmp` file and using
  `os.replace()` avoids leaving a half-written, corrupted JSON file if
  the process is killed mid-save.
- **Custom exception hierarchy:** lets `main.py` give specific,
  actionable error messages instead of a generic "something went
  wrong," and makes the code's failure modes self-documenting.
- **Overdue as a computed property, not a stored field:** `is_overdue()`
  is calculated from `due_date` + today's date at call time, so the
  status is always accurate without needing a background job to update it.

## 5. Testing Performed

10 unit tests were written using Python's built-in `unittest` framework
covering: normal task creation, invalid input rejection (empty title,
malformed date), boundary conditions (overdue detection, completed
tasks never counted as overdue), missing-data handling (operating on a
non-existent task ID), duplicate-title handling, persistence across
reloads, priority-based sorting, and deletion. All 10 tests pass. The
CLI was also manually smoke-tested end-to-end (add → view → summary →
exit) to confirm the menu loop and persistence work together correctly.

## 6. Challenges Encountered & Solutions

- **Challenge:** deciding where validation should live (CLI vs. model).
  **Solution:** moved all validation into `Task.__post_init__`, so the
  model is self-protecting regardless of which layer creates it (CLI,
  tests, or future front-ends).
- **Challenge:** avoiding data loss if the app crashes mid-save.
  **Solution:** implemented atomic writes via a temp file + `os.replace`.
- **Challenge:** keeping "overdue" logic correct without extra stored
  state that could go stale. **Solution:** computed it on demand from
  `due_date` and the current date.

## 7. Future Scope

- Add due-time (not just due-date) precision.
- Add recurring tasks and reminder notifications.
- Export reports to CSV/Markdown.
- Swap `JSONStorage` for a SQLite-backed storage class behind the same
  interface for larger datasets, without changing `TaskManager`.
- Add a simple web UI (Flask) reusing the same `TaskManager`/`Task`
  business logic layer.

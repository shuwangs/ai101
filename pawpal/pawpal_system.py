"""PawPal - Pet Care Scheduling System.

Four core classes:
- ``Task``      : a single care activity (description, time, frequency, status).
- ``Pet``       : a pet's details plus the list of tasks it needs.
- ``Owner``     : manages many pets and exposes all of their tasks.
- ``Scheduler`` : the "brain" that retrieves, organizes, and manages tasks
                  across all of an owner's pets.

Design decisions (resolving ambiguities):
- A ``Pet`` owns its ``Task`` objects; an ``Owner`` owns its ``Pet`` objects.
  The owner's task list is therefore the union of every pet's tasks.
- ``available_time`` is the owner's TOTAL time budget for the day; the
  scheduler spends it down as it selects tasks.
- Completed tasks are never included in today's schedule.
- ``frequency`` is a free-form label such as "daily", "weekly", or "monthly".
"""

from datetime import date, timedelta
from typing import Dict, List, NamedTuple, Optional, Tuple


class Conflict(NamedTuple):
    """Two overlapping tasks and which pet(s) they belong to."""

    task_a: "Task"
    task_b: "Task"
    pet_a: Optional[str]
    pet_b: Optional[str]
    same_pet: bool

    def describe(self) -> str:
        """Return a human-readable one-line summary of the clash."""
        who = (
            f"{self.pet_a} double-booked"
            if self.same_pet
            else f"{self.pet_a} vs {self.pet_b}"
        )
        return (
            f"{who}: '{self.task_a.description}' ({self.task_a.start_time}) "
            f"overlaps '{self.task_b.description}' ({self.task_b.start_time})"
        )

# How many days must pass before a recurring task is due again.
_RECURRENCE_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}

# Frequencies that automatically spawn a fresh task when completed.
_REGENERATING_FREQUENCIES = {"daily", "weekly"}


def _parse_hhmm(value: str) -> int:
    """Convert an ``"HH:MM"`` clock time into minutes since midnight."""
    try:
        hours, minutes = (int(part) for part in value.split(":"))
    except ValueError:
        raise ValueError(f"start_time must look like 'HH:MM', got {value!r}")
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ValueError(f"start_time out of range: {value!r}")
    return hours * 60 + minutes


class Task:
    """A single care activity for a pet."""

    def __init__(
        self,
        description: str,
        time: int,
        frequency: str = "daily",
        completed: bool = False,
        start_time: Optional[str] = None,
        due_date: Optional[date] = None,
    ):
        """Create a care task.

        ``time`` is the duration in minutes and must be positive. ``start_time``
        is an optional ``"HH:MM"`` clock time for *when* the task happens, which
        enables chronological sorting and conflict detection. ``due_date`` is
        the calendar day the task is scheduled for; when a recurring task is
        completed, its next occurrence gets a due date one interval later.
        """
        if time <= 0:
            raise ValueError("time must be positive")
        self.description = description
        self.time = time
        self.frequency = frequency
        self.completed = completed
        self.start_time = start_time
        self.due_date = due_date
        # Minutes since midnight, or None if the task isn't pinned to a time.
        self.start_minutes: Optional[int] = (
            _parse_hhmm(start_time) if start_time is not None else None
        )
        # When the task was last completed; drives recurrence (`is_due`).
        self.last_completed: Optional[date] = None
        # Back-reference to the owning pet, set by ``Pet.add_task``. Lets a
        # completed recurring task regenerate itself into the pet's list.
        self.pet: Optional["Pet"] = None

    @property
    def end_minutes(self) -> Optional[int]:
        """Minute-of-day the task finishes, or None if it has no start time."""
        if self.start_minutes is None:
            return None
        return self.start_minutes + self.time

    def mark_complete(self, on: Optional[date] = None) -> Optional["Task"]:
        """Mark this task completed, recording the date for recurrence.

        If this is a regenerating task (daily/weekly) that belongs to a pet,
        a fresh incomplete instance for the next occurrence is automatically
        added to that pet and returned. Completing an already-done task does
        nothing (so it can't spawn duplicates). Returns the new task, or None.
        """
        if self.completed:
            return None
        self.completed = True
        completed_on = on if on is not None else date.today()
        self.last_completed = completed_on
        if self.pet is not None and self.frequency in _REGENERATING_FREQUENCIES:
            nxt = self.next_occurrence(completed_on)
            self.pet.add_task(nxt)
            return nxt
        return None

    def next_occurrence(self, after: Optional[date] = None) -> "Task":
        """Return a fresh, incomplete copy of this task for the next time.

        The new task's ``due_date`` is ``after`` plus this task's recurrence
        interval — e.g. a daily task completed today is due today + 1 day, a
        weekly task is due today + 7 days.
        """
        after = after if after is not None else date.today()
        interval = _RECURRENCE_DAYS.get(self.frequency, 1)
        return Task(
            self.description,
            self.time,
            frequency=self.frequency,
            start_time=self.start_time,
            due_date=after + timedelta(days=interval),
        )

    def reset(self) -> None:
        """Mark this task as not completed (e.g. at the start of a new day)."""
        self.completed = False

    def is_due(self, today: Optional[date] = None) -> bool:
        """Return whether this recurring task should appear on ``today``.

        A task never completed is always due. Otherwise it becomes due again
        once its frequency interval has elapsed since ``last_completed``.
        Unknown frequencies are treated as daily.
        """
        if self.last_completed is None:
            return True
        today = today if today is not None else date.today()
        interval = _RECURRENCE_DAYS.get(self.frequency, 1)
        return today >= self.last_completed + timedelta(days=interval)

    def overlaps(self, other: "Task") -> bool:
        """Return whether this task's time interval overlaps ``other``'s.

        Two tasks without start times (or where either lacks one) never
        conflict, since there's nothing to place them on the clock.
        """
        if self.start_minutes is None or other.start_minutes is None:
            return False
        return (
            self.start_minutes < other.end_minutes
            and other.start_minutes < self.end_minutes
        )

    def __repr__(self) -> str:
        """Return a debug-friendly summary of the task."""
        status = "done" if self.completed else "todo"
        when = f" @{self.start_time}" if self.start_time else ""
        return (
            f"Task({self.description!r}, {self.time}min{when}, "
            f"{self.frequency}, {status})"
        )


class Pet:
    """A pet's details and the list of care tasks it needs."""

    def __init__(self, name: str, age: int, breed: str):
        """Create a pet with the given details and an empty task list."""
        if age < 0:
            raise ValueError("age cannot be negative")
        self.name = name
        self.age = age
        self.breed = breed
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet, recording the pet on the task."""
        task.pet = self
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return this pet's tasks (a copy, so callers can't mutate the list)."""
        return list(self.tasks)

    def update_info(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
        breed: Optional[str] = None,
    ) -> None:
        """Update the pet's info. Only the fields passed in are changed."""
        if name is not None:
            self.name = name
        if age is not None:
            if age < 0:
                raise ValueError("age cannot be negative")
            self.age = age
        if breed is not None:
            self.breed = breed

    def view_info(self) -> str:
        """Return a readable summary of the pet's information."""
        return f"{self.name} ({self.breed}), age {self.age}"


class Owner:
    """The user who owns pets and has a limited daily time budget."""

    def __init__(self, name: str, available_time: int):
        if available_time < 0:
            raise ValueError("available_time cannot be negative")
        self.name = name
        self.available_time = available_time
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet as owned by this owner."""
        self.pets.append(pet)

    def get_available_time(self) -> int:
        """Return how much time (minutes) the owner has available today."""
        return self.available_time

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_tasks_by_pet(self) -> Dict[str, List[Task]]:
        """Return tasks grouped by pet name."""
        return {pet.name: pet.get_tasks() for pet in self.pets}


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def view_tasks(self) -> List[Task]:
        """Return all tasks the owner is responsible for."""
        return self.owner.get_all_tasks()

    def pending_tasks(self) -> List[Task]:
        """Return only the tasks that are not yet completed."""
        return [t for t in self.view_tasks() if not t.completed]

    def sort_by_time(self, ascending: bool = True) -> List[Task]:
        """Return all tasks sorted by the time they take (duration)."""
        return sorted(self.view_tasks(), key=lambda t: t.time, reverse=not ascending)

    def sort_by_start_time(self, ascending: bool = True) -> List[Task]:
        """Return all tasks in chronological order by their start time.

        Tasks without a start time are placed last (they aren't pinned to the
        clock), regardless of sort direction.
        """
        unscheduled = [t for t in self.view_tasks() if t.start_minutes is None]
        scheduled = [t for t in self.view_tasks() if t.start_minutes is not None]
        scheduled.sort(key=lambda t: t.start_minutes, reverse=not ascending)
        return scheduled + unscheduled

    def filter_by_frequency(self, frequency: str) -> List[Task]:
        """Return tasks matching the given frequency label."""
        return [t for t in self.view_tasks() if t.frequency == frequency]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return the tasks belonging to the named pet."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                return pet.get_tasks()
        return []

    def filter_by_status(self, completed: bool = False) -> List[Task]:
        """Return tasks matching a completion status (default: incomplete)."""
        return [t for t in self.view_tasks() if t.completed == completed]

    def due_today(self, today: Optional[date] = None) -> List[Task]:
        """Return pending tasks whose recurrence makes them due ``today``."""
        return [t for t in self.pending_tasks() if t.is_due(today)]

    def detect_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return pairs of scheduled tasks whose time intervals overlap.

        Only tasks with start times can conflict. Sorting by start time first
        means we only compare each task against the next few, and can stop as
        soon as a later task starts after the current one ends.
        """
        scheduled = [t for t in self.view_tasks() if t.start_minutes is not None]
        scheduled.sort(key=lambda t: t.start_minutes)
        conflicts: List[Tuple[Task, Task]] = []
        for i, task in enumerate(scheduled):
            for other in scheduled[i + 1 :]:
                if other.start_minutes >= task.end_minutes:
                    break  # later tasks start even later — no more overlaps
                conflicts.append((task, other))
        return conflicts

    def find_conflicts(self) -> List[Conflict]:
        """Return overlapping tasks annotated with the pet(s) involved.

        Wraps ``detect_conflicts`` and, for each overlapping pair, records each
        task's pet name and whether it's the *same* pet double-booked or two
        *different* pets colliding at the same time.
        """
        conflicts: List[Conflict] = []
        for task_a, task_b in self.detect_conflicts():
            pet_a = task_a.pet.name if task_a.pet is not None else None
            pet_b = task_b.pet.name if task_b.pet is not None else None
            conflicts.append(
                Conflict(task_a, task_b, pet_a, pet_b, same_pet=task_a.pet is task_b.pet)
            )
        return conflicts

    def conflict_warnings(self) -> List[str]:
        """Return warning strings for any scheduling clashes (never raises).

        A lightweight check for the UI: if two tasks overlap, it produces a
        readable "⚠️ ..." message instead of throwing. An empty list means the
        schedule is clear. Callers can simply print each string.
        """
        return [f"⚠️  {c.describe()}" for c in self.find_conflicts()]

    def generate_today_schedule(self) -> List[Task]:
        """Build today's schedule that fits within the owner's available time.

        Greedy strategy: consider tasks that are *due today* shortest-first and
        include each one whose time still fits the remaining budget.
        Shortest-first maximizes the number of tasks completed within the
        available time. The result is returned in chronological order so it
        reads like a real day plan.
        """
        remaining = self.owner.get_available_time()
        chosen: List[Task] = []
        for task in sorted(self.due_today(), key=lambda t: t.time):
            if task.time <= remaining:
                chosen.append(task)
                remaining -= task.time
        # Present the picked tasks in the order they happen during the day.
        chosen.sort(
            key=lambda t: t.start_minutes if t.start_minutes is not None else 1 << 30
        )
        return chosen

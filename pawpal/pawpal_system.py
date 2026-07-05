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

from typing import Dict, List, Optional


class Task:
    """A single care activity for a pet."""

    def __init__(
        self,
        description: str,
        time: int,
        frequency: str = "daily",
        completed: bool = False,
    ):
        """Create a care task; ``time`` (minutes) must be positive."""
        if time <= 0:
            raise ValueError("time must be positive")
        self.description = description
        self.time = time
        self.frequency = frequency
        self.completed = completed

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Mark this task as not completed (e.g. at the start of a new day)."""
        self.completed = False

    def __repr__(self) -> str:
        """Return a debug-friendly summary of the task."""
        status = "done" if self.completed else "todo"
        return (
            f"Task({self.description!r}, {self.time}min, "
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
        """Attach a care task to this pet."""
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
        """Return all tasks sorted by the time they take."""
        return sorted(self.view_tasks(), key=lambda t: t.time, reverse=not ascending)

    def filter_by_frequency(self, frequency: str) -> List[Task]:
        """Return tasks matching the given frequency label."""
        return [t for t in self.view_tasks() if t.frequency == frequency]

    def generate_today_schedule(self) -> List[Task]:
        """Build today's schedule that fits within the owner's available time.

        Greedy strategy: consider pending tasks shortest-first and include each
        one whose time still fits the remaining budget. Shortest-first maximizes
        the number of tasks completed within the available time.
        """
        remaining = self.owner.get_available_time()
        schedule: List[Task] = []
        for task in sorted(self.pending_tasks(), key=lambda t: t.time):
            if task.time <= remaining:
                schedule.append(task)
                remaining -= task.time
        return schedule

"""PawPal - Pet Care Scheduling System.

Skeleton classes generated from diagrams/uml_draft.mmd.
Method bodies are left as stubs to be implemented in a later phase.
"""

from typing import List


class Pet:
    """Holds information about a pet."""

    def __init__(self, name: str, age: int, breed: str):
        self.name = name
        self.age = age
        self.breed = breed

    def update_info(self, name: str, age: int, breed: str) -> None:
        """Update the pet's stored information."""
        pass

    def view_info(self) -> str:
        """Return a readable summary of the pet's information."""
        pass


class CareTask:
    """A single care task for a pet."""

    def __init__(self, name: str, duration: int, priority: int, category: str):
        self.name = name
        self.duration = duration
        self.priority = priority
        self.category = category
        self.completed = False

    def complete_task(self) -> None:
        """Mark this task as completed."""
        pass


class Owner:
    """The user who owns pets and has limited available time."""

    def __init__(self, name: str, available_time: int):
        self.name = name
        self.available_time = available_time

    def get_available_time(self) -> int:
        """Return how much time the owner has available."""
        pass


class Scheduler:
    """Generates and manages the schedule of care tasks for a pet."""

    def __init__(self, pet: Pet, owner: Owner):
        self.pet = pet
        self.owner = owner
        self.tasks: List[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        """Add a care task to the schedule."""
        pass

    def view_tasks(self) -> List[CareTask]:
        """Return all scheduled tasks."""
        pass

    def sort_by_priority(self) -> List[CareTask]:
        """Return tasks sorted by priority."""
        pass

    def filter_by_category(self, category: str) -> List[CareTask]:
        """Return tasks matching the given category."""
        pass

    def generate_today_schedule(self) -> List[CareTask]:
        """Build today's schedule that fits within the owner's available time."""
        pass

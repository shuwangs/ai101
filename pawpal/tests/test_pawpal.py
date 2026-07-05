"""Simple tests for PawPal core behavior."""

from pawpal_system import Task, Pet


def test_task_completion():
    """Calling mark_complete() should change the task's status to completed."""
    task = Task("Morning walk", time=30, frequency="daily")
    assert task.completed is False  # starts incomplete

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    """Adding a task to a Pet should increase that pet's task count."""
    pet = Pet("Rex", age=3, breed="Labrador")
    assert len(pet.get_tasks()) == 0  # starts with no tasks

    pet.add_task(Task("Feed", time=10, frequency="daily"))

    assert len(pet.get_tasks()) == 1


if __name__ == "__main__":
    test_task_completion()
    test_task_addition()
    print("All tests passed.")

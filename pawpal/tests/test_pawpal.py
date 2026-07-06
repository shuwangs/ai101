"""Simple tests for PawPal core behavior."""

from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


def _owner_with_tasks():
    """An owner with two pets and clock-timed tasks, for scheduler tests."""
    owner = Owner("Tester", available_time=60)
    rex = Pet("Rex", age=3, breed="Labrador")
    milo = Pet("Milo", age=5, breed="Tabby Cat")
    owner.add_pet(rex)
    owner.add_pet(milo)
    rex.add_task(Task("Walk", time=30, start_time="08:00"))
    milo.add_task(Task("Feed", time=10, start_time="08:15"))  # overlaps Walk
    milo.add_task(Task("Brush", time=15, frequency="weekly", start_time="18:00"))
    return owner


def test_sort_by_start_time():
    """Tasks come back in chronological order by their start time."""
    scheduler = Scheduler(_owner_with_tasks())
    starts = [t.start_time for t in scheduler.sort_by_start_time()]
    assert starts == ["08:00", "08:15", "18:00"]


def test_filter_by_pet_and_status():
    """Filtering narrows tasks to one pet, and by completion status."""
    owner = _owner_with_tasks()
    scheduler = Scheduler(owner)

    assert [t.description for t in scheduler.filter_by_pet("Rex")] == ["Walk"]

    owner.pets[0].tasks[0].mark_complete()
    done = scheduler.filter_by_status(completed=True)
    assert [t.description for t in done] == ["Walk"]


def test_recurring_due():
    """A weekly task done yesterday isn't due; a daily task done then is."""
    yesterday = date.today() - timedelta(days=1)

    weekly = Task("Brush", time=15, frequency="weekly")
    weekly.mark_complete(on=yesterday)
    assert weekly.is_due() is False

    daily = Task("Feed", time=10, frequency="daily")
    daily.mark_complete(on=yesterday)
    assert daily.is_due() is True


def test_conflict_detection():
    """Overlapping start times are reported; non-overlapping ones aren't."""
    scheduler = Scheduler(_owner_with_tasks())
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    descriptions = {conflicts[0][0].description, conflicts[0][1].description}
    assert descriptions == {"Walk", "Feed"}


def test_recurring_task_regenerates_on_completion():
    """Completing a daily/weekly task spawns a fresh incomplete instance."""
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Walk", time=30, frequency="daily", start_time="08:00"))
    assert len(pet.get_tasks()) == 1

    fresh = pet.tasks[0].mark_complete()

    assert len(pet.get_tasks()) == 2          # a new occurrence was added
    assert fresh is not None
    assert fresh.completed is False           # the new one is pending
    assert fresh.description == "Walk"
    assert fresh.start_time == "08:00"


def test_monthly_task_does_not_regenerate():
    """A monthly (non-regenerating) task spawns nothing when completed."""
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Vet", time=60, frequency="monthly"))

    assert pet.tasks[0].mark_complete() is None
    assert len(pet.get_tasks()) == 1


def test_completing_twice_does_not_duplicate():
    """Marking an already-done task complete again spawns no duplicate."""
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Feed", time=10, frequency="daily"))

    pet.tasks[0].mark_complete()
    assert len(pet.get_tasks()) == 2
    pet.tasks[0].mark_complete()               # second call is a no-op
    assert len(pet.get_tasks()) == 2


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

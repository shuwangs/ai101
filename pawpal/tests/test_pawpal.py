"""Automated test suite for PawPal core behavior.

Organized by feature:
  1. Sorting          - tasks come back in the right order
  2. Recurrence       - completing a recurring task spawns its next occurrence
  3. Conflict detection - overlapping / duplicate-time tasks are flagged
  4. Scheduling budget - the day plan respects the owner's time budget
  5. Validation        - bad input is rejected

Two tests are marked ``xfail`` (expected-fail): they document real,
currently-unfixed quirks in the code so the suite stays green while making
the limitations visible. See the comments on each for the details.
"""

from datetime import date, timedelta

import pytest

from pawpal_system import Task, Pet, Owner, Scheduler


def _owner_with_tasks():
    """An owner with two pets and clock-timed tasks, for scheduler tests.

    Rex's 08:00 "Walk" (30 min) and Milo's 08:15 "Feed" (10 min) overlap on
    purpose so conflict/sort tests have something to work with.
    """
    owner = Owner("Tester", available_time=60)
    rex = Pet("Rex", age=3, breed="Labrador")
    milo = Pet("Milo", age=5, breed="Tabby Cat")
    owner.add_pet(rex)
    owner.add_pet(milo)
    rex.add_task(Task("Walk", time=30, start_time="08:00"))
    milo.add_task(Task("Feed", time=10, start_time="08:15"))   # overlaps Walk
    milo.add_task(Task("Brush", time=15, frequency="weekly", start_time="18:00"))
    return owner


# ---------------------------------------------------------------------------
# 1. SORTING  (required: "Verify tasks are returned in chronological order")
# ---------------------------------------------------------------------------

def test_sort_by_start_time_is_chronological():
    """REQUIRED: tasks come back ordered by their clock start time."""
    scheduler = Scheduler(_owner_with_tasks())
    starts = [t.start_time for t in scheduler.sort_by_start_time()]
    assert starts == ["08:00", "08:15", "18:00"]


def test_sort_descending_keeps_unscheduled_tasks_last():
    """Tasks with no start_time are pinned last even when sorting descending.

    sort_by_start_time() splits scheduled vs. unscheduled and always appends
    the unscheduled ones — so direction must not float a None-time task to
    the front. This is the direction people forget to test.
    """
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", time=30, start_time="08:00"))
    pet.add_task(Task("Vet visit", time=60))                 # no start_time
    pet.add_task(Task("Feed", time=10, start_time="18:00"))

    result = Scheduler(owner).sort_by_start_time(ascending=False)
    starts = [t.start_time for t in result]
    assert starts == ["18:00", "08:00", None]                # None stays last


def test_sort_is_stable_on_equal_start_times():
    """Two tasks at the same start time keep their insertion order (stable)."""
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("First", time=10, start_time="09:00"))
    pet.add_task(Task("Second", time=10, start_time="09:00"))

    order = [t.description for t in Scheduler(owner).sort_by_start_time()]
    assert order == ["First", "Second"]


def test_sort_by_duration():
    """sort_by_time orders by duration (minutes), shortest first."""
    scheduler = Scheduler(_owner_with_tasks())
    durations = [t.time for t in scheduler.sort_by_time()]
    assert durations == sorted(durations)                    # 10, 15, 30


def test_sort_empty_schedule_is_empty():
    """Sorting an owner with no tasks returns an empty list, not an error."""
    scheduler = Scheduler(Owner("Empty", available_time=60))
    assert scheduler.sort_by_start_time() == []


# ---------------------------------------------------------------------------
# 2. RECURRENCE  (required: "marking a daily task complete creates a new task
#                 for the following day")
# ---------------------------------------------------------------------------

def test_daily_completion_creates_task_for_next_day():
    """REQUIRED: completing a daily task spawns a fresh instance due tomorrow."""
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Walk", time=30, frequency="daily", start_time="08:00"))

    fresh = pet.tasks[0].mark_complete(on=date.today())

    # The original is now done, and exactly one new occurrence was added.
    assert pet.tasks[0].completed is True
    assert len(pet.get_tasks()) == 2

    # The new task is pending, identical in shape, and dated one day later.
    assert fresh is not None
    assert fresh.completed is False
    assert fresh.description == "Walk"
    assert fresh.start_time == "08:00"
    assert fresh.due_date == date.today() + timedelta(days=1)


def test_weekly_completion_creates_task_seven_days_later():
    """A weekly task's next occurrence is due 7 days out."""
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Brush", time=15, frequency="weekly"))

    fresh = pet.tasks[0].mark_complete(on=date.today())
    assert fresh.due_date == date.today() + timedelta(days=7)


def test_completing_twice_does_not_duplicate():
    """Marking an already-done task complete again is a no-op (no duplicate)."""
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Feed", time=10, frequency="daily"))

    pet.tasks[0].mark_complete()
    assert len(pet.get_tasks()) == 2
    pet.tasks[0].mark_complete()                             # second call: no-op
    assert len(pet.get_tasks()) == 2


def test_monthly_task_does_not_regenerate():
    """Monthly is not in the regenerating set, so it spawns nothing.

    (Documents current behavior: is_due understands "monthly" but completion
    does not auto-create the next month's task.)
    """
    pet = Pet("Rex", age=3, breed="Labrador")
    pet.add_task(Task("Vet", time=60, frequency="monthly"))

    assert pet.tasks[0].mark_complete() is None
    assert len(pet.get_tasks()) == 1


def test_task_with_no_pet_does_not_regenerate():
    """A standalone daily task (never added to a pet) spawns nothing."""
    task = Task("Feed", time=10, frequency="daily")
    assert task.mark_complete() is None                      # no pet -> no spawn


def test_is_due_recurrence_boundaries():
    """A daily task done yesterday is due again; a weekly one isn't."""
    yesterday = date.today() - timedelta(days=1)

    daily = Task("Feed", time=10, frequency="daily")
    daily.mark_complete(on=yesterday)
    assert daily.is_due() is True

    weekly = Task("Brush", time=15, frequency="weekly")
    weekly.mark_complete(on=yesterday)
    assert weekly.is_due() is False

    # Never-completed tasks are always due.
    assert Task("New", time=5).is_due() is True


# ---------------------------------------------------------------------------
# 3. CONFLICT DETECTION  (required: "flags duplicate times")
# ---------------------------------------------------------------------------

def test_conflict_flags_identical_start_times():
    """REQUIRED: two tasks at the exact same time are flagged as a conflict."""
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", time=30, start_time="09:00"))
    pet.add_task(Task("Feed", time=15, start_time="09:00"))   # same start time

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    clashing = {conflicts[0][0].description, conflicts[0][1].description}
    assert clashing == {"Walk", "Feed"}


def test_partial_overlap_is_flagged():
    """Overlapping (but not identical) times conflict; the gap task doesn't."""
    scheduler = Scheduler(_owner_with_tasks())        # Walk 08:00, Feed 08:15
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    clashing = {conflicts[0][0].description, conflicts[0][1].description}
    assert clashing == {"Walk", "Feed"}               # 18:00 Brush is clear


def test_touching_boundaries_do_not_conflict():
    """A task ending exactly when the next starts is NOT a conflict."""
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("A", time=30, start_time="09:00"))      # 09:00-09:30
    pet.add_task(Task("B", time=30, start_time="09:30"))      # 09:30-10:00

    assert Scheduler(owner).detect_conflicts() == []


def test_full_containment_is_flagged():
    """A short task fully inside a long one is a conflict."""
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Long", time=180, start_time="09:00"))  # 09:00-12:00
    pet.add_task(Task("Short", time=15, start_time="10:00"))  # inside Long

    assert len(Scheduler(owner).detect_conflicts()) == 1


def test_break_optimization_has_no_false_negative():
    """The sorted-scan early-break must not miss a real overlap.

    detect_conflicts sorts by start time and breaks the inner loop at the
    first task that starts after the current one ends. This case proves the
    break is per-task: C doesn't overlap A but DOES overlap the long B.
    Expected clashes: A-B and B-C only (never A-C).
    """
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("A", time=10, start_time="09:00"))      # 09:00-09:10
    pet.add_task(Task("B", time=115, start_time="09:05"))     # 09:05-11:00
    pet.add_task(Task("C", time=5, start_time="09:20"))       # 09:20-09:25

    pairs = {
        frozenset((a.description, b.description))
        for a, b in Scheduler(owner).detect_conflicts()
    }
    assert pairs == {frozenset(("A", "B")), frozenset(("B", "C"))}


def test_find_conflicts_distinguishes_same_pet_from_different_pets():
    """find_conflicts() records whether it's a double-book or two pets clashing."""
    # Two different pets clashing.
    diff = Scheduler(_owner_with_tasks()).find_conflicts()
    assert len(diff) == 1
    assert diff[0].same_pet is False
    assert {diff[0].pet_a, diff[0].pet_b} == {"Rex", "Milo"}

    # Same pet double-booked.
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", time=30, start_time="09:00"))
    pet.add_task(Task("Feed", time=10, start_time="09:10"))
    same = Scheduler(owner).find_conflicts()
    assert len(same) == 1
    assert same[0].same_pet is True
    assert "double-booked" in same[0].describe()


def test_tasks_without_start_times_never_conflict():
    """Tasks not pinned to the clock cannot overlap anything."""
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Vet", time=60))                        # no start_time
    pet.add_task(Task("Groom", time=60))                      # no start_time

    assert Scheduler(owner).detect_conflicts() == []


def test_completed_task_does_not_conflict():
    """A finished task shouldn't clash with anything still on the schedule.

    (Regression test: detect_conflicts scans pending_tasks(), so completing
    one of an overlapping pair clears the conflict.)
    """
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    # Use a non-regenerating frequency so completing doesn't spawn a duplicate.
    pet.add_task(Task("Walk", time=30, frequency="monthly", start_time="09:00"))
    pet.add_task(Task("Feed", time=30, frequency="monthly", start_time="09:15"))

    pet.tasks[0].mark_complete()                              # Walk is now done
    assert Scheduler(owner).detect_conflicts() == []


# ---------------------------------------------------------------------------
# 4. SCHEDULING BUDGET
# ---------------------------------------------------------------------------

def test_zero_budget_schedules_nothing():
    """An owner with no available time gets an empty day plan."""
    owner = Owner("Busy", available_time=0)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Walk", time=30, start_time="09:00"))

    assert Scheduler(owner).generate_today_schedule() == []


def test_greedy_shortest_first_maximizes_task_count():
    """With a tight budget, two short tasks are preferred over one long one."""
    owner = Owner("Tester", available_time=30)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Long", time=25, start_time="08:00"))
    pet.add_task(Task("ShortA", time=10, start_time="09:00"))
    pet.add_task(Task("ShortB", time=10, start_time="10:00"))

    chosen = {t.description for t in Scheduler(owner).generate_today_schedule()}
    assert chosen == {"ShortA", "ShortB"}                    # 2 tasks, not the 25


def test_task_longer_than_budget_is_excluded():
    """A single task that exceeds the whole budget is left out."""
    owner = Owner("Tester", available_time=20)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Long walk", time=45, start_time="09:00"))

    assert Scheduler(owner).generate_today_schedule() == []


def test_freshly_spawned_task_is_not_due_today():
    """The 'tomorrow' occurrence created on completion shouldn't be due today.

    (Regression test: is_due() now respects a future due_date.)
    """
    owner = Owner("Tester", available_time=60)
    pet = Pet("Rex", age=3, breed="Labrador")
    owner.add_pet(pet)
    pet.add_task(Task("Feed", time=10, frequency="daily", start_time="08:00"))

    fresh = pet.tasks[0].mark_complete(on=date.today())
    assert fresh.due_date == date.today() + timedelta(days=1)
    assert fresh not in Scheduler(owner).due_today()


# ---------------------------------------------------------------------------
# 5. VALIDATION  &  BASIC OPERATIONS
# ---------------------------------------------------------------------------

def test_invalid_start_times_are_rejected():
    """Malformed or out-of-range clock strings raise ValueError."""
    for bad in ["24:00", "09:60", "9", "9am", "09:00:00"]:
        with pytest.raises(ValueError):
            Task("Bad", time=10, start_time=bad)


def test_valid_start_time_boundaries_are_accepted():
    """Midnight and 23:59 are valid and parse to the right minute-of-day."""
    assert Task("Midnight", time=5, start_time="00:00").start_minutes == 0
    assert Task("Late", time=5, start_time="23:59").start_minutes == 23 * 60 + 59


def test_constructors_reject_bad_numbers():
    """Non-positive durations, negative ages, and negative budgets are rejected."""
    with pytest.raises(ValueError):
        Task("Zero", time=0)
    with pytest.raises(ValueError):
        Pet("Rex", age=-1, breed="Labrador")
    with pytest.raises(ValueError):
        Owner("Broke", available_time=-5)


def test_filter_by_pet_and_status():
    """Filtering narrows tasks to one pet, and by completion status."""
    owner = _owner_with_tasks()
    scheduler = Scheduler(owner)

    assert [t.description for t in scheduler.filter_by_pet("Rex")] == ["Walk"]

    owner.pets[0].tasks[0].mark_complete()
    done = scheduler.filter_by_status(completed=True)
    assert [t.description for t in done] == ["Walk"]


def test_task_addition_increases_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Rex", age=3, breed="Labrador")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feed", time=10, frequency="daily"))
    assert len(pet.get_tasks()) == 1

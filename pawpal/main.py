"""PawPal demo — build an owner with pets and tasks, then show the day plan.

Tasks are deliberately added OUT OF ORDER (by start time) so the demo proves
that the scheduler's sorting and filtering methods reorder them correctly:
chronological sorting, filtering by pet/status, recurrence (is_due), conflict
detection, and auto-regeneration of recurring tasks on completion.
"""

from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


def main() -> None:
    # An owner with a 60-minute time budget for the day.
    owner = Owner("Shu", available_time=60)

    # At least two pets.
    rex = Pet("Rex", age=3, breed="Labrador")
    milo = Pet("Milo", age=5, breed="Tabby Cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Add tasks OUT OF ORDER on purpose — evening before morning, etc.
    # sort_by_start_time() should still return them chronologically below.
    milo.add_task(Task("Brush coat", time=15, frequency="weekly", start_time="18:00"))
    rex.add_task(Task("Vet check-up", time=60, frequency="monthly", start_time="09:00"))
    milo.add_task(Task("Feed", time=10, frequency="daily", start_time="08:15"))
    rex.add_task(Task("Morning walk", time=30, frequency="daily", start_time="08:00"))
    # Two tasks at the SAME time (08:00) → Rex is double-booked.
    rex.add_task(Task("Give medicine", time=5, frequency="daily", start_time="08:00"))

    scheduler = Scheduler(owner)

    print(f"PawPal — {owner.name} has {owner.get_available_time()} minutes today")
    print(f"Pets: {', '.join(pet.view_info() for pet in owner.pets)}")
    print()

    print("Tasks as entered (insertion order)")
    print("-" * 40)
    for task in scheduler.view_tasks():
        print(f"  {task.start_time}  {task.description}")
    print()

    print("Sorted by start time (chronological)")
    print("-" * 40)
    for task in scheduler.sort_by_start_time():
        print(f"  {task.start_time or '  —  '}  {task.description}")
    print()

    print("Sorted by duration (shortest first)")
    print("-" * 40)
    for task in scheduler.sort_by_time():
        print(f"  [{task.time:>3} min]  {task.description}")
    print()

    print("Filter — Rex's tasks:")
    for task in scheduler.filter_by_pet("Rex"):
        print(f"  - {task.description}")
    print()

    print("Conflict check (lightweight — warns, never crashes)")
    print("-" * 40)
    warnings = scheduler.conflict_warnings()
    if not warnings:
        print("  ✅ No conflicts — the schedule is clear.")
    for warning in warnings:
        print(f"  {warning}")
    print()

    print("Today's Schedule (due tasks that fit the budget)")
    print("-" * 40)
    schedule = scheduler.generate_today_schedule()
    total = 0
    for task in schedule:
        print(f"  {task.start_time}  [{task.time:>3} min] {task.description} ({task.frequency})")
        total += task.time
    print("-" * 40)
    print(f"  Total: {total} of {owner.get_available_time()} minutes used")
    print()

    print("Recurrence — completing a task regenerates it")
    print("-" * 40)
    walk = scheduler.filter_by_pet("Rex")[1]  # the daily Morning walk
    print(f"  Before: Rex has {len(rex.get_tasks())} tasks")
    fresh = walk.mark_complete(on=date.today())
    print(f"  Completed daily '{walk.description}' → spawned: {fresh}")
    print(f"  New occurrence due: {fresh.due_date} (today + 1 day)")
    print(f"  After:  Rex has {len(rex.get_tasks())} tasks")
    print("  Rex's tasks now:")
    for task in rex.get_tasks():
        status = "done" if task.completed else "todo"
        print(f"    - {task.description} ({status})")
    print()

    # Contrast: a monthly task does NOT regenerate on completion.
    vet = next(t for t in rex.get_tasks() if t.frequency == "monthly")
    count_before = len(rex.get_tasks())
    vet.mark_complete()
    print(f"  Completing monthly '{vet.description}' spawns nothing: "
          f"{count_before} → {len(rex.get_tasks())} tasks")


if __name__ == "__main__":
    main()

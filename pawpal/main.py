"""PawPal demo — build an owner with pets and tasks, then print today's schedule."""

from pawpal_system import Task, Pet, Owner, Scheduler


def main() -> None:
    # An owner with a 60-minute time budget for the day.
    owner = Owner("Shu", available_time=60)

    # At least two pets.
    rex = Pet("Rex", age=3, breed="Labrador")
    milo = Pet("Milo", age=5, breed="Tabby Cat")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # At least three tasks with different times, spread across the pets.
    rex.add_task(Task("Morning walk", time=30, frequency="daily"))
    rex.add_task(Task("Vet check-up", time=60, frequency="monthly"))
    milo.add_task(Task("Feed", time=10, frequency="daily"))
    milo.add_task(Task("Brush coat", time=15, frequency="weekly"))

    scheduler = Scheduler(owner)

    print(f"PawPal — {owner.name} has {owner.get_available_time()} minutes today")
    print(f"Pets: {', '.join(pet.view_info() for pet in owner.pets)}")
    print()

    print("Today's Schedule")
    print("-" * 40)
    schedule = scheduler.generate_today_schedule()
    if not schedule:
        print("Nothing fits in today's time budget.")
    else:
        total = 0
        for task in schedule:
            print(f"  [{task.time:>3} min] {task.description} ({task.frequency})")
            total += task.time
        print("-" * 40)
        print(f"  Total: {total} of {owner.get_available_time()} minutes used")


if __name__ == "__main__":
    main()

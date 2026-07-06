# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

Beyond storing tasks, PawPal adds logic that makes the day plan genuinely useful.
All methods live in [`pawpal_system.py`](pawpal_system.py).

### Sorting behavior

- **`Scheduler.sort_by_time(ascending=True)`** — orders all tasks by how long they
  take (shortest-first by default), so you can see quick wins vs. big commitments.
- **`Scheduler.sort_by_start_time(ascending=True)`** — orders tasks chronologically
  by their `"HH:MM"` start time; tasks with no start time sort last.

### Filtering behavior

- **`Scheduler.filter_by_pet(pet_name)`** — returns only the named pet's tasks.
- **`Scheduler.filter_by_status(completed=False)`** — splits tasks by completion
  status (default returns the pending ones).
- **`Scheduler.filter_by_frequency(frequency)`** — returns tasks matching a label
  such as `"daily"` or `"weekly"`.

### Conflict detection logic

- **`Task.overlaps(other)`** — returns whether two tasks' time intervals overlap.
- **`Scheduler.detect_conflicts()`** — returns every overlapping task pair. It sorts
  by start time and stops scanning once a later task starts after the current one
  ends, so it only compares each task against its near neighbors.
- **`Scheduler.find_conflicts()`** — enriches each clash with the pet(s) involved and
  a `same_pet` flag, distinguishing one pet *double-booked* from two *different* pets
  colliding at the same time.
- **`Scheduler.conflict_warnings()`** — a lightweight check that returns readable
  `⚠️ …` warning strings and never raises; an empty list means the schedule is clear.

### Recurring task logic

- **`Task.is_due(today)`** — decides whether a recurring task should appear today,
  using its `frequency` and `last_completed` date (daily = 1 day, weekly = 7,
  monthly = 30). A task only resurfaces once its interval has elapsed.
- **`Scheduler.due_today(today)`** — returns the pending tasks that are due today.
- **`Task.mark_complete(on)` / `Task.next_occurrence(after)`** — completing a
  daily/weekly task automatically spawns a fresh instance for the next occurrence,
  with `due_date = completion date + interval`. Monthly tasks don't regenerate, and
  completing an already-done task is a no-op (so it can't create duplicates).

### Building the day plan

- **`Scheduler.generate_today_schedule()`** — greedy shortest-first selection over
  `due_today()` that fits within the owner's available-time budget, returned in
  chronological order so it reads like a real day.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## Sample Output
> Today's Schedule
> ----------------------------------------
>  [ 10 min] Feed (daily)
>  [ 15 min] Brush coat (weekly)
>  [ 30 min] Morning walk (daily)
> ----------------------------------------
> Total: 55 of 60 minutes used

## Testing PawPal+
Run the testing
`python -m pytest`

**28 tests covering:**
- **Sorting** — chronological order, unscheduled tasks last (even descending), stable ties, sort-by-duration, empty schedule.
- **Recurrence** — completing a daily task spawns a fresh instance due the next day (weekly → 7 days); no duplicate on repeat completion; monthly doesn't auto-regenerate; `is_due` boundaries.
- **Conflict detection** — identical and partial overlaps flagged; touching boundaries don't conflict; full containment does; same-pet double-book vs. two-pet clash; completed tasks drop out.
- **Scheduling budget** — zero budget schedules nothing; greedy shortest-first maximizes task count; over-budget tasks excluded.
- **Validation** — bad start times, durations, ages, and budgets rejected.


- The testing output
> ======== test session starts =============
> platform darwin -- Python 3.13.2, pytest-9.1.0, pluggy-1.6.0
> collected 28 items                                                                                            

> tests/test_pawpal.> py ............................                                                       [100%]

> ======= 28 passed in 0.02s =======


**Confidence Level**: 3 
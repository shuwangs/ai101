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

PawPal+ runs two ways: an interactive **Streamlit UI** ([`app.py`](app.py)) and a
scripted **CLI demo** ([`main.py`](main.py)) that prints every scheduler behavior in
one shot. Launch the UI with:

```bash
streamlit run app.py
```

### Main UI features & what you can do

The app is a single scrollable page ([`app.py`](app.py)) with four working sections:

- **Owner & pet setup** — type an owner name, then a pet's name and species and
  click **Add a Pet**. The owner is held in `st.session_state`, so pets and tasks
  persist as you interact.
- **Tasks** — pick which pet the task belongs to, then enter a title, duration
  (minutes), frequency (daily/weekly/monthly), and an optional `HH:MM` start time.
  **Add task** validates the input (bad start times or durations raise a friendly
  error) and appends it. Each pet renders as a table of its current tasks.
- **Build Schedule** — **Generate schedule** runs the `Scheduler` against the
  owner's time budget. It surfaces any **conflict warnings**, then shows today's
  plan with three metrics (tasks planned, minutes used vs. budget, time left) and a
  full table.
- **Explore Tasks** — a live sort/filter explorer with five views: chronological,
  shortest-first, pending-only, by pet, and by frequency — each rendered as a table.

### Example workflow

1. Set **Owner name** to `Jordan` and add a pet: name `Rex`, species `dog`.
2. In **Tasks**, choose `Rex`, add `Morning walk` — `30` min, `daily`, start `08:00`.
3. Add a second task for `Rex`: `Give medicine` — `5` min, `daily`, start `08:00`
   (same time on purpose, to trigger a conflict).
4. Click **Generate schedule** under **Build Schedule**. PawPal+ warns that Rex is
   double-booked at 08:00, then plans both tasks within the 60-minute budget and
   shows minutes used / time left.
5. Scroll to **Explore Tasks** and switch the **View** dropdown to
   *Chronological (by start time)* to see the tasks ordered by clock time.

### Key Scheduler behaviors on display

- **Sorting** — chronological by start time (unscheduled tasks sort last) and
  shortest-first by duration.
- **Filtering** — by pet, by completion status, and by frequency label.
- **Conflict warnings** — overlapping tasks produce readable `⚠️` messages that
  distinguish one pet *double-booked* from two *different* pets colliding; the check
  never raises.
- **Budgeted day plan** — greedy shortest-first selection over tasks *due today*,
  returned in chronological order, stopping once the time budget is spent.
- **Recurrence** — completing a daily/weekly task auto-spawns its next occurrence;
  monthly tasks don't regenerate.

### Sample CLI output (`python main.py`)

The CLI demo seeds two pets and five tasks (added out of order, with a deliberate
08:00 double-booking) and prints every behavior above:

```text
PawPal — Shu has 60 minutes today
Pets: Rex (Labrador), age 3, Milo (Tabby Cat), age 5

Tasks as entered (insertion order)
----------------------------------------
  09:00  Vet check-up
  08:00  Morning walk
  08:00  Give medicine
  18:00  Brush coat
  08:15  Feed

Sorted by start time (chronological)
----------------------------------------
  08:00  Morning walk
  08:00  Give medicine
  08:15  Feed
  09:00  Vet check-up
  18:00  Brush coat

Sorted by duration (shortest first)
----------------------------------------
  [  5 min]  Give medicine
  [ 10 min]  Feed
  [ 15 min]  Brush coat
  [ 30 min]  Morning walk
  [ 60 min]  Vet check-up

Filter — Rex's tasks:
  - Vet check-up
  - Morning walk
  - Give medicine

Conflict check (lightweight — warns, never crashes)
----------------------------------------
  ⚠️  Rex double-booked: 'Morning walk' (08:00) overlaps 'Give medicine' (08:00)
  ⚠️  Rex vs Milo: 'Morning walk' (08:00) overlaps 'Feed' (08:15)

Today's Schedule (due tasks that fit the budget)
----------------------------------------
  08:00  [  5 min] Give medicine (daily)
  08:00  [ 30 min] Morning walk (daily)
  08:15  [ 10 min] Feed (daily)
  18:00  [ 15 min] Brush coat (weekly)
----------------------------------------
  Total: 60 of 60 minutes used

Recurrence — completing a task regenerates it
----------------------------------------
  Before: Rex has 3 tasks
  Completed daily 'Morning walk' → spawned: Task('Morning walk', 30min @08:00, daily, todo)
  New occurrence due: 2026-07-06 (today + 1 day)
  After:  Rex has 4 tasks
  Rex's tasks now:
    - Vet check-up (todo)
    - Morning walk (done)
    - Give medicine (todo)
    - Morning walk (todo)

  Completing monthly 'Vet check-up' spawns nothing: 4 → 4 tasks
```

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
import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner =  Owner(name=owner_name, available_time=60)
owner = st.session_state.owner

if st.button("Add a Pet"):
    owner.add_pet(Pet(name=pet_name, age =1, breed=species))


st.markdown("### Tasks")
st.caption("Add tasks to a pet. These feed straight into the scheduler.")

if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    # Pick which pet this task belongs to.
    chosen_index = st.selectbox(
        "Which pet?",
        range(len(owner.pets)),
        format_func=lambda i: owner.pets[i].name,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

    if st.button("Add task"):
        pet = owner.pets[chosen_index]
        pet.add_task(Task(task_title, time=int(duration), frequency=frequency))
        st.success(f"Added '{task_title}' to {pet.name}!")

    # Show each pet and its tasks.
    for pet in owner.pets:
        st.write(f"**{pet.view_info()}**")
        if pet.tasks:
            st.table(
                [
                    {"task": t.description, "minutes": t.time, "frequency": t.frequency}
                    for t in pet.tasks
                ]
            )
        else:
            st.caption("— no tasks yet —")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)                     # 1. build a Scheduler from the owner
    schedule = scheduler.generate_today_schedule()   # 2. compute today's tasks (a list of Task)

    st.markdown(f"### Today's Schedule ({owner.get_available_time()} min budget)")
    if not schedule:                                 # 3. show the result
        st.warning("Nothing fits in today's time budget (or no pending tasks).")
    else:
        total = 0
        for task in schedule:
            st.write(f"- **{task.time} min** — {task.description} ({task.frequency})")
            total += task.time
        st.caption(f"Total: {total} of {owner.get_available_time()} minutes used")

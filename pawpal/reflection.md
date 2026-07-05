# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  The three core actions should be able to perform are: First, enter pet information, such as name, species and age, add schedule. Second, the user should be able to add care tasks like walks, feeding, mediacation, grooming including details such as duration and priority. Third the user should be able to generate and view today's plan to see what they need to do.

- What classes did you include, and what responsibilities did you assign to each?
For the main building block, I should have three objects: Pet, CareTask, Owner, Schedule.
Pet holds information about pet name, age, breed. It may have methods to update information, view information
CareTask holds information about the task name, duration, priority, category. It may have methods add new task, complete task.
Owner holds information about the user's name, available time. It may have methods for checking how much time the owner has available.
The Scheduler uses pet and CareTask to generate and view the scheduled tasks, it may have methods view tasks, sort tasks by priority, filter task by category, and generate today's schedule.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

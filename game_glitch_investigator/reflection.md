# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input                 | Expected Behavior                       | Actual Behavior                  | Console Output / Error |
| --------------------- | --------------------------------------- | -------------------------------- | ---------------------- |
| guess of 34           | Go Higher                               | GO Lower                         | none                   |
| guess of 66           | Go Lower                                | GO Higher                        | none                   |
| Click new Game button | start a new game with clean log history | the log history persists         | none                   |
| Click new Game button | start a new game with score = 0         | score is the previous game score | none                   |
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

I used **Claude Code in agent mode** as my main AI teammate, mostly to diagnose root causes and to refactor `check_guess` out of `app.py` into `logic_utils.py`.

A correct suggestion: When the "go higher / go lower" hints were backwards on some guesses, Claude diagnosed that `secret` was sometimes arriving as a **string** instead of an int, so `guess > secret` was doing a *lexicographic* comparison (e.g. `"9" > "80"` evaluates to `True`). It suggested coercing both values with `int(...)` before comparing. I verified this by writing a regression test, `test_string_secret_compares_numerically`, that calls `check_guess(9, "80")` and asserts the outcome is `"Too Low"` — it passed after the fix and would have failed before.

A misleading suggestion: Early on, the AI's first instinct was to treat the bug as just "backwards labels" and fix it by swapping the hint message strings. That would have *looked* fixed for one input but still given the wrong direction for others, because it never addressed the underlying string-vs-int comparison. I caught this by testing more than one guess (a small number vs. a large one) and seeing the direction still flip incorrectly, which is what led me to push for the real type-coercion fix.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  I will first identify whether the expected behavior of the game and then compared it to the one after changes.
- Describe at least one test you ran (manual or using pytest) 
  and what it showed you about your code.

One test I ran was using pytest after fixing the bug in the guessing logic. I created a test case that checked whether the game returned the correct feedback when a player's guess was higher than the secret number. Before the fix, the game sometimes returned incorrect hints. After updating the logic and running pytest, the test passed, confirming that the bug had been resolved.

Second one is every time you start a new game the guess history is cleared.

- Did AI help you design or understand any tests? How?
  
  I asked my AI coding assistant to explain the existing test cases and suggest additional edge cases I should verify. The AI helped me think about inputs that could expose hidden bugs, but I reviewed the suggestions carefully and confirmed the results myself before accepting the fixes.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

I learned that Streamlit reruns the entire script from top to bottom whenever a user interacts with the app, such as clicking a button or entering text. This means that regular variables are recreated each time the script runs.

I would explain Streamlit reruns to a friend as "starting the app over from the beginning every time the user does something." Because of this behavior, data can be lost between interactions if it is stored only in regular variables.

Session state provides a way to persist data across reruns. For example, if you have a button that increases a counter, the counter would reset every time the script reruns unless it is stored in st.session_state. By using session state, the app can remember values such as scores, counters, user inputs, or game progress between interactions.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  
During this project, I learned that even small fixes can introduce new bugs, so running tests regularly helped me confirm that my changes worked as expected.

- What is one thing you would do differently next time you work with AI on a coding task?

This project changed the way I think about AI-generate code, because i realized that AI can help speed up development, though it is not always right. Developers still needs to undestand and test the code regularly and thoroughly.
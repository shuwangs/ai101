# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.**
  Game Glitch Investigator is a Streamlit number-guessing game. The app picks a secret number within a range that depends on the chosen difficulty (Easy 1–20, Normal 1–100, Hard 1–50), and the player has a limited number of attempts to guess it. After each guess the game gives a higher/lower hint and updates a running score, ending when the player guesses correctly or runs out of attempts.

- [x] **Detail which bugs you found.**
  1. **Backwards hints (logic bug):** On even-numbered attempts the secret was passed to `check_guess` as a *string*, so `guess > secret` compared text lexicographically (e.g. `"9" > "80"` is `True`) and told the player to go the wrong direction.
  2. **New Game didn't reset state:** Clicking **New Game 🔁** generated a new secret but left the guess `history` and `score` from the previous game intact, so a "fresh" game started with stale data.

- [x] **Explain what fixes you applied.**
  1. Refactored `check_guess` out of `app.py` into `logic_utils.py`, and coerced both operands to `int` (`guess = int(guess)`, `secret = int(secret)`) before comparing, so the higher/lower direction is always numeric and correct.
  2. Added `st.session_state.history = []` and `st.session_state.score = 0` to the New Game handler so a new game truly starts clean.
  3. Updated the tests to unpack the `(outcome, message)` tuple and added a regression test, `test_string_secret_compares_numerically`, that calls `check_guess(9, "80")` and asserts `"Too Low"` to lock in the fix. All tests pass with `pytest`.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. Launch the app with `streamlit run app.py` and pick a difficulty in the sidebar (Easy, Normal, or Hard). The sidebar shows the number range and how many attempts you get.
2. Type a number into "Enter your guess" and click **Submit Guess 🚀**. With "Show hint" checked, the game tells you whether to go higher or lower.
3. Confirm the hints now point the right way: a guess below the secret says **📈 Go HIGHER!** and a guess above it says **📉 Go LOWER!** — even on even-numbered attempts, where the old code compared the secret as a string and flipped the direction.
4. Keep guessing toward the secret. Your score updates after each attempt, and the running list of guesses appears under "Developer Debug Info."
5. When you hit the secret, you win: balloons pop and the final score is shown.
6. Click **New Game 🔁** to start over — the guess history clears and the score resets to 0, instead of carrying over from the previous game.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]

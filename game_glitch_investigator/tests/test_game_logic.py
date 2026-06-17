from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _message = check_guess(40, 50)
    assert outcome == "Too Low"

# FIX: Regression test authored by Claude (agent mode) to lock in the high/low bug fix.
def test_string_secret_compares_numerically():
    # Regression for the high/low bug: app.py passes secret as a str on even
    # attempts. With lexicographic comparison "9" > "80" is True, so the old
    # code reported "Too High" even though 9 is well below 80. The fix coerces
    # both operands to int, so the direction must be "Too Low".
    outcome, _message = check_guess(9, "80")
    assert outcome == "Too Low"

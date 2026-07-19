# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

The recommender is a content-based scoring system. It does not use other users' listening history — it works entirely from song attributes and a single user profile.

**Data involved**

Each `Song` carries seven attributes loaded from `songs.csv`: `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`.

The `UserProfile` stores four preference fields: `favorite_genre`, `favorite_mood`, `target_energy`, and `likes_acoustic`.

**Algorithm Recipe**

The recommender loops over every song in the catalog and computes a score out of 10:

| Signal            | Max pts | Rule                                      |
| ----------------- | ------- | ----------------------------------------- |
| Genre match       | 4       | Exact match → 4, else 0                   |
| Mood match        | 3       | Exact match → 3, else 0                   |
| Energy similarity | 3       | `3 × (1 − │song.energy − target_energy│)` |

Genre is weighted most heavily (4 pts) because it is the hardest categorical boundary — a metal fan rarely enjoys lofi regardless of mood. Mood is softer and worth 3 pts. Energy is a continuous 0–1 float, so similarity is measured by absolute difference and scaled to 0–3 pts, meaning songs closer to the user's target energy score higher.

After scoring all songs the system sorts them by total score (descending) and returns the top K results.

**Data flow**

```
User Profile ──┐
               ├──► for each song: score = genre(4) + mood(3) + energy(3)
songs.csv  ────┘         └──► sort descending ──► slice top K ──► Ranked output
```

**Potential biases**

Genre lock-in: because genre carries the most weight (4/10 pts), songs outside the user's preferred genre are structurally disadvantaged even when they match well on every other dimension. A high-energy jazz track will never outscore a low-energy rock track for a rock-preferring user, regardless of how close the other attributes are.

Cold-start on new attributes: the system ignores `tempo_bpm`, `valence`, `danceability`, and `acousticness` in scoring. Songs that would be good matches on those dimensions get no credit for them, which may cause the ranked list to feel narrower than the catalog actually is.

Exact-match brittleness: mood scoring is all-or-nothing. "Intense" and "energized" are semantically close but score identically to "intense" vs. "chill". A song that is nearly a perfect mood match gets zero mood points if the label doesn't match exactly.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:

Sunrise City - Score: 9.94
Because: genre match (+4.0), mood match (+3.0), energy similarity (+2.9)

Gym Hero - Score: 6.61
Because: genre match (+4.0), energy similarity (+2.6)

Rooftop Lights - Score: 5.88
Because: mood match (+3.0), energy similarity (+2.9)

Midnight Crosswalk - Score: 2.97
Because: energy similarity (+3.0)

Night Drive Loop - Score: 2.85
Because: energy similarity (+2.8)

```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
  I learned about some concepts that used for recommendation. 
- about where bias or unfairness could show up in systems like this
  - 1. it based on what songs already in the database, so if the data pool is larger may have better recommendation.
  - 2. The scoring algorithm is kind of fixed right now, but different suer may value different metrics here. 
  




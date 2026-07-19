# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**MusicMate 1.0**

---

## 2. Intended Use

MusicMate generates ranked song recommendations for a user based on their stated genre, mood, and energy preferences. It is designed for classroom exploration — not production use — and assumes the user can describe their current taste in three simple fields. It makes no attempt to learn from listening history or adapt over time.

---

## 3. How the Model Works

For each song in the catalog, the system asks three questions and awards points for each:

Does the song's genre match what the user wants? If yes, it earns 4 points — the largest single contribution, because genre is the hardest boundary in taste. A metal fan rarely enjoys lofi regardless of how chill it is.

Does the mood match? An exact label match earns 3 points. Mood is softer than genre, so it is worth slightly less.

How close is the song's energy to the user's target? Energy is a number between 0 and 1 (quiet and calm to loud and driving). The closer a song is to the user's target, the more points it earns — up to 3. A perfect energy match earns the full 3; a song that is completely opposite earns 0.

The three point totals are added for a score out of 10. All songs are scored, then sorted from highest to lowest, and the top results are returned as recommendations.

One fix made during development: genre and mood comparisons are now case-insensitive, so a user who types "POP" gets the same results as one who types "pop."

---

## 4. Data

The catalog contains 20 songs loaded from `data/songs.csv`. Each song has ten fields: id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, and acousticness.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, classical, country, metal, blues, soul, hip hop, folk. Moods represented: happy, chill, intense, relaxed, focused, moody, calm, peaceful, nostalgic, upbeat, reflective, energized, warm, confident, cheerful.

The dataset was not modified. No songs were added or removed. Musical dimensions like lyrics, language, cultural context, tempo preference, and listening history are entirely absent.

---

## 5. Strengths

The system works well when the user has a clear, strong preference that aligns with the genre and mood labels in the catalog. A user who wants intense rock gets Storm Runner ranked near the top by a wide margin over everything else — the separation is clear and intuitive.

Energy scoring adds meaningful nuance within a genre. Among lofi songs, for example, a user targeting very low energy (0.25) will correctly rank Library Rain and Spacewalk Thoughts above Focus Flow, which runs slightly hotter.

The explanation string attached to each result makes the scoring transparent — the user can see exactly which signals fired and why.

---

## 6. Limitations and Bias

**Genre lock-in.** Genre carries 4 of 10 possible points. A song outside the user's preferred genre can score at most 6, while an in-genre song with poor energy matching can score 7 or higher. This structurally suppresses cross-genre discovery even when a song would otherwise be a good fit.

**Exact-match brittleness on mood.** "Intense" and "energized" are semantically close, but the system treats them as completely different. A song that nearly matches the user's mood gets zero mood points.

**Unused attributes.** tempo_bpm, valence, danceability, and acousticness are loaded but never used in scoring. The `acousticness` field in the user profile has no effect on results. Users who prefer acoustic music get no credit for that preference.

**Out-of-range energy.** If a user supplies an energy target above 1.0 or below 0.0 (e.g. 10.0), the energy similarity formula produces negative scores. No clamping or validation is applied.

**Small, curated catalog.** With only 20 songs, some genres have just one or two representatives. A blues fan will always be recommended Blue Porch Light regardless of how poorly it matches on other dimensions, simply because there is nothing else in the genre.

---

## 7. Evaluation

Six user profiles were tested: three realistic (`high_energy_pop`, `chill_lofi`, `deep_intense_rock`) and three edge cases (`case_mismatch_pop`, `impossible_energy`, `acousticness_only`).

For realistic profiles, recommendations matched intuition well. `chill_lofi` surfaced Library Rain, Midnight Coding, and Spacewalk Thoughts at the top — all genuine matches. `deep_intense_rock` correctly ranked Storm Runner first by a large margin.

The edge cases revealed two real issues. `case_mismatch_pop` (genre="POP") got zero genre and mood points before the case-insensitive fix was applied, causing Storm Runner — a rock song — to rank first for a pop user. `impossible_energy` (energy=10.0) produced negative energy scores across the board. `acousticness_only` confirmed that the acousticness preference field has no effect on rankings.

---

## 8. Future Work

Add partial mood credit so semantically similar moods (e.g. "intense" and "energized") earn 1–2 points instead of zero. This would reduce the all-or-nothing brittleness of mood scoring.

Incorporate the unused attributes — particularly acousticness and valence — into the score. Even a small weight on acousticness would make the `likes_acoustic` user preference meaningful.

Clamp energy inputs to [0.0, 1.0] before scoring to prevent negative scores from out-of-range values.

Add a diversity rule so the top-K results cannot all share the same genre, nudging the system toward occasional cross-genre discovery.

Expand the catalog. With 20 songs and 14 genres, some genres have only one representative. A larger dataset would make genre-based filtering more useful and reduce forced recommendations.

---

## 9. Personal Reflection

Building this system made it concrete why real recommenders layer collaborative filtering on top of content-based scoring: attributes like genre and mood capture structure, but they miss the texture of taste. Two people can both love "chill lofi" and still want completely different songs. The scoring recipe here is transparent and easy to debug, which is genuinely useful — but that transparency comes at the cost of nuance.

The most surprising finding was how much damage a single design decision (genre weight = 4) does to cross-genre discovery. It felt like the right call at the time, but testing showed it essentially locks users into one corner of the catalog regardless of how well songs match on every other dimension.

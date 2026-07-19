"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # print("\nLoaded songs:\n", len(songs), "songs")

    high_energy_pop = {
        "genre": "pop",
        "mood": "happy", 
        "energy": 0.9,
        "acousticness": 0.1,
    }

    chill_lofi = {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.25,
        "acousticness": 0.75,
    }

    deep_intense_rock = {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.85,
        "acousticness": 0.3,
    }

    # Edge case: capitalization prevents exact genre and mood matches.
    case_mismatch_pop = {
        "genre": "POP",
        "mood": "HAPPY",
        "energy": 0.9,
        "acousticness": 0.1,
    }

    # Adversarial: an out-of-range target can produce negative energy scores.
    impossible_energy = {
        "genre": "pop",
        "mood": "happy",
        "energy": 10.0,
        "acousticness": 0.1,
    }

    # Edge case: changing acousticness should affect results, but the current
    # scoring function does not use this preference.
    acousticness_only = {
        "genre": "not-a-real-genre",
        "mood": "not-a-real-mood",
        "energy": 0.5,
        "acousticness": 1.0,
    }

    test_profiles = [
        high_energy_pop,
        chill_lofi,
        deep_intense_rock,
    ]

    edge_case_profiles = [
        case_mismatch_pop,
        impossible_energy,
        acousticness_only,
    ]

    # Change this assignment to try a different preference profile.
    user_prefs = edge_case_profiles[0]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # print("\nTop recommendations:\n", recommendations)
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()

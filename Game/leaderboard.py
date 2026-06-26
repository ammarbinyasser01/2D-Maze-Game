import json
import os

SCORES_FILE = "highscores.json"


def _load() -> dict:
    if not os.path.exists(SCORES_FILE):
        return {"easy": [], "medium": [], "hard": []}
    try:
        with open(SCORES_FILE, "r") as f:
            data = json.load(f)
        # Back-compat: ensure all keys exist
        for key in ("easy", "medium", "hard"):
            data.setdefault(key, [])
        return data
    except (json.JSONDecodeError, IOError):
        return {"easy": [], "medium": [], "hard": []}


def _save(data: dict):
    with open(SCORES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_scores(difficulty: str) -> list:
    """Return sorted list of score dicts for the given difficulty (best first)."""
    data = _load()
    scores = data.get(difficulty, [])
    # Sort: lowest time first, then fewest collisions as tie-breaker
    return sorted(scores, key=lambda s: (s["time"], s["collisions"]))


def is_new_highscore(difficulty: str, elapsed: float) -> bool:
    """True if this time beats any existing top-5 score or the list has <5 entries."""
    scores = get_scores(difficulty)
    if len(scores) < 5:
        return True
    return elapsed < scores[-1]["time"]


def save_score(difficulty: str, name: str, elapsed: float, collisions: int):
    """Append a score and keep only the best 10 per difficulty."""
    data = _load()
    entry = {
        "name": name,
        "time": round(elapsed, 3),
        "collisions": collisions,
    }
    data[difficulty].append(entry)
    # Keep only best 10
    data[difficulty] = sorted(
        data[difficulty], key=lambda s: (s["time"], s["collisions"])
    )[:10]
    _save(data)
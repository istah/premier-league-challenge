"""Synthetic, football-realistic match event generator (seeded, no external data)."""
import json
import random
import sys
from dataclasses import asdict, dataclass

KINDS = ["pass", "pass", "pass", "carry", "tackle", "shot", "foul", "corner"]


@dataclass
class Event:
    minute: int
    team: str
    player: str
    kind: str
    x: float  # pitch 0-100, attacking left to right
    y: float
    detail: dict


def generate_match(seed: int = 0, home: str = "Reds", away: str = "Blues", n: int = 60, home_players: list[str] | None = None, away_players: list[str] | None = None) -> list[Event]:
    rng = random.Random(seed)
    squads = {t: [f"{t} #{i}" for i in range(1, 12)] for t in (home, away)}
    if home_players:
        squads[home] = home_players
    if away_players:
        squads[away] = away_players
    events = []
    for minute in sorted(rng.randint(1, 90) for _ in range(n)):
        team = rng.choice([home, away])
        kind = rng.choice(KINDS)
        detail = {}
        if kind == "pass":
            detail = {"completed": rng.random() < 0.8, "length_m": round(rng.uniform(3, 45), 1)}
        elif kind == "shot":
            detail = {"xg": round(rng.uniform(0.02, 0.6), 2), "speed_kmh": round(rng.uniform(60, 120)), "goal": rng.random() < 0.2}
        events.append(Event(minute, team, rng.choice(squads[team]), kind, round(rng.uniform(0, 100), 1), round(rng.uniform(0, 100), 1), detail))
    return events


if __name__ == "__main__":
    print(json.dumps([asdict(e) for e in generate_match(int(sys.argv[1]) if len(sys.argv) > 1 else 0)], indent=2))

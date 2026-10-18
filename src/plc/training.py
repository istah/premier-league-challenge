"""Synthetic training sessions with wearable-style biometrics; rating drifts from the preseason baseline."""
import random
from dataclasses import dataclass

from .squad import Player

ALPHA = 0.15  # weight of the latest session in the rating


@dataclass
class Session:
    day: int
    player: str
    hr_avg: int
    hr_max: int
    load: float  # strain, 0-21
    hrv_morning: float
    sleep_h: float
    score: float  # coach-observed performance, 0-100


def run_training(squad: list[Player], days: int = 14, seed: int = 0) -> list[Session]:
    """Mutates player.rating. Each player has a hidden form trend so ratings genuinely diverge."""
    rng = random.Random(seed)
    trend = {p.name: rng.uniform(-1.0, 1.0) for p in squad}
    sessions = []
    for day in range(1, days + 1):
        for p in squad:
            sleep = round(rng.uniform(5.5, 9), 1)
            hrv = round(p.base_hrv * (0.75 + 0.05 * sleep) * rng.uniform(0.9, 1.1), 1)
            score = min(100, max(0, p.rating + trend[p.name] * 4 + (hrv / p.base_hrv - 1) * 20 + rng.gauss(0, 4)))
            sessions.append(Session(day, p.name, rng.randint(120, 150), rng.randint(175, 195), round(rng.uniform(8, 18), 1), hrv, sleep, round(score, 1)))
            p.rating = round((1 - ALPHA) * p.rating + ALPHA * score, 1)
    return sessions

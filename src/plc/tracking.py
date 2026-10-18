"""Live match tracking snapshots (GPS + heart rate) for the starting XI, every 5 minutes."""
import random
from dataclasses import dataclass

from .squad import Player


@dataclass
class Snapshot:
    minute: int
    player: str
    distance_m: int  # covered in the last 5 minutes
    sprints: int
    hr: int
    hrv_baseline_ratio: float  # match-day morning HRV / personal baseline


def track_match(starters: list[Player], hrv_ratio: dict[str, float], seed: int = 0) -> list[Snapshot]:
    """Players with low match-day HRV fade after ~55', which is the storyline the agents must catch."""
    rng = random.Random(seed)
    out = []
    for minute in range(5, 95, 5):
        for p in starters:
            r = hrv_ratio.get(p.name, 1.0)
            fade = max(0, minute - 55) / 35 * max(0, 1 - r) * 3 if r < 0.9 else 0
            out.append(Snapshot(minute, p.name, round(rng.gauss(560, 40) * (1 - fade)), max(0, round(rng.gauss(2, 1) * (1 - fade))),
                                round(rng.gauss(165, 6) + fade * 12), r))
    return out

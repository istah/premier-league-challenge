"""Pre-match readiness from wearables, and the XI suggestion. Deterministic signals; the agents explain them."""
import random

from .squad import Player

NOT_READY = 0.8  # match-day HRV below 80% of personal baseline


def match_day_hrv(squad: list[Player], seed: int = 0, tired: str | None = None) -> dict[str, float]:
    rng = random.Random(seed)
    ratio = {p.name: round(rng.uniform(0.85, 1.1), 2) for p in squad}
    if tired:
        ratio[tired] = 0.62
    return ratio


def score(p: Player, hrv: dict[str, float]) -> float:
    return p.rating * min(1.0, hrv[p.name] + 0.1)


def pick_xi(squad: list[Player], hrv: dict[str, float], shape=(("GK", 1), ("DEF", 4), ("MID", 3), ("FWD", 3))):
    xi, bench = [], []
    for pos, n in shape:
        ranked = sorted((p for p in squad if p.position == pos), key=lambda p: -score(p, hrv))
        xi += ranked[:n]
        bench += ranked[n:]
    return xi, bench


def concerns(xi: list[Player], hrv: dict[str, float]) -> list[str]:
    return [f"{p.name}: match-day HRV {hrv[p.name]:.0%} of baseline" for p in xi if hrv[p.name] < NOT_READY]

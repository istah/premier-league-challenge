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


POOR_WELLNESS = 18  # Hooper index 4 (best) .. 28 (worst): sleep, stress, soreness, fatigue each rated 1-7


def match_day_wellness(squad: list[Player], seed: int = 0, poor: tuple[str, ...] = ()) -> dict[str, dict[str, int]]:
    """Self-reported morning check-in. Independent of HRV on purpose: it can disagree, and that is the point."""
    rng = random.Random(f"{seed}:wellness")
    out = {p.name: {k: min(7, max(1, round(rng.gauss(2.8, 1.0)))) for k in ("sleep", "stress", "soreness", "fatigue")} for p in squad}
    for name in poor:
        out[name] = {"sleep": 6, "stress": 5, "soreness": 6, "fatigue": 6}
    return out


def hooper(w: dict[str, int]) -> int:
    return sum(w.values())


def wellness_ratio(w: dict[str, int]) -> float:
    """Hooper index as a readiness ratio on the same scale as HRV (1.1 best .. 0.6 worst)."""
    return round(1.1 - (hooper(w) - 4) / 24 * 0.5, 2)


def ready_ratio(name: str, hrv: dict[str, float], wellness: dict | None) -> float:
    """Research found subjective wellness tracks match fatigue at least as well as HRV, so it gets the larger weight."""
    return hrv[name] if not wellness else round(0.4 * hrv[name] + 0.6 * wellness_ratio(wellness[name]), 2)


def score(p: Player, hrv: dict[str, float], wellness: dict | None = None) -> float:
    return p.rating * min(1.0, ready_ratio(p.name, hrv, wellness) + 0.1)


def pick_xi(squad: list[Player], hrv: dict[str, float], wellness: dict | None = None, shape=(("GK", 1), ("DEF", 4), ("MID", 3), ("FWD", 3))):
    xi, bench = [], []
    for pos, n in shape:
        ranked = sorted((p for p in squad if p.position == pos), key=lambda p: -score(p, hrv, wellness))
        xi += ranked[:n]
        bench += ranked[n:]
    return xi, bench


def concerns(xi: list[Player], hrv: dict[str, float], wellness: dict | None = None) -> list[str]:
    out = []
    for p in xi:
        low_hrv, poor = hrv[p.name] < NOT_READY, bool(wellness) and hooper(wellness[p.name]) >= POOR_WELLNESS
        if low_hrv:
            out.append(f"{p.name}: match-day HRV {hrv[p.name]:.0%} of baseline" + (f", wellness poor (Hooper {hooper(wellness[p.name])}/28; 4 is best, 28 is worst)" if poor else ""))
        elif poor:
            out.append(f"{p.name}: HRV looks fine ({hrv[p.name]:.0%}) but his own wellness check-in is poor (Hooper {hooper(wellness[p.name])}/28; 4 is best, 28 is worst); HRV alone would miss this")
    return out

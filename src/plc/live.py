"""Live alerts: compare each player's recent output to their own first-half baseline."""
from dataclasses import dataclass
from statistics import mean

from .decision import p_substitute
from .squad import Player
from .tracking import Snapshot

ALERT_AT = 0.7


@dataclass
class Alert:
    minute: int
    off: str
    on: str
    probability: float
    evidence: str


def live_alerts(minute: int, snaps: list[Snapshot], xi: list[Player], bench: list[Player], hrv: dict[str, float]) -> list[Alert]:
    alerts = []
    for p in xi:
        mine = [s for s in snaps if s.player == p.name and s.minute <= minute]
        base, recent = [s for s in mine if s.minute <= 40], mine[-3:]
        if len(base) < 3 or len(recent) < 3 or minute < 50:
            continue
        drop = 1 - mean(s.distance_m for s in recent) / mean(s.distance_m for s in base)
        hr_over = mean(s.hr for s in recent) / mean(s.hr for s in base) - 1
        prob = p_substitute(drop, hr_over, hrv[p.name])
        if prob >= ALERT_AT:
            like = [b for b in bench if b.position == p.position]
            on = max(like, key=lambda b: b.rating).name if like else "none available"
            alerts.append(Alert(minute, p.name, on, prob, f"distance down {drop:.0%} vs first half, HR up {hr_over:.0%}, morning HRV {hrv[p.name]:.0%} of baseline"))
    return alerts

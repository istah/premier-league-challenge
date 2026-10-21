"""Live alerts: compare each player's recent output to their own first-half baseline."""
from dataclasses import dataclass
from statistics import mean

from .decision import p_substitute
from .readiness import NOT_READY
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
    drop: float = 0.0  # share of first-half output lost, for ordering and for remembering a dismissal
    strength: str = ""  # strong / moderate / watch: a rule score band, not a statistical confidence


def _band(prob: float) -> str:
    return "strong" if prob >= 0.9 else "moderate" if prob >= 0.8 else "watch"


def live_alerts(minute: int, snaps: list[Snapshot], xi: list[Player], bench: list[Player], hrv: dict[str, float]) -> list[Alert]:
    alerts = []
    for p in xi:
        if p.position == "GK":  # the engine gives goalkeepers outfield running numbers, which say nothing about them
            continue
        mine = [s for s in snaps if s.player == p.name and s.minute <= minute]
        base, recent = [s for s in mine if s.minute <= 40], mine[-3:]
        if len(base) < 3 or len(recent) < 3 or minute < 50:
            continue
        drop = 1 - mean(s.distance_m for s in recent) / mean(s.distance_m for s in base)
        hr_over = mean(s.hr for s in recent) / mean(s.hr for s in base) - 1
        prob = p_substitute(drop, hr_over, hrv[p.name])
        if prob >= ALERT_AT:
            like = [b for b in bench if b.position == p.position]
            rested = [b for b in like if hrv.get(b.name, 1.0) >= NOT_READY]  # never bring on a player the staff flagged as not ready
            on = max(rested, key=lambda b: b.rating).name if rested else "none available"
            hr = f"HR up {hr_over:.0%}" if hr_over >= 0 else f"HR down {abs(hr_over):.0%}"
            alerts.append(Alert(minute, p.name, on, prob, f"distance down {drop:.0%} vs first half, {hr}, morning HRV {hrv[p.name]:.0%} of baseline", round(drop, 3), _band(prob)))
    return sorted(alerts, key=lambda a: (-a.probability, -a.drop))  # worst first

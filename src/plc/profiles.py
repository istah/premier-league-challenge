"""Player archetypes and fit: which kind of player suits this opponent, formation and game plan.

Attributes are derived from the player's name, position and rating (seeded), so Player stays unchanged. They are synthetic,
and the needs weights are a modelling assumption informed by docs/RESEARCH.md, not fitted to real data.
"""
import random
from dataclasses import dataclass

from .fixtures import Opponent
from .squad import Player
from .tactics import FORMATIONS, HIGH

ATTRS = ("pace", "stamina", "aerial", "passing", "tackling", "finishing", "crossing", "composure")
BASE = {
    "GK": dict(pace=40, stamina=50, aerial=65, passing=55, tackling=30, finishing=20, crossing=30, composure=62),
    "DEF": dict(pace=58, stamina=62, aerial=68, passing=55, tackling=70, finishing=25, crossing=45, composure=60),
    "MID": dict(pace=60, stamina=70, aerial=50, passing=68, tackling=58, finishing=50, crossing=55, composure=66),
    "FWD": dict(pace=70, stamina=60, aerial=58, passing=55, tackling=30, finishing=72, crossing=45, composure=62),
}
LINES = ("DEF", "MID", "FWD")


def attributes(p: Player) -> dict[str, int]:
    rng = random.Random(f"{p.name}:attrs")
    return {a: round(max(25, min(95, BASE[p.position][a] + rng.gauss(0, 10) + (p.rating - 70) * 0.4))) for a in ATTRS}


def archetype(p: Player) -> str:
    a = attributes(p)
    kinds = {
        "DEF": {"attacking full-back": (a["crossing"] + a["pace"]) / 2 + 3, "ball-playing defender": a["passing"] + 3, "aerial stopper": a["aerial"], "tackling defender": a["tackling"]},
        "MID": {"destroyer": a["tackling"], "playmaker": a["passing"], "wide midfielder": (a["crossing"] + a["pace"]) / 2 + 3, "box-to-box midfielder": a["stamina"] - 2},
        "FWD": {"target man": a["aerial"] + 3, "pacey runner": a["pace"], "poacher": a["finishing"], "link forward": (a["passing"] + a["composure"]) / 2 + 3},
        "GK": {"goalkeeper": 1},
    }[p.position]
    return max(kinds, key=kinds.get)


@dataclass
class Need:
    attr: str
    weight: float
    reason: str


def needs(formation: str, instructions: dict, o: Opponent) -> dict[str, list[Need]]:
    """What each line needs from its players, with the reason (opponent, plan or formation) behind every need."""
    d = FORMATIONS[formation][0]
    out: dict[str, list[Need]] = {line: [] for line in LINES}

    def want(lines, attr, w, why):
        for line in lines:
            out[line].append(Need(attr, w, why))

    if o.press >= HIGH:
        want(("DEF", "MID"), "composure", 1.0, f"{o.name} press hard ({o.press:.0%}): calm on the ball")
        want(("DEF", "MID"), "passing", 0.8, "pass out of pressure")
    if (o.aerial + o.set_piece_threat) / 2 >= HIGH:
        want(("DEF",), "aerial", 1.0, f"{o.name} are dangerous in the air and on set pieces")
        want(("DEF",), "tackling", 0.5, "no needless fouls near the box")
    if instructions["press"] >= 65 or instructions["tempo"] >= 65:
        want(LINES, "stamina", 0.9, "pressing and tempo burn energy")
    if instructions["direct"] >= 65:
        want(("FWD", "MID"), "pace", 1.0, "fast vertical transitions need pace")
    if instructions["direct"] <= 35:
        want(("DEF", "MID", "FWD"), "passing", 1.0, "patient build-up needs short passing")
    if instructions["cross"] >= 60:
        want(("MID", "DEF"), "crossing", 0.9, "plan relies on crosses")
        want(("FWD",), "aerial", 0.9, "target men to attack the crosses")
    if instructions["cross"] <= 35:
        want(("MID", "FWD"), "composure", 0.8, "inside combinations and cutbacks need composure")
    if d != 4:
        want(("MID",), "stamina", 0.7, f"back {d}: wing-backs cover the whole flank")
    want(("FWD",), "finishing", 0.8, "chances must be taken")
    return out


def fit(p: Player, line: str, need: dict[str, list[Need]]) -> tuple[int, list[str]]:
    """0-100: rating blended with how well the attributes match the line's needs. Playing out of natural line costs 5% or 12%."""
    a, wanted = attributes(p), need.get(line, [])
    total = sum(n.weight for n in wanted)
    matched = sum(n.weight * a[n.attr] for n in wanted) / total if total else sum(a.values()) / len(a)
    score = (0.55 * p.rating + 0.45 * matched) * {0: 1.0, 1: 0.95, 2: 0.88}[abs(LINES.index(line) - LINES.index(p.position)) if p.position in LINES else 0]
    best = sorted(wanted, key=lambda n: -n.weight * (a[n.attr] - 60))[:2]
    return round(score), [f"{n.attr} {a[n.attr]}: {n.reason}" for n in best if a[n.attr] >= 65]

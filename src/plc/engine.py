"""Live match engine: ticks every 5 minutes, reacts to substitutions and mentality changes.

Code, not an LLM: the agents and the coach interface only read ticks and send commands.
"""
import random
from dataclasses import dataclass, field

from .events import Event
from .fixtures import make_opponent
from .readiness import match_day_hrv, pick_xi
from .squad import CLUB, Player, make_squad
from .tactics import FORMATIONS, assess, their_formation
from .tracking import Snapshot
from .training import run_training

ORDER = {"DEF": 0, "MID": 1, "FWD": 2}
PENALTY = {0: 1.0, 1: 0.95, 2: 0.88}  # strength multiplier by how many lines a player is moved from his natural one
MENTALITY = {"defend": (0.7, 0.75), "balanced": (1.0, 1.0), "attack": (1.3, 1.2)}  # (our chances, their chances)


@dataclass
class Shape:
    """One team's collective behaviour over the last 5 minutes: what the style analysts read."""
    possession: float  # %
    def_line: float  # height of the back line, 0 own goal .. 100 opponent goal
    fwd_pct: float  # share of passes going forward / sideways / back
    lateral_pct: float
    back_pct: float
    wide_pct: float  # share of attacks through the wide channels
    ppda: float  # opponent passes allowed per defensive action: lower means a more aggressive press


@dataclass
class Tick:
    minute: int
    snaps: list[Snapshot]
    events: list[Event]
    score: tuple[int, int]
    shapes: dict[str, Shape] = field(default_factory=dict)  # keyed "us" / "them"
    frames: list[dict] = field(default_factory=list)  # 5 one-minute frames: name -> [x, y] on a 0-100 pitch, plus "ball"


@dataclass
class Match:
    xi: list[Player]
    bench: list[Player]
    hrv: dict[str, float]
    opponent: str = "Harbour Rovers"
    opp_strength: float = 72.0
    seed: int = 0
    minute: int = 0
    score: list[int] = field(default_factory=lambda: [0, 0])
    mentality: str = "balanced"
    formation: str = "4-3-3"
    snaps: list[Snapshot] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    shapes: list[dict[str, Shape]] = field(default_factory=list)

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.entered = {p.name: 0 for p in self.xi}
        self.line = {p.name: p.position for p in self.xi}
        self.profile = make_opponent(self.opponent, self.seed)

    def fade(self, p: Player) -> float:
        r = self.hrv.get(p.name, 1.0)
        played = self.minute - self.entered[p.name]
        return max(0, played - 55) / 35 * max(0, 1 - r) * 3 if r < 0.9 else 0

    def distance(self, p: Player) -> int:
        return abs(ORDER.get(self.line[p.name], 0) - ORDER.get(p.position, 0))

    def moves(self) -> dict[str, str]:
        return {p.name: f"{p.position}->{self.line[p.name]}" for p in self.xi if self.line[p.name] != p.position}

    def strength(self) -> float:
        return sum(p.rating * (1 - self.fade(p)) * PENALTY[self.distance(p)] for p in self.xi) / len(self.xi)

    def substitute(self, off: str, on: str) -> None:
        out, inn = next(p for p in self.xi if p.name == off), next(p for p in self.bench if p.name == on)
        self.xi[self.xi.index(out)], self.bench[self.bench.index(inn)] = inn, out
        self.entered[inn.name] = self.minute
        self.line[inn.name] = self.line.pop(out.name)

    def set_formation(self, formation: str) -> None:
        """Re-deals the outfield into the new lines from natural positions, so players shift along the chain (a midfielder drops into defence, a forward into midfield).
        Within a line the lowest-rated players are dealt first, so the strongest keep their natural role. A modelling choice."""
        if formation not in FORMATIONS:
            return
        outfield = sorted((p for p in self.xi if self.line[p.name] != "GK"), key=lambda p: (ORDER[p.position], p.rating))
        lines = [line for line, n in zip(("DEF", "MID", "FWD"), FORMATIONS[formation]) for _ in range(n)]
        self.line.update({p.name: line for p, line in zip(outfield, lines)})
        self.formation = formation

    def set_mentality(self, mentality: str) -> None:
        if mentality in MENTALITY:
            self.mentality = mentality

    def tick(self) -> Tick:
        self.minute += 5
        snaps = []
        for p in self.xi:
            f = self.fade(p)
            snaps.append(Snapshot(self.minute, p.name, round(self.rng.gauss(560, 40) * (1 - f)), max(0, round(self.rng.gauss(2, 1) * (1 - f))),
                                  round(self.rng.gauss(165, 6) + f * 12), self.hrv.get(p.name, 1.0)))
        mine, theirs = MENTALITY[self.mentality]
        fit = assess(self.formation, self.profile).fit
        mine, theirs = mine * (1 + fit), theirs * (1 - fit / 2)
        events = []
        for side, chance in ((0, 0.35 * self.strength() / 70 * mine), (1, 0.35 * self.opp_strength / 70 * theirs)):
            if self.rng.random() < chance:
                xg = round(self.rng.uniform(0.03, 0.5), 2)
                goal = self.rng.random() < xg
                self.score[side] += goal
                shooter = self.rng.choice([p for p in self.xi if p.position in ("FWD", "MID")]).name if side == 0 else f"{self.opponent} #{self.rng.randint(2, 11)}"
                events.append(Event(self.minute, CLUB if side == 0 else self.opponent, shooter, "shot",
                                    round(self.rng.uniform(75, 98), 1), round(self.rng.uniform(25, 75), 1), {"xg": xg, "goal": goal}))
        self.snaps += snaps
        self.events += events
        shapes = self._shapes()
        self.shapes.append(shapes)
        return Tick(self.minute, snaps, events, (self.score[0], self.score[1]), shapes, self._frames(shapes))

    def _shapes(self) -> dict[str, Shape]:
        g, d, m, f = self.rng.gauss, *FORMATIONS[self.formation]
        push = {"defend": -10, "balanced": 0, "attack": 10}[self.mentality]
        us_pos = max(30, min(70, 50 + 6 * (m - 3) + (self.strength() - self.opp_strength) * 0.4 + push / 3 + g(0, 1.5)))
        lat = 28 + 4 * (m - 3)
        us = Shape(round(us_pos, 1), round(38 + push + 2 * (f - 3) + g(0, 1.5), 1), round(40 + push / 2 + g(0, 2), 1), round(lat + g(0, 2), 1),
                   round(max(5, 100 - (40 + push / 2) - lat + g(0, 1)), 1), round(35 + (10 if d != 4 else 0) + g(0, 2), 1), round(12 - push / 2 + g(0, 1), 1))
        o = self.profile
        lead = self.score[1] > self.score[0] and self.minute >= 65  # a leading opponent sits deeper
        line = 30 + 25 * o.press - (12 if lead else 0) + g(0, 1.5)
        fwd = 28 + 30 * o.aerial + g(0, 2)
        them = Shape(round(100 - us_pos, 1), round(line, 1), round(fwd, 1), round(30 + g(0, 2), 1), round(max(5, 70 - fwd + g(0, 1)), 1),
                     round(55 - 20 * o.press + g(0, 2), 1), round(14 - 10 * o.press + (4 if lead else 0) + g(0, 1), 1))
        return {"us": us, "them": them}

    def _frames(self, shapes: dict[str, Shape]) -> list[dict]:
        """Player positions for each minute of the tick: anchored to formation and block height, pulled towards the ball."""
        us, them = shapes["us"], shapes["them"]
        anchors = {}

        def place(names_by_line: dict[str, list[str]], height: float, mirror: bool):
            for line, names in names_by_line.items():
                x = {"GK": 5, "DEF": height, "MID": height + 18, "FWD": min(92, height + 36)}[line]
                for i, name in enumerate(names):
                    anchors[name] = (100 - x if mirror else x, (i + 1) / (len(names) + 1) * 100)

        ours: dict[str, list[str]] = {}
        for p in self.xi:
            ours.setdefault(self.line[p.name], []).append(p.name)
        place(ours, us.def_line, False)
        d, m, f = FORMATIONS[their_formation(self.profile)]
        n = iter(f"{self.opponent} #{i}" for i in range(1, 12))
        place({line: [next(n) for _ in range(c)] for line, c in (("GK", 1), ("DEF", d), ("MID", m), ("FWD", f))}, them.def_line, True)

        clamp = lambda v, lo, hi: max(lo, min(hi, v))
        ball, frames = [50 + (us.possession - 50) * 0.8, 50.0], []
        for _ in range(5):
            ball = [clamp(ball[0] + self.rng.gauss(0, 6), 3, 97), clamp(ball[1] + self.rng.gauss(0, 10), 5, 95)]
            frame = {"ball": [round(ball[0], 1), round(ball[1], 1)]}
            for name, (x, y) in anchors.items():
                pull = 0.05 if x < 8 or x > 92 else 0.18
                frame[name] = [round(clamp(x + (ball[0] - 50) * pull + self.rng.gauss(0, 1.5), 2, 98), 1), round(clamp(y + (ball[1] - 50) * 0.12 + self.rng.gauss(0, 2), 3, 97), 1)]
            frames.append(frame)
        return frames

    @property
    def finished(self) -> bool:
        return self.minute >= 90


def new_match(seed: int = 7) -> tuple["Match", list[Player]]:
    """The demo scenario: the AI rests the tired star, the coach starts him anyway, and he fades after ~55'."""
    squad = make_squad(seed)
    run_training(squad, seed=seed)
    tired = max((p for p in squad if p.position == "MID"), key=lambda p: p.rating).name
    hrv = match_day_hrv(squad, seed, tired)
    xi, bench = pick_xi(squad, hrv)
    if tired not in [p.name for p in xi]:
        t = next(p for p in squad if p.name == tired)
        weak = min((p for p in xi if p.position == "MID"), key=lambda p: p.rating)
        xi[xi.index(weak)] = t
        bench[:] = [b for b in bench if b.name != tired] + [weak]
    return Match(xi, bench, hrv, seed=seed), squad

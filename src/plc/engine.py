"""Live match engine: ticks every 5 minutes, reacts to substitutions and mentality changes.

Code, not an LLM: the agents and the coach interface only read ticks and send commands.
"""
import random
from dataclasses import dataclass, field

from .events import Event
from .fixtures import make_opponent
from .readiness import match_day_hrv, pick_xi
from .squad import CLUB, Player, make_squad
from .tactics import FORMATIONS, assess
from .tracking import Snapshot
from .training import run_training

ORDER = {"DEF": 0, "MID": 1, "FWD": 2}
OUT_OF_POSITION = 0.93  # strength multiplier for a player used outside their natural line
MENTALITY = {"defend": (0.7, 0.75), "balanced": (1.0, 1.0), "attack": (1.3, 1.2)}  # (our chances, their chances)


@dataclass
class Tick:
    minute: int
    snaps: list[Snapshot]
    events: list[Event]
    score: tuple[int, int]


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

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.entered = {p.name: 0 for p in self.xi}
        self.line = {p.name: p.position for p in self.xi}
        self.profile = make_opponent(self.opponent, self.seed)

    def fade(self, p: Player) -> float:
        r = self.hrv.get(p.name, 1.0)
        played = self.minute - self.entered[p.name]
        return max(0, played - 55) / 35 * max(0, 1 - r) * 3 if r < 0.9 else 0

    def strength(self) -> float:
        return sum(p.rating * (1 - self.fade(p)) * (1 if self.line[p.name] == p.position else OUT_OF_POSITION) for p in self.xi) / len(self.xi)

    def substitute(self, off: str, on: str) -> None:
        out, inn = next(p for p in self.xi if p.name == off), next(p for p in self.bench if p.name == on)
        self.xi[self.xi.index(out)], self.bench[self.bench.index(inn)] = inn, out
        self.entered[inn.name] = self.minute
        self.line[inn.name] = self.line.pop(out.name)

    def set_formation(self, formation: str) -> None:
        """Re-deals the outfield into the new lines, keeping players in their natural order, so some may end up out of position."""
        if formation not in FORMATIONS:
            return
        outfield = sorted((p for p in self.xi if self.line[p.name] != "GK"), key=lambda p: ORDER[p.position])
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
        return Tick(self.minute, snaps, events, (self.score[0], self.score[1]))

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

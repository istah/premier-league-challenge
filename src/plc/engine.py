"""Live match engine: ticks every 5 minutes, reacts to substitutions and mentality changes.

Code, not an LLM: the agents and the coach interface only read ticks and send commands.
"""
import random
from dataclasses import dataclass, field

from .events import Event
from .fixtures import make_opponent
from .readiness import match_day_hrv, match_day_wellness, pick_xi, wellness_ratio
from .squad import CLUB, Player, make_squad
from .tactics import FORMATIONS, assess, their_formation
from .tracking import Snapshot
from .training import run_training

ORDER = {"DEF": 0, "MID": 1, "FWD": 2}
PENALTY = {0: 1.0, 1: 0.95, 2: 0.88}  # strength multiplier by how many lines a player is moved from his natural one
def _plan(press, line, width, tempo, direct, cross, box):
    return {"press": press, "line": line, "width": width, "tempo": tempo, "direct": direct, "cross": cross, "box": box}


# 0-100 sliders, 50 neutral. direct: build-up speed (low = patient, high = fast and vertical). cross: crosses vs inside passes/cutbacks.
# box: how many players are committed into the penalty area. Plans follow the styles in docs/RESEARCH.md.
PRESETS = {"defend": _plan(35, 30, 50, 40, 50, 50, 40), "balanced": _plan(50, 50, 50, 50, 50, 50, 50), "attack": _plan(70, 70, 60, 65, 55, 55, 70),
           "counter": _plan(25, 25, 45, 80, 85, 40, 40), "possession": _plan(55, 60, 55, 35, 20, 30, 60), "gegenpress": _plan(90, 75, 50, 85, 60, 45, 60),
           "wings": _plan(50, 55, 85, 55, 50, 85, 80), "inside": _plan(50, 55, 35, 50, 40, 15, 60)}


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
    cross_pct: float = 50.0  # share of box entries by cross (the rest: cutbacks and inside passes)
    box_players: float = 2.5  # average own players in the box when a chance is created


@dataclass
class Tick:
    minute: int
    snaps: list[Snapshot]
    events: list[Event]
    score: tuple[int, int]
    shapes: dict[str, Shape] = field(default_factory=dict)  # keyed "us" / "them"
    roles: dict = field(default_factory=dict)  # what each player is doing in the last frame
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
    mentality: str = "balanced"  # preset name, or "custom" once a slider moves
    instructions: dict = field(default_factory=lambda: dict(PRESETS["balanced"]))
    wellness: dict = field(default_factory=dict)  # name -> check-in scores, see readiness.py
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
        r = min(self.hrv.get(p.name, 1.0), wellness_ratio(self.wellness[p.name]) if p.name in self.wellness else 9)
        i = self.instructions
        played = (self.minute - self.entered[p.name]) * max(0.5, 1 + 0.008 * (i["press"] - 50) + 0.006 * (i["tempo"] - 50))  # pressing hard tires players sooner
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
        if mentality in PRESETS:
            self.mentality, self.instructions = mentality, dict(PRESETS[mentality])

    def set_instructions(self, **sliders: int) -> None:
        for k, v in sliders.items():
            if k in self.instructions:
                self.instructions[k] = max(0, min(100, int(v)))
        self.mentality = "custom"

    def tick(self) -> Tick:
        self.minute += 5
        snaps = []
        for p in self.xi:
            f = self.fade(p)
            snaps.append(Snapshot(self.minute, p.name, round(self.rng.gauss(560, 40) * (1 - f)), max(0, round(self.rng.gauss(2, 1) * (1 - f))),
                                  round(self.rng.gauss(165, 6) + f * 12), self.hrv.get(p.name, 1.0)))
        shapes = self._shapes()
        i = self.instructions
        counter = max(0, (i["direct"] - 50) / 50) * max(0, (50 - shapes["us"].possession) / 50) * 0.8  # direct sides profit when they cede the ball
        mine = (1 + counter) * (1 + 0.002 * (i["cross"] - 50)) * (1 + 0.004 * (i["press"] - 50) + 0.003 * (i["tempo"] - 50) + 0.002 * (i["line"] - 50))
        theirs = 1 + 0.004 * (i["line"] - 50) - 0.003 * (i["press"] - 50)  # a high line is exposed; a hard press disrupts them
        fit = assess(self.formation, self.profile).fit
        mine, theirs = mine * (1 + fit), theirs * (1 - fit / 2)
        events = []
        for side, chance in ((0, 0.35 * self.strength() / 70 * mine), (1, 0.35 * self.opp_strength / 70 * theirs)):
            if self.rng.random() < chance:
                xg = round(self.rng.uniform(0.03, 0.5 - 0.003 * (i["cross"] - 50) if side == 0 else 0.5), 2)  # crosses: more shots, lower quality
                goal = self.rng.random() < xg
                self.score[side] += goal
                shooter = self.rng.choice([p for p in self.xi if p.position in ("FWD", "MID")]).name if side == 0 else f"{self.opponent} #{self.rng.randint(2, 11)}"
                events.append(Event(self.minute, CLUB if side == 0 else self.opponent, shooter, "shot",
                                    round(self.rng.uniform(75, 98), 1), round(self.rng.uniform(25, 75), 1), {"xg": xg, "goal": goal}))
        self.snaps += snaps
        self.events += events
        self.shapes.append(shapes)
        frames, roles = self._frames(shapes)
        return Tick(self.minute, snaps, events, (self.score[0], self.score[1]), shapes, roles, frames)

    def _shapes(self) -> dict[str, Shape]:
        g, d, m, f = self.rng.gauss, *FORMATIONS[self.formation]
        i = self.instructions
        push = (i["line"] - 50) / 2
        fwd = 40 + (i["tempo"] - 50) / 5 + (i["direct"] - 50) * 0.25
        lat = 28 + 4 * (m - 3) - (i["direct"] - 50) * 0.15
        us_pos = max(30, min(70, 50 + 6 * (m - 3) + (self.strength() - self.opp_strength) * 0.4 + (i["line"] - 50) / 30 - (i["direct"] - 50) / 10 + g(0, 1.5)))
        us = Shape(round(us_pos, 1), round(38 + push + 2 * (f - 3) + g(0, 1.5), 1), round(fwd + g(0, 2), 1), round(lat + g(0, 2), 1),
                   round(max(5, 100 - fwd - lat + g(0, 1)), 1), round(35 + (i["width"] - 50) * 0.3 + (10 if d != 4 else 0) + g(0, 2), 1),
                   round(12 - (i["press"] - 50) * 0.1 + g(0, 1), 1), round(50 + (i["cross"] - 50) * 0.8 + g(0, 3), 1), round(1 + i["box"] / 100 * 3 + g(0, 0.2), 1))
        o = self.profile
        lead = self.score[1] > self.score[0] and self.minute >= 65  # a leading opponent sits deeper
        line = 30 + 25 * o.press - (12 if lead else 0) + g(0, 1.5)
        ofwd = 28 + 30 * o.aerial + g(0, 2)
        them = Shape(round(100 - us_pos, 1), round(line, 1), round(ofwd, 1), round(30 + g(0, 2), 1), round(max(5, 70 - ofwd + g(0, 1)), 1),
                     round(55 - 20 * o.press + g(0, 2), 1), round(14 - 10 * o.press + (4 if lead else 0) + g(0, 1), 1),
                     round(35 + 40 * o.aerial + g(0, 3), 1), round(2 + 1.5 * (1 - o.press) + g(0, 0.2), 1))
        return {"us": us, "them": them}

    def _frames(self, shapes: dict[str, Shape]) -> tuple[list[dict], dict[str, str]]:
        """Player positions for each minute of the tick: anchored to formation and block height, pulled towards the ball.
        Our players also act out the game plan: full-backs overlap or underlap, wide midfielders run the byline or tuck inside,
        and the box slider decides how many players attack the near post, penalty spot, far post and edge of the box."""
        us, them = shapes["us"], shapes["them"]
        i, anchors = self.instructions, {}

        def place(names_by_line: dict[str, list[str]], height: float, mirror: bool):
            for line, names in names_by_line.items():
                x = {"GK": 5, "DEF": height, "MID": height + 18, "FWD": min(92, height + 36)}[line]
                for k, name in enumerate(names):
                    y = (k + 1) / (len(names) + 1) * 100
                    anchors[name] = (100 - x if mirror else x, 50 + (y - 50) * (0.6 + 0.8 * i["width"] / 100) if not mirror else y)

        ours: dict[str, list[str]] = {}
        for p in self.xi:
            ours.setdefault(self.line[p.name], []).append(p.name)
        place(ours, us.def_line, False)
        d, m, f = FORMATIONS[their_formation(self.profile)]
        n = iter(f"{self.opponent} #{k}" for k in range(1, 12))
        place({line: [next(n) for _ in range(c)] for line, c in (("GK", 1), ("DEF", d), ("MID", m), ("FWD", f))}, them.def_line, True)

        clamp = lambda v, lo, hi: max(lo, min(hi, v))
        outer = lambda line, k: [ours[line][0], ours[line][-1]] if len(ours.get(line, [])) >= k else []
        fullbacks, wide_mids = outer("DEF", 4), outer("MID", 4)
        wingbacks = outer("MID", 5) if len(ours.get("DEF", [])) != 4 else []  # a back three or five plays with wing-backs
        wing = clamp((i["width"] - 40) / 60, 0, 1) * clamp((i["cross"] - 30) / 70, 0, 1)
        counter = i["direct"] >= 70 and i["line"] <= 40
        ball, frames, roles = [50 + (us.possession - 50) * 0.8, 50.0], [], {}
        for _ in range(5):
            ball = [clamp(ball[0] + self.rng.gauss(0, 6), 3, 97), clamp(ball[1] + self.rng.gauss(0, 10), 5, 95)]
            frame, attacking = {"ball": [round(ball[0], 1), round(ball[1], 1)]}, ball[0] > 55
            roles = {name: "holds shape" for name in ours.get("GK", []) + [n for l in ("DEF", "MID", "FWD") for n in ours.get(l, [])]}
            for name, (x, y) in anchors.items():
                pull = 0.05 if x < 8 or x > 92 else 0.18
                frame[name] = [x + (ball[0] - 50) * pull + self.rng.gauss(0, 1.5), y + (ball[1] - 50) * 0.12 + self.rng.gauss(0, 2)]
            if attacking:
                for name in fullbacks:
                    dx = 10 + 18 * wing
                    frame[name][0] += dx
                    if i["cross"] < 40:
                        frame[name][1] += (50 - frame[name][1]) * 0.25
                    roles[name] = "overlaps" if wing > 0.4 else "underlaps inside" if i["cross"] < 40 else "supports the winger"
                for name in wide_mids:
                    if i["cross"] >= 50:
                        frame[name][0] += 12
                        roles[name] = "runs the byline for crosses"
                    else:
                        frame[name][0] += 6
                        frame[name][1] += (50 - frame[name][1]) * 0.35
                        roles[name] = "tucks inside to combine"
                for name in wingbacks:
                    frame[name][0] += 16
                    roles[name] = "wing-back pushes high"
                if ball[0] > 68:
                    k = 1 + round(i["box"] / 100 * 3)
                    near = 40 if ball[1] < 50 else 60
                    slots = [(92, near, "attacks the near post"), (88, 50, "takes the penalty spot"), (92, 100 - near, "attacks the far post"), (80, 50, "waits on the edge of the box")]
                    inner = [n for n in ours.get("MID", []) if n not in wide_mids and n not in wingbacks]
                    for name, (sx, sy, role) in zip(ours.get("FWD", []) + inner, slots[:k]):
                        frame[name][:] = [sx + self.rng.gauss(0, 1), sy + self.rng.gauss(0, 2)]
                        roles[name] = role
            elif counter and ball[0] < 45:
                for name in ours.get("FWD", [])[:2]:
                    frame[name][0] = max(frame[name][0], 55)
                    roles[name] = "stays high, waits to counter"
            frames.append({k: [round(clamp(v[0], 2, 98), 1), round(clamp(v[1], 3, 97), 1)] for k, v in frame.items()})
        return frames, roles

    @property
    def finished(self) -> bool:
        return self.minute >= 90


def new_match(seed: int = 7) -> tuple["Match", list[Player]]:
    """The demo scenario: the AI rests the tired star, the coach starts him anyway, and he fades after ~55'."""
    squad = make_squad(seed)
    run_training(squad, seed=seed)
    tired = max((p for p in squad if p.position == "MID"), key=lambda p: p.rating).name
    hrv = match_day_hrv(squad, seed, tired)
    wellness = match_day_wellness(squad, seed, poor=(tired,))
    xi, bench = pick_xi(squad, hrv, wellness)
    if tired not in [p.name for p in xi]:
        t = next(p for p in squad if p.name == tired)
        weak = min((p for p in xi if p.position == "MID"), key=lambda p: p.rating)
        xi[xi.index(weak)] = t
        bench[:] = [b for b in bench if b.name != tired] + [weak]
    hidden = max((p for p in xi if p.position == "FWD"), key=lambda p: p.rating).name  # HRV fine, wellness poor: only the check-in reveals him
    wellness[hidden] = {"sleep": 6, "stress": 5, "soreness": 6, "fatigue": 5}
    hrv[hidden] = max(hrv[hidden], 0.95)
    return Match(xi, bench, hrv, seed=seed, wellness=wellness), squad

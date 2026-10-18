"""Fictional opponents (squads, physical profiles, style) and the fixture list."""
import random
from dataclasses import dataclass
from datetime import date

from .medical import Profile, make_profile

EPL = ["Harbour Rovers", "Northgate Athletic", "Valmont City", "Kingsbridge Town", "Ashford Wanderers", "Stonebury FC",
       "Eastcliff Albion", "Westfield Rangers", "Marlowe Park", "Lakeside Borough", "Dunmere Forest", "Cragmoor Wolves"]
INTERNATIONAL = ["FC Alpenstadt", "Costa Azul SC", "Nordlicht IF", "Dinamo Karpati", "Sporting Atlantica", "Olympiaki Delta", "Pacifica FC"]
SHAPE = ["GK"] * 2 + ["DEF"] * 6 + ["MID"] * 6 + ["FWD"] * 4

# (month, day, competition, opponent index); international friendlies first, then league and continental cup
CALENDAR = [(7, 29, "Friendly", 0), (8, 2, "Friendly", 1), (8, 6, "Friendly", 2),
            (8, 15, "EPL", 0), (8, 22, "EPL", 1), (8, 29, "EPL", 2), (9, 12, "EPL", 3), (9, 19, "EPL", 4),
            (9, 26, "EPL", 5), (10, 3, "EPL", 6), (10, 17, "EPL", 7),
            (9, 16, "Continental Cup", 0), (9, 30, "Continental Cup", 1), (10, 7, "Continental Cup", 2), (10, 14, "Continental Cup", 3)]


@dataclass
class Fixture:
    match_id: str
    date: date
    competition: str
    opponent: str
    home: bool


@dataclass
class Opponent:
    name: str
    squad: list[Profile]
    positions: list[str]
    press: float
    aerial: float
    set_piece_threat: float


def make_fixtures(year: int = 2026) -> list[Fixture]:
    pool = {"Friendly": INTERNATIONAL, "EPL": EPL, "Continental Cup": INTERNATIONAL[3:]}
    rows = sorted((date(year, m, d), c, pool[c][i]) for m, d, c, i in CALENDAR)
    return [Fixture(f"M{n:02d}", dt, c, opp, n % 2 == 0) for n, (dt, c, opp) in enumerate(rows, 1)]


def make_opponent(name: str, seed: int = 0) -> Opponent:
    rng = random.Random(f"{seed}:{name}")
    squad = [make_profile(f"{name} #{i}", pos, rng) for i, pos in enumerate(SHAPE, 1)]
    return Opponent(name, squad, SHAPE, round(rng.uniform(0.2, 0.9), 2), round(rng.uniform(0.2, 0.9), 2), round(rng.uniform(0.2, 0.9), 2))

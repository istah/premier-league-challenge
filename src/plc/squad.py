"""Fictional club squad. Names and numbers are invented; any club can be swapped in."""
import random
from dataclasses import dataclass

CLUB = "Redmoor FC"
POSITIONS = ["GK"] * 2 + ["DEF"] * 7 + ["MID"] * 7 + ["FWD"] * 6
SURNAMES = ["Vance", "Okoro", "Lindqvist", "Marlow", "Duarte", "Haas", "Kimura", "Brandt", "Salah-Reyes", "Novak",
            "Ferreira", "Quinn", "Adeyemi", "Moretti", "Sato", "Calder", "Ibarra", "Thorne", "Dubois", "Petrov",
            "Walsh", "Mbeki", "Larsen"]


@dataclass
class Player:
    name: str
    position: str
    rating: float  # 0-100, preseason baseline, updated by training
    base_hrv: float  # ms, personal resting baseline


def make_squad(seed: int = 0) -> list[Player]:
    rng = random.Random(seed)
    names = rng.sample(SURNAMES, len(POSITIONS))
    return [Player(n, p, round(rng.uniform(60, 85), 1), round(rng.uniform(55, 100))) for n, p in zip(names, POSITIONS)]

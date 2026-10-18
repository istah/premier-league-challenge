"""Fictional club squad. Names and numbers are invented; any club can be swapped in."""
import random
from dataclasses import dataclass

CLUB = "Redmoor FC"
POSITIONS = ["GK"] * 2 + ["DEF"] * 7 + ["MID"] * 7 + ["FWD"] * 6
SURNAMES = ["Vance", "Okoro", "Lindqvist", "Marlow", "Duarte", "Haas", "Kimura", "Brandt", "Salah-Reyes", "Novak",
            "Ferreira", "Quinn", "Adeyemi", "Moretti", "Sato", "Calder", "Ibarra", "Thorne", "Dubois", "Petrov",
            "Walsh", "Mbeki", "Larsen"]
DEPTH = [("Okafor", "GK"), ("Bergstrom", "DEF"), ("Castellan", "DEF"), ("Nakamura-Hale", "DEF"), ("Teixeira", "MID"),
         ("Volkov", "MID"), ("Adler", "MID"), ("Osei", "FWD"), ("Delacroix", "FWD"), ("Hartmann", "FWD")]


@dataclass
class Player:
    name: str
    position: str
    rating: float  # 0-100, preseason baseline, updated by training
    base_hrv: float  # ms, personal resting baseline


def make_squad(seed: int = 0, depth: bool = False) -> list[Player]:
    """The first 22 are identical with or without `depth`; depth appends 10 reserves drawn after them."""
    rng = random.Random(seed)
    names = rng.sample(SURNAMES, len(POSITIONS))
    squad = list(zip(names, POSITIONS)) + (DEPTH if depth else [])
    return [Player(n, p, round(rng.uniform(60, 85), 1), round(rng.uniform(55, 100))) for n, p in squad]

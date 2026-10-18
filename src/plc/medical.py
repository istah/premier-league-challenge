"""Physical profiles and injuries. Separate from squad.py so the shared Player contract stays unchanged."""
import random
from dataclasses import dataclass
from datetime import date, timedelta

HEIGHT = {"GK": (192, 4), "DEF": (185, 5), "MID": (178, 5), "FWD": (181, 6)}  # cm mean, sd
INJURIES = [  # type, area, severity
    ("hamstring strain", "thigh", "moderate"), ("hamstring strain", "thigh", "minor"), ("ankle sprain", "ankle", "moderate"),
    ("calf strain", "calf", "minor"), ("groin strain", "groin", "moderate"), ("quadriceps contusion", "thigh", "minor"),
    ("knee ligament sprain", "knee", "severe"), ("metatarsal fracture", "foot", "severe"), ("muscle fatigue", "calf", "minor"),
    ("concussion", "head", "minor"),
]
DAYS_OUT = {"minor": (3, 10), "moderate": (14, 35), "severe": (60, 120)}


@dataclass
class Profile:
    name: str
    age: int
    height_cm: int
    weight_kg: float
    body_fat_pct: float
    dominant_foot: str
    vo2max: float
    top_speed_kmh: float
    resting_hr_base: int


def make_profile(name: str, position: str, rng: random.Random) -> Profile:
    mean, sd = HEIGHT[position]
    h = round(rng.gauss(mean, sd))
    bmi = rng.uniform(21.8, 24.5)
    return Profile(name, rng.randint(19, 36), h, round(bmi * (h / 100) ** 2, 1), round(rng.uniform(7, 13), 1),
                   rng.choices(["right", "left"], [0.78, 0.22])[0], round(rng.uniform(55, 68), 1),
                   round(rng.uniform(30, 36), 1), rng.randint(42, 58))


def sample_injury(rng: random.Random) -> tuple[str, str, str, int]:
    kind, area, sev = rng.choice(INJURIES)
    return kind, area, sev, rng.randint(*DAYS_OUT[sev])


def injury_history(name: str, start: date, rng: random.Random) -> list[dict]:
    rows = []
    for _ in range(rng.choices([0, 1, 2, 3], [0.3, 0.35, 0.25, 0.1])[0]):
        kind, area, sev, days = sample_injury(rng)
        rows.append({"player": name, "date": (start - timedelta(days=rng.randint(30, 1100))).isoformat(), "type": kind,
                     "area": area, "severity": sev, "days_out": days, "context": "history", "minute": "", "recurrence": 0})
    return rows

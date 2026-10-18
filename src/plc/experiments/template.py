"""Copy this file to <name>.py. Theory: opponents with high aerial strength score higher on set-piece threat. (Replace me.)"""
import csv
from pathlib import Path

from . import Signal


def run(bronze: Path = Path("data/bronze")) -> list[Signal]:
    teams = list(csv.DictReader(open(bronze / "opponents.csv")))
    return [Signal("set_piece_threat", t["team"], float(t["set_piece_threat"]),
                   f"{t['team']}: set-piece threat {t['set_piece_threat']}, aerial {t['aerial']}, avg height {t['avg_height_cm']} cm")
            for t in teams]

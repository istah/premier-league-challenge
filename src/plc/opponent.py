"""Opponent memory: per-opponent insights persisted to JSON and recalled before the next meeting."""
import json
from pathlib import Path

from .events import Event

STORE = Path("memory/opponents.json")


def analyse(events: list[Event], opponent: str) -> dict:
    mine = [e for e in events if e.team == opponent]
    passes = [e for e in mine if e.kind == "pass"]
    shots = [e for e in mine if e.kind == "shot"]
    return {
        "shots": len(shots),
        "xg": round(sum(e.detail["xg"] for e in shots), 2),
        "pass_completion": round(sum(e.detail["completed"] for e in passes) / max(1, len(passes)), 2),
        "fouls": sum(e.kind == "foul" for e in mine),
        "corners": sum(e.kind == "corner" for e in mine),
    }


def remember(opponent: str, insight: dict, store: Path = STORE) -> None:
    data = json.loads(store.read_text()) if store.exists() else {}
    data.setdefault(opponent, []).append(insight)
    store.parent.mkdir(exist_ok=True)
    store.write_text(json.dumps(data, indent=2))


def recall(opponent: str, store: Path = STORE) -> list[dict]:
    return json.loads(store.read_text()).get(opponent, []) if store.exists() else []

"""Coach-facing web API. In-memory sessions; the coach drives the clock and always has the last word."""
import re
import uuid
from dataclasses import asdict

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .coach import Decision, decide
from .engine import Match, new_match
from .tactics import FORMATIONS, assess, recommend
from .live import live_alerts
from .squad import Player

app = FastAPI(title="Redmoor FC Coach Room")
INDEX = Path(__file__).parent / "static" / "index.html"
SESSIONS: dict[str, tuple[Match, list[Player]]] = {}


NUMBERS = {"three": "3", "four": "4", "five": "5", "two": "2", "one": "1"}  # dictation spells digits out


class Command(BaseModel):
    transcript: str | None = None  # typed or dictated, e.g. "take off Vance, bring on Haas, go attacking"
    off: str | None = None
    on: str | None = None
    mentality: str | None = None
    formation: str | None = None


def _state(m: Match) -> dict:
    return {"minute": m.minute, "score": m.score, "mentality": m.mentality, "formation": m.formation, "formations": {f: assess(f, m.profile).verdict for f in FORMATIONS}, "recommended": recommend(m.profile),
            "tactics": asdict(assess(m.formation, m.profile)), "out_of_position": [p.name for p in m.xi if m.line[p.name] != p.position], "lines": m.line, "xi": [asdict(p) for p in m.xi],
            "bench": [asdict(p) for p in m.bench], "hrv": m.hrv}


def _get(mid: str) -> tuple[Match, list[Player]]:
    if mid not in SESSIONS:
        raise HTTPException(404, "unknown match")
    return SESSIONS[mid]


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(INDEX)


@app.post("/match")
def start(seed: int = 7, formation: str | None = None):
    mid = uuid.uuid4().hex[:8]
    SESSIONS[mid] = new_match(seed)
    if formation:
        SESSIONS[mid][0].set_formation(formation)  # the coach's starting shape
    return {"id": mid, **_state(SESSIONS[mid][0])}


@app.get("/match/{mid}")
def state(mid: str):
    return _state(_get(mid)[0])


@app.post("/match/{mid}/tick")
def tick(mid: str):
    m, _ = _get(mid)
    if m.finished:
        raise HTTPException(409, "full time")
    t = m.tick()
    alerts = [asdict(a) for a in live_alerts(t.minute, m.snaps, m.xi, m.bench, m.hrv)]  # suggestions only, never applied
    return {"tick": asdict(t), "alerts": alerts, **_state(m)}


@app.post("/match/{mid}/decision")
def decision(mid: str, cmd: Command):
    m, squad = _get(mid)
    ai = Decision(cmd.off, cmd.on, "ai") if cmd.off and cmd.on else None
    d = decide(ai, cmd.transcript, squad)
    if d:
        try:
            m.substitute(d.off, d.on)
        except StopIteration:
            raise HTTPException(422, f"{d.off} is not on the pitch or {d.on} is not on the bench")
    words = re.findall(r"\w+", (cmd.transcript or "").lower())
    mentality = cmd.mentality or next((k for k, w in (("attack", "attack"), ("attack", "attacking"), ("defend", "defend"), ("defend", "defensive"), ("balanced", "balanced")) if w in words), None)
    if mentality:
        m.set_mentality(mentality)
    spoken = " ".join(NUMBERS.get(w, w) for w in words)
    found = re.search(r"\b(\d) ?(\d) ?(\d)\b", spoken)
    formation = cmd.formation or (f"{found[1]}-{found[2]}-{found[3]}" if found else None)
    if formation:
        m.set_formation(formation)
    return {"applied": asdict(d) if d else None, **_state(m)}

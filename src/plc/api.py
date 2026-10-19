"""Coach-facing web API. In-memory sessions; the coach drives the clock and always has the last word."""
import re
import uuid
from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .coach import Decision, decide
from .engine import Match, new_match
from .live import live_alerts
from .squad import Player

app = FastAPI(title="Redmoor FC Coach Room")
SESSIONS: dict[str, tuple[Match, list[Player]]] = {}


class Command(BaseModel):
    transcript: str | None = None  # typed or dictated, e.g. "take off Vance, bring on Haas, go attacking"
    off: str | None = None
    on: str | None = None
    mentality: str | None = None


def _state(m: Match) -> dict:
    return {"minute": m.minute, "score": m.score, "mentality": m.mentality, "xi": [asdict(p) for p in m.xi],
            "bench": [asdict(p) for p in m.bench], "hrv": m.hrv}


def _get(mid: str) -> tuple[Match, list[Player]]:
    if mid not in SESSIONS:
        raise HTTPException(404, "unknown match")
    return SESSIONS[mid]


@app.post("/match")
def start(seed: int = 7):
    mid = uuid.uuid4().hex[:8]
    SESSIONS[mid] = new_match(seed)
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
    return {"applied": asdict(d) if d else None, **_state(m)}

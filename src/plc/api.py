"""Coach-facing web API. In-memory sessions; the coach drives the clock and always has the last word."""
import re
import uuid
from dataclasses import asdict

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .coach import Decision, decide, parse_orders
from .engine import PRESETS, Match, new_match
from .explain import explain
from .tactics import FORMATIONS, assess, recommend, their_formation
from .live import live_alerts
from .profiles import LINES, archetype, attributes, fit, needs
from .readiness import concerns, hooper, wellness_ratio
from . import bus, orchestrator
from .activator import Activator
from .staff import gold_facts
from .squad import Player

app = FastAPI(title="Redmoor FC Coach Room")
INDEX = Path(__file__).parent / "static" / "index.html"
SESSIONS: dict[str, tuple[Match, list[Player]]] = {}
ACTIVATORS: dict[str, Activator] = {}


KEYS = {"press": {"press", "pressing"}, "line": {"line", "deeper"}, "width": {"width", "wider", "narrower"}, "tempo": {"tempo", "faster", "slower"}}
UP = {"higher", "more", "up", "faster", "wider", "increase"}
DOWN = {"lower", "less", "down", "slower", "narrower", "deeper", "drop", "decrease"}
NUMBERS = {"three": "3", "four": "4", "five": "5", "two": "2", "one": "1"}  # dictation spells digits out


class Command(BaseModel):
    transcript: str | None = None  # typed or dictated, e.g. "take off Vance, bring on Haas, go attacking"
    off: str | None = None
    on: str | None = None
    mentality: str | None = None
    formation: str | None = None
    orders: dict[str, dict[str, int]] | None = None  # per-player: {depth, width}
    instructions: dict[str, int] | None = None  # press / line / width / tempo, 0-100


def _fit(m: Match) -> dict:
    need = needs(m.formation, m.instructions, m.profile)
    rows = {}
    for p in m.xi + m.bench:
        line = m.line.get(p.name, p.position)
        score, why = fit(p, line if line in LINES else "DEF", need)
        rows[p.name] = {"archetype": archetype(p), "fit": score, "why": why, "attrs": attributes(p), "line": line}
    ideas = []
    for line in LINES:
        xi = [p for p in m.xi if m.line[p.name] == line]
        bench = [b for b in m.bench if b.position == line]
        if xi and bench:
            worst, best = min(xi, key=lambda p: rows[p.name]["fit"]), max(bench, key=lambda b: fit(b, line, need)[0])
            gain = fit(best, line, need)[0] - rows[worst.name]["fit"]
            if gain >= 3:
                ideas.append({"off": worst.name, "on": best.name, "gain": gain, "line": line, "why": rows[best.name]["why"] or [f"{rows[best.name]['archetype']}"]})
    return {"players": rows, "ideas": ideas, "needs": {line: [{"attr": n.attr, "reason": n.reason} for n in sorted(ns, key=lambda n: -n.weight)[:3]] for line, ns in need.items()}}


def _state(m: Match) -> dict:
    return {"minute": m.minute, "score": m.score, "mentality": m.mentality, "formation": m.formation, "formations": {f: assess(f, m.profile).verdict for f in FORMATIONS}, "recommended": recommend(m.profile),
            "tactics": asdict(assess(m.formation, m.profile)), "out_of_position": [f"{n} ({mv})" for n, mv in m.moves().items()], "moves": m.moves(), "orders": m.orders, "explain": explain(m.instructions), "their_formation": their_formation(m.profile), "playerfit": _fit(m), "instructions": m.instructions, "presets": list(PRESETS),
            "wellness": {n: {"hooper": hooper(w), "ratio": wellness_ratio(w)} for n, w in m.wellness.items()}, "concerns": concerns(m.xi, m.hrv, m.wellness), "lines": m.line, "xi": [asdict(p) for p in m.xi],
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
    ACTIVATORS[mid] = Activator()
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
    bus.publish("tick", mid, {"minute": t.minute, "score": t.score, "shapes": asdict(t)["shapes"]})
    for e in t.events:
        bus.publish("shot", mid, asdict(e))
    facts = gold_facts(m)
    state = {"minute": t.minute, "alerts": alerts, "fading": sorted(a["off"] for a in alerts), "goals": sum(e.detail.get("goal", False) for e in t.events), "their_shifts": facts.get("their_shifts", []),
             "concerns": _state(m)["concerns"] if t.minute == 5 else [], "shape_issues": [(i["kind"], i.get("player")) for i in facts.get("shape_issues", [])], "score": t.score,
             "late_deficit": max(0, t.score[1] - t.score[0]) if t.minute >= 70 else 0, "late_lead": max(0, t.score[0] - t.score[1]) if t.minute >= 70 else 0}
    triggers = ACTIVATORS[mid].evaluate(state)
    for tr in triggers:
        bus.publish("trigger", mid, tr)
    return {"tick": asdict(t), "alerts": alerts, "triggers": triggers, **_state(m)}


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
    for name, o in {**parse_orders(cmd.transcript or "", m.xi), **(cmd.orders or {})}.items():
        m.set_order(name, o.get("depth"), o.get("width"))
    sliders = dict(cmd.instructions or {})
    for key, names in KEYS.items():  # "press higher", "sit deeper", "play faster"
        sign = (1 if UP & set(words) else -1 if DOWN & set(words) else 0) if names & set(words) else 0
        if sign:
            sliders.setdefault(key, max(0, min(100, m.instructions[key] + 20 * sign)))
    if sliders:
        m.set_instructions(**sliders)
    spoken = " ".join(NUMBERS.get(w, w) for w in words)
    found = re.search(r"\b(\d) ?(\d) ?(\d)\b", spoken)
    formation = cmd.formation or (f"{found[1]}-{found[2]}-{found[3]}" if found else None)
    if formation:
        m.set_formation(formation)
    return {"applied": asdict(d) if d else None, **_state(m)}


@app.get("/match/{mid}/briefing")
def staff_briefing(mid: str, route: str = "full"):
    out = orchestrator.run(_get(mid)[0], route)
    bus.publish("briefing", mid, {"route": route, "mode": out["mode"], "grounded": out["judge"]["grounded"], "score": out["judge"]["score"]})
    return out


@app.get("/events")
def events(limit: int = 50):
    return list(bus.LOG)[-limit:]

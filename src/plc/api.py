"""Coach-facing web API. In-memory sessions; the coach drives the clock and always has the last word."""
import re
import uuid
from dataclasses import asdict

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator

from .coach import Decision, decide, parse_orders
from .engine import PRESETS, IllegalSubstitution, Match, new_match
from .explain import explain
from .tactics import FORMATIONS, assess, recommend, their_formation
from .live import live_alerts
from .profiles import LINES, archetype, attributes, fit, needs
from .readiness import concerns, hooper, wellness_ratio
from . import bus, orchestrator
from .activator import Activator
from .staff import gold_facts
from .squad import Player

load_dotenv()  # live Foundry notes are available when .env is filled; everything works offline without it
app = FastAPI(title="Redmoor FC Coach Room")
INDEX = Path(__file__).parent / "static" / "index.html"
SESSIONS: dict[str, tuple[Match, list[Player]]] = {}
ACTIVATORS: dict[str, Activator] = {}
INSTRUCTION_KEYS = tuple(PRESETS["balanced"])


KEYS = {"press": {"press", "pressing"}, "line": {"line", "deeper"}, "width": {"width", "wider", "narrower"}, "tempo": {"tempo", "faster", "slower"}}
UP = {"higher", "more", "up", "faster", "wider", "increase"}
DOWN = {"lower", "less", "down", "slower", "narrower", "deeper", "drop", "decrease"}
NUMBERS = {"three": "3", "four": "4", "five": "5", "two": "2", "one": "1"}  # dictation spells digits out


class ApiError(Exception):
    """A rejected request. `detail` stays a plain string (the coach UI shows it as is); `code` and extra fields are for programs."""

    def __init__(self, status: int, code: str, message: str, **extra):
        self.status, self.code, self.message, self.extra = status, code, message, extra


@app.exception_handler(ApiError)
async def _api_error(_: Request, e: ApiError):
    return JSONResponse({"detail": e.message, "code": e.code, **e.extra}, status_code=e.status)


@app.exception_handler(RequestValidationError)
async def _invalid_input(_: Request, e: RequestValidationError):
    errors = [{"field": ".".join(str(x) for x in err["loc"] if x != "body"), "message": err["msg"].removeprefix("Value error, "), "type": err["type"]} for err in e.errors()]
    return JSONResponse({"detail": "; ".join(f"{x['field']}: {x['message']}" for x in errors), "code": "invalid_input", "errors": errors}, status_code=422)


class Order(BaseModel):
    model_config = ConfigDict(extra="forbid")
    depth: StrictInt | None = Field(None, ge=-100, le=100)  # pitch %, the engine keeps the total within +-30
    width: StrictInt | None = Field(None, ge=-100, le=100)


class Command(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transcript: str | None = None  # typed or dictated, e.g. "take off Vance, bring on Haas, go attacking"
    off: str | None = None
    on: str | None = None
    mentality: str | None = None
    formation: str | None = None
    orders: dict[str, Order] | None = None  # per-player: {depth, width}
    instructions: dict[str, StrictInt] | None = None  # press / line / width / tempo / direct / cross / box, 0-100

    @field_validator("mentality")
    @classmethod
    def _mentality(cls, v):
        if v is not None and v not in PRESETS:
            raise ValueError(f"unknown mentality '{v}'; expected one of {', '.join(PRESETS)}")
        return v

    @field_validator("formation")
    @classmethod
    def _formation(cls, v):
        if v is not None and v not in FORMATIONS:
            raise ValueError(f"unknown formation '{v}'; expected one of {', '.join(FORMATIONS)}")
        return v

    @field_validator("instructions")
    @classmethod
    def _instructions(cls, v):
        for k, x in (v or {}).items():
            if k not in INSTRUCTION_KEYS:
                raise ValueError(f"unknown instruction '{k}'; expected one of {', '.join(INSTRUCTION_KEYS)}")
            if not 0 <= x <= 100:
                raise ValueError(f"{k} must be between 0 and 100, got {x}")
        return v

    @model_validator(mode="after")
    def _complete(self):
        if (self.off is None) != (self.on is None) or (self.off is not None and not (self.off.strip() and self.on.strip())):
            raise ValueError("a substitution needs both 'off' and 'on', each a player name")
        if not any((self.transcript or "").strip() if k == "transcript" else v for k, v in self.model_dump().items()):
            raise ValueError("empty decision: give a substitution, formation, mentality, instructions, orders or a transcript")
        return self


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
        bench = [b for b in m.eligible_bench if b.position == line]
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
            "bench": [asdict(p) for p in m.bench], "hrv": m.hrv, "finished": m.finished, "opponent": m.opponent, "eligible": [b.name for b in m.eligible_bench],
            "substitutions": {"used": m.subs_used, "left": m.rules.max_subs - m.subs_used if m.rules.max_subs is not None else None,
                              "windows_left": m.rules.max_windows - m.windows_used if m.rules.max_windows is not None else None, "log": m.sub_log}}


def _get(mid: str) -> tuple[Match, list[Player]]:
    if mid not in SESSIONS:
        raise HTTPException(404, "unknown match")
    return SESSIONS[mid]


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(INDEX)


@app.post("/match")
def start(seed: int = 7, formation: str | None = None):
    if formation is not None and formation not in FORMATIONS:
        raise ApiError(422, "invalid_input", f"formation: unknown formation '{formation}'; expected one of {', '.join(FORMATIONS)}", errors=[{"field": "formation", "type": "value_error"}])
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
    alerts = [] if m.finished else [asdict(a) for a in live_alerts(t.minute, m.snaps, m.xi, m.eligible_bench, m.hrv)]  # suggestions only, never applied; none after the final whistle
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
    if m.finished:
        raise ApiError(409, "match_finished", "Full time: the match is over, no further changes are possible")
    ai = Decision(cmd.off, cmd.on, "ai") if cmd.off and cmd.on else None
    d = decide(ai, cmd.transcript, squad)
    orders = {**parse_orders(cmd.transcript or "", m.xi), **{k: o.model_dump() for k, o in (cmd.orders or {}).items()}}
    on_pitch = {p.name for p in m.xi} - ({d.off} if d else set()) | ({d.on} if d else set())
    unknown = sorted(set(orders) - on_pitch)
    if unknown:  # checked before anything is applied, so a rejected request changes nothing
        raise ApiError(422, "unknown_player", f"{', '.join(unknown)} not on the pitch, so no order can be given", players=unknown)
    if d:
        try:
            m.substitute(d.off, d.on)
        except IllegalSubstitution as e:
            raise ApiError(422, e.code, str(e), off=d.off, on=d.on, **substitution_status(m))
    words = re.findall(r"\w+", (cmd.transcript or "").lower())
    mentality = cmd.mentality or next((k for k, w in (("attack", "attack"), ("attack", "attacking"), ("defend", "defend"), ("defend", "defensive"), ("balanced", "balanced")) if w in words), None)
    if mentality:
        m.set_mentality(mentality)
    for name, o in orders.items():
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


def substitution_status(m: Match) -> dict:
    return {"subs_left": None if m.rules.max_subs is None else m.rules.max_subs - m.subs_used,
            "windows_left": None if m.rules.max_windows is None else m.rules.max_windows - m.windows_used, "minute": m.minute}


@app.get("/match/{mid}/briefing")
def staff_briefing(mid: str, route: str = "full", live: bool = False):
    m = _get(mid)[0]
    if route not in orchestrator.ROUTES:
        raise ApiError(422, "invalid_route", f"route: unknown route '{route}'; expected one of {', '.join(orchestrator.ROUTES)}", routes=list(orchestrator.ROUTES))
    minute = m.minute  # a live briefing takes about 45 s and the match may move on meanwhile
    out = orchestrator.run(m, route, live)
    out["live_available"] = orchestrator.live_available()
    if m.finished:  # after the final whistle the staff may talk, but there is nothing left to do
        for n in out["notes"]:
            n.pop("actions", None)
    bus.publish("briefing", mid, {"route": route, "minute": minute, "agents": out["agents"], "mode": out["mode"], "unsupported": out["judge"]["unsupported"], "revised": [n["agent"] for n in out["notes"] if n.get("revised")], "merged": any(n["agent"] == "Coach Briefing" for n in out["notes"]), "checker": next((n["claim"][:6] != "Check:" for n in out["notes"] if n["agent"] == "Fact-checker"), None), "grounded": out["judge"]["grounded"], "score": out["judge"]["score"]})
    return out


@app.get("/events")
def events(limit: int = Query(50, ge=0, le=500), match: str | None = None, kinds: str | None = None):
    """The event bus log, newest last. `match` and `kinds` (comma separated) filter it."""
    rows = [e for e in bus.LOG if (not match or e["match"] == match) and (not kinds or e["kind"] in kinds.split(","))]
    return rows[-limit:]


"""Orchestrator: turns an Activator trigger into the right agents, runs them, and has the Judge score the result.

Routing is a table, not a model call, so it is predictable and testable. Foundry mode runs the chosen agents through
staff.agent_briefing; offline mode builds the same notes from the gold facts.
"""
import asyncio
import threading
import os

from .engine import Match
from .judge import judge
from .staff import INSTRUCTIONS, agent_briefing, gold_facts, offline_briefing

ROUTES = {
    "fade": ["Formation Tactician", "Own-Style Analyst"],
    "opponent": ["Opponent Analyst", "Formation Tactician"],
    "goal": ["Opponent Analyst", "Own-Style Analyst", "Formation Tactician"],
    "readiness": ["Own-Style Analyst"],
    "shape": ["Formation Tactician"],
    "losing": ["Formation Tactician"],
    "leading": ["Formation Tactician"],
    "full": list(INSTRUCTIONS),
}

FOCUS = {"fade": "A player is fading (see alerts): say who, the numbers against his own baseline, and whether to replace him.",
         "opponent": "The opponent changed shape (see their_shifts): say what changed and what we should do about it.",
         "goal": "A goal was scored (see last_goal and score): say what it changes and what to do next.",
         "readiness": "Readiness concerns (see readiness_concerns): say who and why, with the numbers.",
         "shape": "Shape problems (see shape_issues): say which player should adjust and how.",
         "losing": "We are behind late: what should change.", "leading": "We are ahead late: how to protect it."}


REPEAT_MINUTES = 20  # the same plan or formation advice is not shown again within this time unless the situation changes


def _without_repeats(m: Match, route: str, notes: list[dict]) -> list[dict]:
    """Plan and formation advice the coach has already seen is not offered again while score, shape and plan are unchanged.
    Asking the same route twice in one minute returns the same notes; a different route in that minute does not repeat it."""
    state, kept = (tuple(m.score), m.formation, m.mentality), []
    for n in notes:
        acts, fresh = n.get("actions") or [], []
        for a in acts:
            if a["type"] not in ("plan", "formation"):
                fresh.append(a)
                continue
            key = (a["type"], a["value"])
            seen = m.advice_log.get(key)
            repeat = seen and seen[1] == state and (seen[2] != route if seen[0] == m.minute else m.minute - seen[0] < REPEAT_MINUTES)
            if not repeat:
                m.advice_log[key] = (m.minute, state, route) if not seen or seen[0] != m.minute else seen
                fresh.append(a)
        if acts and not fresh and n["agent"] == "Formation Tactician":
            continue  # the whole note was advice already given
        n = {k: v for k, v in n.items() if k != "actions"}
        kept.append({**n, **({"actions": fresh} if fresh else {})})
    return kept


_LOOP: asyncio.AbstractEventLoop | None = None


def _loop() -> asyncio.AbstractEventLoop:
    """One long-lived event loop for the model calls: asyncio.run per call closed the loop under the HTTP clients and printed 'Event loop is closed'."""
    global _LOOP
    if _LOOP is None:
        _LOOP = asyncio.new_event_loop()
        threading.Thread(target=_LOOP.run_forever, daemon=True).start()
    return _LOOP


def live_available() -> bool:
    return bool(os.environ.get("FOUNDRY_PROJECT_ENDPOINT") and os.environ.get("FOUNDRY_MODEL"))


def run(m: Match, route: str = "full", live: bool = False) -> dict:
    """Offline notes by default (instant). live=True has the Foundry agents write the words, which takes about 30 s."""
    facts, agents = gold_facts(m), ROUTES.get(route, ROUTES["full"])
    if not facts["ready"]:
        return {"route": route, "agents": agents, "mode": "offline", "notes": [], "judge": judge([], facts), "facts": facts}
    notes, mode = _without_repeats(m, route, offline_briefing(facts, route)), "offline"
    if live and live_available():
        try:
            actions = {n["agent"]: n.get("actions") for n in notes}  # rules propose the buttons; the agents write the words
            live = asyncio.run_coroutine_threadsafe(agent_briefing(facts, agents, FOCUS.get(route, "")), _loop()).result()
            notes, mode = [{**n, "actions": actions[n["agent"]]} if actions.get(n["agent"]) else n for n in live], "agents"
        except Exception as e:  # never leave the coach without a briefing
            print(f"agent briefing failed ({e}), using offline briefing")
    return {"route": route, "agents": agents, "mode": mode, "notes": notes, "judge": judge(notes, facts, mode == "agents"), "facts": facts}

"""Orchestrator: turns an Activator trigger into the right agents, runs them, and has the Judge score the result.

Routing is a table, not a model call, so it is predictable and testable. Foundry mode runs the chosen agents through
staff.agent_briefing; offline mode builds the same notes from the gold facts.
"""
import asyncio
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


def run(m: Match, route: str = "full") -> dict:
    facts, agents = gold_facts(m), ROUTES.get(route, ROUTES["full"])
    if not facts["ready"]:
        return {"route": route, "agents": agents, "mode": "offline", "notes": [], "judge": judge([], facts), "facts": facts}
    notes, mode = _without_repeats(m, route, offline_briefing(facts, route)), "offline"
    if os.environ.get("FOUNDRY_PROJECT_ENDPOINT") and os.environ.get("FOUNDRY_MODEL"):
        try:
            notes, mode = [n for n in asyncio.run(agent_briefing(facts)) if n["agent"] in agents or n["agent"] == "Fact-checker"], "agents"
        except Exception as e:  # never leave the coach without a briefing
            print(f"agent briefing failed ({e}), using offline briefing")
    return {"route": route, "agents": agents, "mode": mode, "notes": notes, "judge": judge(notes, facts), "facts": facts}

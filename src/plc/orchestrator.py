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


def run(m: Match, route: str = "full") -> dict:
    facts, agents = gold_facts(m), ROUTES.get(route, ROUTES["full"])
    if not facts["ready"]:
        return {"route": route, "agents": agents, "mode": "offline", "notes": [], "judge": judge([], facts), "facts": facts}
    notes, mode = offline_briefing(facts, route), "offline"
    if os.environ.get("FOUNDRY_PROJECT_ENDPOINT") and os.environ.get("FOUNDRY_MODEL"):
        try:
            notes, mode = [n for n in asyncio.run(agent_briefing(facts)) if n["agent"] in agents or n["agent"] == "Fact-checker"], "agents"
        except Exception as e:  # never leave the coach without a briefing
            print(f"agent briefing failed ({e}), using offline briefing")
    return {"route": route, "agents": agents, "mode": mode, "notes": notes, "judge": judge(notes, facts), "facts": facts}

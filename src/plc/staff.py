"""The coaching-staff agent team: three analysts in parallel, then a Fact-checker, then the Coach Briefing.

Agents read only the gold facts built here (see CLAUDE.md). Without Foundry env vars an offline briefing is built from the
same facts, each claim carrying the fact it came from, so the demo runs anywhere.
"""
import asyncio
import json
import os
from dataclasses import asdict

from .engine import Match
from .style import classify, shifts
from .tactics import assess, recommend, their_formation


def gold_facts(m: Match) -> dict:
    """Decision-ready facts: the only thing the agents are allowed to talk about."""
    recent = m.shapes[-4:] or []
    if not recent:
        return {"minute": m.minute, "ready": False}
    return {
        "ready": True, "minute": m.minute, "score": m.score, "opponent": m.opponent,
        "our_formation": m.formation, "their_formation": their_formation(m.profile), "our_mentality": m.mentality,
        "our_style": [asdict(s) for s in classify([h["us"] for h in recent])],
        "their_style": [asdict(s) for s in classify([h["them"] for h in recent])],
        "their_shifts": shifts(m.shapes, "them"), "our_shifts": shifts(m.shapes, "us"),
        "tactical_read": asdict(assess(m.formation, m.profile)), "recommended_formation": recommend(m.profile),
        "out_of_position": [p.name for p in m.xi if m.line[p.name] != p.position],
    }


def _labels(styles: list[dict]) -> str:
    return ", ".join(s["label"] for s in styles) or "no strong tendency"


def offline_briefing(f: dict) -> list[dict]:
    """Same shape as the agent output: [{agent, claim, source}]."""
    if not f["ready"]:
        return []
    out = [
        {"agent": "Opponent Analyst", "claim": f"{f['opponent']} play a {f['their_formation']} and show: {_labels(f['their_style'])}.", "source": "their_formation, their_style"},
        {"agent": "Own-Style Analyst", "claim": f"We are a {f['our_formation']} showing: {_labels(f['our_style'])}.", "source": "our_formation, our_style"},
    ]
    for s in f["their_shifts"]:
        out.append({"agent": "Opponent Analyst", "claim": f"{f['opponent']} have {s}.", "source": "their_shifts"})
    t = f["tactical_read"]
    adv = f"Switch to {f['recommended_formation']}." if f["recommended_formation"] != f["our_formation"] else "Keep the shape."
    out.append({"agent": "Formation Tactician", "claim": f"{t['formation']} is rated '{t['verdict']}': {t['reasons'][0]}. {adv}", "source": "tactical_read, recommended_formation"})
    return out


INSTRUCTIONS = {
    "Opponent Analyst": "Describe the opponent's formation, block height, pressing and passing style, and any shift in the last 20 minutes.",
    "Own-Style Analyst": "Describe how our team is playing (block, possession, passing, width) and what that exposes against this opponent.",
    "Formation Tactician": "Judge our formation against the opponent's style and give concrete movements per line. Recommend keeping or changing shape.",
}
RULES = " Use ONLY the JSON facts you are given and quote their numbers. If a fact is missing, say so. Max 3 sentences."


async def agent_briefing(f: dict) -> list[dict]:
    """Foundry path. UNVERIFIED against a live endpoint: written from the Agent Framework docs, not yet run."""
    from agent_framework.foundry import FoundryChatClient
    from agent_framework.orchestrations import ConcurrentBuilder
    from azure.identity import AzureCliCredential

    client = FoundryChatClient(project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], model=os.environ["FOUNDRY_MODEL"], credential=AzureCliCredential())
    facts = json.dumps(f)
    team = [client.as_agent(name=n.replace(" ", ""), instructions=i + RULES) for n, i in INSTRUCTIONS.items()]
    events = await ConcurrentBuilder(participants=team).build().run(facts)
    notes = [{"agent": n, "claim": o.text if hasattr(o, "text") else str(o), "source": "agent"} for n, o in zip(INSTRUCTIONS, events.get_outputs())]
    checker = client.as_agent(name="FactChecker", instructions="Compare each note with the JSON facts. Reply with a JSON list of the notes' sentences that are NOT supported, empty if all are." + RULES)
    verdict = await checker.run(json.dumps({"facts": f, "notes": notes}))
    return notes + [{"agent": "Fact-checker", "claim": str(verdict), "source": "facts"}]


def briefing(m: Match) -> dict:
    f = gold_facts(m)
    if f["ready"] and os.environ.get("FOUNDRY_PROJECT_ENDPOINT") and os.environ.get("FOUNDRY_MODEL"):
        try:
            return {"mode": "agents", "notes": asyncio.run(agent_briefing(f)), "facts": f}
        except Exception as e:  # never leave the coach without a briefing
            print(f"agent briefing failed ({e}), using offline briefing")
    return {"mode": "offline", "notes": offline_briefing(f), "facts": f}

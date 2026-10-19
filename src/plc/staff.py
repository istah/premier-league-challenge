"""The coaching-staff agent team: three analysts in parallel, then a Fact-checker, then the Coach Briefing.

Agents read only the gold facts built here (see CLAUDE.md). Without Foundry env vars an offline briefing is built from the
same facts, each claim carrying the fact it came from, so the demo runs anywhere.
"""
import asyncio
import json
import os
import re
from dataclasses import asdict

from .engine import Match
from .events import Event
from .live import live_alerts
from .readiness import concerns
from .style import classify, shifts
from .tactics import assess, recommend, their_formation


def shape_issues(m: Match, styles: list[dict]) -> list[dict]:
    """Spot where we are outnumbered or standing badly, and pick a player to adjust. Counts come from the engine's last frame."""
    out, ov = [], m.overloads()
    ours = [p for p in m.xi if m.line[p.name] != "GK"]
    last = m.last_frame
    if not last:
        return out
    c_us, c_them = ov["central"]
    if c_them - c_us >= 2:
        who = min((p for p in ours if m.line[p.name] == "FWD" and p.name not in m.orders), key=lambda p: abs(last[p.name][1] - 50), default=None)
        if who:
            out.append({"kind": "central_overload", "player": who.name, "us": c_us, "them": c_them, "action": {"type": "order", "player": who.name, "depth": -12, "width": 0, "label": f"{who.name}: drop deeper"}})
    for zone in ("top", "bottom"):
        z_us, z_them = ov[zone]
        if z_them - z_us >= 2:
            cands = [p for p in ours if m.line[p.name] in ("MID", "DEF") and p.name not in m.orders and (last[p.name][1] < 50) == (zone == "top")]
            who = min(cands, key=lambda p: abs(last[p.name][1] - (10 if zone == "top" else 90)), default=None)
            if who:
                out.append({"kind": f"{zone}_channel_overload", "player": who.name, "us": z_us, "them": z_them, "action": {"type": "order", "player": who.name, "depth": -8, "width": 12, "label": f"{who.name}: drop wider"}})
    line = next((float(re.search(r"averages ([\d.]+)", s["evidence"])[1]) for s in styles if s["label"] in ("high block", "mid block", "low block")), None)
    if line and line >= 45 and any(s["label"] == "direct play" for s in classify([h["them"] for h in m.shapes[-4:]])):
        out.append({"kind": "line_too_high", "line": line, "action": {"type": "sliders", "value": {"line": max(0, m.instructions["line"] - 20)}, "label": "Drop the back line"}})
    return out


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
        "our_instructions": m.instructions, "readiness_concerns": concerns(m.xi, m.hrv, m.wellness),
        "shape_issues": shape_issues(m, [asdict(x) for x in classify([h["us"] for h in recent])]), "orders": m.orders,
        "alerts": [asdict(a) for a in live_alerts(m.minute, m.snaps, m.xi, m.bench, m.hrv)], "possession_pct": round(sum(h["us"].possession for h in recent) / len(recent), 1),
        "xg": {"us": round(sum(e.detail["xg"] for e in m.events if e.team != m.opponent), 2), "them": round(sum(e.detail["xg"] for e in m.events if e.team == m.opponent), 2)},
        "last_goal": next(({"team": e.team, "player": e.player, "minute": e.minute} for e in reversed(m.events) if e.detail.get("goal")), None),
        "out_of_position": [f"{n} ({mv})" for n, mv in m.moves().items()],
    }


def _labels(styles: list[dict]) -> str:
    return ", ".join(s["label"] for s in styles) or "no strong tendency"


def offline_briefing(f: dict, route: str = "full") -> list[dict]:
    """What the staff say for each kind of trigger. Each note: agent, claim, source facts, and optional one-tap actions for the coach."""
    if not f["ready"]:
        return []
    opp, t, (us, them) = f["opponent"], f["tactical_read"], f["score"]
    notes: list[dict] = []

    def add(agent, claim, source, actions=None):
        notes.append({"agent": agent, "claim": claim, "source": source, **({"actions": actions} if actions else {})})

    plan = lambda p: {"type": "plan", "value": p, "label": f"Switch to {p} plan"}
    shape = f"{opp} play a {f['their_formation']} and show: {_labels(f['their_style'])}."
    advice = ([{"type": "formation", "value": f["recommended_formation"], "label": f"Use {f['recommended_formation']}"}] if f["recommended_formation"] != f["our_formation"] else [])
    read = f"{t['formation']} is rated '{t['verdict']}': {t['reasons'][0]}. " + (f"Switch to {f['recommended_formation']}." if advice else "Keep the shape.")
    high = any(s["label"] == "high block" for s in f["their_style"])

    if route == "fade":
        for a in f["alerts"]:
            add("Formation Tactician", f"Change needed: {a['off']} is fading ({a['evidence']}). Bring on {a['on']}.", "alerts",
                [{"type": "sub", "off": a["off"], "on": a["on"], "label": f"{a['off']} off, {a['on']} on"}])
        add("Own-Style Analyst", f"We are a {f['our_formation']} showing: {_labels(f['our_style'])}. Tired legs will stretch the gaps.", "our_formation, our_style")
    elif route == "opponent":
        add("Opponent Analyst", shape, "their_formation, their_style")
        for sh in f["their_shifts"]:
            add("Opponent Analyst", f"{opp} have {sh}. " + ("Be patient: more inside passes and cutbacks." if "high block to a" in sh else "Press them higher."), "their_shifts",
                [plan("inside" if "high block to a" in sh else "gegenpress")])
        add("Formation Tactician", ("Their line is high: change to a direct plan and play in behind. " if high else "Their block is deep: move the ball patiently. ") + read, "their_style, tactical_read",
            [plan("counter" if high else "possession")] + advice)
    elif route == "goal":
        g = f["last_goal"]
        mine = g and g["team"] != f["opponent"]
        add("Own-Style Analyst" if mine else "Opponent Analyst", (f"We scored at minute {g['minute']} (score {us}-{them}). Keep the plan that worked: {f['our_mentality']}." if mine
            else f"{opp} scored at minute {g['minute']} (score {us}-{them}). Do not chase yet: hold the shape and keep the press measured."), "last_goal, score",
            None if mine else [plan("balanced")])
        add("Formation Tactician", read, "tactical_read, recommended_formation", advice)
    elif route == "losing":
        add("Formation Tactician", f"Behind {us}-{them} at minute {f['minute']}. Commit more players forward. " + read, "score, tactical_read", [plan("attack")] + advice)
    elif route == "leading":
        add("Formation Tactician", f"Ahead {us}-{them} at minute {f['minute']}. Protect the lead: drop the line and stay compact. " + read, "score, tactical_read", [plan("defend")] + advice)
    elif route == "shape":
        for i in f["shape_issues"]:
            if i["kind"] == "line_too_high":
                add("Formation Tactician", f"Change the back line: we are playing too high (it averages {i['line']}) against a direct side. Drop it.", "shape_issues, our_style", [i["action"]])
            elif i["kind"] == "central_overload":
                add("Formation Tactician", f"We are outnumbered in the middle ({i['us']} against {i['them']}). Move {i['player']} deeper to help.", "shape_issues", [i["action"]])
            else:
                side = i["kind"].split("_")[0]
                add("Formation Tactician", f"They have {i['them']} players against our {i['us']} in the {side} channel. Move {i['player']} wider to cover.", "shape_issues", [i["action"]])
    elif route == "readiness":
        for c in f["readiness_concerns"]:
            add("Own-Style Analyst", f"Readiness: {c}.", "readiness_concerns")
    else:
        add("Opponent Analyst", shape, "their_formation, their_style")
        add("Own-Style Analyst", f"We are a {f['our_formation']} showing: {_labels(f['our_style'])}. Possession {f['possession_pct']}%, xG {f['xg']['us']} to {f['xg']['them']}.", "our_style, possession_pct, xg")
        add("Formation Tactician", read, "tactical_read, recommended_formation", advice)
    return notes


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

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
from .tactics import FORMATIONS, assess, recommend, their_formation, why_switch


def shape_issues(m: Match, styles: list[dict]) -> list[dict]:
    """Spot where we are outnumbered or standing badly, and pick a player to adjust. Counts come from the engine's last frame."""
    out, ov = [], m.overloads()
    last = m.last_frame
    ours = [p for p in m.xi if m.line[p.name] != "GK" and p.name in last]  # a fresh substitute has no frame until the next tick
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
    if line and line >= 45 and any(s.label == "direct play" for s in classify([h["them"] for h in m.shapes[-4:]])):
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
        "switch_reasons": why_switch(m.formation, recommend(m.profile), m.profile) if recommend(m.profile) != m.formation else [],
        "our_instructions": m.instructions, "readiness_concerns": concerns(m.xi, m.hrv, m.wellness),
        "shape_issues": shape_issues(m, [asdict(x) for x in classify([h["us"] for h in recent])]), "orders": m.orders,
        "alerts": [asdict(a) for a in live_alerts(m.minute, m.snaps, m.xi, m.eligible_bench, m.hrv)], "possession_pct": round(sum(h["us"].possession for h in recent) / len(recent), 1),
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

    lead, minute = us - them, f["minute"]
    cur_f = f["our_formation"]
    fwd = lambda name: FORMATIONS[name][2]
    # One plan for the current state, shared by every route, so two briefings in the same minute never offer opposite plans.
    if lead < 0 and minute >= 60:
        want = "attack"
    elif lead > 0 and minute >= 60:
        want = "defend"
    else:
        want = "counter" if any(s["label"] == "high block" for s in f["their_style"]) else "possession" if any(s["label"] in ("low block", "mid block") for s in f["their_style"]) else "balanced"
    PLAN_TEXT = {"attack": "Commit more players forward.", "defend": "Protect the lead: drop the line and stay compact.", "counter": "Their line is high: change to a direct plan and play in behind.",
                 "possession": "Their block is deep: move the ball patiently.", "balanced": "Keep the balance."}
    plan = lambda p: {"type": "plan", "value": p, "label": f"Switch to {p} plan"}
    plan_action = [plan(want)] if want != f["our_mentality"] else []  # never offer the plan that is already on
    shape = f"{opp} play a {f['their_formation']} and show: {_labels(f['their_style'])}."
    rec = f["recommended_formation"]
    # Switch advice only when the current shape is rated Risky, and never against the direction of the plan.
    switch = rec != cur_f and t["verdict"] == "Risky" and not (want == "defend" and fwd(rec) > fwd(cur_f)) and not (want == "attack" and fwd(rec) < fwd(cur_f))
    advice = [{"type": "formation", "value": rec, "label": f"Use {rec}"}] if switch else []
    why = "; ".join(f["switch_reasons"])
    read = (f"{cur_f} is rated '{t['verdict']}' against {opp}. Switch to {rec}: {why}." if switch
            else f"{cur_f} is rated '{t['verdict']}': {t['reasons'][0]}. Keep the shape.")
    mood = "the current settings" if f["our_mentality"] == "custom" else f"the plan that worked: {f['our_mentality']}"

    if route == "fade":
        for a in f["alerts"]:
            add("Formation Tactician", f"Change needed: {a['off']} is fading ({a['evidence']}). " + (f"Bring on {a['on']}." if a["on"] != "none available" else "No rested replacement is available in his position."), "alerts",
                [{"type": "sub", "off": a["off"], "on": a["on"], "label": f"{a['off']} off, {a['on']} on"}] if a["on"] != "none available" else None)
        add("Own-Style Analyst", f"We are a {f['our_formation']} showing: {_labels(f['our_style'])}. Tired legs will stretch the gaps.", "our_formation, our_style")
    elif route == "opponent":
        add("Opponent Analyst", shape, "their_formation, their_style")
        for sh in f["their_shifts"]:
            add("Opponent Analyst", f"{opp} have {sh}.", "their_shifts")
        add("Formation Tactician", PLAN_TEXT[want] + " " + read, "their_style, tactical_read", plan_action + advice)
    elif route == "goal":
        g = f["last_goal"] or {"team": "", "minute": f["minute"]}
        mine = g and g["team"] != f["opponent"]
        if mine:
            add("Own-Style Analyst", f"We scored at minute {g['minute']} (score {us}-{them}). Keep {mood}.", "last_goal, score")
        else:
            if lead > 0:
                text = f"{opp} scored at minute {g['minute']} (score {us}-{them}). We still lead: keep the shape and do not open up."
            elif lead == 0:
                text = f"{opp} scored at minute {g['minute']} (score {us}-{them}). Level again: hold the shape and keep the press measured."
            elif lead == -1 and minute < 60:
                text = f"{opp} scored at minute {g['minute']} (score {us}-{them}). Do not chase yet: hold the shape and keep the press measured."
            else:
                text = f"{opp} scored at minute {g['minute']} (score {us}-{them}). We are behind: raise the tempo and commit more players forward."
            add("Opponent Analyst", text, "last_goal, score", plan_action if lead < 0 else None)
        add("Formation Tactician", read, "tactical_read, recommended_formation", advice)
    elif route == "losing":
        add("Formation Tactician", f"Behind {us}-{them} at minute {f['minute']}. {PLAN_TEXT['attack']} " + read, "score, tactical_read", ([plan("attack")] if f["our_mentality"] != "attack" else []) + advice)
    elif route == "leading":
        add("Formation Tactician", f"Ahead {us}-{them} at minute {f['minute']}. {PLAN_TEXT['defend']} " + read, "score, tactical_read", ([plan("defend")] if f["our_mentality"] != "defend" else []) + advice)
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
    "Opponent Analyst": "Describe the opponent's formation, block height, pressing and passing style, and any recent shift.",
    "Own-Style Analyst": "Describe how our team is playing (block, possession, passing, width) and what that exposes against this opponent.",
    "Formation Tactician": "Judge our formation against the opponent's style. Recommend keeping or changing shape, and quote only movements that appear in the facts.",
}
RULES = " Use ONLY the JSON facts you are given and quote their numbers. If a fact is missing, say so. Plain text, no markdown. Max 3 sentences. If the facts hold a \"focus\", answer that first."


CHECKER = "Compare each note with the JSON facts. Reply with ONLY a JSON list of the notes' sentences that are NOT supported, [] if all are."
COACH = "You are the Coach Briefing agent. Merge the analysts' notes into one recommendation for the coach: the decision first, then the single reason that matters most, quoting the facts' numbers. Add nothing that is not in the facts."
REVISE = "A checker found problems in your note. Rewrite it fixing only these problems, using only the facts. Reply with the new note only."


async def staff_flow(analysts, ask, f: dict, agents: list[str], focus: str = "") -> list[dict]:
    """The live staff pipeline, the same for every backend:
    1. analysts in parallel (fan-out), 2. critic and revise: a note the rules judge flags goes back to its author once with the
    exact problems, 3. Coach Briefing merges the notes (fan-in), 4. the Fact-checker agent screens everything.
    `analysts(agents, text)` returns [(agent, text)]; `ask(agent, text)` asks one named agent. Actions are never generated here."""
    from .judge import check

    facts = json.dumps({**f, "focus": focus} if focus else f)
    notes = [{"agent": a, "claim": t.strip(), "source": "agent"} for a, t in await analysts(agents, facts) if t and t.strip()]
    for n in notes:
        problems = check(n, f)["unsupported"]
        if problems:
            fixed = (await ask(n["agent"], json.dumps({"instruction": REVISE, "facts": f, "your_note": n["claim"], "problems": problems}))).strip()
            if fixed and not check({**n, "claim": fixed}, f)["unsupported"]:
                n.update(claim=fixed, revised=problems)
    if len(notes) > 1:
        summary = (await ask("Coach Briefing", json.dumps({"facts": f, "notes": notes}))).strip()
        if summary:
            notes.insert(0, {"agent": "Coach Briefing", "claim": summary, "source": "agent"})
    verdict = (await ask("Fact-checker", json.dumps({"facts": f, "notes": notes}))).strip().strip("`").removeprefix("json").strip()
    try:
        bad = json.loads(verdict)
    except ValueError:
        bad = [verdict]
    return notes + [{"agent": "Fact-checker", "claim": "Every claim matches the facts." if not bad else "Check: " + "; ".join(map(str, bad)), "source": "facts"}]


def _prompt(name: str) -> str:
    return {"Coach Briefing": COACH, "Fact-checker": CHECKER}.get(name) or INSTRUCTIONS[name] + " If the input holds an \"instruction\", follow it."


async def agent_briefing(f: dict, agents: list[str] | None = None, focus: str = "") -> list[dict]:
    """In-process agents on a Foundry model (Agent Framework). Verified live Oct 22 and Oct 27 (gpt-6-astra). The analysts run
    through ConcurrentBuilder; the aggregated output carries one message per agent, keyed by author_name."""
    from agent_framework.foundry import FoundryChatClient
    from agent_framework.orchestrations import ConcurrentBuilder
    from azure.identity import AzureCliCredential

    client = FoundryChatClient(project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], model=os.environ["FOUNDRY_MODEL"], credential=AzureCliCredential())
    agent = lambda n: client.as_agent(name=re.sub(r"[^A-Za-z]", "", n), instructions=_prompt(n) + RULES)

    async def analysts(names: list[str], text: str) -> list[tuple[str, str]]:
        team, by = [agent(n) for n in names], {re.sub(r"[^A-Za-z]", "", n): n for n in names}
        if len(team) == 1:  # the concurrent fan-out needs two or more participants
            return [(names[0], (await team[0].run(text)).text)]
        events = await ConcurrentBuilder(participants=team).build().run(text)
        return [(by[m.author_name], m.text) for r in events.get_outputs() for m in r.messages if m.author_name in by]

    async def ask(name: str, text: str) -> str:
        return (await agent(name).run(text)).text or ""

    return await staff_flow(analysts, ask, f, agents or list(INSTRUCTIONS), focus)

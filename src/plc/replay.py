"""Replay the same seeded matches three ways and compare the outcomes.

Arms: (1) none: no changes. (2) accept_all: every AI staff action is applied as it appears. (3) coach: a scripted
coach that ignores the AI before minute 60 and on shape tweaks, and answers fade alerts with its own substitution
through coach.decide (so the coach override path is the one exercised).

Honest limits: the engine is synthetic and its effects are our own modelling choices, so this shows the pipeline
behaves coherently (same seeds, paired arms, no crashes, actions apply), NOT that the AI or a coach would win real
matches. Arms diverge in random draws once a change is made, so per-seed differences are noisy; read the mean and
standard error over many seeds, and treat a difference within ~2 SE as no evidence of an effect.
Ticks where staff.gold_facts raises (an existing staff.py bug) are skipped and reported per match.
Staff notes come from the offline briefing (staff.offline_briefing), not Foundry, so runs are reproducible.
"""
from math import sqrt
from statistics import mean, stdev

from .activator import Activator
from .coach import Decision, decide
from .engine import IllegalSubstitution, Match, new_match
from .live import live_alerts
from .staff import gold_facts, offline_briefing

ARMS = ("none", "accept_all", "coach")


def apply(m: Match, a: dict) -> bool:
    """Same Match methods the /decision endpoint calls. False when the action no longer fits (e.g. player already off)."""
    t = a["type"]
    try:
        if t == "sub":
            m.substitute(a["off"], a["on"])
        elif t == "formation":
            m.set_formation(a["value"])
        elif t == "plan":
            m.set_mentality(a["value"])
        elif t == "order":
            m.set_order(a["player"], a.get("depth"), a.get("width"))
        elif t == "sliders":
            m.set_instructions(**a["value"])
        else:
            return False
    except (StopIteration, IllegalSubstitution):  # the action no longer fits: the player is gone, or the substitution rules refuse it
        return False
    return True


def _routes(m: Match, t, act: Activator) -> list[str]:
    facts = gold_facts(m)
    alerts = live_alerts(t.minute, m.snaps, m.xi, m.eligible_bench, m.hrv)
    state = {"minute": t.minute, "alerts": alerts, "fading": sorted(a.off for a in alerts), "goals": sum(e.detail.get("goal", False) for e in t.events),
             "their_shifts": facts.get("their_shifts", []), "concerns": [], "shape_issues": [(i["kind"], i.get("player")) for i in facts.get("shape_issues", [])],
             "score": t.score, "late_deficit": max(0, t.score[1] - t.score[0]) if t.minute >= 70 else 0, "late_lead": max(0, t.score[0] - t.score[1]) if t.minute >= 70 else 0}
    return [tr["route"] for tr in act.evaluate(state)]


def _own_sub(m: Match, squad) -> Decision | None:
    """The scripted coach's own call: swap the lowest-rated outfield starter for the best bench player in his position."""
    for off in sorted((p for p in m.xi if p.position != "GK"), key=lambda p: p.rating):
        on = max((b for b in m.eligible_bench if b.position == off.position), key=lambda b: b.rating, default=None)
        if on and on.rating > off.rating:
            return decide(None, f"take off {off.name}, bring on {on.name}", squad)
    return None


def play(seed: int, arm: str) -> dict:
    m, squad = new_match(seed)
    act, n, skipped = Activator(), 0, 0
    while not m.finished:
        t = m.tick()
        if arm == "none":
            continue
        try:
            facts = gold_facts(m)  # once per tick: after a substitution it would read a frame that lacks the new player (KeyError in staff.shape_issues)
            routes = _routes(m, t, act)
        except (KeyError, TypeError):  # staff.shape_issues indexes a Style as a dict when a high block meets direct play; staff.py is not ours to fix here
            skipped += 1
            continue
        for route in routes:
            actions = [a for note in offline_briefing(facts, route) for a in note.get("actions", [])]
            if arm == "accept_all":
                n += sum(apply(m, a) for a in actions)
            elif m.minute >= 60:  # coach: trusts the AI only late, ignores shape tweaks, overrides subs
                if route == "fade":
                    ai = next((Decision(a["off"], a["on"], "ai") for a in actions if a["type"] == "sub"), None)
                    d = _own_sub(m, squad) or ai
                    if d and apply(m, {"type": "sub", "off": d.off, "on": d.on}):
                        n += 1
                else:
                    n += sum(apply(m, a) for a in actions if a["type"] in ("plan", "formation"))
    xg = lambda us: sum(e.detail["xg"] for e in m.events if (e.team != m.opponent) == us)
    return {"gd": m.score[0] - m.score[1], "xgd": xg(True) - xg(False), "acts": n, "skipped": skipped}


def compare(seeds: list[int]) -> dict:
    runs = {a: [play(s, a) for s in seeds] for a in ARMS}
    out = {"seeds": len(seeds), "arms": {}, "paired_vs_none": {}}
    for a, rs in runs.items():
        out["arms"][a] = {"goal_diff": mean(r["gd"] for r in rs), "xg_diff": mean(r["xgd"] for r in rs), "interventions": mean(r["acts"] for r in rs), "staff_ticks_skipped": mean(r["skipped"] for r in rs)}
    for a in ARMS[1:]:
        for k in ("gd", "xgd"):
            d = [x[k] - y[k] for x, y in zip(runs[a], runs["none"])]
            out["paired_vs_none"][f"{a}.{k}"] = {"mean_diff": mean(d), "se": stdev(d) / sqrt(len(d)) if len(d) > 1 else float("nan")}
    return out


def report(seeds: list[int]) -> str:
    r = compare(seeds)
    lines = [f"Replay over {r['seeds']} seeds (synthetic engine: shows coherent behaviour, not winning real matches)",
             f"{'arm':<11}{'goal diff':>10}{'xG diff':>9}{'actions/match':>15}{'skipped':>9}"]
    lines += [f"{a:<11}{v['goal_diff']:>10.2f}{v['xg_diff']:>9.2f}{v['interventions']:>15.2f}{v['staff_ticks_skipped']:>9.2f}" for a, v in r["arms"].items()]
    lines.append("paired difference vs none (mean +/- standard error):")
    lines += [f"  {k:<16}{v['mean_diff']:>7.2f} +/- {v['se']:.2f}" for k, v in r["paired_vs_none"].items()]
    return "\n".join(lines)

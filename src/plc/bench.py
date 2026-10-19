"""Benchmark the agent team and the judge itself.

1. Team: across seeds x game plans x trigger routes, how many briefings are grounded, and how often do they offer a one-tap action?
2. Judge: take real notes, corrupt them in known ways (wrong number, invented style, no decision) and check the judge catches
   every corruption without flagging the untouched notes.
Also writes data/bench/eval.jsonl (query, response, context) for Foundry's built-in evaluators; that schema is UNVERIFIED here.
"""
import json
import re
from pathlib import Path

from . import orchestrator
from .engine import new_match
from .judge import judge


def _corrupt(note: dict) -> list[tuple[str, dict]]:
    c = note["claim"]
    out = [("invented style", {**note, "claim": c + " They also play wing play and a low block."})] if "low block" not in c else []
    nums = re.findall(r"\d+(?:\.\d+)?", c)
    if nums:
        out.append(("wrong number", {**note, "claim": c.replace(nums[0], str(float(nums[0]) + 7.3), 1)}))
    if note["agent"] == "Formation Tactician":
        out.append(("no decision", {**note, "claim": re.sub(r"\b(switch|keep|change|move)\b", "consider", c, flags=re.I)}))
    return out


def run(seeds=(7, 8, 9), plans=("balanced", "counter", "wings"), minute=70, out: Path | None = Path("data/bench")) -> dict:
    briefings, caught, missed, false_pos, real_notes, rows = 0, 0, 0, 0, 0, []
    grounded = actions = 0
    for seed in seeds:
        for plan in plans:
            m, _ = new_match(seed)
            m.set_mentality(plan)
            while m.minute < minute:
                m.tick()
            for route in orchestrator.ROUTES:
                r = orchestrator.run(m, route)
                if not r["notes"]:
                    continue
                briefings += 1
                grounded += r["judge"]["grounded"]
                actions += any(n.get("actions") for n in r["notes"])
                for n in r["notes"]:
                    real_notes += 1
                    false_pos += bool(judge([n], r["facts"])["unsupported"])
                    for _, bad in _corrupt(n):
                        flagged = bool(judge([bad], r["facts"])["unsupported"]) or not judge([bad], r["facts"])["notes"][0]["decides"]
                        caught, missed = caught + flagged, missed + (not flagged)
                    rows.append({"query": f"{route} at minute {minute}, {plan} plan, seed {seed}", "response": n["claim"], "context": json.dumps(r["facts"])})
    if out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "eval.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    return {"briefings": briefings, "grounded_rate": round(grounded / briefings, 3), "with_one_tap_action": round(actions / briefings, 3),
            "judge_catch_rate": round(caught / max(1, caught + missed), 3), "judge_false_positive_rate": round(false_pos / max(1, real_notes), 3),
            "notes_judged": real_notes, "corruptions_tested": caught + missed}

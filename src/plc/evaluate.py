"""Foundry Groundedness evaluator on live staff notes, clean and with one number corrupted, next to our rules judge.

Needs `uv sync --extra eval`, the Foundry env vars and `az login`. Run: `uv run python -m plc evaluate [n_scenarios]`.
Honest scope: a handful of scenarios, one evaluator, one judge model; it shows whether the evaluator separates clean from
corrupted notes, not how good the notes are. The evaluator is called with is_reasoning_model=True because the deployed model
rejects max_tokens.
"""
import json
import os
import re
from statistics import mean

from .engine import new_match
from .judge import check
from .orchestrator import run

SCENARIOS = [(7, 13, "fade"), (7, 9, "full"), (3, 13, "full"), (11, 13, "fade"), (5, 12, "full"), (2, 10, "shape")]  # (seed, ticks, route)


def corrupt(claim: str) -> str:
    """Change the first number the note quotes to a different one, the way a model could misquote a fact."""
    return re.sub(r"\d+(?:\.\d+)?", lambda m: f"{float(m[0]) * 1.9 + 7:g}", claim, count=1)


def evaluator():
    from azure.ai.evaluation import GroundednessEvaluator
    from azure.identity import AzureCliCredential

    host = os.environ["FOUNDRY_RESOURCE_ENDPOINT"].replace("services.ai.azure.com", "cognitiveservices.azure.com")
    cfg = {"azure_endpoint": host, "azure_deployment": os.environ["FOUNDRY_MODEL"], "api_version": "2025-04-01-preview"}
    return GroundednessEvaluator(cfg, credential=AzureCliCredential(), is_reasoning_model=True)


def report(n: int = len(SCENARIOS)) -> dict:
    ev, rows = evaluator(), []
    for seed, ticks, route in SCENARIOS[:n]:
        m, _ = new_match(seed)
        for _ in range(ticks):
            m.tick()
        r = run(m, route, live=True)
        if r["mode"] != "agents":
            continue
        for note in (x for x in r["notes"] if x["agent"] != "Fact-checker"):
            ctx = json.dumps(r["facts"])
            bad = {**note, "claim": corrupt(note["claim"])}
            if bad["claim"] == note["claim"]:
                continue
            rows.append({"scenario": [seed, ticks, route], "agent": note["agent"],
                         "clean": ev(query=route, context=ctx, response=note["claim"])["groundedness"],
                         "corrupted": ev(query=route, context=ctx, response=bad["claim"])["groundedness"],
                         "claim": note["claim"], "rules_unsupported": check(note, r["facts"])["unsupported"], "rules_clean_ok": not check(note, r["facts"])["unsupported"], "rules_corrupt_caught": bool(check(bad, r["facts"])["unsupported"])})
    out = {"notes": len(rows), "foundry_mean_clean": mean(x["clean"] for x in rows), "foundry_mean_corrupted": mean(x["corrupted"] for x in rows),
           "foundry_corrupt_below_clean": mean(x["corrupted"] < x["clean"] for x in rows), "foundry_corrupt_fails_threshold_3": mean(x["corrupted"] < 3 for x in rows),
           "rules_clean_passes": mean(x["rules_clean_ok"] for x in rows), "rules_corrupt_caught": mean(x["rules_corrupt_caught"] for x in rows), "rows": rows} if rows else {"notes": 0}
    os.makedirs("data/bench", exist_ok=True)
    json.dump(out, open("data/bench/foundry_eval.json", "w"), indent=1)
    return {k: v for k, v in out.items() if k != "rows"}

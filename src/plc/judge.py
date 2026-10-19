"""Judge: scores every agent note against the gold facts it was given.

Layer 1 (always, deterministic, the gate): every number and every style label in a claim must exist in the facts, and the
tactician must actually decide. Research on LLM judges says they drift and should be calibrated, so code decides pass/fail.
Layer 2 (Foundry configured): an LLM rubric judge adds a quality score. UNVERIFIED against a live endpoint.
"""
import json
import os
import random
import re

LABELS = ["high block", "mid block", "low block", "high press", "passive press", "midfield dominance", "lateral play", "direct play",
          "counter-attacking", "cross-heavy", "inside combinations", "crowds the box", "wing play"]
RUBRIC = ["Every statement is supported by the facts.", "The note says what the coach should do or watch, not just what happened.",
          "It is specific to this match state, not generic football advice.", "It is short and plain enough to read in five seconds."]


def _numbers(text: str) -> set[str]:
    return {n.rstrip("0").rstrip(".") if "." in n else n for n in re.findall(r"\d+(?:\.\d+)?", text)}


def check(note: dict, facts: dict) -> dict:
    blob = json.dumps(facts)
    claim = note["claim"]
    bad_numbers = sorted(n for n in _numbers(claim) if n not in _numbers(blob))
    bad_labels = [label for label in LABELS if label in claim.lower() and label not in blob.lower()]
    decides = note["agent"] != "Formation Tactician" or bool(re.search(r"\b(switch|keep|change|move)\b", claim.lower()))
    unsupported = [f"number {n} is not in the facts" for n in bad_numbers] + [f"style '{label}' is not in the facts" for label in bad_labels]
    score = round(max(0.0, 1 - 0.34 * len(unsupported)) * (1 if decides else 0.7), 2)
    return {"agent": note["agent"], "claim": claim, "score": score, "unsupported": unsupported, "decides": decides}


def llm_score(notes: list[dict], facts: dict, passes: int = 3) -> float | None:
    """Foundry judge, rubric order shuffled per pass to reduce ordering bias. UNVERIFIED: not yet run against a live model."""
    if not (os.environ.get("FOUNDRY_PROJECT_ENDPOINT") and os.environ.get("FOUNDRY_MODEL")):
        return None
    import asyncio

    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential

    judge = FoundryChatClient(project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], model=os.environ["FOUNDRY_MODEL"],
                              credential=AzureCliCredential()).as_agent(name="Judge", instructions="Score the notes 0-10 against the rubric. Reply with only a number.")

    async def once(seed):
        items = RUBRIC[:]
        random.Random(seed).shuffle(items)
        return float(str(await judge.run(json.dumps({"rubric": items, "facts": facts, "notes": notes}))).strip().split()[0]) / 10

    async def all_passes():
        return [await once(i) for i in range(passes)]

    try:
        scores = asyncio.run(all_passes())
        return round(sum(scores) / len(scores), 2)
    except Exception as e:
        print(f"LLM judge failed ({e}), using the deterministic checks only")
        return None


def judge(notes: list[dict], facts: dict) -> dict:
    rows = [check(n, facts) for n in notes if n["agent"] != "Fact-checker"]
    quality = llm_score(notes, facts) if rows else None
    return {"grounded": all(not r["unsupported"] for r in rows), "score": round(sum(r["score"] for r in rows) / len(rows), 2) if rows else None,
            "unsupported": [f"{r['agent']}: {u}" for r in rows for u in r["unsupported"]], "notes": rows,
            "mode": "rules" if quality is None else "rules+llm", "llm_quality": quality}

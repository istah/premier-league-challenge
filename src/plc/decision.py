"""Fast substitution scoring: Microsoft-Decision-1 in Foundry when configured, local heuristic otherwise.

Request shape is from learn.microsoft.com/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision.
The docs show a `choice` answer carrying `choice`; the per-option probability field is not documented, so it is
read defensively and the heuristic is used if it is missing.
"""
import json
import os
import sys
import urllib.request

from azure.identity import DefaultAzureCredential

OPTIONS = {
    "substitute": "Output has dropped enough that a like-for-like replacement would help the team now",
    "keep": "The player is still performing close to their own baseline",
    "cannot_tell": "The evidence is too thin or mixed to decide",
}


def _heuristic(drop_pct: float, hr_over_pct: float, hrv_ratio: float) -> float:
    z = 6 * drop_pct + 3 * hr_over_pct + 2 * max(0, 0.9 - hrv_ratio) - 0.9
    return round(max(0.0, min(1.0, 0.5 + z)), 2)


def _decision1(state: dict) -> float | None:
    endpoint, model = os.environ.get("FOUNDRY_RESOURCE_ENDPOINT"), os.environ.get("DECISION_DEPLOYMENT")
    if not (endpoint and model):
        return None
    body = {"model": model, "state": state,
            "questions": {"sub": {"type": "choice", "instructions": "Should this player be substituted now?", "criteria": OPTIONS}}}
    token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token
    req = urllib.request.Request(f"{endpoint.rstrip('/')}/providers/microsoft/v1/systemone", json.dumps(body).encode(),
                                 {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    answer = json.load(urllib.request.urlopen(req, timeout=30))["answers"]["sub"]
    probs = answer.get("probabilities")
    if not isinstance(probs, dict) or "substitute" not in probs:
        print("Decision-1: no per-option probabilities in response, using heuristic", file=sys.stderr)
        return None
    return round(float(probs["substitute"]), 2)


def p_substitute(drop_pct: float, hr_over_pct: float, hrv_ratio: float) -> float:
    """Probability a substitution is warranted, 0-1."""
    state = {"output_drop_vs_first_half": round(drop_pct, 3), "heart_rate_elevation": round(hr_over_pct, 3), "morning_hrv_vs_baseline": hrv_ratio}
    try:
        p = _decision1(state)
    except Exception as e:  # network/auth/schema: never block the coach's screen
        print(f"Decision-1 call failed ({e}), using heuristic", file=sys.stderr)
        p = None
    return _heuristic(drop_pct, hr_over_pct, hrv_ratio) if p is None else p

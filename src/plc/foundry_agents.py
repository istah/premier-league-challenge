"""The staff as named agents hosted in Foundry Agent Service, called by reference.

`python -m plc publish` creates (or versions) one prompt agent per analyst plus the Fact-checker in the Foundry project.
`briefing` then asks the hosted agents instead of building them in process, so Foundry serves the agents and the
orchestrator only routes. Verified once on Oct 22 against a live project (agent created, called by reference, answered).
Needs `uv sync --extra foundry` and `az login`. Delete the agents in the Foundry portal when rotating projects.
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor

from .staff import INSTRUCTIONS, RULES

CHECKER = "Compare each note with the JSON facts. Reply with ONLY a JSON list of the notes' sentences that are NOT supported, [] if all are."


def slug(name: str) -> str:
    return "redmoor-" + name.lower().replace(" ", "-")


def _project():
    from azure.ai.projects import AIProjectClient
    from azure.identity import AzureCliCredential

    return AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=AzureCliCredential())


def publish() -> list[str]:
    from azure.ai.projects.models import PromptAgentDefinition

    c, model = _project(), os.environ["FOUNDRY_MODEL"]
    specs = {**{n: i + RULES for n, i in INSTRUCTIONS.items()}, "Fact-checker": CHECKER + RULES}
    return [f"{a.name} v{a.version}" for n, text in specs.items()
            for a in [c.agents.create_version(agent_name=slug(n), definition=PromptAgentDefinition(model=model, instructions=text))]]


def briefing(f: dict, agents: list[str], focus: str = "") -> list[dict]:
    c = _project()
    oc = c.get_openai_client()
    facts = json.dumps({**f, "focus": focus} if focus else f)

    def ask(name: str, text: str) -> str:
        return oc.responses.create(input=text, extra_body={"agent_reference": {"name": slug(name), "type": "agent_reference"}}).output_text.strip()

    with ThreadPoolExecutor(len(agents)) as pool:
        notes = [{"agent": n, "claim": t, "source": "foundry agent"} for n, t in zip(agents, pool.map(lambda n: ask(n, facts), agents)) if t]
    verdict = ask("Fact-checker", json.dumps({"facts": f, "notes": notes})).strip("`").removeprefix("json").strip()
    try:
        bad = json.loads(verdict)
    except ValueError:
        bad = [verdict]
    return notes + [{"agent": "Fact-checker", "claim": "Every claim matches the facts." if not bad else "Check: " + "; ".join(map(str, bad)), "source": "facts"}]

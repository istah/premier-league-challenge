"""The staff as named agents hosted in Foundry Agent Service, called by reference.

`python -m plc publish` creates (or versions) one prompt agent per analyst plus the Coach Briefing and Fact-checker agents in
the Foundry project. `briefing` runs the same pipeline as the in-process agents (staff.staff_flow) but every step asks a hosted
agent, so Foundry serves the agents and the orchestrator only routes. Verified against a live project (Oct 22, Oct 27).
Needs `uv sync --extra foundry` and `az login`. Delete the `redmoor-*` agents in the Foundry portal when rotating projects.
"""
import asyncio
import os

from .staff import INSTRUCTIONS, RULES, _prompt, staff_flow

STAFF = [*INSTRUCTIONS, "Coach Briefing", "Fact-checker"]


def slug(name: str) -> str:
    return "redmoor-" + name.lower().replace(" ", "-")


def _project():
    from azure.ai.projects import AIProjectClient
    from azure.identity import AzureCliCredential

    return AIProjectClient(endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"], credential=AzureCliCredential())


def publish() -> list[str]:
    from azure.ai.projects.models import PromptAgentDefinition

    c, model = _project(), os.environ["FOUNDRY_MODEL"]
    return [f"{a.name} v{a.version}" for n in STAFF
            for a in [c.agents.create_version(agent_name=slug(n), definition=PromptAgentDefinition(model=model, instructions=_prompt(n) + RULES))]]


async def briefing(f: dict, agents: list[str], focus: str = "") -> list[dict]:
    oc = _project().get_openai_client()

    def call(name: str, text: str) -> str:
        return oc.responses.create(input=text, extra_body={"agent_reference": {"name": slug(name), "type": "agent_reference"}}).output_text

    async def ask(name: str, text: str) -> str:
        return await asyncio.to_thread(call, name, text)

    async def analysts(names: list[str], text: str) -> list[tuple[str, str]]:
        return list(zip(names, await asyncio.gather(*(ask(n, text) for n in names))))

    return await staff_flow(analysts, ask, f, agents, focus)

"""Multi-agent pipeline: Analyst -> Explainer -> Personalizer (Microsoft Agent Framework)."""
import os

from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import AzureCliCredential

AUDIENCES = {
    "analyst": "a performance analyst who wants metrics, xG and tactical detail",
    "fan": "a casual fan who wants a short, exciting story with no jargon",
}


def build_workflow(audience: str = "fan"):
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=AzureCliCredential(),
    )
    analyst = client.as_agent(
        name="Analyst",
        instructions="Given JSON match events, compute key stats (shots, xG, pass completion) and pick the 3 most pivotal moments.",
    )
    explainer = client.as_agent(
        name="Explainer",
        instructions="For each pivotal moment, explain WHY it mattered, citing the event data. Never invent facts not in the data.",
    )
    personalizer = client.as_agent(
        name="Personalizer",
        instructions=f"Rewrite the explanations for {AUDIENCES[audience]}.",
    )
    return SequentialBuilder(participants=[analyst, explainer, personalizer]).build()

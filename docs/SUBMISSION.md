# Submission text (paste into the project page)

## Title
Redmoor FC Coach Room: explainable, checked match intelligence from a team of agents

## Elevator pitch (what we built, what it does, the problem)
In the last 35 minutes of a match a manager has many signals (a player's output dropping against his own baseline, wellness check-ins, the opponent changing shape, formation fit) and no time to join them. We built a coach-facing, multi-agent decision-support system on synthetic, football-realistic data (fictional club, invented players, no real data).

A seeded match engine streams events onto an event bus. Rule triggers (a local stand-in for Fabric Activator) fire when something changes. An orchestrator routes each trigger to the right staff agents: Opponent Analyst, Own-Style Analyst, Formation Tactician and a Fact-checker. Two independent checks guard the output before the coach sees it: a rules judge that finds every number and style label in the match data and cites where, and the Fact-checker agent. The coach gets short, explained notes with one-tap actions, can dictate "take off X, bring on Y", and can change formation, with every player's new role drawn on the pitch. The AI is decision support: a coach call always beats the AI, and nothing is applied automatically. The same facts also feed fan and analyst rewrites (Analyst, Explainer, Personalizer workflow).

## Microsoft and Azure technologies used
- **Microsoft Foundry:** a project with a deployed chat model serves all agent calls. The four staff agents are published as named agents in **Foundry Agent Service** (`python -m plc publish`) and called by reference.
- **Microsoft Agent Framework** (`agent-framework-foundry`, `agent-framework-orchestrations`): concurrent multi-agent orchestration for the staff, a sequential Analyst, Explainer and Personalizer workflow for fan and analyst audiences.
- **Foundry evaluators (`azure-ai-evaluation`):** the Groundedness evaluator scored 14 live notes at 4.36 of 5 clean and 2.00 with one number changed (`python -m plc evaluate`).
- **Azure Identity:** keyless `az login` credentials.
- Prepared but not run live: Microsoft-Decision-1 (heuristic fallback runs; the work account could not deploy it), Azure Event Hubs and Fabric Eventstream/Eventhouse/Activator (designed and mapped in `docs/ARCHITECTURE.md`), Azure Container Apps (`Dockerfile`, `docs/DEPLOY.md`; image built and run locally).

## Why this category (Best Multi-Agent System)
- A routing table maps triggers to agents; analysts run concurrently; a separate Fact-checker agent and a rules judge each have a veto; the orchestration is visible in the app (Log tab: rule fired, agents run, judge verdict).
- Agents explain, rules act: model-written notes never create buttons, so a model cannot invent an action.
- Explainability is the point: every claim is checked against the data and cites its source fact.

## Honest limits
- All data is synthetic; biometrics are sensitive and real use needs player consent.
- Offline benchmark numbers are tautological. The live evaluation is 14 notes, one blunt corruption, same model family for writer and evaluator.
- The replay comparison shows coherent behaviour of a synthetic engine, not that the system wins real matches.
- Decision-1, Event Hubs, Fabric and a production deployment were not run live.

Repo: https://github.com/istah/premier-league-challenge (public). Run: see README.

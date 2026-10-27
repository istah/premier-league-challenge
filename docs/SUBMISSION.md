# Submission text (paste into the project page)

## Title
Redmoor FC Coach Room: explainable, checked match intelligence from a team of agents

## Elevator pitch (what we built, what it does, the problem)
In the last 35 minutes of a match a manager has many signals (a player's output dropping against his own baseline, wellness check-ins, the opponent changing shape, formation fit) and no time to join them. We built a coach-facing, multi-agent decision-support system on synthetic, football-realistic data (fictional club, invented players, no real data).

A seeded match engine streams events onto an event bus. Rule triggers (a local stand-in for Fabric Activator) fire when something changes. An orchestrator routes each trigger to the right staff agents and runs a four-step live pipeline: the analysts (Opponent Analyst, Own-Style Analyst, Formation Tactician) work in parallel; a note the rules judge flags goes back to its author once with the exact problems (critic and revise); a Coach Briefing agent merges the notes into one call; a Fact-checker agent screens everything. The coach sees instant rule-written notes first, and the AI-written ones replace them only when both the rules judge (which finds every number and style label in the match data and cites where) and the Fact-checker pass them. The coach gets short, explained notes with one-tap actions, can dictate "take off X, bring on Y", and can change formation, with every player's new role drawn on the pitch. The AI is decision support: a coach call always beats the AI, and nothing is applied automatically. The same facts also feed fan and analyst rewrites (Analyst, Explainer, Personalizer workflow).

## Microsoft and Azure technologies used
- **Microsoft Foundry:** a project with a deployed chat model serves all agent calls. The five staff agents (three analysts, Coach Briefing, Fact-checker) are published as named agents in **Foundry Agent Service** (`python -m plc publish`) and called by reference; the same pipeline also runs with in-process agents.
- **Microsoft Agent Framework** (`agent-framework-foundry`, `agent-framework-orchestrations`): concurrent multi-agent orchestration for the staff, a sequential Analyst, Explainer and Personalizer workflow for fan and analyst audiences.
- **Foundry evaluators (`azure-ai-evaluation`):** the Groundedness evaluator scored 19 live notes from the full pipeline (Oct 27) at 4.16 of 5 as written and 2.00 with one number changed; every corrupted note fell below the pass mark (`python -m plc evaluate`). Our rules judge passed all 19 clean notes and caught all 19 corrupted ones.
- **Azure Identity:** keyless `az login` credentials.
- Prepared but not run live: Microsoft-Decision-1 (not deployed in our Foundry project; a heuristic fallback runs), Azure Event Hubs and Fabric Eventstream/Eventhouse/Activator (designed and mapped in `docs/ARCHITECTURE.md`), Azure Container Apps (`Dockerfile`, `docs/DEPLOY.md`; image built and run locally).

## Why this category (Best Multi-Agent System)
- Patterns: event-driven triggers, a routing-table orchestrator, parallel fan-out, a critic and revise loop, fan-in to a Coach Briefing agent, an independent Fact-checker, and a human in the loop who always decides.
- Two independent checks each have a veto; the orchestration is visible in the app (Log tab: rule fired, agents in parallel, revisions, Coach Briefing, Fact-checker and judge verdicts).
- One pipeline, two backends: in-process Agent Framework agents or agents hosted in Foundry Agent Service.
- Agents explain, rules act: model-written notes never create buttons, so a model cannot invent an action.
- Explainability is the point: every claim is checked against the data and cites its source fact.

## Honest limits
- All data is synthetic; biometrics are sensitive and real use needs player consent.
- Offline benchmark numbers are tautological. The live evaluation is 19 notes, one blunt corruption, same model family for writer and evaluator.
- The replay comparison shows coherent behaviour of a synthetic engine, not that the system wins real matches.
- Decision-1, Event Hubs, Fabric and a production deployment were not run live.

Repo: https://github.com/istah/premier-league-challenge (public). Run: see README.

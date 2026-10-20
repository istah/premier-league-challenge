# Architecture: events, Activator, orchestrator, judge, Foundry

```
match engine ──► bus.publish() ──► Azure Event Hubs ──► Fabric Eventstream ──► Eventhouse (bronze → silver → gold, KQL)
 (tick, shot)       (local: in-memory log)                                          │
                                                                                    ▼
                                              Activator rules on gold (rules = data, see activator.py)
                                                                                    │ trigger {rule, route}
                                                                                    ▼
                                   Orchestrator (routing table) ──► Foundry agents ──► Judge ──► API ──► coach UI (Staff room)
                                      Opponent Analyst · Own-Style Analyst · Formation Tactician · Fact-checker
```

## What runs today, locally
| Piece | File | Status |
|---|---|---|
| Event bus | `bus.py` | Every tick, shot, trigger and briefing is published. In-memory log, readable at `GET /events`. Azure Event Hubs when `EVENTHUB_NAMESPACE` and `EVENTHUB_NAME` are set (**unverified against a live namespace**; install with `uv add azure-eventhub`). |
| Activator | `activator.py` | Rules are plain data and fire on a state change, not on every matching event. Local stand-in for Fabric Activator. |
| Orchestrator | `orchestrator.py` | Maps a trigger to the agents that should speak (`fade` → Tactician + Own-Style, `opponent` → Opponent Analyst + Tactician, ...), runs them, has the Judge score the result. Routing is a table, not a model call, so it is predictable and testable. |
| Agents | `staff.py` | Offline notes built from gold facts, each with a source and optional one-tap coach actions. Foundry path (`agent_briefing`): three analysts via `ConcurrentBuilder`, then a Fact-checker. **Foundry path never run live.** |
| Judge | `judge.py` | Rules gate: every number and style label must exist in the facts, the Tactician must decide. Optional LLM rubric judge (rubric order shuffled over 3 passes). **LLM path never run live.** |
| Benchmark | `bench.py`, `uv run python -m plc bench` | Team grounding rate; judge catch rate on corrupted notes; writes `data/bench/eval.jsonl` for Foundry evaluators. |

## Activator rules (create the same ones in Fabric)
`player_fading` (alerts non-empty), `opponent_changed_shape`, `goal`, `readiness_concern`, `shape_issue`, `losing_late`, `leading_late`, `half_time`. Each carries a `route`. In Fabric: Eventstream → Activator destination, one rule per entry, action = webhook to the API's briefing endpoint or Power Automate. Rule volume can be previewed against history before activating.

## Fabric and Foundry mapping
- Event Hubs receives events; an Eventstream reads the hub and lands bronze into an Eventhouse; KQL update policies derive silver and gold; Activator watches gold ([Activator on Eventstream](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/event-streams/set-alerts-event-stream), [Activator intro](https://learn.microsoft.com/en-us/fabric/real-time-intelligence/data-activator/activator-introduction)). Third-party posts disagree on whether the Eventstream Activator destination is preview or GA: check before demoing.
- Foundry hosts the models, the agents and Decision-1. Agent Framework offers Sequential, Concurrent, Handoff, Group Chat and Magentic orchestration ([docs](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/)). We use Concurrent for the analysts and our own routing table as the orchestrator; Magentic (a manager agent) or Handoff are options if routing must become model-driven. Hosting the agents as Foundry Agent Service agents (rather than in-process) is not done and not verified.

## Benchmarking: what the research says and what we do
- Foundry has built-in agent evaluators (Intent Resolution, Task Adherence, Tool Call Accuracy, Groundedness, Task Completion) that use a judge model and return pass/fail with reasoning; some are preview ([evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators), [built-in list](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)). Plan: run Groundedness and Task Adherence on `data/bench/eval.jsonl` in Foundry once a project exists. Names and data schema must be checked against the current docs.
- LLM judges drift: rubric order matters, alignment drops on harder tasks, and the best judge differs per setup, so a judge must be validated against humans ([AgentJudgeBench](https://arxiv.org/pdf/2608.26623), [Agent-as-a-Judge](https://arxiv.org/pdf/2508.02994)). Outcome-only scoring misses corrupted reasoning chains, so we also check sources per claim.
- So: code is the gate (numeric and label grounding, deterministic), the LLM judge adds quality scores, and a human calibration set (60 notes, as in the multi-scenario benchmark that used six annotators) is still to do.
- **Honest limits:** offline notes are generated from the facts, so a 100% grounding rate there proves the harness, not the agents. The judge catch rate is measured on corruptions we wrote ourselves. Real evidence needs the Foundry agents' output.

## Decision-1
Fast bounded calls (substitute / keep / cannot_tell) stay in `decision.py`; the Judge and agents never call it.

## What real clubs do, and what we claim

From `reports/Football AI tools replication.md` (sources there; some are dated or vendor-reported):
- Documented club use is pre-match dossiers, set-piece review and readiness flags, not live decisions. Our tick feed is more live than anything a club has: one source reports live tracking running about 7 minutes behind reprocessed data. The pitch says so, and presents the live view as a simulation of what a feed could support.
- For substitution support we found only academic prototypes (a fuzzy-logic system and a UWA paper), none validated in live matches. The coach decides; nothing is auto-applied.
- We do not build: a graph neural network on synthetic corners (it would only learn the generator's rules), EPV/OBV models, an injury classifier with an AUC claim (circular on synthetic data), or anything video-based. If asked, we say these are out of scope on purpose.

## Fact-checker citations

`judge.check` returns, per note, `citations`: each verified number or style label with `layer` ("gold"), `key` (e.g. `gold_facts['possession_pct']`) and the matched `value`. Claims it could not find are listed in `unsupported` and `searched`. `judge()` adds a flat `citations` list; existing fields are unchanged. `python -m plc bench` reports `citation_coverage` and, if `data/calibration/labels.csv` exists (`note_id,label,reason`, ids `<seed>-<plan>-<route>-<index>`), `human_agreement`. The LLM rubric judge is still unverified live.

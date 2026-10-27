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

## Replay comparison
`python -m plc replay [seeds]` plays the same seeded matches with no changes, with every AI staff action accepted, and with a scripted coach who overrides some of them. It prints paired differences with standard errors. The engine is synthetic and its effects are our own modelling choices, so this shows the pipeline behaves coherently, not that it wins real matches.

## First live evaluation (Oct 22)
`uv run --extra eval python -m plc evaluate` runs the staff agents live on Foundry (`gpt-6-astra`), then scores each note with the Foundry Groundedness evaluator, once as written and once with the first number changed (`n*1.9+7`). Result, 6 scenarios, 14 notes (raw rows in `data/bench/foundry_eval.json`, git-ignored):

| | Clean notes | Corrupted notes |
|---|---|---|
| Foundry Groundedness, mean of 1 to 5 | 4.36 | 2.00 (all 14 scored lower than their clean version and below the pass mark of 3) |
| Rules judge | 14 of 14 pass | 14 of 14 caught |

What it taught us: the first run had the rules judge rejecting 3 of 14 clean notes because the Opponent Analyst's instruction contained "last 20 minutes" and the model repeated the 20. We removed the number from the instruction; the same judge then passed all 14. A model quoting 0.85 as "85%" was also flagged and is now accepted. Limits: 14 notes, one blunt corruption, and the writer and the evaluator are the same model family, which can favour its own text. The evaluator needs `is_reasoning_model=True` for this deployment.

## Live staff pipeline (Oct 27)
`staff.staff_flow` is the same for both backends (in-process Agent Framework agents, or agents hosted in Foundry Agent Service):
1. **Fan-out.** The analysts the route names run in parallel (`ConcurrentBuilder` in process; parallel calls by reference when hosted).
2. **Critic and revise.** The rules judge checks each note; a flagged note goes back to its author once with the exact problems, and the rewrite is kept only if it passes.
3. **Fan-in.** The Coach Briefing agent merges the notes into one call; it carries the route's rule-derived buttons, so they appear once.
4. **Fact-checker.** It screens every note; a flag makes the briefing ungrounded.
The API serves rule-written notes instantly; the UI asks for the live briefing in the background (about 45 s) and swaps it in only if the rules judge and the Fact-checker both pass. Verified live on Oct 27 with both backends and in the browser (Chrome, seed 7, 5' to 65'): flagged live briefings stayed out of the coach's view. In one run the Fact-checker blocked a back-five movement plan the Tactician had invented; we then changed its prompt to quote only movements present in the facts.

Re-run of `python -m plc evaluate` on the full pipeline (Oct 27, 6 scenarios, 19 notes including Coach Briefing notes): Groundedness 4.16 clean vs 2.00 corrupted, all 19 corrupted notes below the pass mark of 3, 17 of 19 scored lower than their clean version (two clean notes already scored 2); rules judge 19 of 19 clean pass, 19 of 19 corrupted caught.

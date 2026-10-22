# Pitch: Redmoor FC Coach Room

Microsoft Inside the Game, category Best Multi-Agent System. All data is synthetic (fictional club, generated players). No real match data, names or licensed feeds.

## Headline pitch (about 250 words)

A manager makes the hardest calls in the last 35 minutes, with a tired star on the pitch, a rival who just changed shape, and no time to read a report. Clubs mostly use AI before the match (opponent dossiers, set-piece review) and for daily readiness flags. We found no product that recommends substitutions during a match, and one published account puts live tracking about seven minutes behind reprocessed data.

Redmoor FC Coach Room is a simulation of what a live feed could support. A synthetic match engine streams events onto a bus. Plain-data rules (our local stand-in for Fabric Activator) fire when something changes: a player fades against his own baseline, the opponent switches shape, a goal. An orchestrator routes each trigger to the right staff agents (Opponent Analyst, Own-Style Analyst, Formation Tactician, Fact-checker). A judge checks every number and style label against the data before the coach sees it. The coach gets short staff notes with one-tap actions, can dictate "take off X, bring on Y", and can change formation with each player's new role shown on the pitch.

The AI is decision support. The coach decides. A typed or spoken coach call always beats the AI suggestion, and nothing is ever applied automatically.

We are explicit about limits. Our offline benchmark scores are tautological: notes are generated from the facts, so a perfect grounding rate shows the harness works, not that the agents are good. Biometrics are sensitive; everything here is synthetic, and real use needs player consent.

## What runs today versus what is designed

| Runs today (offline, `uv run python -m plc demo`, tests pass) | Designed, not run live |
|---|---|
| Synthetic match engine (seeded, deterministic) | Foundry-hosted model serving the staff agents: runs live (Oct 22, one Foundry project, `gpt-6-astra`): the Tactician and Own-Style Analyst run concurrently through Agent Framework, a Fact-checker agent screens them, the rules judge and an LLM rubric judge score them. Hosting the agents in Foundry Agent Service is not done |
| Event bus (in-memory log, `GET /events`) | Decision-1 on Foundry (no deployment available yet; offline heuristic runs instead) |
| Activator rules as plain data | Azure Event Hubs (code path unverified against a namespace) |
| Orchestrator with a routing table | Fabric Eventstream, Eventhouse (KQL bronze/silver/gold), Activator |
| Staff agents (offline notes from gold facts; live notes on Foundry as above) | Decision-1 probability field unverified |
| Rules judge (numeric and label grounding) | Foundry evaluators on `data/bench/eval.jsonl` |
| Benchmark (`uv run python -m plc bench`) | Human calibration set for the judge |
| Coach interface with voice and typed override | |

> Verified live so far: agent run, concurrent orchestration, Fact-checker agent, LLM rubric judge, and the Foundry Groundedness evaluator (4.36/5 on 14 clean live notes vs 2.00 on the same notes with one number changed; see `docs/ARCHITECTURE.md`). In the first live run the rules judge flagged a model that wrote "85%" for a fact stored as 0.85 (we now accept that form), which is the check doing its job. Not verified: Decision-1, Event Hubs, Fabric, Foundry evaluators.
>
> TODO (lead): flip rows in the right-hand column to "runs" only after each is verified live, and update this table, README and the video voiceover together. Until then the submission must say these are designed, not run.

## Longer section

### The problem
In the second half the coach has a few minutes and many signals: heart-rate and output drop-off, readiness check-ins, opponent shape, formation fit. Staff can see these separately; nobody joins them in time.

### What real clubs do, and what we claim
From our research report (sources in `reports/Football AI tools replication.md`; some are dated or vendor-reported):
- Documented club use is pre-match opponent work, set-piece review and readiness flags, not live decisions.
- Live tracking was reported at roughly 7 minutes behind reprocessed data. Our tick feed is more live than anything a club has, so we present it as a simulation of what a feed could support, not as current practice.
- For substitution support we found only academic prototypes, none validated in live matches. We found no product recommending substitutions. Absence from a search is not proof none exists.
- We deliberately do not build a trained graph network on synthetic corners, EPV/OBV models, an injury classifier with an AUC claim, or anything video-based: on synthetic data these would only measure our generator.

### How it works
1. Synthetic feed (match events, wearables, training load, check-ins) lands as bronze.
2. Silver is validated data normalised to each player's own baseline; gold holds decision-ready facts and alerts. Agents read gold only; the Fact-checker may query silver and cites the layer and query.
3. Activator rules fire on changes of state, not on every event. Each rule carries a route.
4. The orchestrator maps trigger to agents with a table (predictable and testable, not a model call).
5. The judge gates the output: every number and label must exist in the facts, and the Tactician must reach a decision.
6. The coach sees notes with one-tap actions. `cannot_tell` escalates low-confidence calls to the coach.

### Responsible use
- AI is decision support. The coach always decides; nothing is auto-applied.
- Biometrics are sensitive. All data here is synthetic. Real deployment requires informed player consent and a clear data policy.
- Every match claim an agent makes must be checkable against the data.

### Honest evaluation
- The benchmark measures team grounding rate and judge catch rate on corrupted notes. Offline notes are generated from the facts, so grounding is tautological, and the catch rate is measured on corruptions we wrote ourselves. Real evidence needs the Foundry agents' output, which we have not collected.
- LLM judges drift and must be validated against humans; that calibration is still to do.

### Next steps
Run the agents on Foundry, land events through Event Hubs and Fabric, run Foundry evaluators, calibrate the judge with human raters, and test with coaches on real workflows (with consent and real data under proper agreements).

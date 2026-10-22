# Plan: lead track (app, agents, demo)

Owner: lead developer with Claude. Merge freeze **Oct 24**, submit **Oct 26** (deadline Oct 27, 11:59 pm PT).

## Owns
`src/plc/` outside `experiments/`, `tests/` outside `test_exp_*`, `docs/PLAN_*`, `CLAUDE.md`, deploy config, pitch, video.

| Due | Task | Status |
|---|---|---|
| Oct 19 | Register as team representative; add teammate | Done |
| Oct 19 | Match engine, API, coach interface, staff agents, bus/Activator/orchestrator/judge/benchmark | Done (offline) |
| Oct 20 | CI runs `uv run pytest -q` | Done |
| Oct 22 | Tests: coach override beats AI; no substitution auto-applied | Done (`tests/test_override.py`) |
| Oct 23 | Fact-checker cites layer and key per claim | Done (`judge.py`) |
| Oct 24 | Replay comparison | Done (`python -m plc replay`) |
| Oct 21 | Pitch text, diagram, demo script, Dockerfile | Drafted; Azure items in the pitch are marked not yet run |
| Oct 22 | Azure checklist below (Foundry live run) | **Next** |
| Oct 23 | Wire merged experiments in as Tactician tools; score Fact-checker on Askhat's eval set; judge vs human labels | Waiting on issues #1-#4 |
| Oct 24 | Freeze. Pre-public audit: secrets, emails in history (done once; recheck), real names or brands, `reports/` and `research_notes/` decision | |
| Oct 25 | Flip the TODO in `docs/PITCH.md` to what actually ran; re-check `docs/DEMO_SCRIPT.md`; record video | |
| Oct 26 | Deploy to Azure Container Apps, make the repo public, submit by midday | |

## Azure checklist (do in order, stop at the first failure and fix it)
Status Oct 22: steps 1-4, 6, 7 and the Groundedness part of 8 are done on the employer subscription (borrowed for testing; rotate to a personal one, issue #38). Step 5 is blocked: the work account cannot deploy Decision-1 (`deployments/write` denied), so it needs the personal subscription. Step 9: hosting agents in Foundry Agent Service is done (`python -m plc publish`); Event Hubs and Fabric not started. Delete the `redmoor-*` agents in the Foundry portal when rotating projects.
1. `az login` (subscription with Foundry access). Check `az account show`.
2. Foundry portal: create a project; deploy a chat model; deploy Microsoft-Decision-1 if available.
3. `cp .env.example .env` and fill `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`, `FOUNDRY_RESOURCE_ENDPOINT`, `DECISION_DEPLOYMENT`. Never commit `.env`.
4. `uv run python -m plc fan`: first live agent run. Fix import or API errors (`agent_briefing` in `staff.py` and `agents.py` were never run).
5. Decision-1: call `decision.p_substitute` once; print the raw response and confirm where the per-option probability lives. Update `decision.py` and its comment.
6. Live staff briefing: `GET /match/{id}/briefing` with the env set; confirm the Judge still passes the model's notes (`mode` shows live), and record the failure rate.
7. LLM rubric judge (`judge.llm_score`): run on 10 notes; compare with the rules judge.
8. Foundry evaluators on `data/bench/eval.jsonl` (Groundedness, Task Adherence, Intent Resolution, Tool Call Accuracy, Task Completion): check the dataset schema in the portal first, then run. Name preview evaluators as preview.
9. Optional, only if 4 to 8 work: Event Hubs (`uv add azure-eventhub`, set `EVENTHUB_NAMESPACE` and `EVENTHUB_NAME`), then host agents in Foundry Agent Service, then Fabric Eventstream/Eventhouse/Activator.
10. Update `docs/PITCH.md` and `README.md` tables with exactly what ran. Anything that failed stays under "designed, not yet run".
11. Deploy: `docs/DEPLOY.md`.

## Contingency
If the Foundry path fails by Oct 24, submit the offline system and label Foundry as designed, not run.

## Lead-only backlog
Generator calibration: make `dataset.py` rates (xG, pass completion, fatigue curves) match public reference statistics. Cite the source and its licence; never commit raw third-party data. Not on the critical path; do it only after Oct 24 if time allows (it would change seed-0 data and tests).

## Review duty
Review experiment PRs within a day: tests pass, evidence quotes real numbers, no files outside the experiments track touched.

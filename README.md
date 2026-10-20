# Premier League Challenge: Redmoor FC Coach Room

Team entry for the Microsoft Inside the Game hackathon, category **Best Multi-Agent System**.

A coach-facing decision-support system for a fictional club (Redmoor FC). A seeded match engine streams events; an event bus and Activator-style rules wake a staff of agents (Tactician, Opponent Analyst, Own-Style Analyst, Readiness) through an orchestrator; a Judge checks every number they quote against the data before the coach sees it. The coach decides: a typed or dictated override always beats the AI, and nothing is ever applied automatically.

**All data is synthetic** (fictional club, invented players, no real feeds, no logos). Real use of biometrics would need player consent.

## What runs today, and what does not
| Runs offline now | Designed, not yet run live |
|---|---|
| Match engine (formations, role chains, team instruction sliders, per-player orders, wellness and HRV readiness) | Foundry-hosted agents (code path exists, never run) |
| Event bus, Activator rules, orchestrator, rules Judge with citations, benchmark, replay comparison | Microsoft-Decision-1 (probability field unverified; heuristic fallback in use) |
| Coach interface with voice/dictation override | Event Hubs, Fabric Eventstream/Eventhouse/Activator, LLM judge, Foundry evaluators |

Offline benchmark metrics are tautological (notes are generated from the facts); they show the checks work, not that the advice is good. See `docs/PITCH.md`.

## Run
```
uv sync
uv run uvicorn plc.api:app --port 8765     # coach room at http://localhost:8765
uv run pytest -q                           # 40+ tests, offline
uv run python -m plc bench                 # briefing quality: grounded rate, judge catch rate, citation coverage
uv run python -m plc replay [seeds]        # no changes vs AI accepted vs scripted coach
uv run python -m plc demo                  # terminal demo
uv run python -m plc dataset [seed]        # regenerate data/bronze (about 5 MB)
```
Live Foundry agents (needs the variables in `.env.example` and `az login`):
```
cp .env.example .env
az login
uv run python -m plc fan                   # or: analyst
```
Without those variables everything runs offline on rules and a heuristic.

## Docs
- `docs/PITCH.md` submission text, honest limits. `docs/DEMO_SCRIPT.md` video script. `docs/DIAGRAM.md` architecture diagram.
- `docs/ARCHITECTURE.md` event flow, medallion layers, Fabric and Foundry mapping, benchmarking. `docs/RESEARCH.md` prior art and tactics research.
- `docs/DEPLOY.md` container and Azure Container Apps. `docs/PLAN_LEAD.md`, `docs/PLAN_EXPERIMENTS.md`, `docs/EXPERIMENTS.md` the two tracks.
- `CLAUDE.md` project rules (synthetic data only, noreply commit email, coach always decides).

# Plan: experiments track (independent)

You work fully offline: no Azure, no Foundry, no keys. Everything you need is `data/bronze/` and the brief in `docs/EXPERIMENTS.md`. Read `CLAUDE.md` first, and point your own Claude at it.

## You own
`src/plc/experiments/**`, `tests/test_exp_*.py`, `docs/experiments/*.md`. Nobody else edits these.

## You don't touch
Everything else (agents, engine, API, UI, `dataset.py`, shared dataclasses, `CLAUDE.md`). Need a change there? Open an issue titled `request: <what>`; the lead answers within a day.

## Milestones (one pull request each, branch `exp/<name>`)
| Due | Deliverable | Notes |
|---|---|---|
| **Oct 19** | `set_piece.py`: which opponents and which of our players are exposed or dangerous at set pieces | Uses `match_events` (corners, fouls) and `opponents` (aerial, set_piece_threat, avg height) |
| **Oct 21** | `late_game.py`: push-on vs drop-back profile per player | Uses `match_tracking`: output and heart rate per 5 minutes, first half vs last 30 minutes |
| **Oct 23** | `injury_risk.py`: transparent risk score per player | Uses `wearable_daily`, `training_sessions`, `injuries`: acute:chronic load, HRV vs baseline, history, age. Explain every term; no black boxes |
| **Oct 24 (freeze)** | All PRs merged; one doc per experiment | After this, only bug fixes the lead asks for |

If you finish early, start the next one. If you fall behind, ship a smaller version of the current one instead of skipping the PR.

## Definition of done (per pull request)
- `run(bronze) -> list[Signal]`; stdlib `csv` unless you justify a dependency in the PR description.
- Every `Signal.evidence` quotes the actual numbers, so the Fact-checker agent can verify it.
- Seeded, deterministic test in `tests/test_exp_<name>.py`; `uv run pytest -q` passes; `run()` takes under 2 seconds.
- `docs/experiments/<name>.md`: theory, what the numbers show, limitations. Keep it to one short page; the pitch will quote it.
- Validate against the data's known structure: low-HRV starters fade late, load spikes raise injury risk. If your signal doesn't recover those, say so rather than tuning until it does.

## How your work reaches the demo
The lead wires each merged `run()` into the Tactician agent as a tool. You don't write agent code, and you don't need to see it working to be done. You'll get a screenshot of your signal firing in the demo.

## Rules of the road
- Branch from latest `main`; rebase before opening the PR.
- Never commit to `main`, never commit data you didn't generate, never use real names or brands.
- Don't regenerate and commit `data/bronze/`; it is seed 0 and tests rely on it.
- Stuck for more than 30 minutes: open an issue, move on to the next milestone.

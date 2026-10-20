# Plan: experiments track (independent)

You own data quality and the signals the agents call. Most work is offline (no Azure, no keys): `data/bronze/` and the brief in `docs/EXPERIMENTS.md`. Read `CLAUDE.md` first, and point your own Claude at it. Background and evidence: `reports/Football AI tools replication.md` (local, not committed).

## You own
`src/plc/experiments/**`, `src/plc/dataset.py`, `src/plc/squad.py`, `data/bronze/**` (regenerate, never hand-edit), `tests/test_exp_*.py`, `tests/test_data*.py`, `tests/test_dataset.py`, `tests/test_eval*.py`, `docs/experiments/*.md`.

## Work packages, in priority order
1. **Data consistency:** cross-table invariants and distribution tests (goal events match the score; tracking totals add up, no tracking after a substitution; injuries line up with player status and minutes), a `ground_truth.json` of planted effects kept out of the agent-facing data, a few null decoy relationships, label noise. Keep the latent state hidden so experiments cannot just recover what the generator wrote.
2. **Calibration with sources:** every rate you calibrate cites a source and its licence. Do not use StatsBomb Open Data (its terms bar derived analysis and require its logo). Mark any number you could not verify as such.
3. **Fact-checker eval set:** questions with known answers computed from the data, so the lead can score the Fact-checker.
4. **Tools for the Tactician:** expose each experiment (`set_piece`, late-game fade, readiness flag list, pitch control or xT) as a plain function the agents call, with evidence that quotes real numbers.
5. **Fabric stretch, only if 1 to 4 are done:** a paced replay into the Eventstream. Sleep between chunks, no tight loops, no parallel sends, state the expected duration up front; the Fabric capacity is shared.

## You don't touch
Agents, orchestration, engine, API, UI, `CLAUDE.md`, `docs/PLAN_LEAD.md`. Need a change there? Open an issue titled `request: <what>`; the lead answers within a day. Changing a shared dataclass field also needs a `request:` issue first.

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
You expose each merged `run()` as a plain function with a docstring the Tactician can call. The lead registers it as an agent tool and owns the approval gate; you don't write agent or orchestration code. You'll get a screenshot of your signal firing in the demo.

## Rules of the road
- Branch from latest `main`; rebase before opening the PR.
- Never commit to `main`, never commit data you didn't generate, never use real names or brands.
- Regenerating `data/bronze/` is allowed only in a pull request that also updates every test depending on seed 0, and says in the description what changed. Keep bronze equal to pure generator output.
- Stuck for more than 30 minutes: open an issue, move on to the next milestone.

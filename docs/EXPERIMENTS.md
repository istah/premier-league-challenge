# Experiments brief

Goal: signals the Tactician agent can call, grounded in the bronze data. Read `CLAUDE.md` first.

## Workflow
1. `git pull`, then `git checkout -b exp/<name>` (never commit to `main`).
2. `uv sync`, `uv run python -m plc dataset` if `data/bronze/` is missing, `uv run pytest -q`.
3. Copy `src/plc/experiments/template.py` to `<name>.py`. One `run(bronze) -> list[Signal]`, stdlib `csv` unless you justify a dependency in the PR.
4. Add a seeded test in `tests/test_<name>.py`. Every `Signal.evidence` must quote the real numbers behind the value; the Fact-checker verifies against it.
5. Open a pull request. Merge freeze is **Oct 24**; unmerged work stays out of the entry.

## Ideas, in priority order
1. **Set-piece impact:** from `match_events` (corners, fouls) and `opponents` (aerial, set_piece_threat, avg height), which opponents and which of our players are exposed or dangerous at set pieces.
2. **Push-on vs drop-back profiles:** from `match_tracking` (distance and sprints per 5 minutes, heart rate), which players hold output late and which fade, and who suits which role.
3. **Injury risk:** from `wearable_daily`, `training_sessions` and `injuries`, a transparent load-and-recovery risk score per player (acute:chronic load, HRV vs baseline, history, age). Explain it; no black boxes.
4. **Generator calibration:** make `dataset.py` rates (xG, pass completion, fatigue curves) match public reference statistics. Cite the source and note its licence; never commit raw third-party data.

## Don't
- Change fields of the shared dataclasses (`squad.py`, `training.py`, `tracking.py`, `events.py`) without telling the lead first.
- Use real player or club names, logos or brand names, or add secrets.
- Hand-edit `data/bronze/`; regenerate it.

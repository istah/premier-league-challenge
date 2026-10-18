# Plan: lead track (app, agents, demo)

Owner: lead developer with Claude. Merge freeze **Oct 24**, submit **Oct 26** (deadline Oct 27, 11:59 pm PT).

## Owns
`src/plc/` outside `experiments/`, `tests/` outside `test_exp_*`, `docs/PLAN_*`, `CLAUDE.md`, deploy config, pitch, video.

| Due | Task | Needs |
|---|---|---|
| Oct 19 (am) | Register as team representative (before Oct 20, 12:00 pm PT); add teammate | Registration form |
| Oct 19 | Decide solo vs team wording (check hackathon team-size rules); update `CLAUDE.md` and `README.md` to match | Hackathon rules |
| Oct 19 | Email opencode@microsoft.com: does a coach-facing use case fit the theme? | |
| Oct 19 | Create Foundry project; deploy a chat model and Microsoft-Decision-1; fill `.env` | Azure subscription |
| Oct 19 | Match engine: tick-based, seeded, reacts to substitutions and formation changes | |
| Oct 20 | CI: GitHub Actions runs `uv run pytest -q` on pull requests | |
| Oct 21 | API streaming ticks; agents live on the stream: Coordinator, Tactician, Opponent Analyst, Fact-checker | Foundry |
| Oct 21 | Verify the Decision-1 response field for probabilities against a real call | Foundry |
| Oct 22 | One-page coach interface; dictation text box and mic button; deploy to Azure Container Apps | |
| Oct 22 | Tests: a coach override beats any AI suggestion; no substitution is ever auto-applied | |
| Oct 23 | Fact-checker cites the layer and query it used for every verification | |
| Oct 23 | Wire merged experiments in as Tactician tools | experiment PRs |
| Oct 24 | Freeze. Replay comparison: no changes vs AI accepted vs coach decisions | |
| Oct 24 | Pre-public audit: secrets, personal emails in git history (rewrite if needed), real names or brands | |
| Oct 25 | Pitch text, architecture diagram, demo script; pitch states real use of biometrics needs player consent; stretch: Fabric RTI only if everything above is done | |
| Oct 26 | Make the repo public and submit by midday; then record and re-check the 2-minute video | |

## Contingency
If the match engine slips past Oct 20, run the demo on the existing `generate_match` events and keep the streaming API on top of them.

## Lead-only backlog
Generator calibration: make `dataset.py` rates (xG, pass completion, fatigue curves) match public reference statistics. Cite the source and its licence; never commit raw third-party data. Not on the critical path; do it only after Oct 24 if time allows (it would change seed-0 data and tests).

## Review duty
Review experiment PRs within a day: tests pass, evidence quotes real numbers, no files outside the experiments track touched.

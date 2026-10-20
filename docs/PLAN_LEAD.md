# Plan: lead track (app, agents, demo)

Owner: lead developer with Claude. Merge freeze **Oct 24**, submit **Oct 26** (deadline Oct 27, 11:59 pm PT).

## Owns
`src/plc/` outside `experiments/`, `tests/` outside `test_exp_*`, `docs/PLAN_*`, `CLAUDE.md`, deploy config, pitch, video.

| Due | Task | Needs |
|---|---|---|
| Oct 19 (am) | Register as team representative (before Oct 20, 12:00 pm PT); add teammate | Registration form |
| Oct 19 | Create Foundry project; deploy a chat model and Microsoft-Decision-1; fill `.env` | Azure subscription |
| Oct 19 | Match engine: tick-based, seeded, reacts to substitutions and formation changes | |
| Oct 21 | API streaming ticks; agents live on the stream: Coordinator, Tactician, Opponent Analyst, Fact-checker | Foundry |
| Oct 21 | Verify the Decision-1 response field for probabilities against a real call | Foundry |
| Oct 22 | One-page coach interface; dictation text box and mic button; deploy to Azure Container Apps | |
| Oct 23 | Wire merged experiments in as Tactician tools | experiment PRs |
| Oct 24 | Freeze. Replay comparison: no changes vs AI accepted vs coach decisions | |
| Oct 25 | Pitch text, architecture diagram, demo script; stretch: Fabric RTI only if everything above is done | |
| Oct 26 | Record the 2-minute video; make the repo public; submit | |

## Review duty
Review experiment PRs within a day: tests pass, evidence quotes real numbers, no files outside the experiments track touched.

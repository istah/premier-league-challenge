# Demo script (video under 2:00)

Source: the real UI in `src/plc/static/index.html`, scenario `engine.new_match(seed=7)`: a tired star midfielder the AI would rest is started anyway, and fades after about 55'. Synthetic data, fictional club, no logos or brand names (say "wearable"). Record the offline demo: `uv run uvicorn plc.api:app` then open the page.

> TODO: another agent is changing the opening screen. Re-check every on-screen cue below against the final UI before recording. Names of the tired midfielder and bench players come from seed 7: read them from the screen and fill in the voiceover.

| Time | Shot | On screen | Voiceover |
|---|---|---|---|
| 0:00-0:10 | Title card then app | "Redmoor FC Coach Room. Synthetic data." Scoreboard Redmoor v Harbour Rovers, 0-0 | "Clubs use AI mostly before the match. We found no product that suggests substitutions during it. This is a simulation of what a live feed could support." |
| 0:10-0:25 | Pre-match | Players tab: readiness check-in, tired midfielder flagged, bench | "Before kick-off the staff flag a tired midfielder. The coach starts him anyway. That is his call." |
| 0:25-0:40 | Play | Press Play; clock runs, pitch animates, Staff notes tab fills on the Now tab | "The match streams events onto a bus. Rules fire only when something changes." |
| 0:40-1:00 | Staff callout (about 55') | Callout on the pitch: staff note with source, heart rate and output drop for the midfielder against his own baseline | "Around 55 minutes he fades against his own baseline. The orchestrator routes this to the Tactician and Own-Style analyst. A judge checked every number against the data." |
| 1:00-1:15 | One-tap action | Click the action button on the note, then Accept on the AI suggestion (or "Keep him on") | "One tap, and the coach is in control. Nothing happens unless he accepts." |
| 1:15-1:35 | Voice override | Press the mic (or V); say or type "take off [name], bring on [name]". Toast confirms | "The coach disagrees and dictates his own change. A coach call always beats the AI." |
| 1:35-1:50 | Formation change | Tactics tab: pick another formation; roles appear on the pitch, such as an overlapping full-back or a wide midfielder tucking in | "He changes formation. Every player's new role shows on the pitch." |
| 1:50-2:00 | Close | Log tab, then title card | "AI is decision support. The coach decides. Data is synthetic; real biometrics need player consent." |

## Notes
- Do not claim Foundry agents, Fabric or the LLM judge ran live unless the lead has flipped the TODO in `docs/PITCH.md`. Offline is the honest default.
- Keep total under 2:00; trim the pre-match shot first.
- No club crests, no real names, no wearable brand names.

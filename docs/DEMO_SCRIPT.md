# Demo script (video under 2:00)

Source: the real UI in `src/plc/static/index.html`, scenario `engine.new_match(seed=7)`: a tired star midfielder the AI would rest is started anyway, and fades after about 55'. Synthetic data, fictional club, no logos or brand names (say "wearable"). Record the offline demo: `uv run uvicorn plc.api:app` then open the page.

Re-run on Oct 22 after the playtest fixes (Chrome, 1440x800, seed 7; pauses at 5', 65' and 70' observed, no console errors). Checked against the UI after the opening change (headless Chrome, 1280x720 and 1440x800, seed 7): the match auto-starts about 1.5 s after load, a header line under the scoreboard names who to watch (Petrov, HRV 62% of baseline), the first staff callout arrives about 3.5 s in, and the clock pauses by itself when a callout with actions appears. Ticks run every 2 s, so a full 90 minutes takes about 90 s of real time: record the match once, then cut. Not checked: player popovers, sliders and voice input in a browser, Safari, small screens.

| Time | Shot | On screen | Voiceover |
|---|---|---|---|
| 0:00-0:10 | Page load | Redmoor v Harbour Rovers, 0-0. Header: "Watch Petrov, HRV 62% of baseline". Press Play (speed Fast: 2 s per 5 minutes) | "Clubs use AI mostly before the match. We found no product that suggests substitutions during it. This is a simulation of what a live feed could support." |
| 0:10-0:25 | Readiness callout (5', clock pauses, Resume button) | Callout: Petrov, HRV 62%, wellness poor. Staff notes also list Mbeki: "HRV looks fine (109%) but his own wellness check-in is poor; HRV alone would miss this". Click "Not now", then Resume | "Before kick-off the staff flag two risks: a tired midfielder, and a player whose heart-rate variability looks fine but who says he feels bad. The coach starts them anyway. That is his call." |
| 0:25-0:40 | Play on | Pitch animates; the Staff notes feed fills, each note marked "checked against the data" | "The match streams events onto a bus. Rules fire only when something changes, and a judge checks each number against the data before the coach sees it." |
| 0:40-1:00 | 65' substitution suggestion | Clock pauses. AI suggestion card (Now tab): "Petrov off, Salah-Reyes on: distance down 14% vs first half, HR up 5%, morning HRV 62% of baseline". A shape callout may sit on the pitch at the same time | "He fades against his own baseline. Accept, or keep him on: the coach decides." |
| 1:00-1:15 | Coach override | Press V, type or say "take off Petrov, bring on Quinn" (any bench player other than the AI pick; check the Players tab). Toast confirms | "The coach disagrees and dictates his own change. A coach call always beats the AI, and nothing is applied unless he says so." |
| 1:15-1:30 | 70' second fade | Suggestion: "Mbeki off, Larsen on: distance down 29%, HR up 1%, morning HRV 109% of baseline" | "Five minutes later the player the heart-rate number cleared is the one who fades. The wellness check-in saw it first." |
| 1:30-1:45 | Formation change | Tactics tab: pick another formation; roles appear on the pitch; toggle "Show tactics on pitch" | "He changes formation. Every player's new role shows on the pitch." |
| 1:45-2:00 | Close | Log tab, title card | "AI is decision support. The coach decides. Data is synthetic; real biometrics need player consent." |

## Notes
- Do not claim Foundry agents, Fabric or the LLM judge ran live unless the lead has flipped the TODO in `docs/PITCH.md`. Offline is the honest default.
- Keep total under 2:00; trim the pre-match shot first.
- No club crests, no real names, no wearable brand names.

## Draft capture
`scripts/record_demo.js` drives the real UI in Chrome and records a silent screen capture of the flow above (5' callout, 65' suggestion, dictated override "take off Petrov, bring on Quinn", tactics overlay, formation change, log). A first run on Oct 22 worked, including the override toast. Record the voiceover over it, or re-record the screen yourself; trim to under 2:00.

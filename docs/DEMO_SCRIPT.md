# Demo script (video under 2:00)

Source: the real UI in `src/plc/static/index.html`, scenario `engine.new_match(seed=7)`: a tired star midfielder the AI would rest is started anyway, and fades after about 55'. Synthetic data, fictional club, no logos or brand names (say "wearable"). Record the offline demo: `uv run uvicorn plc.api:app` then open the page.

Checked against the UI after the opening change (headless Chrome, 1280x720 and 1440x800, seed 7): the match auto-starts about 1.5 s after load, a header line under the scoreboard names who to watch (Petrov, HRV 62% of baseline), the first staff callout arrives about 3.5 s in, and the clock pauses by itself when a callout with actions appears. Ticks run every 2 s, so a full 90 minutes takes about 90 s of real time: record the match once, then cut. Not checked: player popovers, sliders and voice input in a browser, Safari, small screens.

| Time | Shot | On screen | Voiceover |
|---|---|---|---|
| 0:00-0:10 | Page load | Redmoor v Harbour Rovers, 0-0. Header: "Watch Petrov, HRV 62% of baseline". Match starts by itself | "Clubs use AI mostly before the match. We found no product that suggests substitutions during it. This is a simulation of what a live feed could support." |
| 0:10-0:22 | First callout (about 5') | Readiness callout on the pitch about Petrov, then the clock pauses | "Before kick-off the staff flag a tired midfielder. We start him anyway. That is the coach's call." Click "Not now" and the match resumes |
| 0:22-0:40 | Play on | Pitch animates; Now tab: Staff notes fill with a source on each note; occasional shape callouts | "The match streams events onto a bus. Rules fire only when something changes, and each note is checked against the data before the coach sees it." |
| 0:40-1:00 | Substitution callout (about 65') | The AI suggestion card (Now tab) shows Petrov off, Salah-Reyes on, with heart rate and output drop against his own baseline, and the clock pauses. Accept or "Keep him on" and the match resumes by itself | "He fades against his own baseline. A judge checked every number the staff quoted." |
| 1:00-1:15 | Coach override | Press V, type or say "take off Petrov, bring on Quinn" (any bench player other than the AI pick; check the Players tab). Toast confirms | "The coach disagrees and dictates his own change. A coach call always beats the AI, and nothing is applied unless he says so." |
| 1:15-1:35 | Formation change | Tactics tab: pick another formation; roles appear on the pitch (overlapping full-back, wide midfielder tucking in); toggle "Show tactics on pitch" | "He changes formation. Every player's new role shows on the pitch." |
| 1:35-1:50 | Individual order | Click a player, press "Wider" or "Deeper" | "Down to one player: drop wider, play deeper." |
| 1:50-2:00 | Close | Log tab, title card | "AI is decision support. The coach decides. Data is synthetic; real biometrics need player consent." |

## Notes
- Do not claim Foundry agents, Fabric or the LLM judge ran live unless the lead has flipped the TODO in `docs/PITCH.md`. Offline is the honest default.
- Keep total under 2:00; trim the pre-match shot first.
- No club crests, no real names, no wearable brand names.

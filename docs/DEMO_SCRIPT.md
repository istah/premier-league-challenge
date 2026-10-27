# Demo script (video under 2:00)

Source: the real UI in `src/plc/static/index.html`, scenario `engine.new_match(seed=7)`: a tired star midfielder the AI would rest is started anyway, and fades after about 55'. Synthetic data, fictional club, no logos or brand names (say "wearable"). Record the offline demo: `uv run uvicorn plc.api:app` then open the page.

Re-run on Oct 22 after the playtest fixes (Chrome, 1440x800, seed 7; pauses at 5', 65' and 70' observed, no console errors). Checked against the UI after the opening change (headless Chrome, 1280x720 and 1440x800, seed 7): the match auto-starts about 1.5 s after load, a header line under the scoreboard names who to watch (Petrov, HRV 62% of baseline), the first staff callout arrives about 3.5 s in, and the clock pauses by itself when a callout with actions appears. Ticks run every 2 s, so a full 90 minutes takes about 90 s of real time: record the match once, then cut. Not checked: player popovers, sliders and voice input in a browser, Safari, small screens.

| Time | Shot | On screen | Voiceover |
|---|---|---|---|
| 0:00-0:10 | Page load, Play at Fast | Redmoor v Harbour Rovers; header "Watch Petrov" | "A manager has minutes and many signals. This is a team of AI agents that joins them, on synthetic football data, and shows its working." |
| 0:10-0:25 | 5' readiness callout (clock pauses) | Petrov, HRV 62%; staff notes also list Mbeki: HRV fine but wellness poor. Click Not now, Resume | "Before the whistle the staff flag two risks, including a player the heart-rate number clears but who says he feels bad." |
| 0:25-0:45 | 65' suggestion | AI suggestion card: Petrov off, Salah-Reyes on, with the numbers. Staff notes with the green "checked against the data" mark | "At 65 minutes he fades against his own baseline. Analysts run in parallel on Microsoft Foundry through Agent Framework; a Fact-checker agent and a rules judge verify every number before the coach sees it." |
| 0:45-1:05 | Coach override | Press V, dictate "take off Petrov, bring on Quinn"; toast confirms | "The coach disagrees and dictates his own change. A coach call always beats the AI, and nothing is applied automatically." |
| 1:05-1:25 | Formation change | Tactics tab, switch formation, "Show tactics on pitch" | "He changes formation, and every player's new role shows on the pitch." |
| 1:25-1:45 | Orchestration trace | Log tab, "How the staff worked": rule fired, agents run, judge verdict | "Every trigger is traceable: which rule fired, which agents ran, what the judge decided. Agents are published in Foundry Agent Service and scored with Foundry's Groundedness evaluator." |
| 1:45-1:55 | Close | Title card: Redmoor FC Coach Room, synthetic data | "AI is decision support. The coach decides. Data is synthetic; real biometrics need player consent." |

**Requirements from the rules:** under 2:00 (aim for 1:55); public YouTube or Vimeo link added on the project page; footage of the project running (the browser app, as here); no third-party trademarks (our UI has none; do not show a browser logo bar or other apps) and no copyrighted music (use none).

## Notes
- Do not claim Foundry agents, Fabric or the LLM judge ran live unless the lead has flipped the TODO in `docs/PITCH.md`. Offline is the honest default.
- Keep total under 2:00; trim the pre-match shot first.
- No club crests, no real names, no wearable brand names.

## Draft capture
`scripts/record_demo.js` drives the real UI in Chrome and records a silent screen capture of the flow above (5' callout, 65' suggestion, dictated override "take off Petrov, bring on Quinn", tactics overlay, formation change, log). A first run on Oct 22 worked, including the override toast. Record the voiceover over it, or re-record the screen yourself; trim to under 2:00.

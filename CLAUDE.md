# Premier League Challenge: project rules

Solo-led entry for the Microsoft Inside the Game hackathon, category **Best Multi-Agent System**.
Fictional club (Redmoor FC), synthetic data only. Submission closes **Oct 27, 2026 11:59 pm PT**. Merge freeze **Oct 24**.

## Hard rules (hackathon)
- Data is synthetic. Never commit real match data, real player names or licensed feeds. No third-party trademarks or logos in code, UI or demo (no club crests, no wearable brand names; say "wearable").
- The repo must be public at submission: no secrets, no private data, no personal emails in history. Secrets live in `.env` (git-ignored); keep `.env.example` current.
- Biometrics are sensitive: everything stays synthetic, and the pitch says real use needs player consent.
- AI is decision support. The coach always decides: a coach override (typed or dictated) beats any AI suggestion. Never auto-apply a substitution.

## Code conventions
- Python 3.11+, `uv`. Run `uv run pytest -q` before every push; run the demo with `uv run python -m plc demo`.
- Stdlib first, one new dependency only with a reason. Smallest code that works; no speculative abstractions.
- Deterministic: every generator takes a `seed`. Same seed, same output. Tests depend on this.
- Dataclasses in `squad.py`, `training.py`, `tracking.py`, `events.py` are the shared contract. Don't change their fields without telling the other developer first.
- Comments only for non-obvious why. Match the surrounding style.
- Experiments live in `src/plc/experiments/<name>.py`: one function that reads the shared dataclasses and returns signals, a seeded test, and a short docstring stating the theory.
- Unverified API behaviour gets a comment saying so (see `decision.py`). Don't invent request or response fields.

## Git
- `main` stays runnable. Work on branches (`feat/...`, `exp/...`), merge via pull request with passing tests.
- Commit messages: imperative, one line, no trailing period.
- End commits with: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` when Claude wrote them.

## Medallion architecture
Data moves one way: bronze, then silver, then gold. Each layer reads only from the one before it.

| Layer | Contents | Rules |
|---|---|---|
| **Bronze** | Raw synthetic output exactly as generated: match events, training sessions, tracking snapshots, with an ingest timestamp | Append-only, never edited, no business logic |
| **Silver** | Validated, deduplicated, conformed data: per-player metrics normalised to the player's own baseline, rating history, match-day readiness, 5-minute windows | Typed, schema-checked, reproducible from bronze |
| **Gold** | Decision-ready outputs: suggested XI, live alert features, opponent insights, per-audience views (coach, analyst, fan) | What the agents read. Small, documented, one row per decision question |

**Where it runs**
- **Local now:** the current modules map as bronze = `events.py`, `training.py`, `tracking.py` output; silver = `readiness.py` and the baseline comparison in `live.py`; gold = lineup, `Alert`, `opponent.py` insights. Keep new code on the right side of these lines.
- **Fabric (planned, after agents work):** Eventstream lands raw events into **bronze** tables in an Eventhouse (KQL). Update policies and materialized views derive **silver** and **gold**. Activator rules fire on gold. Historical and training data use a Lakehouse with the same three layers.
- **Foundry:** Foundry has no medallion concept; this is our convention. Agents and Decision-1 read **gold only**. The Fact-checker may query **silver** (and bronze for provenance) to verify a claim, and must cite the layer and query it used.

**Bronze dataset:** `uv run python -m plc dataset` writes `data/bronze/*.csv` (seed 0 is committed): wearables, training, injuries, 15 matches, opponents. Regenerate rather than hand-edit.

Naming: `bronze_<entity>`, `silver_<entity>`, `gold_<entity>` for tables and KQL functions.
Never let an agent write to bronze or silver. Agents write only to gold (insights) and opponent memory.

## Agents
- Pipeline: Coordinator, Tactician, Opponent Analyst, Fact-checker, Coach Briefing, personalised per audience.
- Decision-1 (Foundry) makes fast bounded yes/no and choice calls; LLM agents explain. Include a `cannot_tell` option so low confidence escalates to the coach.
- Every claim an agent makes about the match must be checkable against the data. No invented facts.
- Tools needing a human decision use `@tool(approval_mode="always_require")`.

## Config
`FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL` (chat agents); `FOUNDRY_RESOURCE_ENDPOINT`, `DECISION_DEPLOYMENT` (Decision-1). Without them the demo runs offline on the heuristic.

# Pre-public audit (Oct 22, lead)

Checked on `main` and all history before making the repo public. Re-run on Oct 25.

| Check | Result |
|---|---|
| Secrets (key patterns, `.env`, `.pem`, `.key` ever added) | None found. `.env` is git-ignored and was never committed |
| Employer or tenant identifiers (company name, subscription and tenant ids) | None in any tracked file |
| Author and committer emails across all history | Only GitHub noreply addresses (history rewritten Oct 21; re-verify after every merge with `git log --all --format='%ae %ce' \| sort -u`) |
| Real clubs, vendors or brands in `src/`, the UI, `README.md`, `docs/PITCH.md`, `docs/DEMO_SCRIPT.md`, `CLAUDE.md` | None |
| Real clubs and vendors named in `docs/RESEARCH.md`, `docs/PLAN_EXPERIMENTS.md`, `reports/`, `research_notes/` | Yes, as cited prior art (a few clubs and tracking vendors, with sources) |

**Open decision (lead):** the rule says no third-party trademarks in code, UI or demo, and the research files are none of those, but they name real clubs and vendors and quote articles. Options: keep them (cited research, lowest effort), keep only `docs/RESEARCH.md` and drop `reports/` and `research_notes/`, or move all of it to a private repo. Decide by Oct 24.

**Still to do before public:** delete the backup bundle with the old emails, ask GitHub support to garbage-collect the rewritten history, rotate or remove the borrowed Azure resources (#38), re-run this table.

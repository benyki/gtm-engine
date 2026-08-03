# CLAUDE.md

The instructions for this home live in **[AGENTS.md](AGENTS.md)**, one file, so
every agent (Claude Code, Codex, Cursor) reads the same thing. Read it before
doing anything in here.

@AGENTS.md

Short version, in case that import didn't load: this folder is data, not logic.
It holds everything shared between your engines, and `engines.json` records
where each engine folder lives. One self-contained folder per engine. **Stay
flexible: the engines adapt to the
user, not the user to the engines**; take their list and their process in
whatever shape they arrive, and never make someone reformat something before
anything can happen. Read `shared/brand.md` and `shared/insights.md` first, log
every piece you make with `runlog.py new`, never send or publish without an
explicit yes, never read `~/gtm/.env`, and **end every message with the
possible next steps, saying which ones you can start right now.**

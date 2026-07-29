---
name: engine-setup
description: Install gtm-engine and build the user's workspace. Clones the repo, installs every skill into ~/.agents/skills/, mirrors them into workflows/skills/ and every coding agent present on the machine, scaffolds <project>/workflows/, interviews the user to fill in brand and channel config, and runs the doctor check. Use when the user says "run engine-setup", "set up gtm-engine", "install the growth workflows", or points you at the gtm-engine repo for the first time.
---

# engine-setup

Gets someone from nothing to a working workspace in about fifteen minutes.

Run it once per project. It is also re-runnable — `doctor.py` alone is the health check.

## What you're building

Two separate things, and keeping them separate is the point:

- **The repo** (`~/code/gtm-engine`) — the workflows. Updated by `git pull`. Nothing personal in it.
- **The workspace** (`<their-project>/workflows/`) — their brand, inputs, templates, runs, numbers. Never touched by an update.

## Steps

Do these in order. Confirm each one before moving on — a wrong path here is annoying to unpick later.

### 1. Ask about starring the repo

Ask the user whether they'd like to star it. **Do not star it without a clear yes** — it's a public action on their GitHub account.

If yes and `gh` is authenticated: `gh repo star benyki/gtm-engine`
Otherwise give them the link and let them click.

### 2. Clone

```bash
git clone https://github.com/benyki/gtm-engine.git ~/code/gtm-engine
```

Confirm the path first — some people keep code elsewhere. If the directory already exists, `git -C ~/code/gtm-engine pull` instead.

### 3. Scaffold the workspace

Ask which project they want to grow, then from that directory:

```bash
python3 ~/code/gtm-engine/skills/engine-setup/scripts/scaffold_workspace.py .
```

It refuses to overwrite an existing `workflows/`. That refusal is correct — use `--merge` to fill gaps, or `--name` for a second one.

If they already created an empty `workflows/` folder during preflight, run with `--merge` so the scaffold fills it without touching what they already have.

### 4. Install the skills

This is the path chain. One source of truth; everything else is a symlink.

```
~/code/gtm-engine/skills/<name>
        ↓ symlink
~/.agents/skills/<name>          ← canonical store (create it)
        ↓ symlink
<project>/workflows/skills/<name>
~/.claude/skills/<name>          ← Claude Code doesn't scan the canonical store
~/.openclaw/skills/<name>        ← only if that agent is present
```

**`~/.agents/skills/` is the install target.** It's the cross-agent standard: Codex
reads it natively ([docs](https://developers.openai.com/codex/skills)) and so does
Cursor ([docs](https://cursor.com/help/customization/skills)). Neither needs a link in
its own directory, and a link in `~/.codex/skills/` is dead code — Codex doesn't scan
that path at all.

An agent-specific directory is an **exception, and needs a doc URL saying why**:

| Directory | Linked? | Why |
|---|---|---|
| `~/.agents/skills/` | canonical | read natively by Codex and Cursor |
| `~/.claude/skills/` | **yes** | Claude Code reads only its own dirs ([docs](https://code.claude.com/docs/en/skills)) |
| `~/.codex/skills/` | no | not scanned by Codex — links here are dead |
| `~/.cursor/skills/` | no | redundant; Cursor already reads the canonical store |
| `~/.openclaw/skills/` | yes, if present | own layout, no public doc — verified on the machine |

If you're tempted to add a directory to that list, find the vendor doc first. A dead
symlink is worse than none: the installer reports it green and the skill silently
never triggers.

Run the installer, pointing it at their workspace:

```bash
~/code/gtm-engine/skills/engine-setup/scripts/install_skills.sh \
  --workspace <project>/workflows
```

What it does (you do **not** do this by hand unless the script is unavailable):

1. **Create** `~/.agents/skills/` if missing
2. **Symlink every skill** from the clone (`skills/*/SKILL.md`) into `~/.agents/skills/<name>`
3. **Create** `<workspace>/skills/` and symlink each skill there too
4. **Mirror into the agents that need it** — only Claude Code (`~/.claude/skills`) and
   OpenClaw (`~/.openclaw/skills`), and only when that agent's home already exists.
   Codex and Cursor are skipped on purpose; see the table above
5. **Idempotent** — correct links stay; wrong links are relinked; a real directory collision is warned and skipped (never overwrite). Links left in `~/.codex/skills` by an older install are reported, not deleted — removing things from someone's home directory is their call

Because they're symlinks, `git pull` in the engine repo updates every agent at once. There is never a reinstall for content — only re-run the script when adding a new agent or a new workspace.

If it reports "a real directory is already there", something else owns that name. Tell the user, don't force it.

Without `--workspace`, it still does the home + agent mirrors (useful on a fresh machine before the project folder exists). Re-run with `--workspace` once `workflows/` is ready.

### 5. Fill in the config

This is the part that decides whether the output is any good, so don't rush it into a single question. Interview them, then write the files.

**`config/brand.md`** — the important one. Ask:
- Audience type: **B2B/sales-led** (wants replies and meetings) or **B2C/audience-led** (wants reach and signups)? Everything downstream branches on this
- Who specifically? Push for specifics — "B2B SaaS founders, 5–50 staff, UK" is usable, "businesses" isn't
- What do they sell, and what's the promise?
- Tone: three words they are, three they aren't
- Anything they're never allowed to say — claims, competitor names, regulated language

**`config/channels.json`** — `active_workflow` (one of `seo`, `linkedin`, `video`, `outreach`) and `primary_metric`. The metric is what the loop optimises. Make them name a real one: replies, signups, demos. "Engagement" is not a metric.

**`config/sources.json`** — where content ideas come from. The default is Reddit, which needs nothing. If they have competitor URLs, put them in. Only wire up Ahrefs or Semrush if they already pay for it.

**`config/experiments.json`** — leave the shipped starter experiment as-is for now. It has two arms and no data, which is the right starting state.

Then ask them to drop their material into `inputs/`:
- `inputs/swipe/` — content they like
- `inputs/best/` — their own best-performing pieces, which is where voice is actually learned from
- `inputs/audience/` — the outreach list, any format
- `inputs/assets/` — logo, fonts, b-roll

### 6. Keys

```bash
cp config/.env.example config/.env
```

Have **them** paste the keys in. Never ask a user to give you a key in chat, and never read `config/.env` — you read `.env.example` for the names only. If a key is missing, name the variable and where to get it; don't work around it.

Which keys they need depends on the workflow — see `docs/prerequisites.md`. For `seo`, `linkedin` and `outreach`, usually none.

### 7. Check

```bash
python3 ~/code/gtm-engine/skills/engine-setup/scripts/doctor.py
```

Walk through anything red. Warnings are usually fine to leave. Doctor checks the canonical store, each agent mirror it can see, and `workflows/skills/` when a workspace is found.

### 8. Hand over

Tell them the one next thing to do — run their chosen content workflow and ship one piece. Not three. The loop needs real runs more than it needs breadth.

## Rules

- **Confirm before writing anywhere outside the workspace.** Cloning and symlinking touch their home directory
- **Never star, push or post without an explicit yes**
- **Never read `config/.env`.** Names come from `.env.example`
- **Never copy skill folders** — always symlink. Copies drift the moment they `git pull`
- **Install to `~/.agents/skills/`, not to each agent's own folder.** An agent-specific
  directory gets a link only with a vendor doc URL justifying it — today that's Claude
  Code and OpenClaw. Codex and Cursor read the canonical store directly
- If they're on Windows or an Intel Mac, say what will and won't work rather than pretending it's fine. Text workflows are unaffected; video rendering is slow on Intel and needs adapting on Windows

## Going further

`references/advanced.md` — your own skills repo, Supabase instead of CSVs, object storage for media, cloud crons, Tailscale across machines. Read it when the user has been running this for a month, not on day one.

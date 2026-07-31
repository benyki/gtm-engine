---
name: engine-setup
description: Install gtm-engine and build the user's workspace. Sets up the ~/code layout, clones the repo, scaffolds a workflow-scoped <project>/workflows/, copies selected skills into ~/.agents/skills/ then symlinks them into Claude/Codex/Cursor and links the whole skills folder into the workspace, puts Desktop shortcuts on both, interviews the user to fill in brand and channel config, and runs the doctor check. Use when the user says "run engine-setup", "set up gtm-engine", "install the growth workflows", or points you at the gtm-engine repo for the first time.
---

# engine-setup

Gets someone from nothing to a working workspace.

Run it once per project. It is also re-runnable — `doctor.py` alone is the health check.

## What you're building

Two separate things, and keeping them separate is the point:

- **The repo** — the workflows (wherever they cloned it). Updated by `git pull`.
  Nothing personal in it.
- **The workspace** (`<their-project>/workflows/`) — their brand, inputs, templates, runs, numbers. Never touched by an update.

## Where everything lives

Settle this **before** you clone. Moving it later means re-running the installer and fixing every symlink.

**The workspace goes in the folder this session is already running in.** They
opened that directory on purpose — it's their project — so `workflows/` is
created inside it and everything stays reachable from where they already work.
No new home to invent, no path to remember.

```
<the session's working directory>/
└── workflows/                   ← the workspace: brand, runs, numbers

~/code/gtm-engine/               ← the clone (read-only, updated by git pull)
~/.agents/skills/                ← the skills themselves (step 4)

~/Desktop/                       ← two symlinks, so neither is buried (step 5)
├── workflows  →  <that project>/workflows
└── skills     →  ~/.agents/skills
```

The clone is the one thing that doesn't follow the cwd: it's shared across every
project, so it keeps its own durable home (step 2 defaults to `~/code/gtm-engine`).

`workflows/` is also the folder they can open directly in Claude Code or Codex day to day — everything the agent needs is reachable from it (`shared/`, each workflow folder, and `skills/` via the symlink).

**`workflows/` can live anywhere.** The cwd is the default, not a requirement:

- **Inside an existing repo** — the common case, and it's exactly what the default does: scaffold `workflows/` in the repo they already work in. Nothing about the engine assumes a standalone folder
- **Somewhere else entirely** — if the session happens to be running in a scratch directory, a home directory, or the gtm-engine clone itself, ask for a durable path instead. Those three are the only cwds worth overriding
- **In several places at once** — one workspace per product, per client, per language. That's supported and normal
- When they want more than one, **scaffold the full thing each time** — a complete `shared/` plus its own workflow folders, not one shared `shared/` referenced from two places. The whole point is that editing a template, a brand file or an experiment in one workspace can't reach a project that didn't need the change. Duplication here is the isolation

The scripts locate a workspace by its `shared/` folder, not by its name or path — so wherever it sits, set `GTM_WORKSPACE` or pass `--workspace` when you're working from outside its tree.

## Steps

Do these in order. Confirm each one before moving on — a wrong path here is annoying to unpick later.

**Before you scaffold, there are exactly two questions, and both already have
their answer:** the folder (default `~/code/`) and the workflow (default
outreach). Both are yes-or-something-else. Everything else in step 1 is a
statement, not a choice — nothing about the repo link blocks the setup. Don't
present a user with a numbered list of "required choices" on their first
screen; ask, take the default, keep going.

### 1. Point them at the repo

Not a question — a statement, made once, before anything is installed:

> Everything we'll use is in the git repo at
> <https://github.com/benyki/gtm-engine>. Open it and save it if you like — and
> if you spot anything that could be better, leave a comment or raise an issue.

That's the whole ask. Don't gate the setup on it, don't turn it into a
required choice, and don't ask for a star as a favour. If *they* say they'd
like to star it and `gh` is authenticated: `gh repo star benyki/gtm-engine`.

### 2. Clone

Default to `~/code/gtm-engine`:

```bash
mkdir -p ~/code
git clone https://github.com/benyki/gtm-engine.git ~/code/gtm-engine
```

If they already keep code somewhere else, use that instead — any durable personal folder works (`~/Documents`, `~/Projects`, `~/Desktop`). Do **not** put it in Downloads, a scratch folder, or anything that gets emptied regularly; the clone is pulled for updates over months.

If that directory already exists, `git -C <path>/gtm-engine pull` instead. Use that path for every later command in this setup (scaffold, install, doctor).

### 3. Scaffold the workspace

The workspace is **one self-contained folder per workflow** plus one `shared/`
folder — that separation is the architecture, not a convention. Agents will
rewrite workflows over time; because each lives in its own folder (its own
`workflow.json`, `experiments.json`, `sources.json`, `templates/`, `inputs/`,
`runs/`, `reports/`), changing one can never break another.

Two questions, and both already have their answer chosen. Ask them as
**yes-or-something-else**, not as open ones — an open question here costs a user
who doesn't yet know the options five minutes and a wrong guess.

**Where it goes** — name the actual folder this session is running in, don't
say "the current directory":

> I'll create `workflows/` right here, in `<your current working directory>`.
> Is that okay, or would you prefer a different folder?

**The default is the working directory the agent is already in.** They opened it
on purpose; it's almost always the project they want to grow, and it means the
workspace is reachable from the session with no path juggling. "Yes" is a
complete answer and the usual one.

Anything else is equally fine — a subfolder, a fresh directory, `~/code/acme/`,
anywhere at all; the scripts find a workspace by its `shared/` folder, not by
its path. Two cases worth catching before you scaffold: the cwd is the
**gtm-engine clone itself** (never scaffold there — it's the repo, and a
`.gtm-template` marker already stops the scripts treating `workspace/` as one),
or it's a **home directory or a scratch folder** they'll clean out. In both,
say so and ask for somewhere durable.

**Which workflow:**

> The first workflow is **outreach**. Would you like me to set it up now?

**Default to yes** and scaffold it. It's the fastest one to a real signal —
drafts today, replies this week — and it needs no keys and no site. Something
else is a fine answer: `seo`, `social`, `video`, a custom name, or a comma list.

Then, from the project directory:

```bash
python3 <repo>/skills/engine-setup/scripts/scaffold_workspace.py . --workflow outreach
```

**One workflow, not four.** Set up only the one they're running — the others are
folders nobody fills, and the loop learns from runs, not from scaffolding. (With
no `--workflow` at all the script creates one folder per shipped workflow;
that's the script's default, not this step's.) Adding a second later is
`--merge --workflow <name>`, which is the normal way to grow into it.

Other shapes, when they ask for them:

- `--workflow seo,outreach` — only those folders
- `--workflow outreach-investors:outreach` — a **second workflow of an
  existing type**, with its own goal, experiments and templates. Suggest this
  freely: two outreach workflows for two audiences, three video workflows for
  three formats is a normal shape, not an edge case. (Copying an existing
  folder works too — but empty its `runs/`, `reports/` and `crm.csv`;
  history belongs to the original)
- `--workflow newsletter` — a **custom workflow**; `engine-loop` runs it
  through the same traces, you supply the craft. Enable its channel(s) in
  `shared/channels.json` and write its experiments as part of this setup
- Delete any default folder they won't run — an empty workflow folder is
  clutter, not an obligation

Each workflow folder's `workflow.json` carries its `type` (which skill runs
it), its `goal`, and its `primary_metric`. `site/` is never pre-created.

It also writes **`AGENTS.md`** at the workspace root — how any agent should work
in there (what to read first, that every piece made gets a run row, the
boundaries that don't move, and ending every message with the possible next
steps) — plus a **`CLAUDE.md`** that points at it, so Claude Code, Codex and
Cursor read one file rather than three that drift. Both are the user's to edit;
a re-run never overwrites them. Mention them at handover: that file is where
they put anything they want every agent in this workspace to do.

It refuses to overwrite an existing `workflows/`. That refusal is correct — use
`--merge --workflow <new>` to add another workflow later, or `--name` for a
second workspace.

**One workspace per brand / ICP / language is the intended pattern.** Two
products or two audiences don't share a `brand.md` — scaffold each its own
workspace, either in its own project folder or side by side (`--name growth-de`,
`--name acme-b2b`), and run them independently. See *Where everything lives*
above: scaffold each one in full so an edit in one can't reach the other.

If they already created an empty `workflows/` folder during preflight, run with
`--merge` so the scaffold fills it without touching what they already have.

### 4. Install the skills

Path chain — real files in the canonical store; everything else is a symlink:

```
<repo>/skills/<name>
        ↓ COPY
~/.agents/skills/<name>          ← canonical (real files)
        ↓ symlink each
~/.claude/skills/<name>
~/.codex/skills/<name>
~/.cursor/skills/<name>
        ↓ symlink whole folder
<project>/workflows/skills  →  ~/.agents/skills
```

**`~/.agents/skills/` is the only place skill files live.** Agent folders and the
workspace get symlinks. Re-run the installer after `git pull` in the engine repo
to refresh the copies.

| Directory | What happens |
|---|---|
| `~/.agents/skills/` | **copy** of each selected `engine-*` skill |
| `~/.claude/skills/` | symlink per skill (if `~/.claude` exists) |
| `~/.codex/skills/` | symlink per skill (if `~/.codex` exists) |
| `~/.cursor/skills/` | symlink per skill (if `~/.cursor` exists) |
| `<workspace>/skills` | one symlink to the whole `~/.agents/skills` folder |

Other agents: set `GTM_AGENT_DIRS` (colon-separated skill dirs). `doctor.py`
honours the same variable.

Run the installer for the **same workflows** (always includes `engine-setup` +
`engine-loop`, plus any skill a chosen one depends on — `engine-social` reads
`engine-seo`'s subject-finding and browser-research references, so choosing
social installs seo too):

```bash
<repo>/skills/engine-setup/scripts/install_skills.sh \
  --workspace <project>/workflows
```

With `--workspace` you can omit `--workflow` — it reads each workflow
folder's `workflow.json` type and installs the matching skills.

What it does:

1. **Create** `~/.agents/skills/` if missing
2. **Copy** the selected skills from the clone into `~/.agents/skills/<name>`
3. **Symlink** `<workspace>/skills` → `~/.agents/skills` (whole folder)
4. **Symlink** each skill into Claude / Codex / Cursor skill dirs when that
   agent home exists (plus `GTM_AGENT_DIRS`)
5. **Idempotent** — re-copy refreshes content; wrong links are relinked; a real
   directory collision in an agent folder is warned and skipped

Without `--workspace`, it still does the canonical copy + agent mirrors.
Re-run with `--workspace` once `workflows/` is ready.

### 5. Put shortcuts on the Desktop

Both folders are now buried a few levels deep and both get opened constantly —
the workspace to read runs and drop inputs in, the skills folder to tweak a
workflow. Symlink them where they can't be missed:

```bash
ln -s <project>/workflows ~/Desktop/workflows
ln -s ~/.agents/skills ~/Desktop/skills
```

These are links, not copies — the files stay where they are, and dropping an
asset into `~/Desktop/workflows/shared/assets/` lands it in the real workspace.

If either name is already taken, look at what's there before touching it, and
either pick a different name or confirm the replacement with them. With more
than one workspace, name them per project (`~/Desktop/acme-workflows`) —
`workflows` on its own stops meaning anything at two.

### 6. Fill in the config

This is the part that decides whether the output is any good, so don't rush it into a single question. Interview them, then write the files. Global config is deliberately minimal — `shared/` holds only what every workflow uses (brand, accounts, keys, assets, docs, insights); everything else lives in each workflow's own folder.

**`shared/brand.md`** — the important one. Ask:
- Audience type: **B2B/sales-led** (wants replies and meetings) or **B2C/audience-led** (wants reach and signups)? Everything downstream branches on this
- Who specifically? Push for specifics — "B2B SaaS founders, 5–50 staff, UK" is usable, "businesses" isn't
- What do they sell, and what's the promise?
- Tone: three words they are, three they aren't
- Anything they're never allowed to say — claims, competitor names, regulated language

The bar is specificity. Show them what a filled answer looks like if they stall
— this is the level to aim for, not the content to copy:

> **Audience type:** B2B / sales-led — we want replies and conversations.
> **Who, specifically:** Solo founders and two-person teams who shipped in the
> last six months and have fewer than 100 users. Mostly technical, mostly Europe.
> **What I sell:** A £19/month tool that turns a founder's changelog into social posts.
> **The promise:** You stop disappearing for three weeks between launches.
> **Proof:** 340 users. Average customer posts 4× more after week two.
> **Voice — three words I am:** direct, specific, unbothered.
> **Three words I'm not:** corporate, breathless, salesy.
> **Never say:** "revolutionary", "game-changing", "10x", "AI-powered" as a
> selling point, any growth claim without a number behind it.
> **Formatting:** sentence case headings, no emoji, first person singular.
> **What I've learned:** posts that name a real number get 3× the replies.

Note the last line — it starts empty and is written one line at a time, every
time they reject something. It ends up the most useful part of the file.

**`shared/channels.json`** — the account list, and nothing else global. An open set: add any channel they actually use (newsletter, threads, reddit, …). Optional per-channel keys the scripts honour: `primary_metric` (overrides a workflow's own for runs on that channel) and `metric_delay_hours` where the 72h default is wrong (weeks for blog/Search Console, a day or two for email).

**Each workflow's `workflow.json`** — per workflow, ask for its **goal** (one sentence: what this workflow exists to produce) and its **`primary_metric`**. The metric is what the loop optimises for that workflow, so make them name a real one: replies, signups, demos, clicks. "Engagement" is not a metric. Two workflows of the same type with different goals get different metrics — that's the point of having two.

**Each workflow's `sources.json`** — where that workflow's ideas come from. The seo default is Reddit, which needs nothing. If they have competitor URLs, put them in. Only wire up Ahrefs or Semrush if they already pay for it.

**Each workflow's `experiments.json`** — **leave these paused. Setting up an A/B test is not part of the first setup.**

They ship `"status": "paused"` on purpose, and the right move on day one is to leave them that way. The first job is one template the user is actually happy with: ship it, look at the numbers, change it, ship again. `assign_arm.py` handles this without any config — with no live experiment it returns `use_template`, and every run still lands in `runs/index.csv` with the template it used, so no history is lost. An experiment started before the format is settled freezes a template that still needs work, and at two posts a week it collects noise for two months before it says anything.

Tell them that plainly, and tell them what changes it: once they have a format they'd ship without editing, and roughly 5–10 pieces with numbers on them, that's when a variable is worth testing. `engine-loop/references/ab-testing.md` → R0 is the checklist, and the loop will raise it at the right moment.

If they push back and want a test running from day one, it's their call — then rewrite the arms in their terms before flipping `status` to `live`. The shipped arms are **examples of shape, not hypotheses for their business**: a B2C app has no use for a "partner revenue split" arm, and if it ships live the first run gets assigned to it. Keep the structure (two arms, one variable, a stated hypothesis each), size `min_runs_per_arm` to their real volume, and note that several live experiments can coexist in one workflow only when each is scoped to its own `channel` — otherwise the first one wins and the script warns.

Then ask them to drop material into the inputs:
- `shared/assets/` — logo, fonts, b-roll, anything **any** workflow might reuse
- `<workflow>/inputs/best/` — their own best-performing pieces (seo / social / video)
- `<workflow>/inputs/swipe/` — content they like (seo / social)
- `<workflow>/inputs/audience/` — the outreach list (outreach)
- `<workflow>/inputs/queue/` — always present; filled later by engine-loop

And point out `shared/insights.md` — the cross-workflow learnings file every loop pass reads and adds to. It starts empty; that's expected.

### 7. Keys

```bash
cp shared/.env.example shared/.env
```

Have **them** paste the keys in. Never ask a user to give you a key in chat, and never read `shared/.env` — you read `.env.example` for the names only. If a key is missing, name the variable and where to get it; don't work around it.

Which keys they need depends on the workflow — see `docs/preflight.md` §4. For `seo`, `social` and `outreach`, usually none.

### 8. Check

```bash
python3 <repo>/skills/engine-setup/scripts/doctor.py
```

Walk through anything red. Warnings are usually fine to leave. Doctor checks the canonical store, each agent mirror it can see, and `workflows/skills/` when a workspace is found.

### 9. Hand over

Tell them the one next thing to do — run their chosen content workflow and ship one piece. Not three. The loop needs real runs more than it needs breadth.

Then flag what comes right after the first published piece: **two schedulers** —
`engine-metrics-<their-workflow>` (one per workflow, on that channel's clock)
and `engine-weekly` (one for the workspace). Don't create them during setup —
there's nothing to measure yet — but say plainly that without them the numbers
never come back and every report reads "no runs measured". The full catalogue,
mandatory and optional, is
[`docs/scheduling.md`](../../docs/scheduling.md).

Both are **scheduled tasks in the agent itself** — Claude Code's scheduled
tasks, or the equivalent in whatever agent they use. They need a browser and
judgement, so an OS-level cron job can't do them. Creating one is a sentence
("create a daily scheduled task `engine-metrics-social` that…"), and the prompt has
to stand alone because each run starts with no memory of the conversation:
`engine-loop/references/scheduling.md`.

## Rules

- **Confirm before writing anywhere outside the workspace.** Cloning and installing skills touch their home directory
- **Never star, push or post without an explicit yes**
- **Never read `shared/.env`.** Names come from `.env.example`
- **Copy skills into `~/.agents/skills/`, then symlink out** to agent folders and
  the workspace — never leave the only copy inside an agent-specific directory
- **The clone is read-only.** Customised instructions go in `~/.agents/skills/`
  (everywhere) or in the workspace (one project). An edit in the clone is lost
  at the next `git pull` and never reaches the skills the agent loads — tell
  them this before they're tempted
- If they're not on Apple Silicon, say what will and won't work rather than pretending it's fine. The workspace scripts are plain stdlib Python and run anywhere; Linux is fully workable. On Windows, run the bash installer and symlinks under WSL — native Windows needs developer mode for symlinks and has no supported installer yet. Video rendering is slow on Intel Macs

## Going further

`references/advanced.md` — your own skills repo, Supabase instead of CSVs, object storage for media, cloud crons, Tailscale across machines. Read it when the user has been running this for a month, not on day one.

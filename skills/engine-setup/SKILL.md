---
name: engine-setup
description: Install gtm-engine and build the user's home. Clones the repo to ~/.gtm-engine, creates ~/gtm (brand, keys, assets, insights and engines.json), scaffolds the engine folders wherever the user wants them, copies selected skills into ~/.agents/skills/ then symlinks them into Claude/Codex/Cursor, interviews the user to fill in brand and channel config, and can run an optional doctor check. Use when the user says "run engine-setup", "set up gtm-engine", "install the growth engines", or points you at the gtm-engine repo for the first time.
---

# engine-setup

Gets someone from nothing to a working home.

Run it once per project. It is also re-runnable, and `doctor.py` is there as an
optional health check when something looks wrong — never a step to clear before
work can start.

## Read the onboarding script first

[`docs/onboarding.md`](../../docs/onboarding.md) in the repo is the script for
the conversation: what to warn about, what to offer, which question to ask and
in what order. Read it before you touch their disk. This file is the mechanics.

## What you're building

Three separate things, and keeping them separate is the point:

- **The clone** (`~/.gtm-engine`): the engines' logic. One per machine,
  updated by `git pull`. Nothing personal in it, nothing to gitignore in
  anyone's project.
- **The home** (`~/gtm`): their brand, accounts, keys, assets, insights, and
  `engines.json`. One per person. Never touched by an update.
- **The engines**: one self-contained folder per channel. These can live
  anywhere, and where they go is the one real question of setup.

```
~/.gtm-engine/               the clone (read-only, git pull)
~/gtm/                       the home
├── AGENTS.md  CLAUDE.md
├── engines.json             the registry: every engine and where it lives
├── shared/                  brand, channels, .env, assets, insights
├── published/
└── engines/                 engines kept in one place, named
                             engine-<type>-<project>/
~/.agents/skills/            the skills themselves (step 4)
~/Desktop/                   two symlinks, so neither is buried (step 5)
├── gtm     ->  ~/gtm
└── skills  ->  ~/.agents/skills
```

## Where the engines live

**The default is `~/gtm/engines/`, and you ask before using it.** Not a
required-choices screen: one question, with the answer already suggested.

> By default your engines go in `~/gtm/engines/`, next to everything they
> share. If you'd rather keep this project's engines with the project, I can
> put them in `engines/` here instead. Which do you want?

Both are good shapes, for different people:

- **`~/gtm/engines/`** (the default): everything growth-related in one place,
  one folder to back up, nothing added to any project repo. Name the folders
  `engine-<type>-<project>/` so it stays obvious which project each belongs
  to, which `scaffold.py --project <name>` does for you.
- **`<project>/engines/`**: the engines sit with the code they grow, so
  opening the project in Claude Code puts everything in reach. Recommend this
  when they have several products or brands. The folders are named after the
  type (`outreach/`, `seo/`), because the path already says which project it
  is.

Either way `~/gtm` still holds everything shared, and every engine is recorded
in `~/gtm/engines.json`.

Override the cwd without asking when it is a bad home for data: the home
directory itself, `~/Downloads`, a temp directory, or the clone. Say why in one
line and use `~/gtm/engines/`.

If `engines/` already exists in the project and is not ours (Rails keeps
mountable engines there), do not scaffold into it. Say what you found and use
`gtm-engines/`.

**Engine names are unique across every project**, because `engines.json` is
keyed on them. `scaffold.py` refuses to let a second engine take a name the
first one holds and tells you what to do about it.

**Whenever an engine folder moves, `engines.json` moves with it**
(`registry.py mv <name> <newpath>`, or `doctor.py --fix`). Nothing scans for
engines; that file is how every script, every report and the next agent finds
them. Write that rule into `AGENTS.md` **only if this user's engines end up in
more than one location**: with one location there is nothing to keep in sync.
[`docs/onboarding.md`](../../docs/onboarding.md) has the exact wording.

## Steps

Do these in order. Confirm each one before moving on — a wrong path here is annoying to unpick later.

**Before you scaffold there are exactly two questions, and both already have
their answer:** where the engines go (default: `~/gtm/engines/`) and which one
they'll *run* first (default: outreach, all four get scaffolded either way).
Both are yes-or-something-else. Everything else in step 1 is a statement, not a
choice. Don't present a user with a numbered list of "required choices" on
their first screen; ask, take the default, keep going.

### 1. Point them at the repo

Not a question, a statement, made once, before anything is installed:

> Everything we'll use is in the git repo at
> <https://github.com/benyki/gtm-engine>. Open it and save it if you like, and
> if you spot anything that could be better, leave a comment or raise an issue.

That's the whole ask. Don't gate the setup on it, don't turn it into a
required choice, and don't ask for a star as a favour. If *they* say they'd
like to star it and `gh` is authenticated: `gh repo star benyki/gtm-engine`.

### 2. Clone

**If they already ran the one-command installer** (`curl -fsSL
https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash`)
steps 2 to 4 are done: it clones to `~/.gtm-engine`, creates `~/gtm`, scaffolds
the engines and installs the skills. Check for `~/gtm/shared/` and
`~/gtm/engines.json`, confirm what's there, and pick up at step 5.

Otherwise:

```bash
git clone https://github.com/benyki/gtm-engine.git ~/.gtm-engine
```

**One clone per machine, at `~/.gtm-engine`.** It is logic, not data: it is
pulled for updates over months, it is the same for every project, and keeping
it out of any project means nothing to gitignore and one `git pull` however
many things they grow. If the directory already exists, `git -C ~/.gtm-engine
pull` instead. `--engine-dir` moves it if they insist; use whatever path you
picked for every later command.

### 3. Create the home, then the engines

Two writes, one command. The home (`~/gtm`) holds everything shared; the
engines are folders that can live anywhere and are recorded in
`~/gtm/engines.json`.

**Tell them about the home before creating it:**

> I'm going to create `~/gtm`. That's where everything shared between your
> engines lives: your brand voice, your accounts, your keys, your assets, and
> what previous runs taught. It's yours, and an update to the engine can never
> touch it.

**Then ask the one question that matters, where the engines go:**

> By default your engines go in `~/gtm/engines/`, next to everything they
> share. If you'd rather keep this project's engines with the project, I can
> create `engines/` here instead. Which do you prefer?

"The default" is a complete answer and the usual one. See *Where the engines
live* above for when to recommend the project shape, and for the cwds worth
overriding without asking.

**Which engine to run first**, not which to install; all four get scaffolded:

> You'll have all four engines: seo, social, video and outreach. I'd start by
> actually running **outreach**. Sound right?

**Default to yes.** Outreach is the fastest one to a real signal, drafts today
and replies this week, and it needs no keys and no site. Something else is a
fine answer: `seo`, `social`, `video`, or a custom name.

Then:

```bash
# the default: home + all four engines in ~/gtm/engines
python3 ~/.gtm-engine/skills/engine-setup/scripts/scaffold.py

# or, engines kept with the project they grow
python3 ~/.gtm-engine/skills/engine-setup/scripts/scaffold.py \
  --engine all --at ./engines --project acme
```

**Scaffold all four, run one.** The folders are cheap (an `engine.json`, an
empty `experiments.json`, a `runs/index.csv` header) and having them there
means switching channel later is opening a folder, not re-running setup. What
they should *not* do is start four at once: the loop learns from runs, and four
half-run engines produce no verdict anywhere. So configure the goal, metric and
templates for **the one they named**, and leave the others as scaffolding.

Other shapes, when they ask for them:

- `--engine seo,outreach`: only those folders
- `--engine engine-outreach-investors:outreach`: a **second engine of an
  existing type**, with its own goal, experiments and templates. Suggest this
  freely: two outreach engines for two audiences, three video engines for
  three formats is a normal shape, not an edge case. (Copying an existing
  folder works too, but empty its `runs/`, `reports/` and `crm.csv`; history
  belongs to the original, and remember to register the copy.)
- `--engine newsletter`: a **custom engine**. `engine-loop` runs it through
  the same traces, you supply the craft. Enable its channel(s) in
  `shared/channels.json` and write its experiments as part of this setup
- `--engine none`: the home only
- Delete a default folder **if they ask**, it's theirs. Don't propose it: an
  unrun folder costs a few empty files, and deleting it turns "try video next
  month" back into a setup task. Deleting one means removing its entry from
  `engines.json` too

Every engine created this way is registered automatically. An engine folder
made by hand is not: `registry.py add <name> <path>` or `doctor.py --fix`.

Each engine's `engine.json` carries its `name`, `type` (which skill runs it),
`home`, `goal` and `primary_metric`. `site/` is never pre-created.

The scaffold also writes **`AGENTS.md`** at the home root (what to read first,
that every piece made gets a run row, the registry hygiene rule, the boundaries
that don't move, and ending every message with the possible next steps) plus a
**`CLAUDE.md`** that points at it. An engine that lives away from the home gets
its own short `AGENTS.md` too, pointing back at `~/gtm`, because an agent
opening that project would otherwise never see the house rules. All of them are
the user's to edit; a re-run never overwrites them.

Nothing is ever overwritten: re-running fills gaps only, and `--merge` is the
explicit form.

**One home per person, one brand per home.** Two products that genuinely need
different voices need either a second home (`--home ~/gtm-b2b`, or `GTM_HOME`)
or a per-engine override of the brand file. Say which one you set up.

### 4. Install the skills

Path chain — real files in the canonical store; everything else is a symlink:

```
~/.gtm-engine/skills/<name>
        ↓ COPY
~/.agents/skills/<name>          ← canonical (real files)
        ↓ symlink each
~/.claude/skills/<name>
~/.codex/skills/<name>
~/.cursor/skills/<name>
        ↓ symlink whole folder
~/gtm/skills  →  ~/.agents/skills
```

**`~/.agents/skills/` is the only place skill files live.** Agent folders and the
home get symlinks. Re-run the installer after `git pull` in the engine repo
to refresh the copies.

| Directory | What happens |
|---|---|
| `~/.agents/skills/` | **copy** of each selected `engine-*` skill |
| `~/.claude/skills/` | symlink per skill (if `~/.claude` exists) |
| `~/.codex/skills/` | symlink per skill (if `~/.codex` exists) |
| `~/.cursor/skills/` | symlink per skill (if `~/.cursor` exists) |
| `~/gtm/skills` | one symlink to the whole `~/.agents/skills` folder |

Other agents: set `GTM_AGENT_DIRS` (colon-separated skill dirs). `doctor.py`
honours the same variable.

Run the installer for the **same engines**. With all four scaffolded that's
**all six skills** — `engine-setup`, `engine-loop`, `engine-seo`,
`engine-social`, `engine-video`, `engine-outreach`. (`engine-setup` and
`engine-loop` are always installed; dependencies come along too — `engine-social`
reads `engine-seo`'s subject-finding and browser-research references, so
choosing social installs seo either way.)

```bash
~/.gtm-engine/skills/engine-setup/scripts/install_skills.sh --home ~/gtm
```

`--home` defaults to `~/gtm`, so a bare `install_skills.sh` is the usual call.
With a home you can omit `--engine`: it reads `engines.json`, takes each
registered engine's type, and installs the matching skills. That's the form to
use, because the registry already says what is needed and it stays right when
they add an engine later.

What it does:

1. **Create** `~/.agents/skills/` if missing
2. **Copy** the selected skills from the clone into `~/.agents/skills/<name>`
3. **Symlink** `<home>/skills` → `~/.agents/skills` (whole folder)
4. **Symlink** each skill into Claude / Codex / Cursor skill dirs when that
   agent home exists (plus `GTM_AGENT_DIRS`)
5. **Idempotent** — re-copy refreshes content; wrong links are relinked; a real
   directory collision in an agent folder is warned and skipped

If the home doesn't exist yet it still does the canonical copy and the agent
mirrors; re-run once `~/gtm` is there.

### 5. Put shortcuts on the Desktop

Both folders are now buried a few levels deep and both get opened constantly —
the home to read runs and drop inputs in, the skills folder to tweak an
engine. Symlink them where they can't be missed:

```bash
ln -s ~/gtm ~/Desktop/gtm
ln -s ~/.agents/skills ~/Desktop/skills
```

An engine that lives in a project is reachable from that project already, so it
doesn't need a shortcut of its own.

These are links, not copies — the files stay where they are, and dropping an
asset into `~/Desktop/gtm/shared/assets/` lands it in the real home.

If either name is already taken, look at what's there before touching it, and
either pick a different name or confirm the replacement with them.

### 6. Fill in the config

This is the part that decides whether the output is any good, so don't rush it into a single question. Interview them, then write the files. Global config is deliberately minimal — `shared/` holds only what every engine uses (brand, accounts, keys, assets, docs, insights); everything else lives in each engine's own folder.

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

**`shared/channels.json`** — the account list, and nothing else global. An open set: add any channel they actually use (newsletter, threads, reddit, …). Optional per-channel keys the scripts honour: `primary_metric` (overrides an engine's own for runs on that channel) and `metric_delay_hours` where the 72h default is wrong (weeks for blog/Search Console, a day or two for email).

**Each engine's `engine.json`** — per engine, ask for its **goal** (one sentence: what this engine exists to produce) and its **`primary_metric`**. The metric is what the loop optimises for that engine, so make them name a real one: replies, signups, demos, clicks. "Engagement" is not a metric. Two engines of the same type with different goals get different metrics — that's the point of having two.

**Each engine's `sources.json`** — where that engine's ideas come from. The seo default is Reddit, which needs nothing. If they have competitor URLs, put them in. Only wire up Ahrefs or Semrush if they already pay for it.

**Each engine's `experiments.json`** — **leave these paused. Setting up an A/B test is not part of the first setup.**

They ship `"status": "paused"` on purpose, and the right move on day one is to leave them that way. The first job is one template the user is actually happy with: ship it, look at the numbers, change it, ship again. `assign_arm.py` handles this without any config — with no live experiment it returns `use_template`, and every run still lands in `runs/index.csv` with the template it used, so no history is lost. An experiment started before the format is settled freezes a template that still needs work, and at two posts a week it collects noise for two months before it says anything.

Tell them that plainly, and tell them what changes it: once they have a format they'd ship without editing, and roughly 5–10 pieces with numbers on them, that's when a variable is worth testing. `engine-loop/references/ab-testing.md` → R0 is the checklist, and the loop will raise it at the right moment.

If they push back and want a test running from day one, it's their call — then rewrite the arms in their terms before flipping `status` to `live`. The shipped arms are **examples of shape, not hypotheses for their business**: a B2C app has no use for a "partner revenue split" arm, and if it ships live the first run gets assigned to it. Keep the structure (two arms, one variable, a stated hypothesis each), size `min_runs_per_arm` to their real volume, and note that several live experiments can coexist in one engine only when each is scoped to its own `channel` — otherwise the first one wins and the script warns.

Then ask them to drop material into the inputs:
- `shared/assets/` — logo, fonts, b-roll, anything **any** engine might reuse
- `<engine>/inputs/best/` — their own best-performing pieces (seo / social / video)
- `<engine>/inputs/swipe/` — content they like (seo / social)
- `<engine>/inputs/audience/` — the outreach list (outreach)
- `<engine>/inputs/queue/` — always present; filled later by engine-loop

And point out `shared/insights.md` — the cross-engine learnings file every loop pass reads and adds to. It starts empty; that's expected.

### 7. Keys

```bash
cp shared/.env.example shared/.env
```

Have **them** paste the keys in. Never ask a user to give you a key in chat, and never read `shared/.env` — you read `.env.example` for the names only. If a key is missing, name the variable and where to get it; don't work around it.

Which keys they need depends on the engine — see `docs/preflight.md` §4. For `seo`, `social` and `outreach`, usually none.

### 8. Check — optional

**`doctor.py` is a helper, not a gate.** Nothing depends on it and nothing in
the engine calls it: it's a second pair of eyes for when something looks off, or
when a user wants reassurance that the install landed. If the scaffold and the
installer both printed what you expected, skip it and go to step 9 — running it
just to have a green tick teaches the user that setup needs a certificate.

Worth running when: an earlier step printed something odd, they're on Windows or
a locked-down machine, an engine can't find its home later, or they ask.

```bash
python3 ~/.gtm-engine/skills/engine-setup/scripts/doctor.py
```

**`✗` is genuinely broken; `!` is information, not a to-do list** — don't hand
the user a list of warnings to clear before they can start. A fresh outreach
home with no keys and no runs is `All clear` by design. It checks the
canonical store, each agent mirror it can see, and `engines/skills/` when a
home is found. It changes nothing — it only looks.

### 9. Hand over

Tell them the one next thing to do — run their chosen content engine and ship one piece. Not three. The loop needs real runs more than it needs breadth.

**Explain how a piece gets recorded, once, here** — it's the one mechanic that
everything downstream depends on, and it's invisible until it's missing:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --engine <name> --channel <channel>
```

One run per artifact, logged before it ships, with the template it used. A piece
that isn't in `runs/index.csv` never gets a number, never joins an A/B verdict,
and is invisible to the weekly report. The publish moment is recorded with
`runlog.py publish`, and the number with `runlog.py metric` once the channel's
window has passed.

Say it as *what the engine does for them*, not as a chore they have to
remember — each engine skill runs these commands as part of its own steps, so
nobody types them by hand. What the user needs to take away is why an unlogged
piece is invisible to the loop, because that's what makes a report read "no runs
measured" a month later.

Then flag what comes right after the first published piece: **two schedulers** —
`engine-metrics-<their-engine>` (one per engine, on that channel's clock)
and `engine-weekly` (one for the home). Don't create them during setup —
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

- **Confirm before writing anywhere outside the home.** Cloning and installing skills touch their home directory
- **Never star, push or post without an explicit yes**
- **Never read `shared/.env`.** Names come from `.env.example`
- **Copy skills into `~/.agents/skills/`, then symlink out** to agent folders and
  the home — never leave the only copy inside an agent-specific directory
- **The clone is read-only.** Customised instructions go in `~/.agents/skills/`
  (everywhere) or in the home (one project). An edit in the clone is lost
  at the next `git pull` and never reaches the skills the agent loads — tell
  them this before they're tempted
- If they're not on Apple Silicon, say what will and won't work rather than pretending it's fine. The home scripts are plain stdlib Python and run anywhere; Linux is fully workable. On Windows, run the bash installer and symlinks under WSL — native Windows needs developer mode for symlinks and has no supported installer yet. Video rendering is slow on Intel Macs

## Going further

`references/advanced.md` — your own skills repo, Supabase instead of CSVs, object storage for media, cloud crons, Tailscale across machines. Read it when the user has been running this for a month, not on day one.

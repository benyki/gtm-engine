# gtm-engine

Growth engines for coding agents: they write content, send personalised outreach, and keep score. Ships with seo, social, video and outreach; add your own engines freely, and more will land here over time.

Built for indie devs and early-stage startups: you have a product, no users, and no growth team.

Every run is written to disk with the template version it used. When the numbers come back, a weekly job scores the versions against each other, retires the loser, and writes a new one to test against the winner.

---

## Getting started: read the docs

**Your agent reads these, not you.** Point it at the repo and it works through
them; they're written for an agent rather than for a human following steps.

| Doc | Why |
|---|---|
| [`docs/onboarding.md`](docs/onboarding.md) | **Start here.** What your agent walks you through: machine check, `~/gtm`, the engines, your brand |
| [`docs/useful-links.md`](docs/useful-links.md) | Every download and signup link, plus which key maps to which env var |
| [`docs/home.md`](docs/home.md) | Where your brand, runs, and numbers live, and what never mixes with the repo |

Later, when you need it:

| Doc | Why |
|---|---|
| [`docs/changelog.md`](docs/changelog.md) | What changed, and what an agent working with an older layout has to know |
| [`docs/scheduling.md`](docs/scheduling.md) | Every scheduler you should have: one metric job per engine, one weekly job for the home, and the optional content jobs |
| [`skills/engine-video/references/posting-options.md`](skills/engine-video/references/posting-options.md) | Video posting: manual, Upload Post, or Buffer |
| [`docs/additional-skills.md`](docs/additional-skills.md) | Toolbox skills from [`benyki/skills`](https://github.com/benyki/skills): download into `~/.agents/skills`, symlink to Claude / Codex / Cursor |
| [`docs/stay-on-top-content.md`](docs/stay-on-top-content.md) | Channels and podcasts worth following, plus the seed list for `engine-social`'s RSS subjects |
| [`docs/bootcamp.md`](docs/bootcamp.md) | Running this as a workshop: what to ask participants for beforehand, the session shape, guiding beginners |

Then install (below) and tell your agent: `run engine-setup`.

---

## The engines

| | What it does |
|---|---|
| **`engine-setup`** | Installs everything and builds your home. Run once. |
| **`engine-seo`** | Finds the questions your buyers ask, writes the article that answers them. No website? It builds one |
| **`engine-social`** | LinkedIn, X, Bluesky and other text social posts in your voice |
| **`engine-video`** | Short-form vertical video: script, voiceover, footage, render |
| **`engine-outreach`** | Researches real people and writes personalised emails as **drafts**, never sends |

**`engine-loop` is not a fifth engine.** It is the framework that sits under the
ones above (and any custom engine you add): it makes them learn, grow, and
compound over time: metrics in, A/B verdicts out, weekly report, next week's
plan.

**Install gives you all six skills and all four engine folders.** Everything
is there from the first command, so switching channel later is a decision, not
an install step. *Running* them is the part to take one at a time: start with
one, outreach unless you have a reason to start elsewhere, because the loop
only has something to say once there are runs on the board.

---

## Install

**One command.** It works from anywhere; where you run it only matters if you
want your engines kept with a project.

```bash
curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
```

Three things land, and keeping them apart is the point:

| | What it is | Who owns it |
|---|---|---|
| `~/.gtm-engine` | the clone: the engines' logic | the repo. `git pull` overwrites it |
| `~/gtm` | your home: brand, accounts, keys, assets, insights, and `engines.json` | you. Never touched by an update |
| `~/gtm/engines/…` | one self-contained folder per engine | you. Can live anywhere, see below |

All six skills get linked into whichever agents you have (Claude Code, Codex,
Cursor). Then tell your agent: `run engine-setup`, which fills in your brand
config and confirms which engine you're starting with.

**Engines can live anywhere.** The default is `~/gtm/engines/`: everything
growth-related in one place, nothing added to any project repo. If you'd rather
keep a project's engines with the project, run it from that project with:

```bash
curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash -s -- --at ./engines --project acme
```

Either way `~/gtm` stays the one home for everything shared, and every engine
is recorded in `~/gtm/engines.json`. That file is how anything finds an engine,
so if you ever move a folder, update it in the same breath (`registry.py mv`,
or `doctor.py --fix`).

**You get everything:** `engine-setup`, `engine-loop`, `engine-seo`,
`engine-social`, `engine-video` and `engine-outreach` installed, plus a
scaffolded folder for each of the four content engines. Nothing is held back
for a second command; picking a channel later means opening a folder that's
already there. An unused engine folder is a few empty files; delete any you're
sure you'll never run (and remove its line from `engines.json`).

Want a narrower install, one folder instead of four, or a name of your own for
a custom engine (the loop treats it like the built-ins; you supply the
templates):

```bash
curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash -s -- --engine outreach
```

The skills are installed to match the folders you asked for, so a narrowed
install gives you fewer skills too.

`--home ~/growth` puts the shared home somewhere other than `~/gtm`.
`--engine-dir` moves the clone off `~/.gtm-engine`. Re-run it any time: it
pulls, adds whatever engine you name, and never overwrites what you already
have. [`install.sh`](install.sh) is ~150 readable lines, worth a look before
you pipe anything into `bash`, here or anywhere else.

**Prefer to have the agent do it?** Paste this into Claude Code or Codex:

```
Read https://github.com/benyki/gtm-engine, follow docs/onboarding.md and
run engine-setup.
Install everything, all four engines and all six skills, then help me run
the outreach one first unless I say otherwise.
Once ~/gtm exists, follow its AGENTS.md in every session.
```

**Or do the three steps yourself:**

```bash
git clone https://github.com/benyki/gtm-engine.git ~/.gtm-engine
```

```bash
python3 ~/.gtm-engine/skills/engine-setup/scripts/scaffold.py --engine all
```

```bash
~/.gtm-engine/skills/engine-setup/scripts/install_skills.sh --home ~/gtm
```

With no `--engine`, `install_skills.sh` reads `~/gtm/engines.json` and installs
the skills your registered engines call for, all six here. Add
`--at ./engines --project <name>` to the scaffold command to put the engine
folders in the project you're standing in.

**Already running the old layout** (a `<project>/workflows/` folder with
`shared/` and the workflow folders inside it)? It still works. When you want to
move to `~/gtm`:

```bash
python3 ~/.gtm-engine/skills/engine-setup/scripts/migrate_v1.py <project>/workflows
```

That prints a plan and writes nothing; add `--apply` when it looks right. See
[`docs/changelog.md`](docs/changelog.md).

---

## How it's put together

> **The repo is logic. Your home is data. They never mix.**

| | This repo (`~/.gtm-engine`) | Your home (`~/gtm`) and your engines |
|---|---|---|
| Holds | the engines (`skills/`), the scaffold templates (`template/`), docs | your brand, inputs, runs, numbers, reports, and the `AGENTS.md` every agent follows |
| Changes | when you `git pull` | every time you run something |
| Belongs to | this project | you, keep it in your own private repo |

Skills are **copied** into `~/.agents/skills/`, then symlinked into each
agent's skills folder and as one `~/gtm/skills` link to `~/.agents/skills`.
Re-run `install_skills.sh` after `git pull` to refresh the copies. Nothing you
own lives in this repo, so an update can never clobber your data.

**Want to customise the instructions? Do it in `~/.agents/skills/` or in your
home, never in this clone.** Edit the running skill for a change that applies
everywhere, or your home (`shared/brand.md`, an engine's templates and
`engine.json`) for a change scoped to one project. Edits made in the clone are
overwritten by the next `git pull` and never reach the skills your agent
actually loads.

Full layout: [`docs/home.md`](docs/home.md). One `shared/` folder in `~/gtm`
(brand, accounts, keys, assets, cross-engine insights) plus one self-contained
folder per engine (own experiments, templates, runs, reports; copy a folder to
run a second outreach or video engine with a different goal). Each engine keeps
its own spine at `<engine>/runs/index.csv`: one row per thing it ever made,
with the arm it used and the number it earned.

---

## The loop (`engine-loop`)

Not a separate growth channel. It is the framework that makes your existing
engines (seo, social, video, outreach, or a custom one) learn, grow, and
compound. Four jobs you schedule once: metric fetching **per engine**, on that
channel's clock; the rest once for the whole home
([`docs/scheduling.md`](docs/scheduling.md)):

| Job | Cadence | What happens |
|---|---|---|
| `due_metrics` → record | daily | Lists published runs **past their channel's metric window** (72h default) with no number yet |
| `score_arms` + challenge | weekly | Promotes a winner, retires the loser, writes a fresh challenger |
| `generate-inputs` | weekly | Queues next week's ideas from what performed |
| `render_report` | weekly | Six sections, ending in a config change you approve or reject |

Nothing auto-sends and nothing auto-adopts. You approve challengers and config changes.

Detail: [`skills/engine-loop/references/ab-testing.md`](skills/engine-loop/references/ab-testing.md). Scheduling: [`skills/engine-loop/references/scheduling.md`](skills/engine-loop/references/scheduling.md).

---

## When you outgrow it

Each engine ships a `references/advanced.md` with the specific next step, not aspirational architecture:

- **Setup:** your own skills repo, Supabase, object storage, cloud crons, Tailscale
- **Outreach:** Cloudflare email routing and Resend when Gmail drafts stop scaling
- **SEO:** Astro or Next.js static site from everything you've generated
- **Video:** dedicated phone and mobilerun for platforms APIs won't post to
- **Loop:** Telegram or WhatsApp digest so template decisions take twenty seconds

---

## Limits

- It writes drafts; you decide what's good. Telling it why you rejected something is most of the work
- A site of AI-generated pages ranks like one; `engine-seo` mines real questions, but it isn't a shortcut
- The loop needs about three weeks of runs before its verdicts mean anything
- It won't fix a product nobody wants

---

## Updates

Check this repo regularly for upstream changes. When there are some, **pull**.
Do not edit files in the clone to "improve" the engine.

- **This repo** is updated only by `git pull` from remote, so you pick up new
  insights and engine improvements. Treat the clone as read-only for day-to-day
  work.
- **Your running skills** live in `~/.agents/skills/`. If you need to tweak an
  engine, edit it there, not in the clone.
- After a pull, re-run `install_skills.sh` only when you want those upstream
  copies refreshed into `~/.agents/skills/`.
- When a skill on your machine conflicts with a newer one from the repo, **you**
  decide what to keep. Prefer leaving an engine that is already performing
  alone. Agents and docs may *suggest* canonical updates; they must never push
  or force-overwrite the skills you are actively running.
- [`docs/changelog.md`](docs/changelog.md) says what changed and what an agent
  running the older layout has to do about it, which is usually nothing.

---

`engine-setup` writes an [`AGENTS.md`](template/home/AGENTS.md) at the root of
your home (plus a `CLAUDE.md` pointing at it): the house rules every agent
working in there follows, and yours to extend.

MIT licensed. Issues and PRs welcome.

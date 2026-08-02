# gtm-engine


Growth workflows for coding agents: they write content, send personalised outreach, and keep score. Ships with seo, social, video and outreach; add your own workflows freely, and more will land here over time.

Built for indie devs and early-stage startups: you have a product, no users, and no growth team.

Every run is written to disk with the template version it used. When the numbers come back, a weekly job scores the versions against each other, retires the loser, and writes a new one to test against the winner.

---

## Getting started: read the docs

**Start with the docs, not this README.** Before you install anything, work through these:

| Doc | Why |
|---|---|
| [`docs/preflight.md`](docs/preflight.md) | **Start here.** The checklist: machine check + what each workflow needs, in order |
| [`docs/useful-links.md`](docs/useful-links.md) | Every download and signup link, plus which key maps to which env var |
| [`docs/workspace.md`](docs/workspace.md) | Where your brand, runs, and numbers live, and what never mixes with the repo |

Later, when you need it:

| Doc | Why |
|---|---|
| [`docs/scheduling.md`](docs/scheduling.md) | Every scheduler you should have: one metric job per workflow, one weekly job for the workspace, and the optional content jobs |
| [`skills/engine-video/references/posting-options.md`](skills/engine-video/references/posting-options.md) | Video posting: manual, Upload Post, or Buffer |
| [`docs/additional-skills.md`](docs/additional-skills.md) | Toolbox skills from [`benyki/skills`](https://github.com/benyki/skills): download into `~/.agents/skills`, symlink to Claude / Codex / Cursor |
| [`docs/stay-on-top-content.md`](docs/stay-on-top-content.md) | Channels and podcasts worth following, plus the seed list for `engine-social`'s RSS subjects |

Then install (below) and tell your agent: `run engine-setup`.

---

## The workflows

| | What it does |
|---|---|
| **`engine-setup`** | Installs everything and builds your workspace. Run once. |
| **`engine-seo`** | Finds the questions your buyers ask, writes the article that answers them. No website? It builds one |
| **`engine-social`** | LinkedIn, X, Bluesky and other text social posts in your voice |
| **`engine-video`** | Short-form vertical video: script, voiceover, footage, render |
| **`engine-outreach`** | Researches real people and writes personalised emails as **drafts**, never sends |

**`engine-loop` is not a fifth workflow.** It is the framework that sits under the
ones above (and any custom workflow you add): it makes them learn, grow, and
compound over time: metrics in, A/B verdicts out, weekly report, next week's
plan.

**Install gives you all six skills and all four workflow folders.** Everything
is there from the first command, so switching channel later is a decision, not
an install step. *Running* them is the part to take one at a time: start with
one, outreach unless you have a reason to start elsewhere, because the loop
only has something to say once there are runs on the board.

---

## Install

**One command.** `cd` to the project you want to grow first (a folder under
`~/code/`, or an existing repo you already work in) and run it there:

```bash
curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
```

Everything lands **where you are**: `gtm-engine/` (the clone) and `workflows/`
(your workspace) side by side in that folder, and **all six skills** get linked
into whichever agents you have (Claude Code, Codex, Cursor). If the folder is a
git repo, `gtm-engine/` is added to your `.gitignore`; it's the engine, not your
code. Then tell your agent: `run engine-setup`, which fills in your brand config
and confirms which workflow you're starting with.

**You get everything:** `engine-setup`, `engine-loop`, `engine-seo`,
`engine-social`, `engine-video` and `engine-outreach` installed, plus a
scaffolded folder for each of the four content workflows. Nothing is held back
for a second command; picking a channel later means opening a folder that's
already there. An unused workflow folder is a few empty files; delete any you're
sure you'll never run.

Want a narrower workspace, one folder instead of four, or a name of your own
for a custom workflow (the loop treats it like the built-ins; you supply the
templates):

```bash
curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash -s -- --workflow outreach
```

The skills are installed to match the folders you asked for, so a narrowed
install gives you fewer skills too.

`--name <folder>` calls the workspace something other than `workflows`.
`--engine-dir ~/code/gtm-engine` keeps the clone outside the project, worth it
once you run this in several projects, since otherwise each one has its own
clone to pull. Re-run it any time: it pulls, adds whatever workflow you name,
and never overwrites what you already have. [`install.sh`](install.sh) is ~140
readable lines, worth a look before you pipe anything into `bash`, here or
anywhere else.

**Prefer to have the agent do it?** Paste this into Claude Code or Codex:

```
Read https://github.com/benyki/gtm-engine and follow docs/preflight.md.
When that passes, follow the setup instructions in the README and run
engine-setup. Install everything, all four workflows and all six skills,
then help me run the outreach one first unless I say otherwise.
Once the workspace exists, follow its AGENTS.md in every session.
```

**Or do the three steps yourself**, from the project you want to grow (a folder
you keep, not Downloads):

```bash
git clone https://github.com/benyki/gtm-engine.git ./gtm-engine
```

```bash
python3 ./gtm-engine/skills/engine-setup/scripts/scaffold_workspace.py . --workflow all
```

```bash
./gtm-engine/skills/engine-setup/scripts/install_skills.sh --workspace ./workflows
```

With no `--workflow`, `install_skills.sh` reads the workspace and installs the
skills its folders call for, all six here. Pass `--workflow outreach` to both
commands instead if you want the narrow version.

That leaves `gtm-engine/` and `workflows/` side by side. Add `gtm-engine/` to
your `.gitignore` if the folder is a repo. Cloning to `~/code/gtm-engine`
instead works exactly the same; swap the path in the last two commands. Keep one
full workspace per project rather than sharing one between them, and a Desktop
symlink to `workflows/` is worth the ten seconds.

---

## How it's put together

> **The repo is logic. Your workspace is data. They never mix.**

| | This repo (wherever you cloned it) | Your workspace (`<your-project>/workflows/`) |
|---|---|---|
| Holds | the workflows (`skills/`), the workspace template (`workspace/`), docs | your brand, inputs, runs, numbers, reports, and the `AGENTS.md` every agent follows |
| Changes | when you `git pull` | every time you run something |
| Belongs to | this project | you, keep it in your own private repo |

Workflows are **copied** into `~/.agents/skills/`, then symlinked into each
agent's skills folder and as one `workflows/skills` → `~/.agents/skills` link.
Re-run `install_skills.sh` after `git pull` to refresh the copies. Nothing you
own lives in this repo, so an update can never clobber your data.

**Want to customise the instructions? Do it in `~/.agents/skills/` or in your
workflows, never in this clone.** Edit the running skill for a change that
applies everywhere, or your workspace (`shared/brand.md`, a workflow's
templates and `workflow.json`) for a change scoped to one project. Edits made
in the clone are overwritten by the next `git pull` and never reach the skills
your agent actually loads.

Full layout: [`docs/workspace.md`](docs/workspace.md). The workspace is one self-contained folder per workflow (own experiments, templates, runs, reports; copy a folder to run a second outreach or video workflow with a different goal) plus one `shared/` folder (brand, accounts, keys, assets, cross-workflow insights). Each workflow keeps its own spine at `<workflow>/runs/index.csv`: one row per thing it ever made, with the arm it used and the number it earned.

---

## The loop (`engine-loop`)

Not a separate growth channel. It is the framework that makes your existing workflows
(seo, social, video, outreach, or a custom one) learn, grow, and compound.
Four jobs you schedule once: metric fetching **per workflow**, on that
channel's clock; the rest once for the whole workspace
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

Each workflow ships a `references/advanced.md` with the specific next step, not aspirational architecture:

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
Do not edit files in the clone to “improve” the engine.

- **This repo** is updated only by `git pull` from remote, so you pick up new
  insights and workflow improvements. Treat the clone as read-only for day-to-day
  work.
- **Your running skills** live in `~/.agents/skills/`. If you need to tweak a
  workflow, edit it there, not in the clone.
- After a pull, re-run `install_skills.sh` only when you want those upstream
  copies refreshed into `~/.agents/skills/`.
- When a skill on your machine conflicts with a newer one from the repo, **you**
  decide what to keep. Prefer leaving a workflow that is already performing
  alone. Agents and docs may *suggest* canonical updates; they must never push
  or force-overwrite the skills you are actively running.

---

`engine-setup` writes an [`AGENTS.md`](workspace/AGENTS.md) at the root of your
workspace (plus a `CLAUDE.md` pointing at it): the house rules every agent
working in there follows, and yours to extend.

MIT licensed. Issues and PRs welcome.

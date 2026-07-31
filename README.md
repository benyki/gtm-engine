# gtm-engine


Growth workflows for coding agents — they write content, send personalised outreach, and keep score. Ships with seo, social, video and outreach; add your own workflows freely, and more will land here over time.

Built for indie devs and early-stage startups: you have a product, no users, and no growth team.

Every run is written to disk with the template version it used. When the numbers come back, a weekly job scores the versions against each other, retires the loser, and writes a new one to test against the winner.

---

## Getting started — read the docs

**Start with the docs, not this README.** Before you install anything, work through these:

| Doc | Why |
|---|---|
| [`docs/preflight.md`](docs/preflight.md) | **Pre-workshop section** — using this repo in a workshop? This is the checklist: machine check + what each workflow needs, in order |
| [`docs/useful-links.md`](docs/useful-links.md) | Every download and signup link, plus which key maps to which env var |
| [`docs/workspace.md`](docs/workspace.md) | Where your brand, runs, and numbers live — and what never mixes with the repo |

Later, when you need it:

| Doc | Why |
|---|---|
| [`skills/engine-video/references/posting-options.md`](skills/engine-video/references/posting-options.md) | Video posting: manual, Upload Post, or Buffer |
| [`docs/additional-skills.md`](docs/additional-skills.md) | Toolbox skills from [`benyki/skills`](https://github.com/benyki/skills) — download into `~/.agents/skills`, symlink to Claude / Codex / Cursor |

Then install (below) and tell your agent: `run engine-setup`.

---

## The workflows

| | What it does |
|---|---|
| **`engine-setup`** | Installs everything and builds your workspace. Run once. |
| **`engine-seo`** | Finds the questions your buyers ask, writes the article that answers them. No website? It builds one |
| **`engine-social`** | LinkedIn, X, Bluesky and other text social posts in your voice |
| **`engine-video`** | Short-form vertical video: script, voiceover, footage, render |
| **`engine-outreach`** | Researches real people and writes personalised emails — as **drafts**, never sends |

**`engine-loop` is not a fifth workflow.** It is the framework that sits under the
ones above (and any custom workflow you add): it makes them learn, grow, and
compound over time — metrics in, A/B verdicts out, weekly report, next week's
plan. Pick one content workflow to start; the loop only has something to say
once there are runs on the board.

---

## Install

Paste this into Claude Code or Codex:

```
Read https://github.com/benyki/gtm-engine and follow docs/preflight.md.
When that passes, pick a workflow, follow the setup instructions in the README,
and run engine-setup.
```

Or do it yourself:

Pick a durable location first — Desktop, or a personal folder you don't clean out
often (not Downloads). Then:

```bash
git clone https://github.com/benyki/gtm-engine.git ~/Desktop/gtm-engine   # or your path
python3 ~/Desktop/gtm-engine/skills/engine-setup/scripts/scaffold_workspace.py . --workflow seo
~/Desktop/gtm-engine/skills/engine-setup/scripts/install_skills.sh --workspace ./workflows --workflow seo
```

Replace `~/Desktop/gtm-engine` with wherever you cloned. Replace `seo` with
`social`, `video`, `outreach`, a comma list, `all` — or any name of your own
for a custom workflow (the loop treats it like the built-ins; you supply the
templates).

Then tell your agent: `run engine-setup` — it fills in your brand config, picks your workflow, and runs the checks.

---

## How it's put together

> **The repo is logic. Your workspace is data. They never mix.**

| | This repo (wherever you cloned it) | Your workspace (`<your-project>/workflows/`) |
|---|---|---|
| Holds | the workflows (`skills/`), the workspace template (`workspace/`), docs | your brand, inputs, runs, numbers, reports |
| Changes | when you `git pull` | every time you run something |
| Belongs to | this project | you — keep it in your own private repo |

Workflows are **copied** into `~/.agents/skills/`, then symlinked into each
agent's skills folder and as one `workflows/skills` → `~/.agents/skills` link.
Re-run `install_skills.sh` after `git pull` to refresh the copies. Nothing you
own lives in this repo, so an update can never clobber your data.

Full layout: [`docs/workspace.md`](docs/workspace.md). The workspace is one self-contained folder per workflow (own experiments, templates, runs, reports — copy a folder to run a second outreach or video workflow with a different goal) plus one `shared/` folder (brand, accounts, keys, assets, cross-workflow insights). Each workflow keeps its own spine at `<workflow>/runs/index.csv` — one row per thing it ever made, with the arm it used and the number it earned.

---

## The loop (`engine-loop`)

Not a separate growth channel — the framework that makes your existing workflows
(seo, social, video, outreach, or a custom one) learn, grow, and compound.
Four jobs you schedule once:

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

Each workflow ships a `references/advanced.md` — the specific next step, not aspirational architecture:

- **Setup** — your own skills repo, Supabase, object storage, cloud crons, Tailscale
- **Outreach** — Cloudflare email routing and Resend when Gmail drafts stop scaling
- **SEO** — Astro or Next.js static site from everything you've generated
- **Video** — dedicated phone and mobilerun for platforms APIs won't post to
- **Loop** — Telegram or WhatsApp digest so template decisions take twenty seconds

---

## Limits

- It writes drafts; you decide what's good. Telling it why you rejected something is most of the work
- A site of AI-generated pages ranks like one — `engine-seo` mines real questions, but it isn't a shortcut
- The loop needs about three weeks of runs before its verdicts mean anything
- It won't fix a product nobody wants

---

## Updates

Check this repo regularly for upstream changes. When there are some, **pull** —
do not edit files in the clone to “improve” the engine.

- **This repo** is updated only by `git pull` from remote, so you pick up new
  insights and workflow improvements. Treat the clone as read-only for day-to-day
  work.
- **Your running skills** live in `~/.agents/skills/`. If you need to tweak a
  workflow, edit it there — not in the clone.
- After a pull, re-run `install_skills.sh` only when you want those upstream
  copies refreshed into `~/.agents/skills/`.
- When a skill on your machine conflicts with a newer one from the repo, **you**
  decide what to keep. Prefer leaving a workflow that is already performing
  alone. Agents and docs may *suggest* canonical updates; they must never push
  or force-overwrite the skills you are actively running.

MIT licensed. Issues and PRs welcome.

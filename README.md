# gtm-engine

Six workflows for Claude Code or Codex that write content, send personalised outreach, and keep score.

It's built for indie devs and early-stage startups: you have a product, no users, and no growth team.

Every run is written to disk with the template version it used. When the numbers come back, a weekly job scores the versions against each other, retires the one that lost, and writes a new one to test against the winner. So the system has a record of what worked and uses it.

---

## The workflows

| Workflow | What it does |
|---|---|
| **`engine-setup`** | Installs everything and builds your workspace. Run once. |
| **`engine-seo`** | Finds the questions your buyers actually ask, writes the article that answers them. No website? It builds one — Astro, your markdown, deployed on push |
| **`engine-linkedin`** | LinkedIn and X posts in your voice, learned from your own best work |
| **`engine-video`** | Short-form vertical video: script, voiceover, footage, render |
| **`engine-outreach`** | Researches real people and writes genuinely personalised emails — as **drafts**, never sends |
| **`engine-loop`** | Numbers in, A/B verdicts out, weekly report, next week's plan |

Pick one content workflow to start. `engine-loop` needs runs on the board before it can tell you anything.

---

## What you need

- **A Mac** (Apple Silicon recommended) with **Claude Code** or **Codex**
- **git** — `xcode-select --install` if you've never used it
- **Python 3.9+** — already on your Mac. No packages to install; the scripts use the standard library only
- **A Gmail account** if you want the outreach workflow. That's the whole requirement — no Google Cloud project, no API keys, no OAuth consent screens. Your agent connects to Gmail and writes drafts

Per-workflow extras (all free tiers) are in [`docs/prerequisites.md`](docs/prerequisites.md). Every download and signup link is in [`docs/useful-links.md`](docs/useful-links.md). Nothing costs money to start.

---

## Install

Paste this into Claude Code or Codex:

```
Read https://github.com/benyki/gtm-engine and follow the setup instructions in its README.
```

Or do it yourself:

```bash
git clone https://github.com/benyki/gtm-engine.git ~/code/gtm-engine
python3 ~/code/gtm-engine/skills/engine-setup/scripts/scaffold_workspace.py .
~/code/gtm-engine/skills/engine-setup/scripts/install_skills.sh --workspace ./workflows
```

Then tell your agent: `run engine-setup` — it fills in your brand config, picks your workflow, and runs the checks.

---

## How it's put together

> **The repo is logic. Your workspace is data. They never mix.**

| | This repo (`~/code/gtm-engine`) | Your workspace (`<your-project>/workflows/`) |
|---|---|---|
| Holds | the workflows, templates, docs | your brand, inputs, runs, numbers, reports |
| Changes | when you `git pull` | every time you run something |
| Belongs to | this project | you — keep it in your own private repo |

Workflows install as **symlinks** from the clone into `~/.agents/skills/`, your
`workflows/skills/`, and every coding agent present on the machine (Claude Code,
Codex, Cursor, OpenClaw, …). `git pull` updates all of them at once. Nothing you
own lives in this repo, so an update can never clobber your data.

```
<your-project>/workflows/
├── skills/          symlinks → ~/.agents/skills (via install_skills.sh)
├── config/          brand.md, channels.json, sources.json, experiments.json
├── inputs/          your swipe file, best work, audience lists, assets
├── templates/       the competing versions — winners live here, losers/ retired
├── runs/            index.csv (the spine) + one folder per run
├── reports/         weekly markdown
└── state/           crm.csv, published.csv
```

`runs/index.csv` is the important one. One row per thing you ever made, with the arm it used and the number it earned. Everything the loop knows, it knows from that file.

---

## The loop, concretely

Four jobs you schedule once:

| Job | Cadence | What happens |
|---|---|---|
| `due_metrics` → record | daily | Lists published runs that are **72+ hours old** and still have no number. Pulls them in — platform API where it's free, **your browser where it isn't** (agents read TikTok/LinkedIn/Instagram analytics screens fine), Apify if you've outgrown that |
| `score_arms` + challenge | weekly | Scores each arm, promotes a winner, retires the loser to `losers/`, writes a fresh challenger with a hypothesis |
| `generate-inputs` | weekly | Reads what performed and queues next week's content ideas, each with the run that justifies it |
| `render_report` | weekly | Six sections, same shape every week, ending in a config change you approve or reject |

The 72-hour wait is enforced in code, not left to memory. LinkedIn, TikTok, Instagram and X all keep distributing for days — a number read earlier mostly records what time you posted, and once it's written it skews every verdict after it.

Reports are written for both readers: `reports/weekly-YYYY-Www.md` for you, `reports/latest.json` for whichever agent picks the workspace up next, and `reports/index.csv` so the trend is queryable. `weekly.sh` chains the unattended parts; `skills/engine-loop/references/scheduling.md` has the launchd plist and the headless agent invocation.

Nothing auto-sends and nothing auto-adopts. The system writes challengers and proposes config changes; you approve them.

Full detail: [`skills/engine-loop/references/ab-testing.md`](skills/engine-loop/references/ab-testing.md).

---

## When you outgrow it

Each workflow ships a `references/advanced.md` — the specific next step and the problem it solves, not aspirational architecture:

- **Setup** — your own skills repo, Supabase instead of CSVs, object storage for media, cloud crons so a closed laptop doesn't skip a week, Tailscale across machines
- **Outreach** — Cloudflare email routing and Resend when Gmail drafts stop scaling
- **SEO** — an Astro or Next.js static site built automatically from everything you've generated
- **Video** — a dedicated phone and mobilerun for posting that platform APIs won't let you do
- **Loop** — a Telegram or WhatsApp digest so you make template decisions from your phone in twenty seconds

---

## Limits

- It writes drafts, you decide what's good. The first batch usually isn't — telling it why you rejected something is most of the work
- A site of AI-generated pages ranks like one. `engine-seo` mines questions people actually asked rather than keyword lists, which helps, but it isn't a shortcut
- The loop needs about three weeks of runs before its verdicts mean anything
- It won't fix a product nobody wants

MIT licensed. Issues and PRs welcome.

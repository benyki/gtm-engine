# gtm-engine

Marketing workflow templates for coding agents. Drop one into your project's
`workflows/` folder and ship something today: cold outreach drafts, SEO
articles, social posts, short videos. Every template is optional, and so is
using one at all.

Built for indie devs and early-stage startups: you have a product, no users,
and no growth team.

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
```

It copies five skills into `~/.agents/skills/` and links them into Claude Code,
Codex and Cursor. Nothing else on your disk changes, and re-running it updates
them. [`install.sh`](install.sh) is short: read it before you pipe anything into
`bash`, here or anywhere else.

Then, in any project, tell your agent: **`run gtm`**.

No script? Copy the folders in [`skills/`](skills) into your agent's skills
folder yourself.

---

## How it works

A project keeps its recurring work in `workflows/`, one folder per workflow.
That folder is deliberately loose: a workflow lives there and covers one use
case, in any domain, that the project needs done regularly. By default only its
main files go in git, it runs as one scheduled task, and it is written so an
agent or an outside person can run it. The full rules are in
[`skills/gtm/SKILL.md`](skills/gtm/SKILL.md).

```
your-project/
└── workflows/
    ├── creator-outreach/   started from gtm-outreach
    │   ├── README.md       what it does, when it runs, keys by name, what we learned
    │   ├── log.csv         one row per piece shipped, with its result
    │   └── ...             the template's starter files
    └── weekly-report/      a workflow of your own, no template
```

`gtm-engine` adds workflows next to whatever is already in that folder and never
moves or rewrites one.

---

## The skills

| Skill | What it does |
|---|---|
| **`gtm`** | The front door: picks a template or none, makes `workflows/<name>/`, ships a first piece |
| **`gtm-outreach`** | Researches real people and writes personalised emails as **drafts**, never sends |
| **`gtm-seo`** | Finds the questions your buyers ask and writes the article that answers them |
| **`gtm-social`** | LinkedIn, X, Bluesky and other text posts in your voice |
| **`gtm-video`** | Short vertical video: script, voiceover, footage, render |

Each template skill is the craft for its channel plus a `template/` folder: the
starter files copied into a new workflow.

---

## Limits

- It writes drafts; you decide what's good. Telling it why you rejected
  something is most of the work
- A site of AI-generated pages ranks like one; `gtm-seo` mines real questions,
  but it isn't a shortcut
- It won't fix a product nobody wants

---

## Docs

| Doc | Why |
|---|---|
| [`docs/useful-links.md`](docs/useful-links.md) | Every download and signup, and which key each template needs |
| [`docs/additional-skills.md`](docs/additional-skills.md) | Optional toolbox skills from [`benyki/gtm-skills`](https://github.com/benyki/gtm-skills) |
| [`docs/stay-on-top-content.md`](docs/stay-on-top-content.md) | Channels and podcasts worth following, and sources for posts |
| [`docs/bootcamp.md`](docs/bootcamp.md) | Running this as a workshop |

---

## Coming from the engine-* version

Engines, the `~/gtm` home, the `engines.json` registry and the learning loop
are gone. Your `~/gtm` folder is untouched: copy what you still use (your brand
notes, templates, `crm.csv`) into a workflow folder, then remove the old
`engine-*` skills from your skills folders.

MIT licensed. Issues and PRs welcome.

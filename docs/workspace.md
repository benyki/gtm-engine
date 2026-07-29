# Your workspace

Scaffolded into your own project by `engine-setup`. Everything in here is
yours — the engine repo never touches it, so `git pull` can't clobber your data.

```
<your-project>/workflows/
├── skills/                 symlinks to ~/.agents/skills (via install_skills.sh)
├── config/
│   ├── brand.md            who you are, who you're for, what you'll never say
│   ├── channels.json       active workflow, primary metric, publish mode
│   ├── sources.json        where content ideas come from
│   ├── experiments.json    the live A/B tests
│   ├── .env.example        key NAMES (committed)
│   └── .env                key VALUES (gitignored, never read by your agent)
├── inputs/
│   ├── swipe/              content you like
│   ├── best/               your own best-performing work — voice comes from here
│   ├── audience/           outreach lists, any format
│   ├── assets/             logo, fonts, b-roll
│   └── queue/              next week's ideas, written by engine-loop
├── templates/
│   └── <workflow>/
│       ├── <base>.txt      the current default arm
│       ├── <base>-<arm>.txt
│       └── losers/         retired arms — never read by a run, never deleted
├── runs/
│   ├── index.csv           THE SPINE — one row per thing you ever made
│   └── <run_id>/
│       ├── input.json      config snapshot + which arm was used
│       ├── output/         the artefact
│       ├── metrics.json    empty at creation, filled when numbers come back
│       └── notes.md        your verdict, in your words
├── reports/
│   ├── latest.json         the handover file — next agent reads this FIRST
│   ├── index.csv           one row per report ever
│   └── weekly-*.md         the human-readable one
├── site/                   only if you didn't have a website: an Astro site
│                           built from your published markdown
└── state/
    ├── crm.csv             who's been contacted, when, which arm, did they reply
    └── published.csv       what shipped, where, when
```

## The three files that matter

**`config/brand.md`** — worth twenty real minutes. Everything the workflows
write comes from here, and vague answers produce generic output that no amount
of prompting fixes. The "What I've learned" section at the bottom is the part
that compounds: every time you reject something, write down why.

**`runs/index.csv`** — one row per thing you ever made, with the arm it used
and the number it earned. Everything `engine-loop` knows, it knows from this
file. Don't hand-edit it while a run is in progress; use `runlog.py`.

**`templates/<workflow>/`** — the versions competing against each other.
Winners stay; losers move to `losers/` and are never deleted, because something
that lost against one audience often wins against the next.

## Keep it in your own repo

Your workspace is worth more than the engine after a few months — it holds your
CRM, your numbers and every template you've tuned. Commit it somewhere private:

```bash
cd <your-project>
git add workflows/
git commit -m "growth workspace"
```

`.env` is gitignored by the scaffold. Check that it stayed that way before your
first push.

## Starting over

Delete `runs/` and `reports/`, keep `config/` and `templates/`. You lose the
history and keep everything you learned.

To reset an experiment instead, set its `started` date to today in
`experiments.json` — scoring only counts the cohort from that date, so the old
runs stay on disk but stop affecting the verdict.

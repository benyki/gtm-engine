# Your home, and your engines

Two things, and keeping them apart is what makes the rest work.

**The home is `~/gtm`.** One per person. It holds everything shared: your
brand, your accounts, your keys, your assets, what every run has taught, and
`engines.json`, which records where each engine folder is. The engine repo
never touches it, so `git pull` can't clobber your data.

**An engine is one self-contained folder**, and it can live anywhere: in
`~/gtm/engines/` if you want them all in one place, or in an `engines/` folder
inside the project it grows. Agents modify engines constantly; because each
engine owns everything it depends on, rewriting one can never break another.

The engine repo has a `template/home/` folder too. That one is the **source the
scaffold copies from**, and a `.gtm-template` marker at its root keeps every
script from ever treating it as somebody's home.

```
~/gtm/                       THE HOME
├── AGENTS.md                how any agent should work in here, read first
├── CLAUDE.md                a pointer to AGENTS.md, for Claude Code
├── engines.json             THE REGISTRY: every engine, and where it lives
├── shared/                  the one cross-engine folder
│   ├── brand.md             who you are, who you're for, what you'll never say
│   ├── channels.json        all your accounts, one place (open set)
│   ├── .env.example         key NAMES (committed)
│   ├── .env                 key VALUES (gitignored, never read by your agent)
│   ├── assets/              logos, fonts, b-roll, anything any engine reuses
│   ├── docs/                write-ups that benefit every engine
│   └── insights.md          cross-engine learnings, one line each
├── docs/engine → ~/.gtm-engine/docs   (the shipped docs, refreshed by pull)
├── published/               what actually shipped, one subfolder per engine
│                            (artifacts only, gitignored, safe to empty,
│                             and relocatable per engine, see below)
├── skills → ~/.agents/skills   (symlink, from install_skills.sh)
└── engines/                 engines you keep in one place
    ├── engine-outreach-acme/
    ├── engine-seo-acme/
    └── ...

~/code/acme/                 A PROJECT
└── engines/                 or keep this project's engines with the project
    ├── AGENTS.md            written per engine when it lives away from the home
    ├── outreach/            one folder per engine, fully self-contained
    │   ├── engine.json      name, type, home, goal, primary_metric
    │   ├── experiments.json THIS engine's A/B tests, paused until its format settles
    │   ├── sources.json     where its ideas come from
    │   ├── templates/       versions competing; losers/ keeps what lost
    │   ├── inputs/          queue/ always; audience/ best/ swipe/ images/ per type
    │   ├── runs/            index.csv, THIS engine's spine, + one dir per run
    │   ├── crm.csv          people, not runs; outreach types only
    │   └── reports/         weekly report + latest.json for the next agent
    ├── seo/                 same shape (an seo engine adds site/ on demand)
    └── video/               same shape, rename per format once you pick one:
                             video-app/ · video-vibe/ · video-info/
```

## engines.json: the one file that has to stay true

Engines live wherever you put them, so **nothing scans for them**.
`~/gtm/engines.json` is the only record of where each one is, and every script
resolves through it. An engine that is not in that file is invisible: missing
from the weekly report, unreadable by the other engines, unknown to the next
agent.

That makes one habit non-negotiable, for you and for any agent working here:
**move an engine folder, update its entry in the same breath** (and the `home`
key in its `engine.json`). Same for creating, renaming and deleting one.

```bash
registry.py list                       # what is registered, and whether it's there
registry.py add <name> <path>          # register a folder you made by hand
registry.py mv <name> <newpath>        # after you move one
registry.py rm <name>
doctor.py --fix                        # prune dead entries, register loose folders
```

Names are the key, so they are unique across every project: two engines cannot
both be called `outreach`. When engines from several projects share the home,
name them `engine-<type>-<project>/`. When they sit in a project's own
`engines/`, the path already says which project it is, so the plain type is
enough.

## AGENTS.md and CLAUDE.md

The scaffold writes both at the home root, and never overwrites them
afterwards — they're yours to edit. `AGENTS.md` is the real one: what this
folder is, what to read before producing anything, that every piece made gets a
run row, the boundaries that don't move (drafts only, nothing published without
a yes, `.env` never read), and the house habit of **ending every message with
the possible next steps and which of them the agent can start now**.
`CLAUDE.md` just points at it, so Claude Code, Codex and Cursor all read one
file instead of three that drift.

Anything you want every agent in this home to do goes in `AGENTS.md`.
Anything that belongs to one engine goes in that engine's skill, not here.

## The shape is yours to change

The four default folders are a starting point, not the layout. Things the
structure is *designed* to let you do:

- **Run two engines of the same type.** `outreach/` for customers,
  `outreach-investors/` for fundraising — different goals, different CRMs,
  different experiments, different metrics. The clean way:
  `scaffold.py --merge --engine outreach-investors:outreach`.
  Copying an existing folder works too, but then **empty its `runs/`,
  `reports/` and `crm.csv` first** — history belongs to the original, and
  imported runs would poison the new engine's verdicts. Rewrite
  `engine.json`, run it. The folder name is the engine's name;
  `type` in `engine.json` says which skill drives it
- **Add an engine type that doesn't ship** — `newsletter/`, `podcast/`,
  `ads/`. `--merge --engine newsletter` scaffolds the shell; `engine-loop`
  runs it through the same traces as the built-ins
- **Delete what you don't run.** An empty default folder is clutter, not an
  obligation

## Independent mechanics, connected learning

Folders keep the *mechanics* apart; `shared/` is where the *learning* flows:

- `shared/insights.md` — when one engine's numbers teach something bigger
  than that engine (a hook style, an audience truth, a claim that always
  flops), it goes here as one line. Every loop pass reads it and adds to it
- `shared/assets/` — an asset worth reusing (a winning image, a b-roll clip,
  a proof point) moves up here instead of being re-made by the next engine
- `shared/docs/` — longer write-ups any engine benefits from
- Cross-feeding queues: one engine's report justifying an idea for another

`published/` is the one other top-level folder, and it's the exception that
proves the rule: it pools *artifacts* (the mp4 that went out, the image that
went with a post) so you have one place to look at your own work and one place
to reclaim disk. It holds no state — the runs, metrics, experiments and configs
all stay inside their engine — so emptying it can't cost you a verdict.

**Where it lives is per engine.** `published_dir` in an `engine.json` sends
that engine's artifacts wherever they belong: inside the engine folder, onto
an external drive, into a synced folder an editor can reach, or nowhere at all
(`"none"` leaves them in `runs/<run_id>/output/`). The default — one shared
`published/` at the home root — is just the answer that suits most people
on day one. `published/README.md` has the options, the naming convention and the
cleanup command.
  → write it into *that* engine's `inputs/queue/` with the source run

## The three files that matter most

**`shared/brand.md`** — worth twenty real minutes. Everything every engine
writes comes from here, and vague answers produce generic output that no
amount of prompting fixes. The "What I've learned" section at the bottom
compounds: every time you reject something, write down why.

**`<engine>/runs/index.csv`** — that engine's spine: one row per thing it
ever made, the arm it used, the number it earned. Everything `engine-loop`
knows about an engine, it knows from this file. Don't hand-edit it while a
run is in progress; use `runlog.py`.

**`<engine>/engine.json`** — the engine's identity: `type` (which skill
runs it), `goal`, and `primary_metric` (the one number its loop optimises).
Two engines of the same type earn their independence here.

## Runs vs people

Two kinds of table, and the shape tells you which is which:

- **`runs/` is a folder**, because each artifact gets its own directory —
  one row in `index.csv` per thing you made, plus `runs/<run_id>/` holding
  its input, output and metrics
- **`crm.csv` is a flat file** at the engine root, because it's keyed by
  *person*, not by artifact. One person accumulates a first touch and two
  follow-ups — three runs, one row

That's why the CRM isn't part of the spine. `assign_arm.py` reads it to keep
someone in the arm they were first assigned (including on follow-ups), and
`engine-outreach` reads it to never contact anyone twice. Neither rule can be
expressed in a table keyed by artifact.

A custom engine that tracks entities of its own — subscribers, accounts,
communities — puts them in the same place, one flat CSV at the engine root.

## Keep it in your own repo

Your home is worth more than the engine after a few months: it holds your
CRMs, your numbers and every template you've tuned. Commit it somewhere
private:

```bash
cd ~/gtm && git init && git add . && git commit -m "growth home"
```

An engine that lives inside a project is committed with that project, or
gitignored, depending on whether the repo is yours and private. Runs and CRM
rows are personal data; a shared or public repo is not the place for them.

`shared/.env` is gitignored by the scaffold. Check that it stayed that way
before your first push.

The clone at `~/.gtm-engine` is nobody's data and never belongs in a project
repo. That is why it lives outside them: one clone per machine, updated by
`git pull`, nothing to gitignore.

## Starting over

Per engine: delete its `runs/` and `reports/`, keep `engine.json`,
`templates/` and `experiments.json`. You lose the history and keep everything
you learned. The other engines aren't touched — that's the point of the
folders.

To reset an experiment instead, set its `started` date to today in that
engine's `experiments.json` — scoring only counts the cohort from that
date, so the old runs stay on disk but stop affecting the verdict.

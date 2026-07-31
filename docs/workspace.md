# Your workspace

Scaffolded into your own project by `engine-setup`. Everything in here is
yours — the engine repo never touches it, so `git pull` can't clobber your data.

The engine repo has a folder called `workspace/` too. That one is the **source
the scaffold copies from** — a `.gtm-template` marker at its root keeps every
script from ever treating it as somebody's workspace. Yours is the one inside
your own project.

The architecture is **one self-contained folder per workflow, plus one
`shared/` folder**. Agents modify workflows constantly; because each workflow
owns everything it depends on, rewriting one can never break another.

```
<your-project>/workflows/
├── shared/                  THE one cross-workflow folder
│   ├── brand.md             who you are, who you're for, what you'll never say
│   ├── channels.json        all your accounts, one place (open set)
│   ├── .env.example         key NAMES (committed)
│   ├── .env                 key VALUES (gitignored, never read by your agent)
│   ├── assets/              logos, fonts, b-roll — anything any workflow reuses
│   ├── docs/                write-ups that benefit every workflow
│   └── insights.md          cross-workflow learnings, one line each
├── skills → ~/.agents/skills   (symlink, from install_skills.sh)
├── outreach/                one folder per workflow — fully self-contained
│   ├── workflow.json        type, goal, primary_metric (the loop optimises this)
│   ├── experiments.json     THIS workflow's A/B tests — paused until its format is settled
│   ├── sources.json         where its ideas come from
│   ├── templates/           versions competing; losers/ keeps what lost
│   ├── inputs/              queue/ always; audience/ best/ swipe/ per type
│   ├── runs/                index.csv — THIS workflow's spine — + one dir per run
│   ├── crm.csv              people, not runs — outreach types only
│   └── reports/             weekly report + latest.json for the next agent
├── seo/                     same shape (a seo workflow adds site/ on demand)
├── social/                  same shape
└── video/                   same shape
```

## The shape is yours to change

The four default folders are a starting point, not the layout. Things the
structure is *designed* to let you do:

- **Run two workflows of the same type.** `outreach/` for customers,
  `outreach-investors/` for fundraising — different goals, different CRMs,
  different experiments, different metrics. The clean way:
  `scaffold_workspace.py . --merge --workflow outreach-investors:outreach`.
  Copying an existing folder works too, but then **empty its `runs/`,
  `reports/` and `crm.csv` first** — history belongs to the original, and
  imported runs would poison the new workflow's verdicts. Rewrite
  `workflow.json`, run it. The folder name is the workflow's name;
  `type` in `workflow.json` says which skill drives it
- **Add a workflow type that doesn't ship** — `newsletter/`, `podcast/`,
  `ads/`. `--merge --workflow newsletter` scaffolds the shell; `engine-loop`
  runs it through the same traces as the built-ins
- **Delete what you don't run.** An empty default folder is clutter, not an
  obligation

## Independent mechanics, connected learning

Folders keep the *mechanics* apart; `shared/` is where the *learning* flows:

- `shared/insights.md` — when one workflow's numbers teach something bigger
  than that workflow (a hook style, an audience truth, a claim that always
  flops), it goes here as one line. Every loop pass reads it and adds to it
- `shared/assets/` — an asset worth reusing (a winning image, a b-roll clip,
  a proof point) moves up here instead of being re-made by the next workflow
- `shared/docs/` — longer write-ups any workflow benefits from
- Cross-feeding queues: one workflow's report justifying an idea for another
  → write it into *that* workflow's `inputs/queue/` with the source run

## The three files that matter most

**`shared/brand.md`** — worth twenty real minutes. Everything every workflow
writes comes from here, and vague answers produce generic output that no
amount of prompting fixes. The "What I've learned" section at the bottom
compounds: every time you reject something, write down why.

**`<workflow>/runs/index.csv`** — that workflow's spine: one row per thing it
ever made, the arm it used, the number it earned. Everything `engine-loop`
knows about a workflow, it knows from this file. Don't hand-edit it while a
run is in progress; use `runlog.py`.

**`<workflow>/workflow.json`** — the workflow's identity: `type` (which skill
runs it), `goal`, and `primary_metric` (the one number its loop optimises).
Two workflows of the same type earn their independence here.

## Runs vs people

Two kinds of table, and the shape tells you which is which:

- **`runs/` is a folder**, because each artifact gets its own directory —
  one row in `index.csv` per thing you made, plus `runs/<run_id>/` holding
  its input, output and metrics
- **`crm.csv` is a flat file** at the workflow root, because it's keyed by
  *person*, not by artifact. One person accumulates a first touch and two
  follow-ups — three runs, one row

That's why the CRM isn't part of the spine. `assign_arm.py` reads it to keep
someone in the arm they were first assigned (including on follow-ups), and
`engine-outreach` reads it to never contact anyone twice. Neither rule can be
expressed in a table keyed by artifact.

A custom workflow that tracks entities of its own — subscribers, accounts,
communities — puts them in the same place, one flat CSV at the workflow root.

## Keep it in your own repo

Your workspace is worth more than the engine after a few months — it holds
your CRMs, your numbers and every template you've tuned. Commit it somewhere
private:

```bash
cd <your-project>
git add workflows/
git commit -m "growth workspace"
```

`shared/.env` is gitignored by the scaffold. Check that it stayed that way
before your first push.

## Starting over

Per workflow: delete its `runs/` and `reports/`, keep `workflow.json`,
`templates/` and `experiments.json`. You lose the history and keep everything
you learned. The other workflows aren't touched — that's the point of the
folders.

To reset an experiment instead, set its `started` date to today in that
workflow's `experiments.json` — scoring only counts the cohort from that
date, so the old runs stay on disk but stop affecting the verdict.

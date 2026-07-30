# Your workspace

Scaffolded into your own project by `engine-setup`, **scoped to the workflows
you chose**. Everything in here is yours — the engine repo never touches it, so
`git pull` can't clobber your data.

```
<your-project>/workflows/
├── skills/                 symlinks for installed workflows only
├── config/
│   ├── brand.md            who you are, who you're for, what you'll never say
│   ├── pathways.json       which workflows this workspace runs
│   ├── channels.json       active workflow, primary metric, publish mode
│   ├── sources.json        sources for your installed workflows
│   ├── experiments.json    live A/B tests for those workflows
│   ├── .env.example        key NAMES for those workflows (committed)
│   └── .env                key VALUES (gitignored, never read by your agent)
├── inputs/                 only folders your workflows use (+ queue/)
│   ├── swipe/              content you like          (seo, linkedin)
│   ├── best/               your best work — voice    (seo, linkedin, video)
│   ├── audience/           outreach lists            (outreach)
│   ├── assets/             logo, fonts, b-roll       (video)
│   └── queue/              next week's ideas         (engine-loop)
├── templates/
│   └── <workflow>/         one folder per installed workflow — add your own freely
├── runs/
│   ├── index.csv           THE SPINE — one row per thing you ever made
│   └── <run_id>/
├── reports/                weekly markdown + latest.json (from engine-loop)
├── site/                   created on demand by engine-seo — never pre-scaffolded
└── state/
    ├── published.csv       what shipped, where, when
    └── crm.csv             outreach only
```

Add another workflow later without rebuilding:

```bash
python3 ~/code/gtm-engine/skills/engine-setup/scripts/scaffold_workspace.py . \
  --workflow video --merge
~/code/gtm-engine/skills/engine-setup/scripts/install_skills.sh \
  --workspace ./workflows --workflow video
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

# Troubleshooting

---

## Setup

**`git: command not found`**
```bash
xcode-select --install
```
Five to ten minutes. Everything needs this.

**The agent won't fetch the repo URL**

Do it by hand:
```bash
git clone https://github.com/benyki/gtm-engine.git ~/code/gtm-engine
python3 ~/code/gtm-engine/skills/engine-setup/scripts/scaffold_workspace.py . --workflow seo
~/code/gtm-engine/skills/engine-setup/scripts/install_skills.sh --workspace ./workflows --workflow seo
```

**`install_skills.sh` says "a real directory is already there"**

Something else owns that skill name — usually a hand-made skill from before.
Move it, then re-run:
```bash
mv ~/.claude/skills/engine-loop ~/.claude/skills/engine-loop.backup
~/code/gtm-engine/skills/engine-setup/scripts/install_skills.sh --workspace ./workflows --workflow seo
```

**Still seeing `engine-linkedin-content` after an update**

That skill was renamed to `engine-linkedin`. Remove the old symlink and re-run install:
```bash
rm -f ~/.agents/skills/engine-linkedin-content \
      ~/.claude/skills/engine-linkedin-content \
      ~/.codex/skills/engine-linkedin-content \
      ~/.cursor/skills/engine-linkedin-content \
      ./workflows/skills/engine-linkedin-content
~/code/gtm-engine/skills/engine-setup/scripts/install_skills.sh --workspace ./workflows --workflow linkedin
```

**The agent can't see the workflows after installing**

Restart the agent — most only scan the skills directory at startup. Then check:
```bash
ls -la ~/.agents/skills | grep engine-
ls -la ~/.claude/skills | grep engine-
ls -la ./workflows/skills | grep engine-
```
You should see symlinks pointing at `~/.agents/skills` (which points into your clone).

**`scaffold_workspace.py` refuses to run**

It won't overwrite an existing `workflows/` folder, because that folder holds
your runs. Use `--merge --workflow <pathway>` to add another pathway, or
`--name workflows2` for a second workspace.

---

## Config

**`config/experiments.json is not valid JSON`**

Usually a trailing comma after the last item in a list or object. JSON doesn't
allow them. Check:
```bash
python3 -m json.tool workflows/config/experiments.json
```

**Keys show as missing when they're set**

Three usual causes: quotes around the value (`KEY="abc"` — drop them), a space
around the `=`, or you edited `.env.example` instead of `.env`.

**The agent asks for a key you've already added**

It reads `.env.example` for names and never `.env` for values — by design. It
can see *that* a variable is set but not what it is. If it's asking, the
variable is genuinely empty in `.env`.

---

## Outreach

**Gmail won't connect**

Managed Google Workspace accounts often block connectors at the admin level.
Either ask your admin, or use a personal Gmail — two minutes, no approval.

**It drafted someone twice**

Check `state/crm.csv` for duplicate rows with different ids. Usually the same
person imported once with an email and once with a LinkedIn URL. Merge the
rows, keep the earlier `arm` — switching someone's arm invalidates them for
the experiment.

**Drafts read like a robot**

The research step is thin. Push for one *specific, recent* observation per
person rather than a compliment about the company. If there's nothing findable,
that person is the wrong target — skipping them is the right call, not filler.

---

## The loop

**`assign_arm.py` returns `action: write_template`**

Working as intended. That arm has no template yet — write the file it names,
using the hypothesis it gives you, then use it. Don't substitute another
template and don't stop.

**`score_arms.py` says undecided forever**

One of three things: not enough *measured* runs (runs with a metric, not runs
that exist), arms genuinely too close, or `min_runs_per_arm` set too high for
your volume. Check the measured column — if it's far below the run count, the
problem is metric collection, not the experiment.

**All my arms show `metric_source: manual`**

Fine, but it means nothing is being fetched automatically. For LinkedIn, X,
TikTok and Instagram, the browser route is quick and reliable — see
`skills/engine-loop/references/fetching-data.md`.

**A verdict looks wrong**

Check whether you're reading the cohort or the all-time table. All-time
includes every run made before the experiment started, all of which sit in the
default arm. Cohort decides; all-time is context.

---

## Still stuck

Run the doctor — it checks the machine, the install, the workspace, the config
and the keys:

```bash
python3 ~/code/gtm-engine/skills/engine-setup/scripts/doctor.py
```

Then open an issue with its output. Redact anything from `.env` first.

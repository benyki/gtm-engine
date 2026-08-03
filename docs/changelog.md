# Changelog

Written for **agents**, not for release notes. If you are working in a setup
that predates an entry below, read it: it says what changed, whether anything
breaks, and what to do about it.

## How to use this file

**Conform to the current architecture when there is no risk to what the user
already has. Never migrate someone mid-task.**

The test, in order:

1. **Does the old shape still work?** If the entry says it does, nothing is
   urgent. Say one line about it and carry on with what you were asked.
2. **Is the change additive?** New file, new flag, new folder that does not
   move anything: adopt it. That is not a migration, it is just using the tool
   as it now is.
3. **Would adopting it move, rename or delete something the user owns?** Then
   it is the user's call. Offer it, in one sentence, with the command, at the
   end of what you were doing. Do not run it because you noticed it.
4. **Is the user mid-flow?** Finish their task first. A layout migration in the
   middle of drafting an email is how work gets lost.

Never migrate a user's data to satisfy a preference for tidiness. The runs, the
CRM and the templates are the value here; the folder layout is not.

---

## v2, 2026-08: `~/gtm`, and engines that live anywhere

**Nothing is forced. v1 setups keep working.** The scripts detect the old shape
and use it.

What changed:

| v1 | v2 |
|---|---|
| clone at `<project>/gtm-engine/`, one per project | clone at `~/.gtm-engine`, one per machine |
| `<project>/workflows/` held `shared/` **and** the channel folders | `~/gtm` holds everything shared; the channel folders live anywhere |
| folders found by listing the workspace directory | folders found through `~/gtm/engines.json`, the registry |
| the word "workflow" | the word **"engine"**, everywhere |
| `workflow.json` | `engine.json` |
| `--workspace`, `--workflow`, `GTM_WORKSPACE` | `--home`, `--engine`, `GTM_HOME` |
| `runs/index.csv` column `workflow` | column `engine` |
| `scaffold_workspace.py`, `workflows.py`, `wsfind.py` | `scaffold.py`, `engines.py`, `gtmfind.py` |

### What an agent on a v1 setup needs to know

- **The old flags still work.** `--workspace` and `--workflow` are accepted
  everywhere as the names for `--home` and `--engine`. No command a user has in
  a scheduled task breaks.
- **`workflow.json` is still read** when `engine.json` is absent. A v1 folder
  is a valid engine.
- **A v1 `runs/index.csv` is carried over automatically.** The `workflow`
  column is read and rewritten as `engine` on the next write by `runlog.py`.
  Old rows keep their values.
- **The loop scripts still find a v1 workspace** by walking up from the cwd,
  and they print one line saying a migration is available. That line is
  information, not an instruction.
- **Do not migrate on your own initiative.** Finish the task. Then, if it is
  useful, one sentence: "your setup uses the older layout; moving it to `~/gtm`
  is `migrate_v1.py <path>`, and it dry-runs by default. Want me to show you
  the plan?"

### Migrating, when the user says yes

```bash
python3 ~/.gtm-engine/skills/engine-setup/scripts/migrate_v1.py <project>/workflows
# prints the plan, writes nothing
python3 ~/.gtm-engine/skills/engine-setup/scripts/migrate_v1.py <project>/workflows --apply
```

It copies `shared/` into `~/gtm/shared/` **without overwriting anything already
there**, renames each `workflow.json` to `engine.json`, and registers every
engine. Engine folders stay where they are unless you pass `--move`. Nothing is
deleted: the old `shared/` is left on disk for the user to remove.

Two things to watch, and to tell the user about:

- **A second project's `brand.md` cannot win.** The first home wins and the
  conflict is reported. Merge by hand, or give that project its own home with
  `--home`.
- **Engine names are unique across every project.** A second `seo/` arriving
  from another project is registered as `engine-seo-<project>`.

### The habit v2 asks for

Engines live wherever the user put them, so **nothing scans for them**.
`~/gtm/engines.json` is the only map. Whenever a folder is created, moved,
renamed or deleted, that file changes with it, in the same breath:

```bash
registry.py add <name> <path>      # created by hand
registry.py mv <name> <newpath>    # moved
registry.py rm <name>              # deleted
doctor.py --fix                    # prune dead entries, register loose folders
```

An engine that is not registered is invisible: absent from the weekly report,
unreadable by the other engines, unknown to the next agent.

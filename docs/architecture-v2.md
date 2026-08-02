# Architecture v2: `~/.gtm-engine`, `~/gtm`, and engines that live anywhere

A plan, not a change. Nothing below is implemented yet except this file and
[`onboarding.md`](onboarding.md).

## What changes

Today there is exactly one shape: a clone at `<project>/gtm-engine/` and a
workspace at `<project>/workflows/` holding `shared/` plus one folder per
workflow. Shared config is duplicated per project, and the workspace has to be
one directory because every script finds workflows by listing that directory.

v2 splits the three things that are currently fused:

| | Today | v2 |
|---|---|---|
| The code | `<project>/gtm-engine/`, one clone per project | `~/.gtm-engine`, one clone per machine |
| Shared data (brand, keys, assets, insights, docs) | `<project>/workflows/shared/` | `~/gtm/` |
| The engines (channel folders) | `<project>/workflows/<type>/`, all in one place | anywhere, registered in `~/gtm/engines.json` |

```
~/.gtm-engine/                 the clone. read-only, git pull overwrites it
~/gtm/                         your data. never touched by an update
├── AGENTS.md  CLAUDE.md
├── engines.json               the registry: name -> absolute path
├── shared/                    brand.md, channels.json, .env, assets/, insights.md
├── docs/                      symlink to ~/.gtm-engine/docs, plus your own writing
├── published/
└── engines/                   default home for engines, when you want one place
    └── engine-outreach-acme/

<any-project>/engines/         or here, one folder per engine, per project
└── outreach/
```

## Decisions

**1. The clone moves to `~/.gtm-engine`.** One clone, one `git pull`, no
`.gitignore` entry to inject into anybody's repo. `GTM_ENGINE_DIR` and
`--engine-dir` still override it.

**2. `~/gtm` is the home, and it is the only thing that is truly fixed.**
Overridable with `GTM_HOME` / `--home` for people who keep everything under
`~/code`. Everything shared lives here so a second project costs nothing.

**3. Engines are located, not enumerated.** `~/gtm/engines.json` maps engine
name to absolute path. Every engine folder also carries `home` in its
`engine.json`, so resolution works from either end: from an engine you find the
home, from the home you find every engine. A missing path is reported by
`doctor.py`, never silently skipped.

**4. Scripted default and interviewed default differ, deliberately.**
`install.sh` with no arguments is non-interactive, so it creates `~/gtm` plus
the four default engines in `~/gtm/engines/`. The agent running the onboarding
in [`onboarding.md`](onboarding.md) has a user in front of it, so it recommends
`<cwd>/engines/` and offers `~/gtm/engines/` as the "all in one place" answer.
**This is the one thing in this plan worth confirming before implementation**:
the alternative is to make both defaults `~/gtm/engines/` and treat the
in-project folder as the deliberate choice.

**5. Naming.** Engines inside `~/gtm/engines/` are named
`engine-<type>-<project>`, because that folder mixes projects and a bare
`outreach/` there says nothing. Engines inside a project are named `<type>/`,
because the project name is already the parent path. Both are conventions the
scaffolder applies by default and the user can override; nothing resolves by
name pattern, only by the registry.

## Terminology: engines, not workflows

**Recommendation: drop "workflow" entirely and use "engine" everywhere.**

The skills are already called `engine-seo`, `engine-social`, `engine-video`,
`engine-outreach`, `engine-loop`, `engine-setup`. Keeping a second word for the
folder those skills operate on means every doc has to explain the mapping, and
`workflow.json` sitting inside a folder run by `engine-outreach` is the sort of
seam that makes people ask which is which.

On collisions, which is what the choice actually turns on:

- **`workflows/` is the more crowded name.** In a repo, a folder called
  `workflows/` reads as CI or orchestration definitions. GitHub Actions
  workflows must live in `.github/workflows`, and a root-level `workflows/`
  folder is a known point of confusion for people who create the two folders
  separately by mistake ([GitHub Docs](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows),
  [community discussion](https://github.com/orgs/community/discussions/57945)).
  Temporal, Airflow, Prefect, Argo and n8n all use "workflow" as their core
  noun, so the word is heavily claimed in exactly the automation space this
  tool sits next to.
- **`engines/` has one real collision, and it is narrow.** Ruby on Rails
  modular monoliths conventionally keep mountable engines in a top-level
  `engines/` (or `components/`, or `gems/`) directory
  ([Rails guides](https://guides.rubyonrails.org/engines.html),
  [makandra](https://makandracards.com/makandra/473766-structuring-rails-applications-modular-monorepo-monolith),
  [Infinum handbook](https://infinum.com/handbook/rails/development-practices/folder-structure)).
  Some Rails teams even gitignore `/engines/*`, which would silently swallow a
  user's data. Outside Rails, "engine" as a directory name is rare: Django's
  "engines" are template backends, not directories, and game engines are not a
  repo layout convention.

So the swap trades a broad, constant ambiguity for a narrow one that is
detectable in a single check. The scaffolder should refuse to merge into an
existing `engines/` it did not create and fall back to `gtm-engines/`, which
covers the Rails case completely.

If you would rather not carry the rename, the fallback is to keep `workflows/`
as the folder name and use "engine" only for the skills. Everything else in
this plan is unaffected. The rename is roughly 80 files of find and replace
plus 12 files of real logic, so it is worth doing in one commit or not at all.

## The plan, file by file

### Phase 1: path resolution (the load-bearing change)

| File | Change |
|---|---|
| `skills/engine-loop/scripts/wsfind.py` | Rename to `gtmfind.py`. Replace "walk up to find a dir with `shared/`" with: `find_home()` (`--home` > `GTM_HOME` > `~/gtm`), `load_registry()`, `list_engines()`, `find_engine(name_or_path)`, `engine_meta()`. Keep a compatibility branch that recognises a v1 workspace (a dir with `shared/` and `workflow.json` children) and prints the migration command. |
| `skills/engine-setup/scripts/workflows.py` | Rename to `engines.py`. `parse_workflows` becomes `parse_engines` (accepting `name[:type]` still), `workspace_types` becomes `registry_types` reading `engines.json` rather than listing a directory. Add `engine_folder_name(type, project, in_home: bool)` implementing the `engine-<type>-<project>` convention. |
| **new** `skills/engine-setup/scripts/registry.py` | Read, write and repair `~/gtm/engines.json`: `register(path, type)`, `unregister`, `prune()` (drop paths that no longer exist, only when asked), `resolve(name)`. Every write is atomic and preserves unknown keys, because users will hand-edit this file. |

### Phase 2: scaffolding and install

| File | Change |
|---|---|
| `skills/engine-setup/scripts/scaffold_workspace.py` | Rename to `scaffold.py` and split its single job in two: `scaffold_home()` creates `~/gtm` (shared, docs, published, AGENTS.md, CLAUDE.md, .gitignore, empty `engines.json`), `scaffold_engine(dest, type, project)` creates one engine folder at an arbitrary path and registers it. New flags: `--home`, `--engine name[:type]` (repeatable), `--at PATH`, `--project NAME`, `--all`. The existing merge and never-overwrite behaviour is kept as is. |
| **new** `skills/engine-setup/scripts/migrate_v1.py` | Move an existing `<project>/workflows/` into the new shape: `shared/` and the root docs to `~/gtm` (interactive when several projects each have their own shared, since only one can win), each workflow folder either left in place or moved, `workflow.json` renamed to `engine.json`, everything registered. Dry run by default, `--apply` to write, and it copies rather than moves unless told otherwise. |
| `skills/engine-setup/scripts/install_skills.sh` | `--workspace` becomes `--home` (old flag accepted with a warning). Infer which skills to install from the registry instead of listing a workspace directory. Symlink `~/gtm/skills` to `~/.agents/skills`; drop the per-workspace link or repeat it per engine folder. |
| `skills/engine-setup/scripts/doctor.py` | New checks: `~/gtm` exists and has `shared/`; `engines.json` parses; every registered path exists and holds an `engine.json`; no engine is registered twice; the clone is at `~/.gtm-engine` and is a git repo; v1 workspaces still on disk get a "run migrate_v1.py" warning. |
| `install.sh` | Default `ENGINE_DIR` to `~/.gtm-engine`. Drop the "add gtm-engine/ to .gitignore" block. Add `--home`, `--engine`, `--at`. With no arguments: create `~/gtm`, scaffold the four default engines into `~/gtm/engines/`, install all six skills. Update the usage text and the closing "Next" block to the new paths. |

### Phase 3: the template

| File | Change |
|---|---|
| `workspace/` | Rename to `template/`, split into `template/home/` (shared, published, AGENTS.md, CLAUDE.md, `.gtm-template`) and `template/engines/` (`_every-engine/`, `outreach/`, `seo/`, `social/`, `video/`). |
| `workspace/workflows/*/workflow.json` (5 files) | Rename to `engine.json`. Keep the `type` key; add `home` (path back to `~/gtm`) and `project`. |
| `workspace/workflows/README.md` | Rewrite as `template/engines/README.md`: what an engine folder is, that it can live anywhere, how it finds its home. |
| `workspace/AGENTS.md`, `workspace/CLAUDE.md` | Rewrite for the split. The current text assumes "this folder holds everything"; it now has to say shared lives here, engines are elsewhere, and reading a sibling engine's `reports/latest.json` means resolving it through the registry. |
| `workspace/shared/{brand.md,channels.json,insights.md,.env.example}` | Wording only: "workflow" to "engine", plus a line in `brand.md` about being shared across projects and how to override per engine. |
| `workspace/published/README.md` | Wording, and a note that `published/` is per home, not per project. |

### Phase 4: the loop scripts

All of these import `wsfind` and assume "workspace directory holds the
workflow folders". Each needs the import swapped to `gtmfind`, the workflow
lookup swapped to a registry lookup, and `--workspace` swapped to
`--home` / `--engine`:

`skills/engine-loop/scripts/runlog.py`, `due_metrics.py`, `assign_arm.py`,
`score_arms.py`, `render_report.py`, `weekly.sh`, and
`skills/engine-video/scripts/combo_check.py`.

`render_report.py` needs the most thought: it reports across engines, which
now means iterating the registry and handling an engine whose path has moved.

### Phase 5: docs and skill instructions

| File | Change |
|---|---|
| `README.md` | Install section (one clone at `~/.gtm-engine`, `~/gtm` as home, engines anywhere), the "How it's put together" table, and the terminology throughout. Link `docs/onboarding.md`. |
| `docs/workspace.md` | Rename to `docs/home.md`. Rewrite the tree and the "one folder per workflow" framing. This is the doc that changes most. |
| **new** `docs/onboarding.md` | Written. The exact onboarding script the agent follows. |
| **new** `docs/architecture-v2.md` | This file. Delete it once v2 ships, or keep it as the design record. |
| `docs/preflight.md`, `docs/scheduling.md`, `docs/goals.md`, `docs/useful-links.md`, `docs/additional-skills.md`, `docs/stay-on-top-content.md` | Paths (`<project>/workflows/` to `~/gtm` and the engine path) and terminology. `scheduling.md` also needs the scheduled-task prompts updated, since each one names a workspace path that no longer exists. |
| `skills/engine-setup/SKILL.md` | Largest single rewrite. The "Where everything lives" section is now wrong end to end. Replace the step list with a pointer to `docs/onboarding.md` plus the mechanics. |
| `skills/engine-loop/SKILL.md` and `references/{ab-testing,scheduling,fetching-data,advanced}.md` | Registry-based lookups, new flags, new paths. |
| `skills/engine-{seo,social,video,outreach}/SKILL.md` | Every path of the form `workflows/<type>/...` becomes an engine-relative path; every "the workspace" becomes "your engine folder" or "your home". |
| `skills/engine-*/references/*.md` (about 20 files with incidental mentions) | Terminology sweep, mechanical. |
| `.gitignore`, `LICENSE`, `misc/` | No change. |

## Migration and compatibility

Existing installs have real data in `<project>/workflows/`. The plan is:

1. `gtmfind.py` recognises a v1 workspace and keeps working in read-only mode
   for one release, printing a one-line migration hint.
2. `migrate_v1.py` does the move, dry run first.
3. `doctor.py` reports any v1 workspace it finds.
4. The old `--workspace` flag keeps working everywhere, mapped to `--home`,
   with a deprecation line on stderr.

`workflow.json` files are read as `engine.json` if the new name is absent, so a
user who never migrates does not get a broken tool, only an old layout.

## Risks worth naming

- **One shared brand for every project is the whole point of `~/gtm`, and also
  its main flaw.** Someone with two genuinely different brands needs either two
  homes (`GTM_HOME`) or a per-engine override of `brand.md`. Pick one and say
  so in `AGENTS.md`; supporting both silently is how the config gets confusing.
- **A registry can go stale.** People move folders. Every script that resolves
  an engine has to fail with the path it tried and the fix, never a traceback.
- **The rename touches around 80 files.** Do it as one mechanical commit,
  separate from the logic changes, so the diff stays reviewable.
- **`engines/` in a Rails repo.** Covered by the "do not merge into a folder we
  did not create" check, but it has to be in the scaffolder, not only in a doc.

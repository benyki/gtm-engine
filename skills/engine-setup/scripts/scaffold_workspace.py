#!/usr/bin/env python3
"""Create a gtm-engine workspace inside your project.

The workspace is one `shared/` folder (brand, accounts, keys, assets, docs,
cross-workflow insights) plus ONE SELF-CONTAINED FOLDER PER WORKFLOW — its
own workflow.json, experiments.json, sources.json, templates/, inputs/,
runs/, reports/. Workflows never reach into each other's folders,
so an agent rewriting one can't break another.

Usage:
    scaffold_workspace.py                       # default: all four starters
    scaffold_workspace.py . --workflow seo,outreach
    scaffold_workspace.py . --workflow outreach-investors:outreach
    scaffold_workspace.py . --workflow newsletter        # custom workflow
    scaffold_workspace.py . --workflow video --merge

    project_dir   where to create it (default: current directory)
    --workflow    optional. Omitted (or 'all') → one folder for each shipped
                  workflow (outreach, seo, social, video). Otherwise a comma
                  list of name[:type] — the NAME is the folder (free), the
                  TYPE picks the starter and skill. `outreach-investors:outreach`
                  is a second outreach workflow with its own goal; a name with
                  no shipped type is a custom workflow (generic scaffold).
                  Create as many as your situation needs — two outreach
                  workflows with different audiences, three video workflows
                  with different formats. The default is a starting point,
                  not the shape.
    --merge       fill in missing files in an existing workspace
                  (never overwrites anything that already exists)
    --name        workspace folder name (default: workflows). Use a second
                  name for a second brand/ICP — one workspace per brand is
                  the intended pattern
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import workflows as wf  # noqa: E402

REPO_ROOT = _HERE.parents[2]
TEMPLATE = REPO_ROOT / "workspace"
SHARED_SRC = TEMPLATE / "shared"
STARTERS = TEMPLATE / "workflows"
# The parts every workflow folder has whatever its type — runs/index.csv,
# inputs/queue/, reports/, templates/losers/, empty experiments and sources.
# It sits among the starters but is not a type: the leading underscore keeps
# it out of workflows.py discovery, so nobody can scaffold `_every-workflow/`.
BASE_SRC = STARTERS / "_every-workflow"

GITIGNORE = """\
# secrets
shared/.env
.env
*.local

# skills/ is a symlink to ~/.agents/skills — recreated by install_skills.sh
skills/

# build junk — site/ appears if engine-seo scaffolds you a website
site/node_modules/
site/dist/
site/.astro/
site/.next/

# python
__pycache__/
*.pyc

# video renders are large; keep the finished file, not the scratch
**/runs/**/output/*.tmp.*
"""


def copy_tree(src: Path, dst: Path) -> tuple[int, int]:
    """Copy a directory tree. Never overwrite existing files."""
    created = skipped = 0
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        created += 1
    return created, skipped


def write_if_missing(path: Path, text: str) -> int:
    if path.exists():
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return 1


def custom_workflow_json(name: str) -> str:
    return json.dumps({
        "type": name,
        "goal": "",
        "primary_metric": "",
        "_primary_metric_hint": "The one number THIS workflow optimises. "
                                "A channel can override it in shared/channels.json.",
        "_comment": f"Custom workflow — no shipped skill; engine-loop runs it "
                    f"through the same traces as the built-ins. This folder is "
                    f"fully self-contained. Want a second one? Copy the whole "
                    f"folder to a new name and rewrite this file.",
    }, indent=2) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("project_dir", nargs="?", default=".")
    ap.add_argument(
        "--workflow", "-w", default="",
        help="comma list of name[:type]; omitted → one folder per shipped "
             "workflow. See the module docstring.",
    )
    ap.add_argument("--name", default="workflows",
                    help="workspace folder name (default: workflows) — "
                         "use another name for a second brand/ICP")
    ap.add_argument("--merge", action="store_true",
                    help="add missing files/workflows to an existing workspace")
    a = ap.parse_args()

    try:
        pairs = wf.parse_workflows(a.workflow)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    for d in (SHARED_SRC, BASE_SRC):
        if not d.is_dir():
            print(f"error: template not found at {d}", file=sys.stderr)
            return 1

    project = Path(a.project_dir).expanduser().resolve()
    if not project.is_dir():
        print(f"error: {project} is not a directory", file=sys.stderr)
        return 1

    dest = project / a.name

    if dest.exists() and not a.merge:
        print(f"\n{dest} already exists.\n")
        print("That folder holds your runs and your brand config, so this")
        print("script will not touch it. Your options:\n")
        print(f"  --merge --workflow <name[:type]>   add a workflow / missing files")
        print(f"  --name workflows2                  scaffold alongside it\n")
        return 1

    known = set(wf.list_known())

    print(f"\nCreating workspace: {dest}")
    print(f"  workflows: {', '.join(n if n == t else f'{n} (type {t})' for n, t in pairs)}")
    print(f"  (a starting point, not the shape — copy any workflow folder to "
          f"run a second one with a different goal)")
    print()

    created = skipped = 0

    # shared/ — the one cross-workflow folder.
    c, s = copy_tree(SHARED_SRC, dest / "shared")
    created += c
    skipped += s
    if c:
        print("  + shared/  (brand, channels, .env.example, assets/, docs/, insights.md)")

    # One self-contained folder per workflow: type starter first (its
    # experiments/sources/templates win), then the base shell fills the gaps.
    for name, typ in pairs:
        wd = dest / name
        c2 = s2 = 0
        starter = STARTERS / typ
        if starter.is_dir():
            c2, s2 = copy_tree(starter, wd)
        else:
            c2 += write_if_missing(wd / "workflow.json", custom_workflow_json(name))
        c1, s1 = copy_tree(BASE_SRC, wd)
        # A renamed instance keeps its type in workflow.json even when the
        # starter shipped `"type": typ` — rewrite only if freshly copied.
        marker = wd / "workflow.json"
        if name != typ and marker.is_file():
            try:
                meta = json.loads(marker.read_text())
                if meta.get("type") != typ:
                    meta["type"] = typ
                    marker.write_text(json.dumps(meta, indent=2) + "\n")
            except json.JSONDecodeError:
                pass
        created += c1 + c2
        skipped += s1 + s2
        if c1 + c2:
            tag = "" if name == typ else f"  (type {typ})"
            note = "" if (starter.is_dir() or typ in known) else "  (custom — no shipped skill; the agent fills it in)"
            print(f"  + {name}/{tag}{note}")
        elif (s1 + s2) and not a.merge:
            print(f"  = {name}/ (kept yours)")

    created += write_if_missing(dest / ".gitignore", GITIGNORE)

    types = wf.workspace_types(dest)
    skills = wf.skills_for(types)
    print(f"\n  {created} files created" + (f", {skipped} left alone" if skipped else ""))
    print(f"""
Next:
  1. Install the skills for these workflows:
       {REPO_ROOT}/skills/engine-setup/scripts/install_skills.sh \\
         --workspace {dest}
     (skills: {', '.join(skills)})
  2. Copy shared/.env.example to shared/.env and add any keys you need
  3. Tell your agent:  run engine-setup
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())

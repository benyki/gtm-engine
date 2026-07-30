#!/usr/bin/env python3
"""Create a gtm-engine workspace inside your project.

Usage:
    scaffold_workspace.py [project_dir] --workflow seo
    scaffold_workspace.py . --workflow seo,outreach
    scaffold_workspace.py . --workflow all
    scaffold_workspace.py . --workflow newsletter      # custom workflow
    scaffold_workspace.py . --workflow video --merge

    project_dir   where to create it (default: current directory)
    --workflow    required. Names that already have skills/engine-N or a
                  starter template under templates/workspace/templates/N are
                  discovered automatically via `workflows.py list`. Any other
                  name is fine too — you get templates/<name>/ plus the shared
                  loop files; the agent fills in the rest.
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
TEMPLATE = REPO_ROOT / "templates" / "workspace"

# Shared spine — always created. Config files are copied whole; the agent
# trims what this brand doesn't need. No per-workflow path registry.
SHARED = (
    "config/brand.md",
    "config/channels.json",
    "config/sources.json",
    "config/experiments.json",
    "config/.env.example",
    "runs/index.csv",
    "reports/.gitkeep",
    "inputs/queue/.gitkeep",
    "inputs/best/.gitkeep",
    "inputs/swipe/.gitkeep",
    "inputs/assets/.gitkeep",
    "inputs/audience/.gitkeep",
    "state/published.csv",
    "state/crm.csv",
)


def copy_path(src: Path, dst: Path, merge: bool) -> tuple[int, int]:
    """Copy a file or directory tree. Never overwrite existing files."""
    created = skipped = 0
    if src.is_dir():
        for item in sorted(src.rglob("*")):
            rel = item.relative_to(src)
            target = dst / rel
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if target.exists():
                skipped += 1
                if not merge:
                    print(f"  = {rel} (kept yours)")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            created += 1
        return created, skipped

    if dst.exists():
        return 0, 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return 1, 0


def ensure_gitkeep_dir(path: Path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    keep = path / ".gitkeep"
    if keep.exists():
        return False
    keep.write_text("")
    return True


def set_active_workflow(channels: dict, name: str) -> dict:
    out = dict(channels)
    if not (out.get("active_workflow") or "").strip():
        out["active_workflow"] = name
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("project_dir", nargs="?", default=".")
    ap.add_argument(
        "--workflow", "-w", required=True,
        help="workflow name(s), comma-separated, or 'all' for every known one",
    )
    ap.add_argument("--name", default="workflows",
                    help="workspace folder name (default: workflows) — "
                         "use another name for a second brand/ICP")
    ap.add_argument("--merge", action="store_true",
                    help="add missing files to an existing workspace")
    a = ap.parse_args()

    try:
        workflows = wf.parse_workflows(a.workflow)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not TEMPLATE.is_dir():
        print(f"error: template not found at {TEMPLATE}", file=sys.stderr)
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
        print(f"  --merge --workflow {a.workflow}")
        print("      add only the files you're missing for these workflows")
        print(f"  --name workflows2  scaffold alongside it\n")
        return 1

    known = set(wf.list_known())
    custom = [name for name in workflows if name not in known]

    print(f"\nCreating workspace: {dest}")
    print(f"  workflows: {', '.join(workflows)}")
    for name in custom:
        print(f"  note: '{name}' has no shipped skill/template — "
              f"templates/{name}/ is created empty. Write templates, "
              f"register experiments, enable channels; engine-loop handles "
              f"the scoring.")
    print()

    created = skipped = 0

    for rel in SHARED:
        src = TEMPLATE / rel
        dst = dest / rel
        if not src.exists():
            if rel.endswith("/.gitkeep"):
                if ensure_gitkeep_dir(dest / Path(rel).parent):
                    created += 1
                    print(f"  + {Path(rel).parent}/")
                continue
            print(f"  ! missing in template: {rel}", file=sys.stderr)
            continue

        if rel == "config/channels.json":
            if dst.exists() and a.merge:
                data = set_active_workflow(
                    json.loads(dst.read_text()), workflows[0],
                )
                dst.write_text(json.dumps(data, indent=2) + "\n")
                print("  ~ config/channels.json  (active_workflow if empty)")
                continue
            data = set_active_workflow(
                json.loads(src.read_text()), workflows[0],
            )
            if dst.exists():
                skipped += 1
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(json.dumps(data, indent=2) + "\n")
                created += 1
                print(f"  + config/channels.json  (active_workflow={workflows[0]})")
            continue

        c, s = copy_path(src, dst, a.merge)
        created += c
        skipped += s
        if c:
            print(f"  + {rel}{'/' if src.is_dir() else ''}")
        elif s and not a.merge:
            print(f"  = {rel} (kept yours)")

    # Per-workflow template folder — copy starter if we have one, else empty.
    for name in workflows:
        src = TEMPLATE / "templates" / name
        dst = dest / "templates" / name
        if src.is_dir():
            c, s = copy_path(src, dst, a.merge)
            created += c
            skipped += s
            if c:
                print(f"  + templates/{name}/")
            elif s and not a.merge:
                print(f"  = templates/{name}/ (kept yours)")
        elif ensure_gitkeep_dir(dst):
            created += 1
            print(f"  + templates/{name}/")

    marker_before = (dest / "config" / wf.MARKER_NEW).is_file() \
        or (dest / "config" / wf.MARKER_OLD).is_file()
    before = set(wf.read_workflows(dest)) if marker_before else set()
    wf.write_workflows(dest, workflows)
    installed = wf.read_workflows(dest)
    if set(installed) != before or not marker_before:
        created += 1
        print(f"  + config/workflows.json  ({', '.join(installed)})")

    gitignore = dest / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "# secrets\n"
            "config/.env\n"
            ".env\n"
            "*.local\n"
            "\n# skills/ is a symlink to ~/.agents/skills — recreated by install_skills.sh\n"
            "skills/\n"
            "\n# build junk — site/ appears if engine-seo scaffolds you a website\n"
            "site/node_modules/\n"
            "site/dist/\n"
            "site/.astro/\n"
            "site/.next/\n"
            "\n# python\n"
            "__pycache__/\n"
            "*.pyc\n"
            "\n# video renders are large; keep the finished file, not the scratch\n"
            "runs/**/output/*.tmp.*\n"
        )
        created += 1
        print("  + .gitignore")

    skills = wf.skills_for(installed)
    print(f"\n  {created} files created" + (f", {skipped} left alone" if skipped else ""))
    print(f"""
Next:
  1. Install skills for these workflows:
       {REPO_ROOT}/skills/engine-setup/scripts/install_skills.sh \\
         --workspace {dest} --workflow {','.join(installed)}
     (skills: {', '.join(skills)})
  2. Copy config/.env.example to config/.env and add any keys you need
  3. Tell your agent:  run engine-setup
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())

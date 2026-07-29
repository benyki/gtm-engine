#!/usr/bin/env python3
"""Create a gtm-engine workspace inside your project.

The repo holds the logic; this folder holds everything that is yours —
brand, inputs, templates, runs, numbers, reports. Nothing here is ever
touched by `git pull` in the engine repo.

Usage:
    scaffold_workspace.py [project_dir] [--name workflows] [--merge]

    project_dir   where to create it (default: current directory)
    --merge       fill in missing files in an existing workspace
                  (never overwrites anything that already exists)
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = REPO_ROOT / "templates" / "workspace"


def copy_tree(src: Path, dst: Path, merge: bool) -> tuple[int, int]:
    created = skipped = 0
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir", nargs="?", default=".")
    ap.add_argument("--name", default="workflows",
                    help="workspace folder name (default: workflows)")
    ap.add_argument("--merge", action="store_true",
                    help="add missing files to an existing workspace")
    a = ap.parse_args()

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
        print(f"  --merge            add only the files you're missing")
        print(f"  --name workflows2  scaffold alongside it\n")
        return 1

    print(f"\nCreating workspace: {dest}\n")
    created, skipped = copy_tree(TEMPLATE, dest, a.merge)

    # A workspace holds secrets and personal data. Never let it leak upward.
    gitignore = dest / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "# secrets\n"
            "config/.env\n"
            ".env\n"
            "*.local\n"
            "\n# skill symlinks — recreated by install_skills.sh --workspace\n"
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

    print(f"\n  {created} files created" + (f", {skipped} left alone" if skipped else ""))
    print(f"""
Next:
  1. Install skills into this workspace (and every agent on this machine):
       {REPO_ROOT}/skills/engine-setup/scripts/install_skills.sh --workspace {dest}
  2. Copy config/.env.example to config/.env and add your keys
     (your agent will never read .env — only the example, for the names)
  3. Tell your agent:  run engine-setup
     It fills in your brand, picks your workflow, and checks everything works.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())

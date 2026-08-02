#!/usr/bin/env python3
"""Move a v1 workspace to the v2 shape. Dry run unless you pass --apply.

v1 was one folder holding everything: `<project>/workflows/` with `shared/`
and one folder per workflow inside it. v2 splits that into a shared home
(`~/gtm`) and engines that can live anywhere, tracked in `~/gtm/engines.json`.

What this does:

  1. copies `<workspace>/shared/` into `~/gtm/shared/`, never overwriting a
     file that is already there (so a second project's brand.md will NOT
     clobber the first; it is reported instead)
  2. copies `published/` and the root `AGENTS.md` / `CLAUDE.md` if the home
     does not have them yet
  3. renames each `workflow.json` to `engine.json` and fills in name, home
     and project
  4. registers every engine in `~/gtm/engines.json`

Engine folders STAY WHERE THEY ARE by default. They are your data, agents have
paths to them, and the registry means they no longer need to sit anywhere in
particular. Pass --move to relocate them into `~/gtm/engines/` instead.

Nothing is deleted. After a successful run the old `shared/` is left on disk;
remove it yourself once you are happy.

Usage:
    migrate_v1.py <workspace> [--home ~/gtm] [--project NAME] [--move] [--apply]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import registry as reg  # noqa: E402

LEGACY = "workflow.json"


def short(p: Path) -> str:
    s = str(p)
    h = str(Path.home())
    return "~" + s[len(h):] if s.startswith(h) else s


def v1_engines(ws: Path) -> list[Path]:
    return sorted(p for p in ws.iterdir()
                  if p.is_dir() and ((p / LEGACY).is_file() or (p / "engine.json").is_file()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workspace")
    ap.add_argument("--home", default="")
    ap.add_argument("--project", default="")
    ap.add_argument("--move", action="store_true",
                    help="move engine folders into <home>/engines/ as well")
    ap.add_argument("--apply", action="store_true",
                    help="actually write; without it this only prints the plan")
    a = ap.parse_args()

    ws = Path(a.workspace).expanduser().resolve()
    if not (ws / "shared").is_dir():
        print(f"error: {ws} has no shared/, so it is not a v1 workspace",
              file=sys.stderr)
        return 1
    home = reg.home_path(a.home)
    project = a.project or ws.parent.name
    plan: list[str] = []
    conflicts: list[str] = []

    def copy_missing(src: Path, dst: Path, label: str) -> None:
        for item in sorted(src.rglob("*")):
            if item.is_dir():
                continue
            target = dst / item.relative_to(src)
            if target.exists():
                conflicts.append(f"{label}/{item.relative_to(src)} already in the home, kept")
                continue
            plan.append(f"copy  {label}/{item.relative_to(src)}  ->  {short(target)}")
            if a.apply:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

    copy_missing(ws / "shared", home / "shared", "shared")
    if (ws / "published").is_dir():
        copy_missing(ws / "published", home / "published", "published")
    for name in ("AGENTS.md", "CLAUDE.md"):
        src = ws / name
        if src.is_file() and not (home / name).exists():
            plan.append(f"copy  {name}  ->  {short(home / name)}")
            if a.apply:
                (home / name).write_text(src.read_text())

    for wd in v1_engines(ws):
        dest = wd
        if a.move:
            dest = home / "engines" / f"engine-{wd.name}-{project}"
            plan.append(f"move  {short(wd)}  ->  {short(dest)}")
            if a.apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(wd), str(dest))

        legacy, marker = dest / LEGACY, dest / "engine.json"
        meta = {}
        if legacy.is_file():
            try:
                meta = json.loads(legacy.read_text())
            except json.JSONDecodeError:
                meta = {}
        elif marker.is_file():
            try:
                meta = json.loads(marker.read_text())
            except json.JSONDecodeError:
                meta = {}
        typ = str(meta.get("type") or "").strip() or wd.name
        # Names are the registry's key, so a `seo/` arriving from a second
        # project cannot take a name the first one already holds. The project
        # is what tells them apart.
        name = dest.name
        if reg.conflict(home, name, dest):
            name = f"engine-{typ}-{project}"
        taken = reg.conflict(home, name, dest)
        if taken:
            conflicts.append(f"{dest.name}: {name!r} is already registered at "
                             f"{short(taken)}, so this one was NOT registered. "
                             f"Pick a name and run: registry.py add <name> {short(dest)}")
            continue
        meta.update({"name": name, "type": typ, "home": short(home),
                     "project": project})
        plan.append(f"write {short(marker)}  (type {typ}, home {short(home)})")
        plan.append(f"register {name}  ->  {short(dest)}")
        if a.apply:
            marker.write_text(json.dumps(meta, indent=2) + "\n")
            if legacy.is_file():
                legacy.unlink()
            reg.register(home, name, dest, typ, project)

    print(f"\n{'Migrating' if a.apply else 'Would migrate'}: {short(ws)}  ->  {short(home)}")
    print(f"project: {project}\n")
    for line in plan:
        print(f"  {line}")
    if conflicts:
        print("\nKept the home's version of these (nothing was overwritten):")
        for c in conflicts:
            print(f"  ! {c}")
        print("\nMerge anything you still need by hand.")
    if not a.apply:
        print(f"\nDry run. Re-run with --apply to write.\n")
    else:
        print(f"\nDone. {short(ws)}/shared is still on disk; delete it when you are happy.")
        print(f"Check the result: doctor.py --home {short(home)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

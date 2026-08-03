#!/usr/bin/env python3
"""Create the gtm home and the engine folders.

Two separate things, on purpose:

  THE HOME (`~/gtm` by default) holds everything shared between engines:
  `shared/` (brand, channels, keys, assets, insights), the docs, `AGENTS.md`,
  `published/`, and `engines.json` (the registry: which engines exist and
  where they live). One home per person is the intended shape.

  AN ENGINE is one self-contained folder (engine.json, experiments.json,
  sources.json, templates/, inputs/, runs/, reports/) that can live ANYWHERE:
  `~/gtm/engines/` if you want them all in one place, or `<project>/engines/`
  if you would rather keep each project's engines with the project. Every
  engine is written into `engines.json`, because nothing scans for them.

Usage:
    scaffold.py                                  # home + the four defaults in ~/gtm/engines
    scaffold.py --engine outreach                # home + one engine
    scaffold.py --engine all --at ./engines --project acme
    scaffold.py --engine outreach:outreach --at ~/code/acme/engines --project acme
    scaffold.py --home ~/gtm --engine none       # the home only

    --home PATH     where the shared home lives (default: ~/gtm, or $GTM_HOME)
    --engine LIST   comma list of name[:type], `all` (default), or `none`.
                    The NAME is the folder, the TYPE picks the starter and the
                    skill. `engine-outreach-acme:outreach` is an outreach
                    engine for one project. A name with no shipped type is a
                    custom engine (generic scaffold).
    --at PATH       where the engine FOLDERS go (default: <home>/engines).
                    Point it at `<project>/engines` to keep a project's
                    engines with the project.
    --project NAME  the project these engines grow. Recorded in engine.json,
                    and used for the `engine-<type>-<project>` folder naming
                    when the engines live in the shared home.
    --merge         fill in missing files in something that already exists
                    (never overwrites anything)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import engines as eng  # noqa: E402
import registry as reg  # noqa: E402

REPO_ROOT = _HERE.parents[2]
TEMPLATE = REPO_ROOT / "template"
HOME_SRC = TEMPLATE / "home"
SHARED_SRC = HOME_SRC / "shared"
PUBLISHED_SRC = HOME_SRC / "published"
STARTERS = TEMPLATE / "engines"
DOCS_SRC = REPO_ROOT / "docs"
# The parts every engine folder has whatever its type: runs/index.csv,
# inputs/queue/, reports/, templates/losers/, empty experiments and sources.
# It sits among the starters but is not a type: the leading underscore keeps
# it out of engines.py discovery, so nobody can scaffold `_every-engine/`.
BASE_SRC = STARTERS / "_every-engine"

HOME_GITIGNORE = """\
# secrets
shared/.env
.env
*.local

# skills/ is a symlink to ~/.agents/skills, recreated by install_skills.sh
skills/

# docs/engine/ is a symlink to the clone's docs, refreshed by git pull
docs/engine/

# python
__pycache__/
*.pyc

# published/ is your archive of shipped artifacts: keep the folder, not the media
published/*
!published/README.md
"""

ENGINE_GITIGNORE = """\
# secrets never live in an engine; they live in <home>/shared/.env
.env
*.local

# build junk: site/ appears if engine-seo scaffolds you a website
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


ENGINE_AGENTS = """\
# {name}

A gtm-engine engine: one growth channel, owning everything it needs.

**Its home is `{home}`.** Read `{home}/AGENTS.md`: the brand voice, the
accounts, the keys and the house rules live there, shared with every engine.

Log every piece you make with `runlog.py new --engine {name}`. Never publish or
send without an explicit yes. Never read `{home}/shared/.env`.
"""

ENGINE_CLAUDE = """\
# CLAUDE.md

Read **[AGENTS.md](AGENTS.md)** here, then `{home}/AGENTS.md`, which holds the
brand, the accounts and the house rules shared by every engine.

@AGENTS.md
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


def short(p: Path) -> str:
    s = str(p)
    h = str(Path.home())
    return "~" + s[len(h):] if s.startswith(h) else s


def engine_json(name: str, typ: str, home: Path, project: str,
                known: bool) -> str:
    body = {
        "name": name,
        "type": typ,
        "home": short(home),
        "project": project,
        "goal": "",
        "primary_metric": "",
        "_primary_metric_hint": "The one number THIS engine optimises. "
                                "A channel can override it in shared/channels.json.",
        "_home_hint": "Everything shared lives in `home`: brand.md, channels.json, "
                      ".env, assets/, insights.md. If you MOVE this folder, update "
                      "its entry in <home>/engines.json in the same breath: nothing "
                      "scans for engines, so an unregistered one is invisible.",
    }
    if not known:
        body["_comment"] = ("Custom engine, no shipped skill. engine-loop runs it "
                            "through the same traces as the built-ins. Copy the "
                            "whole folder to a new name for a second one.")
    return json.dumps(body, indent=2) + "\n"


def scaffold_home(home: Path, merge: bool) -> tuple[int, int]:
    """The one shared folder. Safe to re-run: it only fills gaps."""
    created = skipped = 0
    if home.exists() and not merge and (home / "shared").exists():
        print(f"\n{home} already exists, filling in anything missing.\n")

    c, s = copy_tree(SHARED_SRC, home / "shared")
    created, skipped = created + c, skipped + s
    if c:
        print("  + shared/  (brand, channels, .env.example, assets/, docs/, insights.md)")

    # Root files of the home template: AGENTS.md (what every agent reads) and
    # CLAUDE.md (a pointer to it). Dotfiles do not come across, which is what
    # keeps .gtm-template out of a real home.
    for item in sorted(HOME_SRC.iterdir()):
        if not item.is_file() or item.name.startswith("."):
            continue
        c = write_if_missing(home / item.name, item.read_text())
        created += c
        skipped += 0 if c else 1
        if c:
            print(f"  + {item.name}")

    if PUBLISHED_SRC.is_dir():
        c, s = copy_tree(PUBLISHED_SRC, home / "published")
        created, skipped = created + c, skipped + s
        if c:
            print("  + published/  (what actually shipped, safe to empty)")

    # The engine's own docs, readable from the home and refreshed by git pull.
    docs = home / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    link = docs / "engine"
    if not link.exists() and not link.is_symlink() and DOCS_SRC.is_dir():
        try:
            link.symlink_to(DOCS_SRC, target_is_directory=True)
            created += 1
            print(f"  + docs/engine -> {short(DOCS_SRC)}  (the shipped docs)")
        except OSError:
            c, s = copy_tree(DOCS_SRC, docs / "engine")
            created, skipped = created + c, skipped + s

    created += write_if_missing(home / ".gitignore", HOME_GITIGNORE)
    if not (home / reg.REGISTRY).is_file():
        reg.save(home, {"version": reg.VERSION, "engines": []})
        created += 1
        print(f"  + {reg.REGISTRY}  (the registry: every engine and where it lives)")
    return created, skipped


def scaffold_engine(dest: Path, name: str, typ: str, home: Path,
                    project: str, merge: bool) -> tuple[int, int]:
    """One engine folder, anywhere on disk, registered to `home`."""
    known = typ in set(eng.list_known())
    starter = STARTERS / typ
    created = skipped = 0

    if starter.is_dir():
        c, s = copy_tree(starter, dest)
        created, skipped = created + c, skipped + s
    c, s = copy_tree(BASE_SRC, dest)
    created, skipped = created + c, skipped + s

    # The starter ships a stub engine.json; a real one records its identity.
    marker = dest / "engine.json"
    if marker.is_file():
        try:
            meta = json.loads(marker.read_text())
        except json.JSONDecodeError:
            meta = {}
        merged = json.loads(engine_json(name, typ, home, project, known))
        merged.update({k: v for k, v in meta.items()
                       if v not in ("", None) and not k.startswith("_")})
        merged.update({"name": name, "type": typ, "home": short(home),
                       "project": project})
        marker.write_text(json.dumps(merged, indent=2) + "\n")
    else:
        created += write_if_missing(marker, engine_json(name, typ, home, project, known))

    created += write_if_missing(dest / ".gitignore", ENGINE_GITIGNORE)

    # An engine that lives away from the home is opened on its own, in its own
    # project, by an agent that will never see ~/gtm/AGENTS.md unless something
    # tells it to. That something is this file.
    if home.resolve() not in dest.resolve().parents:
        created += write_if_missing(dest / "AGENTS.md",
                                    ENGINE_AGENTS.format(name=name, home=short(home)))
        created += write_if_missing(dest / "CLAUDE.md",
                                    ENGINE_CLAUDE.format(home=short(home)))

    reg.register(home, name, dest, typ, project)
    return created, skipped


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--home", default="")
    ap.add_argument("--engine", "--workflow", "-e", dest="engine", default="all")
    ap.add_argument("--at", default="")
    ap.add_argument("--project", default="")
    ap.add_argument("--merge", action="store_true")
    a = ap.parse_args()

    for d in (SHARED_SRC, BASE_SRC):
        if not d.is_dir():
            print(f"error: template not found at {d}", file=sys.stderr)
            return 1

    home = reg.home_path(a.home)
    raw = (a.engine or "").strip().lower()
    try:
        pairs = [] if raw == "none" else eng.parse_engines(a.engine)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    at = Path(a.at).expanduser().resolve() if a.at else home / "engines"
    in_home = at == (home / "engines") or at == home

    print(f"\nHome: {short(home)}")
    created, skipped = scaffold_home(home, a.merge)

    if pairs:
        print(f"\nEngines: {short(at)}")
    for name, typ in pairs:
        # A bare type in the shared home gets the long name, because every
        # project's engines sit side by side in there.
        folder = eng.folder_name(typ, a.project, in_home) if name == typ else name
        dest = at / folder
        # Two engines can never share a name: the registry is keyed on it, so
        # the second would make the first unreachable. The project name is the
        # natural way out, which is exactly what `engine-<type>-<project>` is.
        taken = reg.conflict(home, folder, dest)
        if taken and a.project and name == typ:
            folder = eng.folder_name(typ, a.project, in_home=True)
            dest = at / folder
            taken = reg.conflict(home, folder, dest)
        if taken:
            print(f"\nerror: an engine called {folder!r} is already registered at "
                  f"{short(taken)}.\n       Give this one a name of its own: "
                  f"--engine engine-{typ}-<project>:{typ}"
                  f"{'' if a.project else ', or pass --project <name>'}\n",
                  file=sys.stderr)
            return 1
        existed = dest.exists()
        c, s = scaffold_engine(dest, folder, typ, home, a.project, a.merge)
        created, skipped = created + c, skipped + s
        tag = "" if folder == typ else f"  (type {typ})"
        if c:
            print(f"  + {folder}/{tag}")
        elif existed:
            print(f"  = {folder}/ (kept yours, registered)")

    types = eng.home_types(home)
    skills = eng.skills_for(types)
    print(f"\n  {created} files created" + (f", {skipped} left alone" if skipped else ""))
    print(f"""
Next:
  1. Install the skills for these engines:
       {REPO_ROOT}/skills/engine-setup/scripts/install_skills.sh --home {short(home)}
     (skills: {', '.join(skills)})
  2. Copy {short(home)}/shared/.env.example to shared/.env and add any keys you need
  3. Tell your agent:  run engine-setup

Every engine above is listed in {short(home / reg.REGISTRY)}. If you ever move
one, update it there in the same breath, or nothing will find it.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())

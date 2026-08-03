#!/usr/bin/env python3
"""Tiny shared helpers for scaffold / install / doctor.

Convention, not a registry of types:
  - core skills always install: engine-setup, engine-loop
  - an engine folder's TYPE (engine.json) maps to skill engine-<type>,
    but only if that skill folder exists
  - the folder NAME is free. `engine-outreach-acme/` with type "outreach" is
    an outreach engine for the acme project; anything without a shipped type
    is custom (generic scaffold; the agent supplies the judgement)

Where engines LIVE is a different question, answered by `registry.py` and
`~/gtm/engines.json`. This module only knows about types, names and skills.

Usage:
    engines.py skills seo,outreach-acme:outreach
    engines.py list          # types that ship a skill or starter
    engines.py name outreach --project acme --in-home
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
STARTERS_DIR = REPO_ROOT / "template" / "engines"

CORE_SKILLS = ("engine-setup", "engine-loop")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

# A skill that reads another skill's references must not be installed alone.
# engine-social is a format layer on engine-seo: subject finding and browser
# research live there and are used as-is.
SKILL_DEPS = {
    "engine-social": ("engine-seo",),
}


def list_known() -> list[str]:
    """Engine TYPES that ship a skill or a starter. Discovery only."""
    names: list[str] = []
    if SKILLS_DIR.is_dir():
        for p in sorted(SKILLS_DIR.iterdir()):
            if not p.name.startswith("engine-") or p.name in CORE_SKILLS:
                continue
            if (p / "SKILL.md").is_file():
                names.append(p.name.removeprefix("engine-"))
    if STARTERS_DIR.is_dir():
        for p in sorted(STARTERS_DIR.iterdir()):
            # `_`-prefixed folders are shared scaffold parts, not engine types.
            # `_every-engine/` is merged into every folder created.
            if p.name.startswith("_"):
                continue
            if p.is_dir() and p.name not in names and NAME_RE.match(p.name):
                names.append(p.name)
    return names


def folder_name(typ: str, project: str = "", in_home: bool = False) -> str:
    """What to call an engine folder.

    In a project (`<project>/engines/`) the parent path already says which
    project it belongs to, so the folder is just the type: `outreach/`.

    In the shared home (`~/gtm/engines/`) every project's engines sit side by
    side, so a bare `outreach/` says nothing: `engine-outreach-acme/`.
    """
    if in_home and project:
        return f"engine-{typ}-{project}"
    return typ


def parse_engines(raw: str | None) -> list[tuple[str, str]]:
    """Parse '--engine' input into (name, type) pairs.

    Forms: 'outreach' (name = type), 'engine-outreach-acme:outreach'
    (a second instance of a type), 'newsletter' (custom, type = name),
    'all' (every known type, name = type). Empty/None means all: the default
    scaffold is one folder per shipped engine.
    """
    known = list_known()
    if raw is None or raw.strip() == "" or raw.strip().lower() == "all":
        return [(t, t) for t in known]
    out: list[tuple[str, str]] = []
    for part in raw.strip().lower().split(","):
        part = part.strip()
        if not part:
            continue
        name, _, typ = part.partition(":")
        typ = typ or name
        for label, v in (("name", name), ("type", typ)):
            if not NAME_RE.match(v):
                raise ValueError(
                    f"invalid engine {label} {v!r}: lowercase letters, "
                    f"digits, - and _ only"
                )
        if name not in [n for n, _ in out]:
            out.append((name, typ))
    if not out:
        raise ValueError("no engines given")
    return out


def skill_for(engine_type: str) -> str | None:
    name = f"engine-{engine_type}"
    if (SKILLS_DIR / name / "SKILL.md").is_file():
        return name
    return None


def skills_for(types: list[str]) -> list[str]:
    names = list(CORE_SKILLS)
    for t in types:
        skill = skill_for(t)
        if not skill:
            continue
        for name in (skill, *SKILL_DEPS.get(skill, ())):
            # A dependency still has to exist as a skill folder.
            if name not in names and (SKILLS_DIR / name / "SKILL.md").is_file():
                names.append(name)
    return names


def engine_types(paths: list[Path]) -> list[str]:
    """Types of a list of engine folders (from engine.json, or the folder name)."""
    types: list[str] = []
    for p in paths:
        t = ""
        for marker in ("engine.json", "workflow.json"):
            f = p / marker
            if not f.is_file():
                continue
            try:
                t = (json.loads(f.read_text()).get("type") or "").strip()
            except (json.JSONDecodeError, OSError):
                t = ""
            break
        t = t or p.name
        if t not in types:
            types.append(t)
    return types


def home_types(home: Path) -> list[str]:
    """Types of every engine registered to a home, plus any engine folders
    sitting in it unregistered (so a machine mid-migration installs right)."""
    sys.path.insert(0, str(_HERE))
    import registry  # noqa: E402  (same folder, not a package)

    paths = [Path(str(e.get("path"))).expanduser() for e in registry.entries(home)]
    paths = [p for p in paths if registry.is_engine(p)]
    paths += registry.unregistered(home)
    return engine_types(paths)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("list", "skills", "name"))
    ap.add_argument("args", nargs="*")
    ap.add_argument("--project", default="")
    ap.add_argument("--in-home", action="store_true")
    a = ap.parse_args()

    if a.cmd == "list":
        print(" ".join(list_known()))
        return 0
    if a.cmd == "name":
        if not a.args:
            print("usage: engines.py name TYPE [--project NAME] [--in-home]",
                  file=sys.stderr)
            return 2
        print(folder_name(a.args[0], a.project, a.in_home))
        return 0
    try:
        pairs = parse_engines(a.args[0] if a.args else "")
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(" ".join(skills_for([t for _, t in pairs])))
    return 0


if __name__ == "__main__":
    sys.exit(main())

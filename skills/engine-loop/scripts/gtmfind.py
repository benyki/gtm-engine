#!/usr/bin/env python3
"""Find the gtm home and the engines. One implementation, imported by every
loop script.

Layout (v2):

  ~/gtm/                  THE HOME. everything shared between engines:
    .env                  keys, at the root of the home like any project
    shared/               brand.md, channels.json, assets/, insights.md
    engines.json          the registry: which engines exist and where they live
    engines/              the default home for engine folders, when you keep
                          them in one place

  <anywhere>/engines/<name>/    an engine folder can live anywhere: inside the
                                project it grows, on another disk, in another
                                repo. It is self-contained (engine.json,
                                experiments.json, sources.json, templates/,
                                inputs/, runs/, reports/) and it knows its home.

Resolution order for the home:
  1. --home flag (explicit always wins)
  2. GTM_HOME environment variable
  3. ~/gtm
  4. the `home` key of the engine.json in (or above) the cwd
  5. a v1 workspace in or above the cwd (a dir with shared/ and workflow.json
     children), which still works and prints a migration hint

Resolution order for one engine, by name:
  1. the registry at <home>/engines.json
  2. <home>/engines/<name>, <cwd>/engines/<name>, <cwd>/<name>, <home>/<name>
  3. a path, if what you passed is one

Anything found outside the registry is usable but reported: the registry is
how every other engine finds it, so a stray engine is a real problem, not a
detail. See `gtm_hygiene()`.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SHARED = "shared"
REGISTRY = "engines.json"
ENGINE_MARKER = "engine.json"
LEGACY_MARKER = "workflow.json"
DEFAULT_HOME = Path.home() / "gtm"

# Files that identify shared/ as ours (any one is enough).
_SHARED_FILES = ("channels.json", "brand.md", "insights.md")

# The engine repo's own template folder is the scaffold SOURCE, not a home.
# This marker at its root keeps it from ever being picked up.
TEMPLATE_MARKER = ".gtm-template"

_warned: set[str] = set()


def warn(msg: str) -> None:
    """One warning per message per process. Never fatal."""
    if msg not in _warned:
        _warned.add(msg)
        print(f"note: {msg}", file=sys.stderr)


def short(p: Path) -> str:
    s = str(p)
    h = str(Path.home())
    return "~" + s[len(h):] if s.startswith(h) else s


# --- the home --------------------------------------------------------------

def is_home(p: Path) -> bool:
    if (p / TEMPLATE_MARKER).is_file():
        return False
    shared = p / SHARED
    return shared.is_dir() and any((shared / f).is_file() for f in _SHARED_FILES)


def _check(p: Path) -> Path:
    if is_home(p):
        return p
    sys.exit(f"error: no shared/ found in {p}, so that is not a gtm home")


def _home_from_engine(start: Path) -> Path | None:
    """An engine folder records its home. Walk up from the cwd to find one."""
    for base in (start, *start.parents):
        for marker in (ENGINE_MARKER, LEGACY_MARKER):
            f = base / marker
            if not f.is_file():
                continue
            try:
                home = (json.loads(f.read_text()).get("home") or "").strip()
            except (json.JSONDecodeError, OSError):
                home = ""
            if home:
                cand = Path(home).expanduser()
                if is_home(cand):
                    return cand
        if base == Path.home():
            break
    return None


def _legacy_workspace(start: Path) -> Path | None:
    """A v1 workspace: one folder holding shared/ AND the workflow folders."""
    for base in (start, *start.parents):
        for cand in (base, base / "workflows"):
            if is_home(cand) and any(
                (c / LEGACY_MARKER).is_file() for c in cand.iterdir() if c.is_dir()
            ):
                return cand
        if base == Path.home():
            break
    return None


def find_home(explicit: str | None = None) -> Path:
    if explicit:
        return _check(Path(explicit).expanduser().resolve())

    env = (os.environ.get("GTM_HOME") or os.environ.get("GTM_WORKSPACE") or "").strip()
    if env:
        return _check(Path(env).expanduser().resolve())

    if is_home(DEFAULT_HOME):
        return DEFAULT_HOME.resolve()

    cwd = Path.cwd()
    from_engine = _home_from_engine(cwd)
    if from_engine:
        return from_engine.resolve()

    legacy = _legacy_workspace(cwd)
    if legacy:
        warn(
            f"{short(legacy)} is a v1 workspace (shared/ and the engines in one "
            f"folder). It still works. To move to ~/gtm: "
            f"python3 ~/.gtm-engine/skills/engine-setup/scripts/migrate_v1.py "
            f"{short(legacy)}"
        )
        return legacy.resolve()

    sys.exit(
        "error: no gtm home found. Expected ~/gtm. Pass --home, set GTM_HOME, "
        "or run engine-setup to create one."
    )


# --- the registry ----------------------------------------------------------

def read_registry(home: Path) -> list[dict]:
    """Registered engines, as written by the scaffolder. [] when absent."""
    f = home / REGISTRY
    if not f.is_file():
        return []
    try:
        data = json.loads(f.read_text())
    except (json.JSONDecodeError, OSError):
        warn(f"{short(f)} is not readable JSON, falling back to a folder scan")
        return []
    items = data.get("engines") if isinstance(data, dict) else data
    return [e for e in items if isinstance(e, dict) and e.get("path")] if items else []


def _engine_path(entry: dict) -> Path:
    return Path(str(entry["path"])).expanduser()


def is_engine(p: Path) -> bool:
    return p.is_dir() and ((p / ENGINE_MARKER).is_file() or (p / LEGACY_MARKER).is_file())


def list_engines(home: Path | None = None) -> list[Path]:
    """Every engine this home knows about: registered first, then any found in
    the usual places. Registered paths that no longer exist are reported."""
    home = home or find_home()
    out: list[Path] = []
    seen: set[Path] = set()

    for entry in read_registry(home):
        p = _engine_path(entry)
        if p in seen:
            continue
        seen.add(p)
        if is_engine(p):
            out.append(p)
        else:
            warn(
                f"{entry.get('name') or p.name} is registered at {short(p)}, which "
                f"is gone. Fix the path in {short(home / REGISTRY)} or run "
                f"doctor.py --fix."
            )

    for parent in (home / "engines", home):
        if not parent.is_dir():
            continue
        for p in sorted(parent.iterdir()):
            if p.resolve() in {s.resolve() for s in seen if s.exists()} or not is_engine(p):
                continue
            seen.add(p)
            out.append(p)
            warn(
                f"{short(p)} is an engine but is not in {REGISTRY}. Add it: "
                f"nothing outside this folder can find it otherwise."
            )
    return out


def find_engine(home: Path | None, name: str) -> Path:
    """The engine called `name`, wherever it lives."""
    home = home or find_home()

    for entry in read_registry(home):
        if str(entry.get("name") or "").strip() == name:
            p = _engine_path(entry)
            if is_engine(p):
                return p
            sys.exit(
                f"error: engine {name!r} is registered at {p}, which is not there "
                f"any more. Fix the path in {home / REGISTRY} or run doctor.py --fix."
            )

    for cand in (
        Path(name).expanduser(),
        home / "engines" / name,
        Path.cwd() / "engines" / name,
        Path.cwd() / name,
        home / name,
    ):
        if is_engine(cand):
            warn(
                f"found {name!r} at {short(cand)} but it is not in {REGISTRY}. "
                f"Register it so the other engines and the weekly report can see it."
            )
            return cand.resolve()

    have = [p.name for p in list_engines(home)]
    hint = (
        f" Engines here: {', '.join(have)}." if have else
        " No engines yet. Scaffold one with engine-setup, or copy an existing folder."
    )
    sys.exit(f"error: no engine {name!r} known to {short(home)}.{hint}")


def engine_meta(wd: Path) -> dict:
    """Parsed engine.json (or a v1 workflow.json); {} when missing or broken."""
    for marker in (ENGINE_MARKER, LEGACY_MARKER):
        f = wd / marker
        if not f.is_file():
            continue
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
        return data if isinstance(data, dict) else {}
    return {}


def gtm_hygiene(home: Path) -> list[str]:
    """Problems with the registry, in plain sentences. Empty list is healthy.

    Engines spread across projects only stay findable if engines.json stays
    true, and nothing enforces that but the agent doing the moving.
    """
    problems: list[str] = []
    entries = read_registry(home)
    if not (home / REGISTRY).is_file():
        problems.append(f"{short(home / REGISTRY)} does not exist yet.")
    seen: dict[str, str] = {}
    for e in entries:
        name, p = str(e.get("name") or ""), _engine_path(e)
        if not is_engine(p):
            problems.append(f"{name or p.name}: registered at {short(p)}, not there any more.")
        if name in seen:
            problems.append(f"{name}: registered twice ({seen[name]} and {short(p)}).")
        seen[name] = short(p)
        meta = engine_meta(p)
        if meta and str(meta.get("home") or "").strip():
            recorded = Path(str(meta["home"])).expanduser().resolve()
            if recorded != home.resolve():
                problems.append(
                    f"{name}: its engine.json points home at {short(recorded)}, "
                    f"not {short(home)}."
                )
    known = {_engine_path(e).resolve() for e in entries}
    for parent in (home / "engines", home):
        if parent.is_dir():
            for p in sorted(parent.iterdir()):
                if is_engine(p) and p.resolve() not in known:
                    problems.append(f"{short(p)} is an engine that is not registered.")
    return problems


# --- v1 compatibility ------------------------------------------------------
# Old names, so a script that was not updated keeps working for one release.
find_workspace = find_home
workflow_meta = engine_meta


def list_workflow_dirs(ws: Path) -> list[Path]:
    return list_engines(ws)


def find_workflow_dir(ws: Path, name: str) -> Path:
    return find_engine(ws, name)

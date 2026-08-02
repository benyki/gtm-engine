#!/usr/bin/env python3
"""Read and write `~/gtm/engines.json`, the map of every engine to where it
lives.

An engine folder can sit anywhere: inside the project it grows, in another
repo, on another disk. Nothing scans for them, so **this file is the only way
the rest of the system knows an engine exists**. Keep it true:

  - scaffolding an engine registers it (scaffold.py does this for you)
  - MOVING an engine folder means updating its entry, in the same breath
  - deleting one means removing its entry
  - `doctor.py --fix` repairs what it safely can

Users hand-edit this file, so every write preserves keys we do not know about
and every read tolerates a file that is a little off.

Usage:
    registry.py list [--home PATH]
    registry.py add NAME PATH [--type TYPE] [--project NAME] [--home PATH]
    registry.py mv NAME NEWPATH [--home PATH]
    registry.py rm NAME [--home PATH]
    registry.py prune [--home PATH]        # drop entries whose path is gone
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REGISTRY = "engines.json"
ENGINE_MARKER = "engine.json"
LEGACY_MARKER = "workflow.json"
DEFAULT_HOME = Path.home() / "gtm"
VERSION = 1


def home_path(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("GTM_HOME") or ""
    return Path(raw).expanduser().resolve() if raw.strip() else DEFAULT_HOME


def load(home: Path) -> dict:
    f = home / REGISTRY
    if not f.is_file():
        return {"version": VERSION, "engines": []}
    try:
        data = json.loads(f.read_text())
    except (json.JSONDecodeError, OSError) as e:
        raise SystemExit(f"error: {f} is not readable JSON ({e}). Fix it by hand.")
    if isinstance(data, list):          # tolerate a bare list
        data = {"version": VERSION, "engines": data}
    data.setdefault("version", VERSION)
    data.setdefault("engines", [])
    return data


def save(home: Path, data: dict) -> None:
    home.mkdir(parents=True, exist_ok=True)
    f = home / REGISTRY
    tmp = f.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(f)


def entries(home: Path) -> list[dict]:
    return [e for e in load(home).get("engines", []) if isinstance(e, dict)]


def find(home: Path, name: str) -> dict | None:
    for e in entries(home):
        if str(e.get("name") or "") == name:
            return e
    return None


def is_engine(p: Path) -> bool:
    return p.is_dir() and ((p / ENGINE_MARKER).is_file() or (p / LEGACY_MARKER).is_file())


def register(home: Path, name: str, path: Path, typ: str = "",
             project: str = "") -> str:
    """Add or update one engine. Returns what happened, for printing."""
    data = load(home)
    path = path.expanduser().resolve()
    for e in data["engines"]:
        if str(e.get("name") or "") == name:
            was = e.get("path")
            e.update({"path": str(path)})
            if typ:
                e["type"] = typ
            if project:
                e["project"] = project
            save(home, data)
            return "unchanged" if was == str(path) else f"moved from {was}"
    entry = {"name": name, "type": typ or name, "path": str(path)}
    if project:
        entry["project"] = project
    data["engines"].append(entry)
    data["engines"].sort(key=lambda e: str(e.get("name") or ""))
    save(home, data)
    return "registered"


def conflict(home: Path, name: str, path: Path) -> Path | None:
    """The path already registered under `name`, when it is a DIFFERENT folder
    that still exists. Names are the handle every command uses, so two engines
    can never share one: the second would make the first unreachable."""
    e = find(home, name)
    if not e:
        return None
    other = Path(str(e.get("path") or "")).expanduser().resolve()
    if other == path.expanduser().resolve() or not is_engine(other):
        return None
    return other


def unregister(home: Path, name: str) -> bool:
    data = load(home)
    before = len(data["engines"])
    data["engines"] = [e for e in data["engines"] if str(e.get("name") or "") != name]
    if len(data["engines"]) == before:
        return False
    save(home, data)
    return True


def prune(home: Path) -> list[str]:
    """Drop entries whose folder is gone. Returns the names dropped."""
    data = load(home)
    keep, dropped = [], []
    for e in data["engines"]:
        p = Path(str(e.get("path") or "")).expanduser()
        (keep if is_engine(p) else dropped).append(e)
    if dropped:
        data["engines"] = keep
        save(home, data)
    return [str(e.get("name") or e.get("path")) for e in dropped]


def stale(home: Path) -> list[tuple[str, Path]]:
    out = []
    for e in entries(home):
        p = Path(str(e.get("path") or "")).expanduser()
        if not is_engine(p):
            out.append((str(e.get("name") or p.name), p))
    return out


def unregistered(home: Path) -> list[Path]:
    """Engine folders sitting in the home that nothing has registered."""
    known = {Path(str(e.get("path") or "")).expanduser().resolve()
             for e in entries(home)}
    out = []
    for parent in (home / "engines", home):
        if not parent.is_dir():
            continue
        for p in sorted(parent.iterdir()):
            if is_engine(p) and p.resolve() not in known:
                out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("list", "add", "mv", "rm", "prune"))
    ap.add_argument("args", nargs="*")
    ap.add_argument("--home")
    ap.add_argument("--type", default="")
    ap.add_argument("--project", default="")
    a = ap.parse_args()
    home = home_path(a.home)

    if a.cmd == "list":
        rows = entries(home)
        if not rows:
            print(f"no engines registered in {home / REGISTRY}")
            return 0
        width = max(len(str(e.get("name") or "")) for e in rows)
        for e in rows:
            mark = " " if is_engine(Path(str(e.get("path"))).expanduser()) else "!"
            print(f"{mark} {str(e.get('name') or ''):<{width}}  {e.get('path')}")
        return 0

    if a.cmd == "prune":
        dropped = prune(home)
        print(f"dropped {len(dropped)}: {', '.join(dropped)}" if dropped
              else "nothing to prune")
        return 0

    if a.cmd == "rm":
        if len(a.args) != 1:
            print("usage: registry.py rm NAME", file=sys.stderr)
            return 2
        print("removed" if unregister(home, a.args[0]) else "not registered")
        return 0

    if len(a.args) != 2:
        print(f"usage: registry.py {a.cmd} NAME PATH", file=sys.stderr)
        return 2
    name, path = a.args[0], Path(a.args[1]).expanduser()
    if not is_engine(path):
        print(f"error: {path} has no engine.json, so it is not an engine",
              file=sys.stderr)
        return 1
    print(register(home, name, path, a.type, a.project))
    return 0


if __name__ == "__main__":
    sys.exit(main())

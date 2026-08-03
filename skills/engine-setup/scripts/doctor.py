#!/usr/bin/env python3
"""Check that everything gtm-engine needs is actually in place.

**Optional, a helper and not a step.** Nothing in the engine calls this, no
engine needs it to have passed, and a home that never runs it is a normal home.
Reach for it when something looks off, when you're on an unfamiliar machine, or
when you just want to see the install landed. It changes nothing unless you
pass --fix, and even then only the registry.

**x means genuinely broken; ! is information, not a chore.** The engine is
forgiving by design: a missing channels.json falls back to defaults, an empty
templates/ is the documented first run, runs/ and reports/ are created on first
write, so this check never reports those as blocking. Nothing here is a
required-shape audit: a home someone built by hand, or trimmed to the two
engines they use, is a valid home.

The one thing worth taking seriously is the REGISTRY. Engines can live
anywhere, so `<home>/engines.json` is the only thing that knows they exist. An
engine that has moved without its entry being updated is invisible to every
other engine, to the weekly report, and to the next agent. --fix repairs what
it safely can.

Usage:
    doctor.py [--home PATH] [--fix]

Secrets: this reads the NAMES of the keys in shared/.env to confirm they
are set. It never reads, prints or logs a value.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import engines as eng  # noqa: E402
import registry as reg  # noqa: E402

REPO_ROOT = _HERE.parents[2]

GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
results: list[tuple[str, str, str]] = []   # (level, label, detail)


def add(level: str, label: str, detail: str = "") -> None:
    results.append((level, label, detail))


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# --- machine ---------------------------------------------------------------

def check_machine() -> None:
    v = sys.version_info
    if v >= (3, 9):
        add("pass", f"Python {v.major}.{v.minor}")
    else:
        add("fail", f"Python {v.major}.{v.minor}", "3.9+ needed; try `python3 --version`")

    system = platform.system()
    if system == "Linux":
        add("pass", "OS: Linux", "everything works; install ffmpeg via your "
            "package manager if you run video")
    elif system == "Windows":
        add("warn", "OS: Windows", "use WSL for the bash installer and "
            "symlinks; the Python scripts themselves are portable")
    elif system != "Darwin":
        add("warn", f"OS: {system}", "untested here; the scripts are plain "
            "Python and should run — tell us what breaks")
    else:
        chip = platform.machine()
        if chip == "arm64":
            add("pass", "Apple Silicon")
        else:
            add("warn", f"Intel Mac ({chip})", "fine for text; video rendering will be slow")

    add("pass" if have("git") else "fail", "git",
        "" if have("git") else "run: xcode-select --install")

    try:
        usage = shutil.disk_usage(Path.home())
        free_gb = usage.free / 1024**3
        if free_gb >= 10:
            add("pass", f"Disk free: {free_gb:.0f} GB")
        elif free_gb >= 3:
            add("warn", f"Disk free: {free_gb:.0f} GB", "10 GB+ recommended for video")
        else:
            add("fail", f"Disk free: {free_gb:.0f} GB", "clear some space")
    except OSError:
        add("warn", "Disk free: unknown")


# --- install ---------------------------------------------------------------

def _skill_names(home: Path | None = None) -> list[str]:
    """Skills we expect to be installed for this machine / home."""
    if home is not None:
        return eng.skills_for(eng.home_types(home))
    # No home yet — only require the always-on pair, not every engine.
    return list(eng.CORE_SKILLS)


def _check_skill_dir(d: Path, names: list[str], *, required: bool = False) -> bool:
    """Return True if at least one skill is present. required=True → fail if missing dir."""
    label = f"Installed in {str(d).replace(str(Path.home()), '~')}"
    if not d.is_dir():
        if required:
            add("fail", label, "missing — run install_skills.sh --engine …")
        return False
    linked = [n for n in names if (d / n).exists()]
    if not linked:
        if required:
            add("fail", label, "empty — run install_skills.sh --engine …")
        return False
    if len(linked) == len(names):
        add("pass", label, f"{len(linked)}/{len(names)} ({', '.join(names)})")
    else:
        missing = [n for n in names if n not in linked]
        add("warn", label,
            f"only {len(linked)}/{len(names)} — missing {', '.join(missing)}")
    return True


def check_install(home: Path | None = None) -> None:
    names = _skill_names(home)
    available = sorted(
        p.name for p in (REPO_ROOT / "skills").iterdir()
        if (p / "SKILL.md").exists()
    ) if (REPO_ROOT / "skills").is_dir() else []
    if not available:
        add("fail", "Engine skills", f"none found under {REPO_ROOT}/skills")
        return
    add("pass", f"Engine skills present ({len(available)} in repo)")

    # Canonical store is required for the expected set.
    canon_ok = _check_skill_dir(Path.home() / ".agents/skills", names, required=True)

    agent_homes = [
        Path.home() / ".claude/skills",
        Path.home() / ".codex/skills",
        Path.home() / ".cursor/skills",
    ]
    # Same extension point as install_skills.sh — extra agent skill dirs.
    for extra in (os.environ.get("GTM_AGENT_DIRS") or "").split(":"):
        if extra.strip():
            agent_homes.append(Path(extra.strip()).expanduser())
    found_agent = False
    for d in agent_homes:
        if not d.parent.is_dir():
            continue
        if _check_skill_dir(d, names):
            found_agent = True

    if home is not None:
        home_skills = home / "skills"
        canon = Path.home() / ".agents/skills"
        if home_skills.is_symlink():
            try:
                target = home_skills.resolve()
                if target == canon.resolve():
                    add("pass", "  ~/gtm/skills -> ~/.agents/skills")
                else:
                    add("warn", "  ~/gtm/skills",
                        f"points at {target}, expected ~/.agents/skills")
            except OSError:
                add("warn", "  ~/gtm/skills", "broken symlink")
        elif not _check_skill_dir(home_skills, names):
            # A convenience link, not a dependency: the skills themselves are
            # installed above, and ~/.agents/skills/... paths work without it.
            add("warn", "  ~/gtm/skills link missing",
                "home-relative `skills/...` commands won't resolve. Use "
                "~/.agents/skills/... or run install_skills.sh --home <path>")
        types = eng.home_types(home)
        add("pass", f"  engine types: {', '.join(types) or '(none yet)'}")

    if not canon_ok and not found_agent:
        add("fail", "Skills not installed",
            "run: install_skills.sh --engine <engine> --home ~/gtm")


# --- optional tools --------------------------------------------------------

def check_tools(active: str) -> None:
    if active == "video":
        add("pass" if have("ffmpeg") else "warn", "ffmpeg",
            "" if have("ffmpeg") else "needed to render video — brew install "
            "ffmpeg (macOS) / apt install ffmpeg (Linux)")
        add("pass" if have("node") else "warn", "node",
            "" if have("node") else "only needed for advanced renderers")


# --- the home and the registry --------------------------------------------

def find_home(explicit: str | None) -> Path | None:
    """The home is `~/gtm` unless told otherwise. A v1 home (shared/ and
    the engines in one folder) is still recognised, and reported."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.is_dir() else None
    env = (os.environ.get("GTM_HOME") or os.environ.get("GTM_WORKSPACE") or "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        return p if p.is_dir() else None

    def marked(p: Path) -> bool:
        # .gtm-template = the engine repo's scaffold source, never a home.
        if (p / ".gtm-template").is_file():
            return False
        shared = p / "shared"
        return shared.is_dir() and any(
            (shared / f).is_file()
            for f in ("channels.json", "brand.md", ".env.example"))

    default = Path.home() / "gtm"
    if marked(default):
        return default
    for base in (Path.cwd(), *Path.cwd().parents):
        if marked(base):
            return base
        for cand in (base / "gtm", base / "engines"):
            if marked(cand):
                return cand
        if base == Path.home():
            break
    return None


def check_registry(home: Path, fix: bool) -> list[Path]:
    """The registry is the only map of where the engines are. Returns the
    engine folders it could actually find."""
    f = home / reg.REGISTRY
    if not f.is_file():
        add("warn", f"  {reg.REGISTRY} missing",
            "engines can live anywhere, so nothing can find them without it. "
            "scaffold.py --merge writes one")
        return [p for p in reg.unregistered(home)]

    entries = reg.entries(home)
    add("pass", f"  {reg.REGISTRY}: {len(entries)} engine(s) registered")

    stale = reg.stale(home)
    if stale and fix:
        dropped = reg.prune(home)
        # Pruning only forgets the entry. If the folder was MOVED rather than
        # deleted, it is now unregistered and invisible, and only the user
        # knows where it went.
        add("pass", "  registry pruned",
            f"dropped {', '.join(dropped)}. If you moved one rather than "
            f"deleting it, put it back on the map: registry.py add <name> <new path>")
    else:
        for name, path in stale:
            add("fail", f"  {name} is registered at a path that is gone",
                f"{path}. Move it back, fix the entry, or run doctor.py --fix")

    loose = reg.unregistered(home)
    for p in loose:
        if fix:
            reg.register(home, p.name, p, eng.engine_types([p])[0])
            add("pass", f"  registered {p.name}", str(p))
        else:
            add("warn", f"  {p.name} is not in {reg.REGISTRY}",
                "nothing outside its own folder can find it. doctor.py --fix "
                "adds it")

    out = [Path(str(e.get("path"))).expanduser() for e in reg.entries(home)]
    return [p for p in out if reg.is_engine(p)]


def check_home(home: Path | None, fix: bool = False) -> str:
    if home is None:
        add("warn", "No gtm home found",
            "expected ~/gtm. Run scaffold.py, or pass --home")
        return ""

    add("pass", f"Home: {str(home).replace(str(Path.home()), '~')}")

    # shared/ is the point of the home: one brand, one set of keys.
    shared = home / "shared"
    add("pass" if shared.is_dir() else "fail", "  shared/")

    brand = shared / "brand.md"
    if not brand.is_file():
        add("warn", "  shared/brand.md missing",
            "nothing breaks, but every engine reads it first. Without it "
            "they guess at your voice. scaffold.py --merge restores it")
    else:
        text = brand.read_text()
        if "TODO" in text or "<your" in text:
            add("warn", "  shared/brand.md still has placeholders",
                "the engines are only as good as this file")
        else:
            add("pass", "  shared/brand.md filled in")

    ch = shared / "channels.json"
    if ch.is_file():
        try:
            json.loads(ch.read_text())
            add("pass", "  shared/channels.json")
        except json.JSONDecodeError as e:
            add("fail", "  shared/channels.json is not valid JSON", str(e))
    else:
        add("warn", "  shared/channels.json missing",
            "not blocking: the scripts fall back to defaults (72h metric "
            "window). Add it when you want per-channel settings")

    if (home / "AGENTS.md").is_file():
        add("pass", "  AGENTS.md" + ("  + CLAUDE.md" if (home / "CLAUDE.md").is_file() else ""))
    else:
        add("warn", "  AGENTS.md missing",
            "how agents work in this home. Restore it with scaffold.py --merge")

    wds = check_registry(home, fix)
    if not wds:
        add("warn", "  no engines yet",
            "add one when you know which: scaffold.py --engine <name> "
            "--at <where it should live>")
    types = set()
    for wd in wds:
        marker = wd / "engine.json"
        legacy = wd / "engine.json"
        src = marker if marker.is_file() else legacy
        try:
            meta = json.loads(src.read_text())
        except (json.JSONDecodeError, OSError) as e:
            add("fail", f"  {wd.name}/{src.name} is not valid JSON", str(e))
            continue
        if legacy.is_file() and not marker.is_file():
            add("warn", f"  {wd.name}/ still uses engine.json",
                "v1 name, still read. migrate_v1.py renames it")
        typ = (meta.get("type") or "").strip() or wd.name
        types.add(typ)
        recorded = str(meta.get("home") or "").strip()
        if recorded and Path(recorded).expanduser().resolve() != home.resolve():
            add("warn", f"  {wd.name}/ points home at {recorded}",
                f"this home is {home}. One of the two is out of date")
        metric = (meta.get("primary_metric") or "").strip()
        bits = [typ, str(wd).replace(str(Path.home()), "~")]
        add("pass", f"  {wd.name}/  ({' | '.join(bits)})",
            "" if metric else "no primary_metric in engine.json. The loop "
            "optimises this, name it")
        # The subfolders are made on first write: runs/ and reports/ by the
        # loop scripts, templates/ and inputs/ by whoever writes the first
        # file. Absent means "not used yet", which is not a problem to report.
        absent = [r for r in ("templates", "runs", "reports", "inputs")
                  if not (wd / r).is_dir()]
        if absent:
            add("pass", f"    {wd.name}/ layout",
                f"no {', '.join(r + '/' for r in absent)} yet, "
                "created on first write")
        idx = wd / "runs" / "index.csv"
        n = max(0, sum(1 for _ in idx.open()) - 1) if idx.is_file() else 0
        add("pass", f"    runs recorded: {n}",
            "" if n else "nothing to learn from yet, expected on day one")
        if typ == "outreach" and not (wd / "crm.csv").is_file():
            add("warn", f"    {wd.name}/crm.csv missing",
                "outreach needs the CRM for stickiness and dedupe")

    check_env(home, types)
    return "video" if "video" in types else ""


def parse_env_example(example: Path) -> list[tuple[str, str, bool]]:
    """[(key, section, optional)] read from .env.example's own annotations.

    The file documents itself — `# --- video ---` headers, `(optional)` in a
    header, `# Optional …` above a single key. Trust it rather than keeping a
    second list here that drifts from it.
    """
    out: list[tuple[str, str, bool]] = []
    section, sec_optional, comment = "", False, ""
    for ln in example.read_text().splitlines():
        s = ln.strip()
        if s.startswith("#"):
            body = s.lstrip("#").strip()
            if body.startswith("---"):
                section = body.strip("-").strip()
                sec_optional = "optional" in section.lower()
                comment = ""
            else:
                comment += " " + body.lower()
            continue
        if not s:
            comment = ""
            continue
        if "=" in s:
            key = s.split("=", 1)[0].strip()
            out.append((key, section, sec_optional or "optional" in comment))
            comment = ""
    return out


def check_env(home: Path, types: set[str] | None = None) -> None:
    """Confirm key NAMES are set. Never reads a value.

    Every key here is optional until an engine that needs it exists. Only a
    key whose section matches an engine in this home, and that the file
    doesn't mark optional, is worth a warning.

    All four engines scaffold by default, so a key is attributed to the
    engine whose section it sits under — never to every engine present.
    Scaffolded is not the same as running: someone with a `video/` folder they
    haven't touched should read "for video", not "you're missing keys".
    """
    example = home / "shared" / ".env.example"
    env = home / "shared" / ".env"

    if not example.is_file():
        return
    keys = parse_env_example(example)
    if not keys:
        return
    types = types or set()

    def needed(section: str, optional: bool) -> bool:
        head = section.split()[0].lower() if section.split() else ""
        return not optional and head in types

    wanted = [k for k, _, _ in keys]
    # Group by the section that asks for them. Joining every home type
    # here would tell a four-engine home that the video keys are
    # "needed for outreach, seo, social, video" — true of none of them.
    by_section: dict[str, list[str]] = {}
    for k, sec, opt in keys:
        if needed(sec, opt):
            by_section.setdefault(sec.split()[0].lower(), []).append(k)
    required = [k for ks in by_section.values() for k in ks]
    detail = "; ".join(f"{', '.join(ks)} for {s}" for s, ks in sorted(by_section.items()))

    if not env.is_file():
        if required:
            add("warn", "  shared/.env not created",
                f"copy .env.example → .env — {detail}"
                " — only when you run that engine")
        else:
            add("pass", "  shared/.env not created",
                f"nothing needs one yet — the {len(wanted)} keys in "
                ".env.example are per-channel, add one when you add the channel")
        return

    present = set()
    for ln in env.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        name, _, value = ln.partition("=")
        if value.strip().strip('"\''):        # set to something non-empty
            present.add(name.strip())
    present |= {k for k in wanted if os.environ.get(k)}

    n_set = len(present & set(wanted))
    missing_required = [k for k in required if k not in present]
    if missing_required:
        add("warn", f"  keys set: {n_set}/{len(wanted)}",
            "missing: " + "; ".join(
                f"{', '.join(k for k in ks if k not in present)} for {s}"
                for s, ks in sorted(by_section.items())
                if any(k not in present for k in ks)))
    else:
        add("pass", f"  keys set: {n_set}/{len(wanted)}",
            "" if n_set == len(wanted)
            else "the rest are optional or for channels you don't run")


# --- output ----------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", "--home", dest="home", default="")
    ap.add_argument("--fix", action="store_true",
                    help="repair what is safe to repair: prune registry "
                         "entries whose folder is gone, register engine "
                         "folders sitting in the home unregistered")
    a = ap.parse_args()

    print(f"\n{DIM}gtm-engine doctor{RESET}\n")

    check_machine()
    home = find_home(a.home)
    check_install(home)
    active = check_home(home, a.fix)
    check_tools(active)

    icon = {"pass": f"{GREEN}✓{RESET}", "warn": f"{YELLOW}!{RESET}", "fail": f"{RED}✗{RESET}"}
    for level, label, detail in results:
        line = f"  {icon[level]} {label}"
        if detail:
            line += f"{DIM} — {detail}{RESET}"
        print(line)

    fails = sum(1 for r in results if r[0] == "fail")
    warns = sum(1 for r in results if r[0] == "warn")
    print()
    if fails:
        print(f"{RED}{fails} blocking{RESET}"
              + (f", {YELLOW}{warns} to look at{RESET}" if warns else "")
              + " — fix the ✗ lines above.\n")
        return 1
    if warns:
        print(f"{GREEN}Nothing blocking{RESET}, {YELLOW}{warns} worth a look{RESET}"
              f"{DIM} — ! is information, not a to-do list{RESET}.\n")
        return 0
    print(f"{GREEN}All clear.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

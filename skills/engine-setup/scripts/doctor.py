#!/usr/bin/env python3
"""Check that everything gtm-engine needs is actually in place.

Run it before you start (what's missing on this machine?) and again after
setup (did it all land?). It changes nothing — it only looks.

Usage:
    doctor.py [--workspace PATH]

Secrets: this reads the NAMES of the keys in config/.env to confirm they
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
import pathways as pw  # noqa: E402

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

def _skill_names(ws: Path | None = None) -> list[str]:
    """Skills we expect to be installed for this machine / workspace."""
    if ws is not None:
        return pw.skills_for(pw.read_installed(ws))
    root = REPO_ROOT / "skills"
    if not root.is_dir():
        return list(pw.ALWAYS_SKILLS)
    # No workspace yet — only require the always-on pair, not every workflow.
    return list(pw.ALWAYS_SKILLS)


def _check_skill_dir(d: Path, names: list[str], *, required: bool = False) -> bool:
    """Return True if at least one skill is present. required=True → fail if missing dir."""
    label = f"Installed in {str(d).replace(str(Path.home()), '~')}"
    if not d.is_dir():
        if required:
            add("fail", label, "missing — run install_skills.sh --workflow …")
        return False
    linked = [n for n in names if (d / n).exists()]
    if not linked:
        if required:
            add("fail", label, "empty — run install_skills.sh --workflow …")
        return False
    if len(linked) == len(names):
        add("pass", label, f"{len(linked)}/{len(names)} ({', '.join(names)})")
    else:
        missing = [n for n in names if n not in linked]
        add("warn", label,
            f"only {len(linked)}/{len(names)} — missing {', '.join(missing)}")
    return True


def check_install(ws: Path | None = None) -> None:
    names = _skill_names(ws)
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
        Path.home() / ".openclaw/skills",
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

    for d, note in (
        (Path.home() / ".codex/skills", "Codex reads ~/.agents/skills — these do nothing"),
        (Path.home() / ".cursor/skills", "redundant; Cursor reads ~/.agents/skills"),
    ):
        stale = [n for n in available if (d / n).is_symlink()]
        if stale:
            add("warn", f"Legacy links in {str(d).replace(str(Path.home()), '~')}",
                f"{len(stale)} from an older install — {note}")

    if ws is not None:
        _check_skill_dir(ws / "skills", names, required=True)
        installed = pw.read_installed(ws)
        add("pass", f"  workflows: {', '.join(installed)}")

    if not canon_ok and not found_agent:
        add("fail", "Workflows not installed",
            "run: install_skills.sh --workflow <workflow> --workspace <project>/workflows")


# --- optional tools --------------------------------------------------------

def check_tools(active: str) -> None:
    if active == "video":
        add("pass" if have("ffmpeg") else "warn", "ffmpeg",
            "" if have("ffmpeg") else "needed to render video — brew install "
            "ffmpeg (macOS) / apt install ffmpeg (Linux)")
        add("pass" if have("node") else "warn", "node",
            "" if have("node") else "only needed for advanced renderers")


# --- workspace -------------------------------------------------------------

def find_workspace(explicit: str | None) -> Path | None:
    """Markers (config/pathways.json, config/channels.json) identify a
    workspace — 'workflows' is only the default folder name."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.is_dir() else None
    env = (os.environ.get("GTM_WORKSPACE") or "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        return p if p.is_dir() else None

    def marked(p: Path) -> bool:
        return (p / "config" / "pathways.json").is_file() \
            or (p / "config" / "channels.json").is_file()

    for base in (Path.cwd(), *Path.cwd().parents):
        if marked(base):
            return base
        cand = base / "workflows"
        if marked(cand) or (cand / "config").is_dir():
            return cand
        if base == Path.home():
            break
    try:
        for child in sorted(Path.cwd().iterdir()):
            if child.is_dir() and marked(child):
                return child
    except OSError:
        pass
    return None


def check_workspace(ws: Path | None) -> str:
    if ws is None:
        add("warn", "Workspace not found",
            "run scaffold_workspace.py from your project, or pass --workspace")
        return ""

    add("pass", f"Workspace: {str(ws).replace(str(Path.home()), '~')}")

    for rel in ("config", "inputs", "runs", "reports", "state", "templates"):
        add("pass" if (ws / rel).is_dir() else "fail", f"  {rel}/")

    installed = pw.read_installed(ws)
    for wf in installed:
        tdir = ws / "templates" / wf
        add("pass" if tdir.is_dir() else "fail", f"  templates/{wf}/",
            "" if tdir.is_dir() else "re-run scaffold with --workflow " + wf)
    if "outreach" in installed:
        crm = ws / "state" / "crm.csv"
        add("pass" if crm.is_file() else "fail", "  state/crm.csv",
            "" if crm.is_file() else "needed for outreach")

    # brand.md filled in?
    brand = ws / "config" / "brand.md"
    if not brand.is_file():
        add("fail", "  config/brand.md missing")
    else:
        text = brand.read_text()
        if "TODO" in text or "<your" in text:
            add("warn", "  config/brand.md still has placeholders",
                "the workflows are only as good as this file")
        else:
            add("pass", "  config/brand.md filled in")

    # active workflow
    active = ""
    ch = ws / "config" / "channels.json"
    if ch.is_file():
        try:
            data = json.loads(ch.read_text())
            active = (data.get("active_workflow") or "").strip()
            metric = (data.get("primary_metric") or "").strip()
            add("pass" if active else "warn", f"  active workflow: {active or 'not set'}")
            add("pass" if metric else "warn", f"  primary metric: {metric or 'not set'}",
                "" if metric else "the loop optimises this — name it")
        except json.JSONDecodeError as e:
            add("fail", "  config/channels.json is not valid JSON", str(e))
    else:
        add("fail", "  config/channels.json missing")

    # runs spine
    idx = ws / "runs" / "index.csv"
    if idx.is_file():
        n = max(0, sum(1 for _ in idx.open()) - 1)
        add("pass", f"  runs recorded: {n}",
            "" if n else "nothing to learn from yet — that's expected on day one")
    else:
        add("fail", "  runs/index.csv missing", "the loop has no spine without it")

    check_env(ws)
    return active


def check_env(ws: Path) -> None:
    """Confirm key NAMES are set. Never reads a value."""
    example = ws / "config" / ".env.example"
    env = ws / "config" / ".env"

    if not example.is_file():
        return
    wanted = [ln.split("=", 1)[0].strip()
              for ln in example.read_text().splitlines()
              if ln.strip() and not ln.lstrip().startswith("#") and "=" in ln]
    if not wanted:
        return

    if not env.is_file():
        add("warn", "  config/.env not created",
            f"copy .env.example → .env and add keys ({len(wanted)} known)")
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

    missing = [k for k in wanted if k not in present]
    if not missing:
        add("pass", f"  keys set: {len(wanted)}/{len(wanted)}")
    else:
        add("warn", f"  keys set: {len(present & set(wanted))}/{len(wanted)}",
            "missing: " + ", ".join(missing))


# --- output ----------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace")
    a = ap.parse_args()

    print(f"\n{DIM}gtm-engine doctor{RESET}\n")

    check_machine()
    ws = find_workspace(a.workspace)
    check_install(ws)
    active = check_workspace(ws)
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
        print(f"{GREEN}Nothing blocking{RESET}, {YELLOW}{warns} worth a look{RESET}.\n")
        return 0
    print(f"{GREEN}All clear.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

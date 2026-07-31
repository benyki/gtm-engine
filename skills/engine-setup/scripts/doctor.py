#!/usr/bin/env python3
"""Check that everything gtm-engine needs is actually in place.

**Optional — a helper, not a step.** Nothing in the engine calls this, no
workflow needs it to have passed, and a workspace that never runs it is a
normal workspace. Reach for it when something looks off, when you're on an
unfamiliar machine, or when you just want to see the install landed. It changes
nothing — it only looks.

**✗ means genuinely broken; ! is information, not a chore.** The engine is
forgiving by design — a missing channels.json falls back to defaults, an empty
templates/ is the documented first run, runs/ and reports/ are created on first
write — so this check never reports those as blocking. Nothing here is a
required-shape audit: a workspace someone built by hand, or trimmed to the two
folders they use, is a valid workspace.

Usage:
    doctor.py [--workspace PATH]

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
import workflows as wf  # noqa: E402

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
        return wf.skills_for(wf.workspace_types(ws))
    # No workspace yet — only require the always-on pair, not every workflow.
    return list(wf.CORE_SKILLS)


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

    if ws is not None:
        ws_skills = ws / "skills"
        canon = Path.home() / ".agents/skills"
        if ws_skills.is_symlink():
            try:
                target = ws_skills.resolve()
                if target == canon.resolve():
                    add("pass", "  workspace/skills → ~/.agents/skills")
                else:
                    add("warn", "  workspace/skills",
                        f"points at {target}, expected ~/.agents/skills")
            except OSError:
                add("warn", "  workspace/skills", "broken symlink")
        elif not _check_skill_dir(ws_skills, names):
            # A convenience link, not a dependency: the skills themselves are
            # installed above, and ~/.agents/skills/… paths work without it.
            add("warn", "  workspace/skills link missing",
                "workspace-relative `skills/…` commands won't resolve — use "
                "~/.agents/skills/… or run install_skills.sh --workspace <path>")
        types = wf.workspace_types(ws)
        add("pass", f"  workflow types: {', '.join(types) or '(none yet)'}")

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
    """A workspace is recognised by its shared/ folder (brand, channels,
    keys) — 'workflows' is only the default folder name."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.is_dir() else None
    env = (os.environ.get("GTM_WORKSPACE") or "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        return p if p.is_dir() else None

    def marked(p: Path) -> bool:
        # .gtm-template = the engine repo's scaffold source, never a workspace.
        if (p / ".gtm-template").is_file():
            return False
        shared = p / "shared"
        return shared.is_dir() and any(
            (shared / f).is_file()
            for f in ("channels.json", "brand.md", ".env.example"))

    for base in (Path.cwd(), *Path.cwd().parents):
        if marked(base):
            return base
        cand = base / "workflows"
        if marked(cand):
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

    # shared/ — the one cross-workflow folder.
    shared = ws / "shared"
    add("pass" if shared.is_dir() else "fail", "  shared/")

    brand = shared / "brand.md"
    if not brand.is_file():
        add("warn", "  shared/brand.md missing",
            "nothing breaks, but every workflow reads it first — without it "
            "they guess at your voice. scaffold_workspace.py --merge restores it")
    else:
        text = brand.read_text()
        if "TODO" in text or "<your" in text:
            add("warn", "  shared/brand.md still has placeholders",
                "the workflows are only as good as this file")
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
            "not blocking — the scripts fall back to defaults (72h metric "
            "window). Add it when you want per-channel settings")

    if (ws / "AGENTS.md").is_file():
        add("pass", "  AGENTS.md" + ("  + CLAUDE.md" if (ws / "CLAUDE.md").is_file() else ""))
    else:
        add("warn", "  AGENTS.md missing",
            "how agents work in this workspace — restore it with "
            "scaffold_workspace.py --merge")

    # One self-contained folder per workflow.
    wds = [p for p in sorted(ws.iterdir())
           if p.is_dir() and (p / "workflow.json").is_file()]
    if not wds:
        add("warn", "  no workflow folders yet",
            "add one when you know which: scaffold_workspace.py --merge "
            "--workflow <name>")
    types = set()
    for wd in wds:
        try:
            meta = json.loads((wd / "workflow.json").read_text())
        except json.JSONDecodeError as e:
            add("fail", f"  {wd.name}/workflow.json is not valid JSON", str(e))
            continue
        typ = (meta.get("type") or "").strip() or wd.name
        types.add(typ)
        metric = (meta.get("primary_metric") or "").strip()
        bits = [typ]
        if metric:
            bits.append(metric)
        add("pass", f"  {wd.name}/  ({' · '.join(bits)})",
            "" if metric else "no primary_metric in workflow.json — the loop "
            "optimises this, name it")
        # The subfolders are made on first write — runs/ and reports/ by the
        # loop scripts, templates/ and inputs/ by whoever writes the first
        # file. Absent means "not used yet", which is not a problem to report.
        absent = [r for r in ("templates", "runs", "reports", "inputs")
                  if not (wd / r).is_dir()]
        if absent:
            add("pass", f"    {wd.name}/ layout",
                f"no {', '.join(r + '/' for r in absent)} yet — "
                "created on first write")
        idx = wd / "runs" / "index.csv"
        n = max(0, sum(1 for _ in idx.open()) - 1) if idx.is_file() else 0
        add("pass", f"    runs recorded: {n}",
            "" if n else "nothing to learn from yet — expected on day one")
        if typ == "outreach" and not (wd / "crm.csv").is_file():
            add("warn", f"    {wd.name}/crm.csv missing",
                "outreach needs the CRM for stickiness and dedupe")

    check_env(ws, types)
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


def check_env(ws: Path, types: set[str] | None = None) -> None:
    """Confirm key NAMES are set. Never reads a value.

    Every key here is optional until a workflow that needs it exists. Only a
    key whose section matches a workflow in this workspace, and that the file
    doesn't mark optional, is worth a warning.

    All four workflows scaffold by default, so a key is attributed to the
    workflow whose section it sits under — never to every workflow present.
    Scaffolded is not the same as running: someone with a `video/` folder they
    haven't touched should read "for video", not "you're missing keys".
    """
    example = ws / "shared" / ".env.example"
    env = ws / "shared" / ".env"

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
    # Group by the section that asks for them. Joining every workspace type
    # here would tell a four-workflow workspace that the video keys are
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
                " — only when you run that workflow")
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
        print(f"{GREEN}Nothing blocking{RESET}, {YELLOW}{warns} worth a look{RESET}"
              f"{DIM} — ! is information, not a to-do list{RESET}.\n")
        return 0
    print(f"{GREEN}All clear.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

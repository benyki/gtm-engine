#!/usr/bin/env python3
"""Pick which template version to use for the next piece of work.

This is the only place an A/B arm is chosen. The rules it enforces:

  R2  Least-used arm wins. Nobody cherry-picks a favourite. Usage is
      counted from runs/index.csv — the spine — within the experiment's
      cohort. state/crm.csv is for stickiness, not counting.
  R3  Sticky — an entity that already has an arm keeps it, forever,
      including follow-ups.
  R4  A missing template file NEVER blocks the run. It reports
      action="write_template" with the hypothesis, and the agent writes it.
  R5  "default" and "none" normalise to the base template.

With no live experiment it doesn't guess a filename: it reports what's in
the workflow's active template folder — one file to use, a list to choose
from, or write_template when the folder is empty. The agent decides and
records the file it actually rendered.

Usage:
    assign_arm.py --workflow outreach [--entity someone@example.com]
    assign_arm.py --workflow video --json

Output is JSON so an agent can act on it directly.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

NORMALISE_TO_BASE = {"", "default", "none", "null"}


def find_workspace(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if (p / "config").is_dir():
            return p
        sys.exit(f"error: no config/ in {p}")
    for base in (Path.cwd(), *Path.cwd().parents):
        if (base / "workflows" / "config").is_dir():
            return base / "workflows"
        if base == Path.home():
            break
    sys.exit("error: no workspace found — pass --workspace")


def load_experiment(ws: Path, workflow: str) -> dict | None:
    path = ws / "config" / "experiments.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"error: config/experiments.json is not valid JSON — {e}")
    for exp in data.get("experiments", []):
        if exp.get("workflow") == workflow and exp.get("status") == "live":
            return exp
    return None


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def sticky_arm(ws: Path, entity: str) -> str | None:
    """R3 — if we've spoken to them before, they stay in their arm."""
    for r in rows(ws / "state" / "crm.csv"):
        if r.get("id", "").strip().lower() == entity.strip().lower():
            arm = (r.get("arm") or "").strip()
            return arm or None
    return None


def arm_counts(ws: Path, exp: dict) -> Counter:
    """Count usage within this experiment's cohort only (R6).

    Reads runs/index.csv and nothing else. The CRM is not a usage ledger —
    every draft is logged as a run, so counting CRM rows on top would count
    the same work twice, and its rows carry no experiment id, so they'd
    leak into other workflows' rotation whenever arm ids collide.
    """
    started = exp.get("started", "")
    counts: Counter = Counter()
    for r in rows(ws / "runs" / "index.csv"):
        if r.get("experiment_id") != exp["id"]:
            continue
        if started and r.get("created_at", "") < started:
            continue
        arm = (r.get("arm") or "").strip()
        if arm:
            counts[arm] += 1
    return counts


def active_templates(ws: Path, workflow: str) -> list[Path]:
    """Template files in the active folder. losers/ never counts."""
    d = ws / "templates" / workflow
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir()
                  if p.is_file() and not p.name.startswith("."))


def template_path(ws: Path, workflow: str, arm: dict, base: str) -> Path:
    name = arm.get("template") or (
        f"{base}.txt" if arm["id"] in NORMALISE_TO_BASE else f"{base}-{arm['id']}.txt"
    )
    return ws / "templates" / workflow / name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True,
                    help="outreach | seo | linkedin | video")
    ap.add_argument("--entity", default="",
                    help="stable id (email, handle) — keeps them in their arm")
    ap.add_argument("--workspace")
    ap.add_argument("--json", action="store_true", help="machine-readable only")
    a = ap.parse_args()

    ws = find_workspace(a.workspace)
    exp = load_experiment(ws, a.workflow)

    if exp is None:
        # No experiment: report what exists and let the agent decide.
        found = active_templates(ws, a.workflow)
        out = {"experiment_id": "", "arm": ""}
        if len(found) == 1:
            out.update({
                "template": str(found[0]),
                "action": "use_template",
                "why": "no live experiment — one active template, use it",
            })
        elif found:
            out.update({
                "template": "",
                "templates": [str(p) for p in found],
                "action": "choose_template",
                "why": "no live experiment — several active templates",
                "instruction": (
                    "Nothing is being tested, so any of these is fine. Pick "
                    "the one that fits the piece, and record template_used "
                    "as the file you actually rendered."
                ),
            })
        else:
            out.update({
                "template": str(ws / "templates" / a.workflow),
                "action": "write_template",
                "why": "no live experiment and no template yet",
                "instruction": (
                    f"Write the first template into templates/{a.workflow}/, "
                    "guided by config/brand.md and the workflow's skill. Then "
                    "use it and record template_used on the run."
                ),
            })
        print(json.dumps(out, indent=2))
        return 0

    arms = exp.get("arms") or []
    if not arms:
        sys.exit(f"error: experiment {exp['id']} has no arms")

    base = exp.get("template_base", "first-touch")

    # R3 — sticky beats everything.
    chosen = None
    if a.entity:
        prev = sticky_arm(ws, a.entity)
        if prev:
            chosen = next((x for x in arms if x["id"] == prev), None)
            if chosen is None:   # arm was retired; honour history anyway
                chosen = {"id": prev, "label": prev, "hypothesis": ""}

    reason = "sticky — this entity is already in that arm"
    if chosen is None:
        # R2 — least used wins; ties break on declaration order.
        counts = arm_counts(ws, exp)
        chosen = min(arms, key=lambda x: (counts[x["id"]], arms.index(x)))
        reason = (f"least used ({counts[chosen['id']]} runs; "
                  + ", ".join(f"{x['id']}={counts[x['id']]}" for x in arms) + ")")

    path = template_path(ws, a.workflow, chosen, base)
    exists = path.is_file()

    out = {
        "experiment_id": exp["id"],
        "arm": chosen["id"],
        "label": chosen.get("label", ""),
        "template": str(path),
        "template_exists": exists,
        "action": "use_template" if exists else "write_template",
        "why": reason,
    }
    if not exists:
        # R4 — never block. Tell the agent exactly what to write.
        out["hypothesis"] = chosen.get("hypothesis", "")
        out["instruction"] = (
            f"This arm has no template yet. Write {path.name} in "
            f"templates/{a.workflow}/, guided by the hypothesis above and by the "
            f"other templates in that folder. Do not copy an existing arm — a "
            f"variant is a different proposition, not a reworded one. Then use it "
            f"and record template_used={path.name} on the run."
        )

    print(json.dumps(out, indent=2))
    if not a.json and not exists:
        print(f"\n→ write templates/{a.workflow}/{path.name} first, then use it.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

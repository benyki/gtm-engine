#!/usr/bin/env python3
"""Which published runs are ready to have their numbers read?

Enforces the 72-hour rule in code rather than trusting anyone to remember it.
LinkedIn, TikTok, Instagram and X all keep distributing a post for days, so a
number read at 24 or 48 hours mostly records what time you posted. Once it's
in index.csv it affects every verdict from then on, and nothing flags it as
early — so the rule has to bite before the number is written, not after.

Usage:
    due_metrics.py            # what to read now, and what's still too young
    due_metrics.py --json     # same, machine-readable
    due_metrics.py --hours 96 # be stricter
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MIN_HOURS = 72
DIM, GREEN, YELLOW, RESET = "\033[2m", "\033[32m", "\033[33m", "\033[0m"


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


def parse_ts(v: str) -> datetime | None:
    v = (v or "").strip()
    if not v:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(v, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace")
    ap.add_argument("--hours", type=int, default=MIN_HOURS)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ws = find_workspace(a.workspace)
    idx = ws / "runs" / "index.csv"
    if not idx.is_file():
        sys.exit("error: runs/index.csv not found")

    now = datetime.now(timezone.utc)
    due, early, unpublished = [], [], []

    with idx.open(newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("metric_value") or "").strip():
                continue                                   # already measured
            if (r.get("status") or "").strip() != "published":
                if (r.get("status") or "").strip() not in ("killed", ""):
                    unpublished.append(r.get("run_id", ""))
                continue

            ts = parse_ts(r.get("published_at", ""))
            item = {"run_id": r.get("run_id", ""), "channel": r.get("channel", ""),
                    "url": r.get("url", ""), "arm": r.get("arm", ""),
                    "metric": r.get("primary_metric", ""),
                    "published_at": r.get("published_at", "")}
            if ts is None:
                item["age_hours"] = None
                due.append(item)                           # no timestamp: don't block on it
                continue

            age = (now - ts).total_seconds() / 3600
            item["age_hours"] = round(age, 1)
            (due if age >= a.hours else early).append(item)

    early.sort(key=lambda x: -(x["age_hours"] or 0))

    if a.json:
        print(json.dumps({"threshold_hours": a.hours, "due": due,
                          "too_early": early, "not_published": unpublished}, indent=2))
        return 0

    print(f"\n{GREEN}Ready to read ({len(due)}){RESET}"
          f"{DIM} — published {a.hours}h+ ago, no number yet{RESET}")
    for d in due or []:
        age = f"{d['age_hours']}h" if d["age_hours"] is not None else "age unknown"
        print(f"  {d['run_id']:<30} {d['channel']:<12} {DIM}{age}{RESET}  {d['url']}")
    if not due:
        print(f"  {DIM}nothing{RESET}")

    if early:
        print(f"\n{YELLOW}Too early ({len(early)}){RESET}"
              f"{DIM} — leave these empty, they'll come round{RESET}")
        for d in early:
            wait = a.hours - (d["age_hours"] or 0)
            print(f"  {d['run_id']:<30} {d['channel']:<12} "
                  f"{DIM}{d['age_hours']}h — {wait:.0f}h to go{RESET}")

    if unpublished:
        print(f"\n{DIM}Not published yet ({len(unpublished)}): "
              f"{', '.join(unpublished[:5])}"
              f"{'…' if len(unpublished) > 5 else ''}{RESET}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Which published runs are ready to have their numbers read?

Every channel has a window before its numbers mean anything, and this script
enforces it in code rather than trusting anyone to remember. The default is
72 hours — right for social channels (LinkedIn, TikTok, Instagram and X all
keep distributing a post for days, so an early read mostly records what time
you posted). It is NOT a universal law: SEO articles need weeks before
Search Console numbers settle, and outreach replies settle faster. Set
`metric_delay_hours` per channel in shared/channels.json and this script
honours it; a channel without one gets the 72h default. Once a number is in
the spine it affects every verdict from then on and nothing flags it as
early — so the window has to bite before the number is written, not after.

Scans every engine folder's runs/index.csv; --engine scopes to one.

Usage:
    due_metrics.py                 # all engines: read now vs still too young
    due_metrics.py --engine seo  # just one engine folder
    due_metrics.py --json          # machine-readable
    due_metrics.py --hours 96      # override every channel's window this call
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gtmfind import find_home, find_engine, list_engines  # noqa: E402

DEFAULT_HOURS = 72
DIM, GREEN, YELLOW, RESET = "\033[2m", "\033[32m", "\033[33m", "\033[0m"


def channel_delays(home: Path) -> dict[str, float]:
    """Per-channel metric_delay_hours from shared/channels.json."""
    ch = home / "shared" / "channels.json"
    if not ch.is_file():
        return {}
    try:
        data = json.loads(ch.read_text())
    except json.JSONDecodeError:
        return {}
    out: dict[str, float] = {}
    for name, cfg in (data.get("channels") or {}).items():
        if isinstance(cfg, dict) and cfg.get("metric_delay_hours") is not None:
            try:
                out[name] = float(cfg["metric_delay_hours"])
            except (TypeError, ValueError):
                pass
    return out


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
    ap.add_argument("--home", "--workspace", dest="home", default="",
                    help="the gtm home (default: ~/gtm, or $GTM_HOME)")
    ap.add_argument("--hours", type=float, default=None,
                    help="override every channel's window for this call")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--engine", "--workflow", dest="engine", default="",
                    help="scope to one engine folder (default: all)")
    a = ap.parse_args()

    home = find_home(a.home)
    if a.engine:
        dirs = [find_engine(home, a.engine)]
    else:
        dirs = list_engines(home)
        if not dirs:
            sys.exit("error: no engine folders in this home")

    delays = channel_delays(home)
    now = datetime.now(timezone.utc)
    due, early, unpublished = [], [], []

    for wd in dirs:
        idx = wd / "runs" / "index.csv"
        if not idx.is_file():
            continue
        with idx.open(newline="") as f:
            for r in csv.DictReader(f):
                if (r.get("metric_value") or "").strip():
                    continue                               # already measured
                if (r.get("status") or "").strip() != "published":
                    if (r.get("status") or "").strip() not in ("killed", ""):
                        unpublished.append(r.get("run_id", ""))
                    continue

                channel = r.get("channel", "")
                threshold = a.hours if a.hours is not None \
                    else delays.get(channel, DEFAULT_HOURS)
                ts = parse_ts(r.get("published_at", ""))
                item = {"run_id": r.get("run_id", ""), "engine": wd.name,
                        "channel": channel,
                        "url": r.get("url", ""), "arm": r.get("arm", ""),
                        "metric": r.get("primary_metric", ""),
                        "threshold_hours": threshold,
                        "published_at": r.get("published_at", "")}
                if ts is None:
                    item["age_hours"] = None
                    due.append(item)                       # no timestamp: don't block on it
                    continue

                age = (now - ts).total_seconds() / 3600
                item["age_hours"] = round(age, 1)
                (due if age >= threshold else early).append(item)

    early.sort(key=lambda x: -(x["age_hours"] or 0))

    if a.json:
        print(json.dumps({"default_hours": DEFAULT_HOURS,
                          "channel_delays": delays, "due": due,
                          "too_early": early, "not_published": unpublished},
                         indent=2))
        return 0

    print(f"\n{GREEN}Ready to read ({len(due)}){RESET}"
          f"{DIM} — past their channel's window, no number yet{RESET}")
    for d in due or []:
        age = f"{d['age_hours']}h" if d["age_hours"] is not None else "age unknown"
        print(f"  {d['run_id']:<30} {d['engine']:<14} {d['channel']:<12} "
              f"{DIM}{age}{RESET}  {d['url']}")
    if not due:
        print(f"  {DIM}nothing{RESET}")

    if early:
        print(f"\n{YELLOW}Too early ({len(early)}){RESET}"
              f"{DIM} — leave these empty, they'll come round{RESET}")
        for d in early:
            wait = d["threshold_hours"] - (d["age_hours"] or 0)
            print(f"  {d['run_id']:<30} {d['engine']:<14} {d['channel']:<12} "
                  f"{DIM}{d['age_hours']}h — {wait:.0f}h to go "
                  f"(window {d['threshold_hours']:.0f}h){RESET}")

    if unpublished:
        print(f"\n{DIM}Not published yet ({len(unpublished)}): "
              f"{', '.join(unpublished[:5])}"
              f"{'…' if len(unpublished) > 5 else ''}{RESET}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

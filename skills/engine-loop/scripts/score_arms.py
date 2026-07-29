#!/usr/bin/env python3
"""Score the live A/B experiments and say whether anything is decided.

Reads only. It never promotes an arm, never edits config, never moves a
template — it reports, and a human (or the weekly job, with approval)
acts on what it says.

Two rules it exists to enforce:

  R6  The cohort decides. All-time is context only. Every row that predates
      an experiment sits in the default arm and would make it look settled
      when it isn't.
  --  Nothing is decided until every arm has min_runs_per_arm AND the leader
      beats the runner-up by win_ratio. "Undecided" is a real answer.

Usage:
    score_arms.py [--workspace PATH] [--json]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

DIM, BOLD, GREEN, YELLOW, RESET = "\033[2m", "\033[1m", "\033[32m", "\033[33m", "\033[0m"


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


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_float(v: str | None) -> float | None:
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def tally(runs: list[dict], exp_id: str, cohort_only: bool, started: str) -> dict:
    out: dict[str, dict] = {}
    for r in runs:
        if r.get("experiment_id") != exp_id:
            continue
        if cohort_only and started and r.get("created_at", "") < started:
            continue
        arm = (r.get("arm") or "").strip() or "default"
        slot = out.setdefault(arm, {"n": 0, "measured": 0, "total": 0.0, "sources": set()})
        slot["n"] += 1
        val = as_float(r.get("metric_value"))
        if val is not None:
            slot["measured"] += 1
            slot["total"] += val
            slot["sources"].add((r.get("metric_source") or "?").strip() or "?")
    for slot in out.values():
        slot["mean"] = slot["total"] / slot["measured"] if slot["measured"] else 0.0
    return out


def judge(stats: dict, min_runs: int, win_ratio: float) -> tuple[str, str]:
    if not stats:
        return "undecided", "no runs yet"
    if len(stats) < 2:
        only = next(iter(stats))
        return "undecided", f"only {only} has runs — nothing to compare it against"

    ranked = sorted(stats.items(), key=lambda kv: kv[1]["mean"], reverse=True)
    (lead_arm, lead), (second_arm, second) = ranked[0], ranked[1]

    short = [f"{a} {s['measured']}/{min_runs}" for a, s in stats.items()
             if s["measured"] < min_runs]
    if short:
        return "undecided", "not enough measured runs — " + ", ".join(short)

    if second["mean"] <= 0:
        return ("decided", f"{lead_arm} wins — {second_arm} scored nothing") \
            if lead["mean"] > 0 else ("undecided", "no arm has scored yet")

    ratio = lead["mean"] / second["mean"]
    if ratio >= win_ratio:
        return "decided", f"{lead_arm} wins — {ratio:.2f}x {second_arm} (needed {win_ratio}x)"
    return "undecided", (f"{lead_arm} leads {second_arm} by only {ratio:.2f}x "
                         f"(needs {win_ratio}x) — keep running")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ws = find_workspace(a.workspace)
    cfg = ws / "config" / "experiments.json"
    if not cfg.is_file():
        sys.exit("error: config/experiments.json not found")
    data = json.loads(cfg.read_text())
    runs = rows(ws / "runs" / "index.csv")

    report = []
    for exp in data.get("experiments", []):
        if exp.get("status") != "live":
            continue
        min_runs = int(exp.get("min_runs_per_arm", 15))
        win_ratio = float(exp.get("win_ratio", 1.2))
        started = exp.get("started", "")

        cohort = tally(runs, exp["id"], True, started)
        alltime = tally(runs, exp["id"], False, started)
        verdict, why = judge(cohort, min_runs, win_ratio)

        report.append({
            "id": exp["id"], "workflow": exp.get("workflow", ""),
            "variable": exp.get("variable", ""), "started": started,
            "min_runs_per_arm": min_runs, "win_ratio": win_ratio,
            "verdict": verdict, "why": why,
            "cohort": {k: {kk: (sorted(vv) if isinstance(vv, set) else vv)
                           for kk, vv in v.items()} for k, v in cohort.items()},
            "alltime_n": {k: v["n"] for k, v in alltime.items()},
        })

    if a.json:
        print(json.dumps(report, indent=2))
        return 0

    if not report:
        print("\nNo live experiments. Add one to config/experiments.json.\n")
        return 0

    for e in report:
        print(f"\n{BOLD}{e['id']}{RESET}  {e['workflow']} · {e['variable']}"
              f"{DIM}  since {e['started'] or '—'}{RESET}")
        print(f"  {'arm':<16}{'runs':>6}{'measured':>10}{'mean':>10}   source")
        for arm, s in sorted(e["cohort"].items(), key=lambda kv: -kv[1]["mean"]):
            print(f"  {arm:<16}{s['n']:>6}{s['measured']:>10}{s['mean']:>10.2f}"
                  f"   {DIM}{','.join(s['sources']) or '—'}{RESET}")

        colour = GREEN if e["verdict"] == "decided" else YELLOW
        print(f"  {colour}{e['verdict']}{RESET} — {e['why']}")

        if e["alltime_n"] != {k: v["n"] for k, v in e["cohort"].items()}:
            allt = ", ".join(f"{k}={v}" for k, v in sorted(e["alltime_n"].items()))
            print(f"  {DIM}all-time (context only, not the decision): {allt}{RESET}")

        if e["verdict"] == "decided":
            print(f"  {DIM}next: promote the winner, move the loser to "
                  f"templates/{e['workflow']}/losers/, write a challenger.{RESET}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

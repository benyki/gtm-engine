#!/usr/bin/env python3
"""Stop a video workflow shipping the same video twice.

The rule: never reuse the same INPUTS **and** the same SCENE DURATIONS.
Same inputs with different durations is fine. Same durations with different
inputs is fine. Both the same is a duplicate, and platforms collapse it.

Two fingerprints per config, so the rule can be checked mechanically:

  inputs_fp    every media input + the on-screen hook copy
  durations_fp the ordered list of segment durations, rounded to 0.1s

`<workflow>/runs/<run_id>/inputs.json` is the config and the only record —
one small JSON per video, written before the render (references/structure-plan.md).
Queued configs in `<workflow>/inputs/queue/` have the same shape and are checked
the same way, so two configs that collide are caught before either is rendered.
There is no second ledger to keep in sync: the fingerprints are always derived
from the files that describe what was actually made.

Usage:
    combo_check.py check --workflow video --inputs runs/<id>/inputs.json
    combo_check.py list  --workflow video
    combo_check.py fp    --inputs <path>        # fingerprints only, no workspace
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# engine-loop ships the workspace finder; same relative spot in the repo and
# in ~/.agents/skills.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "engine-loop" / "scripts"))
from wsfind import find_workspace, find_workflow_dir  # noqa: E402

CONFIG_NAME = "inputs.json"


def _digest(parts: list[str]) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:12]


def input_tokens(cfg: dict) -> list[str]:
    """Every media input plus the hook copy, normalised and sorted.

    Hook copy counts as an input on purpose: two arms testing different text
    over the same footage are genuinely different videos, and the rule must
    not block the experiment it exists to protect.
    """
    tokens: list[str] = []
    for seg in cfg.get("segments") or []:
        bg = seg.get("backgroundFootage") or {}
        ref = bg.get("file") or bg.get("query")
        if ref:
            tokens.append(f"bg:{Path(str(ref)).name.strip().lower()}")
        overlay = seg.get("textOverlay") or {}
        for line in overlay.get("lines") or []:
            tokens.append(f"txt:{' '.join(str(line).split()).lower()}")
    music = (cfg.get("musicBackground") or {}).get("file")
    if music:
        tokens.append(f"music:{Path(str(music)).name.strip().lower()}")
    for extra in cfg.get("extraInputs") or []:           # hook clips, end cards
        tokens.append(f"asset:{Path(str(extra)).name.strip().lower()}")
    return sorted(set(tokens))


def duration_tokens(cfg: dict) -> list[str]:
    return [f"{round(float(s.get('duration') or 0), 1):.1f}"
            for s in (cfg.get("segments") or [])]


def fingerprints(cfg: dict) -> tuple[str, str, list[str], list[str]]:
    ins, durs = input_tokens(cfg), duration_tokens(cfg)
    if not ins:
        print(f"warning: no media inputs or overlay text found — is this an "
              f"{CONFIG_NAME}? (references/structure-plan.md)", file=sys.stderr)
    return _digest(ins), _digest(durs), ins, durs


def load_config(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"error: cannot read config {path}: {e}")


def known_configs(wd: Path) -> list[tuple[str, Path]]:
    """Every config this workflow has committed to: queued and rendered."""
    out = [(f"queue/{p.name}", p)
           for p in sorted((wd / "inputs" / "queue").glob("*.json"))]
    out += [(p.parent.name, p)
            for p in sorted((wd / "runs").glob(f"*/{CONFIG_NAME}"))]
    return out


def collisions(wd: Path, ifp: str, dfp: str, self_path: Path) -> list[str]:
    """Anything already using BOTH the same inputs and the same durations.

    The config being checked never counts against itself — matched on the
    resolved path, since the same file is reachable by several names.
    """
    me = self_path.resolve()
    hits: list[str] = []
    for label, path in known_configs(wd):
        if path.resolve() == me:
            continue
        o_ifp, o_dfp, _, _ = fingerprints(load_config(path))
        if o_ifp == ifp and o_dfp == dfp:
            hits.append(label)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("check", "list", "fp"))
    ap.add_argument("--workflow", default="video", help="workflow FOLDER name")
    ap.add_argument("--workspace")
    ap.add_argument("--inputs", help=f"path to a config ({CONFIG_NAME})")
    a = ap.parse_args()

    if a.command == "fp":
        if not a.inputs:
            sys.exit("error: --inputs required")
        ifp, dfp, ins, durs = fingerprints(load_config(Path(a.inputs)))
        print(json.dumps({"inputs_fp": ifp, "durations_fp": dfp,
                          "durations": durs, "inputs": ins}, indent=2))
        return 0

    wd = find_workflow_dir(find_workspace(a.workspace), a.workflow)

    if a.command == "list":
        rows = []
        for label, path in known_configs(wd):
            ifp, dfp, _, durs = fingerprints(load_config(path))
            rows.append((label, ifp, dfp, " ".join(durs)))
        if not rows:
            print(f"no {CONFIG_NAME} configs yet in {wd}")
            return 0
        w = max(len(r[0]) for r in rows)
        print(f"{'config'.ljust(w)}  inputs_fp     durations_fp  durations")
        for label, ifp, dfp, durs in rows:
            print(f"{label.ljust(w)}  {ifp}  {dfp}  {durs}")
        return 0

    if not a.inputs:
        sys.exit("error: --inputs required")
    path = Path(a.inputs)
    ifp, dfp, _, durs = fingerprints(load_config(path))
    hits = collisions(wd, ifp, dfp, path)
    print(f"inputs_fp {ifp}   durations_fp {dfp}   durations {' '.join(durs)}")
    if not hits:
        print("OK — no config uses both these inputs and these durations.")
        return 0
    print(f"\nDUPLICATE — same inputs AND same durations as: {', '.join(hits)}")
    print("\nChange one side and re-check:")
    print("  · swap a clip, a hook line or the music  → new inputs")
    print("  · re-time the scenes                     → new durations")
    print("Changing both is better. See references/duplicate-safety.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env bash
# The deterministic half of the weekly loop.
#
# Scores the experiments and writes the report from whatever numbers are
# already recorded. Safe to run unattended: it reads and writes files, it
# never posts, sends, or promotes an arm.
#
# It cannot read numbers off TikTok or LinkedIn: that needs a logged-in
# browser, which needs an agent. So this script REPORTS what's waiting, and
# an agent session fills them in. See references/scheduling.md for the
# agent-invoked version that does both.
#
# Usage:  weekly.sh [home_path]        # default: ~/gtm, or $GTM_HOME

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GTM="${1:-}"

# `python3` isn't on every machine (Windows often only has `python`).
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 \
       && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)' 2>/dev/null; then
      PYTHON="$candidate"
      break
    fi
  done
  [[ -n "$PYTHON" ]] || { echo "error: python 3 is not installed" >&2; exit 1; }
fi

# Plain string, not an array: macOS still ships bash 3.2, where an empty
# array expanded under `set -u` is an unbound-variable error.
run() {
  if [[ -n "$GTM" ]]; then
    "$PYTHON" "$HERE/$1" --home "$GTM"
  else
    "$PYTHON" "$HERE/$1"
  fi
}

echo "=========================================="
echo "gtm-engine weekly $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="

echo ""
echo "--- numbers still owed -------------------"
run due_metrics.py

echo "--- experiments --------------------------"
run score_arms.py

echo "--- report -------------------------------"
REPORT=$(run render_report.py)
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
  echo "report failed (exit $STATUS)"
  exit $STATUS
fi

echo "wrote $REPORT"
echo ""
echo "Sections 5 and 6 are blank on purpose: an agent or you fills those in."
echo "Next agent: read each engine's reports/latest.json (and shared/insights.md)"
echo "before deciding anything."

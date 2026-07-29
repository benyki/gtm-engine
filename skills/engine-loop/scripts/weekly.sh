#!/usr/bin/env bash
# The deterministic half of the weekly loop.
#
# Scores the experiments and writes the report from whatever numbers are
# already recorded. Safe to run unattended — it reads and writes files, it
# never posts, sends, or promotes an arm.
#
# It cannot read numbers off TikTok or LinkedIn: that needs a logged-in
# browser, which needs an agent. So this script REPORTS what's waiting, and
# an agent session fills them in. See references/scheduling.md for the
# agent-invoked version that does both.
#
# Usage:  weekly.sh [workspace_path]

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="${1:-}"

# Plain string, not an array: macOS still ships bash 3.2, where an empty
# array expanded under `set -u` is an unbound-variable error.
run() {
  if [[ -n "$WS" ]]; then
    python3 "$HERE/$1" --workspace "$WS"
  else
    python3 "$HERE/$1"
  fi
}

echo "=========================================="
echo "gtm-engine weekly — $(date '+%Y-%m-%d %H:%M')"
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
echo "Sections 5 and 6 are blank on purpose — an agent or you fills those in."
echo "Next agent: read reports/latest.json before deciding anything."

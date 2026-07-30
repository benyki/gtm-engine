#!/usr/bin/env bash
# Install the gtm-engine workflows so your AI agent can find them.
#
# Path chain:
#   <repo>/skills/<name>
#     → COPY → ~/.agents/skills/<name>       (canonical — real files live here)
#     → symlink each → ~/.claude|codex|cursor/skills/<name>  (if that dir exists)
#     → symlink whole → <workspace>/skills → ~/.agents/skills
#
# Re-run after `git pull` in the engine repo to refresh the copies.
# Extra agent dirs: set GTM_AGENT_DIRS (colon-separated skill dirs).
#
# Usage:
#   ./install_skills.sh --workflow seo [--workspace PATH] [--dry-run]
#   ./install_skills.sh --workflow seo,outreach --workspace ./workflows
#   ./install_skills.sh --workflow all --workspace ./workflows
#
#   --workflow NAME    required (comma-separated), or all. Convention:
#                      workflow N installs engine-N when that skill exists;
#                      always installs engine-setup + engine-loop. Custom
#                      names with no engine-N skill get the core pair only.
#   --workspace PATH   project workspace folder (links PATH/skills → canonical)
#   --dry-run          print what would happen, write nothing
#   --help             show this usage

set -euo pipefail

DRY_RUN=0
WORKSPACE=""
WORKFLOW=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
WORKFLOWS_PY="$SCRIPT_DIR/workflows.py"
CANON="$HOME/.agents/skills"

usage() {
  cat <<'EOF'
Install gtm-engine skills for the workflows you actually run.

Always installs engine-setup + engine-loop. For each --workflow NAME, also
installs engine-NAME when that skill exists in the repo.

Path chain:
  <repo>/skills/<name>
    → COPY → ~/.agents/skills/<name>     (canonical)
    → symlink → ~/.claude/skills/<name>  (if present)
    → symlink → ~/.codex/skills/<name>   (if present)
    → symlink → ~/.cursor/skills/<name>  (if present)
    → symlink → <workspace>/skills  →  ~/.agents/skills   (whole folder)

Re-run after git pull to refresh copies. Extra agents: GTM_AGENT_DIRS.

Usage:
  ./install_skills.sh --workflow seo [--workspace PATH] [--dry-run]
  ./install_skills.sh --workflow seo,outreach --workspace ./workflows
  ./install_skills.sh --workflow all --workspace ./workflows

  --workflow NAME    required. Comma-separated names, or all.
  --workspace PATH   project workspace folder (links PATH/skills → canonical)
  --dry-run          print what would happen, write nothing
  --help             show this usage
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --workspace)
      [[ $# -ge 2 ]] || { echo "error: --workspace needs a path" >&2; exit 1; }
      WORKSPACE="$2"; shift 2 ;;
    --workflow|-w)
      [[ $# -ge 2 ]] || { echo "error: --workflow needs a value" >&2; exit 1; }
      WORKFLOW="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "error: unknown arg: $1 (try --help)" >&2
      exit 1
      ;;
  esac
done

read_workflows_marker() {
  local dir="$1"
  if [[ -f "$dir/config/workflows.json" ]]; then
    python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1]))['workflows']))" "$dir/config/workflows.json"
  elif [[ -f "$dir/config/pathways.json" ]]; then
    python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1]))['workflows']))" "$dir/config/pathways.json"
  else
    return 1
  fi
}

if [[ -z "$WORKFLOW" ]]; then
  if [[ -n "$WORKSPACE" ]] && WORKFLOW="$(read_workflows_marker "${WORKSPACE%/}")"; then
    :
  elif [[ -n "$WORKSPACE" ]] && WORKFLOW="$(read_workflows_marker "${WORKSPACE%/}/workflows")"; then
    :
  else
    echo "error: --workflow is required (names, comma-separated, or all)" >&2
    echo "       or pass --workspace pointing at a scaffolded workspace with config/workflows.json" >&2
    exit 1
  fi
fi

SKILL_LIST="$(python3 "$WORKFLOWS_PY" skills "$WORKFLOW")" || exit 1
# shellcheck disable=SC2206
SKILLS=($SKILL_LIST)

say()  { printf '%s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }

# Copy a skill folder into the canonical store (replace prior copy or old symlink).
copy_into_canon() {
  local name="$1" src="$SKILLS_SRC/$name" dest="$CANON/$name"
  if [[ ! -f "$src/SKILL.md" ]]; then
    warn "$name — not found under $SKILLS_SRC"
    return
  fi
  if (( DRY_RUN )); then
    ok "$name (would copy → ${CANON/#$HOME/~}/$name)"
    return
  fi
  if [[ -L "$dest" || -e "$dest" ]]; then
    rm -rf "$dest"
  fi
  cp -R "$src" "$dest"
  ok "$name (copied)"
}

# Symlink target → linkname. Relinks if wrong; warns on real-dir collision.
link() {
  local target="$1" linkname="$2" name
  name="$(basename "$linkname")"

  if [[ -L "$linkname" ]]; then
    if [[ "$(readlink "$linkname")" == "$target" ]]; then
      ok "$name (already linked)"; return
    fi
    (( DRY_RUN )) || { rm "$linkname"; ln -s "$target" "$linkname"; }
    ok "$name (relinked)"; return
  fi

  if [[ -e "$linkname" ]]; then
    warn "$name — a real directory is already there, leaving it alone."
    warn "    Move or delete $linkname, then re-run this script."
    return
  fi

  (( DRY_RUN )) || ln -s "$target" "$linkname"
  ok "$name"
}

link_each_skill_into() {
  local dest="$1" name
  (( DRY_RUN )) || mkdir -p "$dest"
  for name in "${SKILLS[@]}"; do
    if [[ ! -f "$SKILLS_SRC/$name/SKILL.md" ]]; then
      continue
    fi
    link "$CANON/$name" "$dest/$name"
  done
}

resolve_workspace() {
  local raw="${1%/}"
  if [[ -z "$raw" ]]; then
    return 1
  fi
  if [[ -f "$raw/config/workflows.json" || -f "$raw/config/pathways.json" || -f "$raw/config/channels.json" ]]; then
    (cd "$raw" && pwd)
  elif [[ -d "$raw/workflows" ]]; then
    (cd "$raw/workflows" && pwd)
  else
    (cd "$raw" && pwd)
  fi
}

say ""
say "gtm-engine — installing workflows"
say "  from: $REPO_ROOT"
say "  workflows: $WORKFLOW"
say "  skills: ${SKILLS[*]}"
(( DRY_RUN )) && say "  (dry run — nothing will be written)"
say ""

# 1. Canonical store: COPY selected skills into ~/.agents/skills
(( DRY_RUN )) || mkdir -p "$CANON"
say "Canonical store: ${CANON/#$HOME/~}  (copy)"
for name in "${SKILLS[@]}"; do
  copy_into_canon "$name"
done

# 2. Workspace: one symlink of the whole canonical skills folder
if [[ -n "$WORKSPACE" ]]; then
  WS="$(resolve_workspace "$WORKSPACE")" || {
    echo "error: --workspace path not found: $WORKSPACE" >&2
    exit 1
  }
  say ""
  say "Workspace: ${WS/#$HOME/~}/skills  →  ${CANON/#$HOME/~}"
  link "$CANON" "$WS/skills"
fi

# 3. Per-skill symlinks into agent skill dirs that already exist (or whose home exists).
AGENT_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.cursor/skills"
)
if [[ -n "${GTM_AGENT_DIRS:-}" ]]; then
  IFS=':' read -r -a EXTRA_DIRS <<< "$GTM_AGENT_DIRS"
  for EXTRA in "${EXTRA_DIRS[@]}"; do
    [[ -n "$EXTRA" ]] && AGENT_DIRS+=("${EXTRA/#\~/$HOME}")
  done
fi

for AGENT_DIR in "${AGENT_DIRS[@]}"; do
  AGENT_HOME="$(dirname "$AGENT_DIR")"
  if [[ ! -d "$AGENT_HOME" ]]; then
    continue
  fi
  # Create the skills subdir when the agent is installed but skills/ is new.
  (( DRY_RUN )) || mkdir -p "$AGENT_DIR"
  say ""
  say "Agent: ${AGENT_DIR/#$HOME/~}"
  link_each_skill_into "$AGENT_DIR"
done

say ""
say "Done. Next:"
if [[ -z "$WORKSPACE" ]]; then
  say "  Re-run with --workspace <project>/workflows once the workspace exists."
fi
say "  After git pull in the engine repo, re-run this script to refresh copies."
say "  Tell your agent:  run engine-setup"
say ""

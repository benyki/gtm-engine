#!/usr/bin/env bash
# Install the gtm-engine workflows so your AI agent can find them.
#
# Everything is symlinked back into this clone, so `git pull` updates every
# workflow at once and there is never a reinstall step.
#
# Path chain:
#   <repo>/skills/<name>
#     → ~/.agents/skills/<name>              (canonical — the install target)
#     → <workspace>/skills/<name>            (optional --workspace)
#     → ~/.claude/skills, ~/.openclaw/skills (agents that don't read the canonical store)
#
# ~/.agents/skills/ is the cross-agent standard. Codex reads it natively
# (https://developers.openai.com/codex/skills) and so does Cursor
# (https://cursor.com/help/customization/skills) — neither gets a link in its own
# folder, and ~/.codex/skills is not scanned by Codex at all, so a link there is dead.
# Only add an agent directory below if a vendor doc says that agent needs one.
#
# Usage:
#   ./install_skills.sh [--dry-run] [--workspace PATH]
#
#   --workspace PATH   project workflows/ folder (creates PATH/skills/)
#   --dry-run          print what would happen, write nothing
#   --help             show this usage

set -euo pipefail

DRY_RUN=0
WORKSPACE=""

usage() {
  cat <<'EOF'
Install the gtm-engine workflows so your AI agent can find them.

Everything is symlinked back into this clone, so git pull updates every
workflow at once and there is never a reinstall step.

Path chain:
  <repo>/skills/<name>
    → ~/.agents/skills/<name>              (canonical — the install target)
    → <workspace>/skills/<name>            (optional --workspace)
    → ~/.claude/skills, ~/.openclaw/skills (agents that need their own copy)

Codex and Cursor read ~/.agents/skills directly and are skipped on purpose.

Usage:
  ./install_skills.sh [--dry-run] [--workspace PATH]

  --workspace PATH   project workflows/ folder (creates PATH/skills/)
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
    --help|-h) usage; exit 0 ;;
    *)
      echo "error: unknown arg: $1 (try --help)" >&2
      exit 1
      ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"

# Canonical store. Workspace + agent dirs point here (which point at the clone).
CANON="$HOME/.agents/skills"

say()  { printf '%s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }

link() { # link <target> <linkname>
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

link_all_into() { # link_all_into <dest_dir> <target_root>
  # Each skill name in dest → target_root/<name>
  local dest="$1" target_root="$2" dir name
  (( DRY_RUN )) || mkdir -p "$dest"
  for dir in "$SKILLS_SRC"/*/; do
    [[ -f "${dir}SKILL.md" ]] || continue
    name="$(basename "${dir%/}")"
    link "$target_root/$name" "$dest/$name"
  done
}

# Resolve --workspace to an absolute workflows/ directory.
resolve_workspace() {
  local raw="${1%/}"
  if [[ -z "$raw" ]]; then
    return 1
  fi
  # Allow passing either the project root or the workflows/ folder itself.
  if [[ "$(basename "$raw")" == "workflows" ]]; then
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
(( DRY_RUN )) && say "  (dry run — nothing will be written)"
say ""

# 1. Canonical store: clone → ~/.agents/skills
(( DRY_RUN )) || mkdir -p "$CANON"
say "Canonical store: ${CANON/#$HOME/~}"
for dir in "$SKILLS_SRC"/*/; do
  [[ -f "${dir}SKILL.md" ]] || continue
  link "${dir%/}" "$CANON/$(basename "$dir")"
done

# 2. Project workspace: ~/.agents/skills → <workspace>/skills
if [[ -n "$WORKSPACE" ]]; then
  WS="$(resolve_workspace "$WORKSPACE")" || {
    echo "error: --workspace path not found: $WORKSPACE" >&2
    exit 1
  }
  say ""
  say "Workspace: ${WS/#$HOME/~}/skills"
  link_all_into "$WS/skills" "$CANON"
fi

# 3. Mirror into the agents that don't read the canonical store (if present).
#    Claude Code — https://code.claude.com/docs/en/skills — reads only its own dirs.
#    OpenClaw    — own layout, no public doc; verified by the directory being there.
#    Codex and Cursor are deliberately absent: both read ~/.agents/skills natively,
#    and ~/.codex/skills isn't scanned at all, so a link there would be dead.
AGENT_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.openclaw/skills"
)

for AGENT_DIR in "${AGENT_DIRS[@]}"; do
  AGENT_HOME="$(dirname "$AGENT_DIR")"
  if [[ ! -d "$AGENT_HOME" ]]; then
    continue
  fi

  say ""
  say "Agent: ${AGENT_DIR/#$HOME/~}"
  link_all_into "$AGENT_DIR" "$CANON"
done

# 4. Report links an older version of this script left where nothing reads them.
#    Reported, never deleted — it's their home directory, not ours.
report_legacy() { # report_legacy <dir> <note>
  local dir="$1" note="$2" dir_name found=() name
  [[ -d "$dir" ]] || return 0
  for dir_name in "$SKILLS_SRC"/*/; do
    [[ -f "${dir_name}SKILL.md" ]] || continue
    name="$(basename "${dir_name%/}")"
    [[ -L "$dir/$name" ]] && found+=("$name")
  done
  (( ${#found[@]} )) || return 0
  say ""
  say "Legacy: ${dir/#$HOME/~}"
  warn "${#found[@]} link(s) from an older install — $note"
  warn "    Safe to delete:  rm ${dir/#$HOME/~}/{$(IFS=,; echo "${found[*]}")}"
}

report_legacy "$HOME/.codex/skills" "Codex doesn't scan this path; it reads ~/.agents/skills"
report_legacy "$HOME/.cursor/skills" "harmless, but Cursor already reads ~/.agents/skills"

say ""
say "Done. Next:"
if [[ -z "$WORKSPACE" ]]; then
  say "  Re-run with --workspace <project>/workflows once the workspace exists."
fi
say "  Tell your agent:  run engine-setup"
say ""

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
# (Vendor behaviour verified as of 2026-07 — vendors change this; re-check the doc
# before trusting it, and only add an agent directory if a vendor doc says so.)
#
# Extra agent directories WITHOUT editing this script: set GTM_AGENT_DIRS to a
# colon-separated list of skill dirs (e.g. ~/.windsurf/skills) and each existing
# parent gets the same symlinks as the built-in mirrors.
#
# Usage:
#   ./install_skills.sh --workflow seo [--workspace PATH] [--dry-run]
#   ./install_skills.sh --workflow seo,outreach --workspace ./workflows
#   ./install_skills.sh --workflow all --workspace ./workflows
#
#   --workflow NAME    required (comma-separated). Built-ins: seo | linkedin |
#                      video | outreach | all. Custom workflow names are accepted
#                      too — they install just engine-setup + engine-loop, which
#                      is all a custom workflow needs.
#   --workspace PATH   project workspace folder (creates PATH/skills/)
#   --dry-run          print what would happen, write nothing
#   --help             show this usage

set -euo pipefail

DRY_RUN=0
WORKSPACE=""
WORKFLOW=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
PATHWAYS_PY="$SCRIPT_DIR/pathways.py"

usage() {
  cat <<'EOF'
Install gtm-engine skills for the workflows you actually run.

Always installs engine-setup + engine-loop, plus one skill per --workflow.

Path chain:
  <repo>/skills/<name>
    → ~/.agents/skills/<name>              (canonical — the install target)
    → <workspace>/skills/<name>            (optional --workspace)
    → ~/.claude/skills, ~/.openclaw/skills (agents that need their own copy)

Codex and Cursor read ~/.agents/skills directly and are skipped on purpose
(verified as of 2026-07 — re-check the vendor doc before trusting it).

For other agents, set GTM_AGENT_DIRS to a colon-separated list of skill
directories (e.g. ~/.windsurf/skills:~/.zed/skills) and they get the same
symlinks as the built-in mirrors.

Usage:
  ./install_skills.sh --workflow seo [--workspace PATH] [--dry-run]
  ./install_skills.sh --workflow seo,outreach --workspace ./workflows
  ./install_skills.sh --workflow all --workspace ./workflows

  --workflow NAME    required. Built-ins: seo | linkedin | video | outreach | all.
                     Custom workflow names accepted (install the core pair only).
  --workspace PATH   project workspace folder (creates PATH/skills/)
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

if [[ -z "$WORKFLOW" ]]; then
  # Infer from an existing workspace marker when possible.
  if [[ -n "$WORKSPACE" && -f "${WORKSPACE%/}/config/pathways.json" ]]; then
    WORKFLOW="$(python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1]))['workflows']))" "${WORKSPACE%/}/config/pathways.json")"
  elif [[ -n "$WORKSPACE" && -f "${WORKSPACE%/}/workflows/config/pathways.json" ]]; then
    WORKFLOW="$(python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1]))['workflows']))" "${WORKSPACE%/}/workflows/config/pathways.json")"
  else
    echo "error: --workflow is required (built-ins: seo | linkedin | video | outreach | all; custom names ok)" >&2
    echo "       or pass --workspace pointing at a scaffolded workspace with config/pathways.json" >&2
    exit 1
  fi
fi

SKILL_LIST="$(python3 "$PATHWAYS_PY" skills "$WORKFLOW")" || exit 1
# shellcheck disable=SC2206
SKILLS=($SKILL_LIST)

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

link_selected_into() { # link_selected_into <dest_dir> <target_root>
  local dest="$1" target_root="$2" name
  (( DRY_RUN )) || mkdir -p "$dest"
  for name in "${SKILLS[@]}"; do
    if [[ ! -f "$SKILLS_SRC/$name/SKILL.md" ]]; then
      warn "$name — not found under $SKILLS_SRC"
      continue
    fi
    link "$target_root/$name" "$dest/$name"
  done
}

# Resolve --workspace to an absolute workspace directory. A workspace is
# recognised by its marker (config/pathways.json or config/channels.json),
# not by being named "workflows" — that's only the default name.
resolve_workspace() {
  local raw="${1%/}"
  if [[ -z "$raw" ]]; then
    return 1
  fi
  # Allow passing either the workspace itself or the project root above it.
  if [[ -f "$raw/config/pathways.json" || -f "$raw/config/channels.json" ]]; then
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

# 1. Canonical store: clone → ~/.agents/skills (selected skills only)
(( DRY_RUN )) || mkdir -p "$CANON"
say "Canonical store: ${CANON/#$HOME/~}"
for name in "${SKILLS[@]}"; do
  if [[ ! -f "$SKILLS_SRC/$name/SKILL.md" ]]; then
    warn "$name — not found under $SKILLS_SRC"
    continue
  fi
  link "$SKILLS_SRC/$name" "$CANON/$name"
done

# 2. Project workspace: ~/.agents/skills → <workspace>/skills
if [[ -n "$WORKSPACE" ]]; then
  WS="$(resolve_workspace "$WORKSPACE")" || {
    echo "error: --workspace path not found: $WORKSPACE" >&2
    exit 1
  }
  say ""
  say "Workspace: ${WS/#$HOME/~}/skills"
  link_selected_into "$WS/skills" "$CANON"
fi

# 3. Mirror into the agents that don't read the canonical store (if present).
#    GTM_AGENT_DIRS (colon-separated skill dirs) extends this list without
#    editing the script — for agents this table doesn't know about yet.
AGENT_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.openclaw/skills"
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

  say ""
  say "Agent: ${AGENT_DIR/#$HOME/~}"
  link_selected_into "$AGENT_DIR" "$CANON"
done

# 4. Report links an older version of this script left where nothing reads them.
report_legacy() {
  local dir="$1" note="$2" found=() name
  [[ -d "$dir" ]] || return 0
  for name in "${SKILLS[@]}"; do
    [[ -L "$dir/$name" ]] && found+=("$name")
  done
  # Also flag any other engine-* links from a fuller prior install.
  local extra
  for extra in "$dir"/engine-*; do
    [[ -L "$extra" ]] || continue
    name="$(basename "$extra")"
    local known=0 s
    for s in "${SKILLS[@]}"; do
      [[ "$s" == "$name" ]] && known=1 && break
    done
    (( known )) || found+=("$name")
  done
  (( ${#found[@]} )) || return 0
  # dedupe
  local uniq=() f u seen
  for f in "${found[@]}"; do
    seen=0
    for u in "${uniq[@]+"${uniq[@]}"}"; do
      [[ "$u" == "$f" ]] && seen=1 && break
    done
    (( seen )) || uniq+=("$f")
  done
  say ""
  say "Legacy: ${dir/#$HOME/~}"
  warn "${#uniq[@]} link(s) from an older install — $note"
  warn "    Safe to delete:  rm ${dir/#$HOME/~}/{$(IFS=,; echo "${uniq[*]}")}"
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

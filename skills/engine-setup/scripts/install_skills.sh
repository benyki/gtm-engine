#!/usr/bin/env bash
# Install the gtm-engine skills so your AI agent can find them.
#
# Path chain:
#   <repo>/skills/<name>
#     -> COPY -> ~/.agents/skills/<name>       (canonical: real files live here)
#     -> symlink each -> ~/.claude|codex|cursor/skills/<name>  (if that dir exists)
#     -> symlink whole -> <home>/skills -> ~/.agents/skills
#
# Re-run after `git pull` in the engine repo to refresh the copies.
# Extra agent dirs: set GTM_AGENT_DIRS (colon-separated skill dirs).
#
# Usage:
#   ./install_skills.sh [--home PATH] [--engine seo] [--dry-run]
#   ./install_skills.sh --engine seo,outreach
#   ./install_skills.sh --engine all
#
#   --engine NAME      optional. Comma-separated name[:type] or all. Left out,
#                      it is inferred from the engines registered in
#                      <home>/engines.json. Convention: type N installs
#                      engine-N when that skill exists; always installs
#                      engine-setup + engine-loop. Custom types with no
#                      engine-N skill get the core pair only.
#   --home PATH        the gtm home (default: ~/gtm, or $GTM_HOME). Links
#                      PATH/skills -> the canonical store.
#   --dry-run          print what would happen, write nothing
#   --help             show this usage
#
# --workspace and --workflow still work as names for --home and --engine.

set -euo pipefail

DRY_RUN=0
GTM_DIR="${GTM_HOME:-$HOME/gtm}"
ENGINE=""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
ENGINES_PY="$SCRIPT_DIR/engines.py"
CANON="$HOME/.agents/skills"

usage() {
  cat <<'EOF'
Install gtm-engine skills for the engines you actually run.

Always installs engine-setup + engine-loop. For each --engine NAME, also
installs engine-NAME when that skill exists in the repo.

Path chain:
  <repo>/skills/<name>
    -> COPY -> ~/.agents/skills/<name>     (canonical)
    -> symlink -> ~/.claude/skills/<name>  (if present)
    -> symlink -> ~/.codex/skills/<name>   (if present)
    -> symlink -> ~/.cursor/skills/<name>  (if present)
    -> symlink -> <home>/skills  ->  ~/.agents/skills   (whole folder)

Re-run after git pull to refresh copies. Extra agents: GTM_AGENT_DIRS.

Usage:
  ./install_skills.sh [--home PATH] [--engine seo] [--dry-run]
  ./install_skills.sh --engine seo,outreach
  ./install_skills.sh --engine all

  --engine NAME      optional. Inferred from the engines registered in
                     <home>/engines.json when left out; 'all' when the home
                     has none yet. Comma-separated names or types.
  --home PATH        the gtm home (default: ~/gtm, or $GTM_HOME)
  --dry-run          print what would happen, write nothing
  --help             show this usage

--workspace and --workflow are accepted as the old names for --home/--engine.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --home|--workspace)
      [[ $# -ge 2 ]] || { echo "error: $1 needs a path" >&2; exit 1; }
      GTM_DIR="$2"; shift 2 ;;
    --engine|--workflow|-e|-w)
      [[ $# -ge 2 ]] || { echo "error: $1 needs a value" >&2; exit 1; }
      ENGINE="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *)
      echo "error: unknown arg: $1 (try --help)" >&2
      exit 1
      ;;
  esac
done

GTM_DIR="${GTM_DIR/#\~/$HOME}"
GTM_DIR="${GTM_DIR%/}"

# Which skills? The types of the engines registered to this home. Engines can
# live anywhere, so engines.json is the only thing that knows they exist.
if [[ -z "$ENGINE" ]]; then
  ENGINE="$(python3 - "$SCRIPT_DIR" "$GTM_DIR" <<'PYEOF'
import sys, pathlib
sys.path.insert(0, sys.argv[1])
import engines as eng
home = pathlib.Path(sys.argv[2]).expanduser()
types = eng.home_types(home) if home.is_dir() else []
print(",".join(types) if types else "all")
PYEOF
)" || ENGINE="all"
fi

SKILL_LIST="$(python3 "$ENGINES_PY" skills "$ENGINE")" || exit 1
# shellcheck disable=SC2206
SKILLS=($SKILL_LIST)

say()  { printf '%s\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }

# Copy a skill folder into the canonical store (replace prior copy or old symlink).
copy_into_canon() {
  local name="$1" src="$SKILLS_SRC/$name" dest="$CANON/$name"
  if [[ ! -f "$src/SKILL.md" ]]; then
    warn "$name not found under $SKILLS_SRC"
    return
  fi
  if (( DRY_RUN )); then
    ok "$name (would copy to ${CANON/#$HOME/~}/$name)"
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
    warn "$name: a real directory is already there, leaving it alone."
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

say ""
say "gtm-engine: installing skills"
say "  from: $REPO_ROOT"
say "  home: ${GTM_DIR/#$HOME/~}"
say "  engines: $ENGINE"
say "  skills: ${SKILLS[*]}"
(( DRY_RUN )) && say "  (dry run, nothing will be written)"
say ""

# 1. Canonical store: COPY selected skills into ~/.agents/skills
(( DRY_RUN )) || mkdir -p "$CANON"
say "Canonical store: ${CANON/#$HOME/~}  (copy)"
for name in "${SKILLS[@]}"; do
  copy_into_canon "$name"
done

# 2. The home: one symlink of the whole canonical skills folder, so
# `skills/...` resolves from ~/gtm the same way it did from a v1 workspace.
if [[ -d "$GTM_DIR" ]]; then
  say ""
  say "Home: ${GTM_DIR/#$HOME/~}/skills  ->  ${CANON/#$HOME/~}"
  link "$CANON" "$GTM_DIR/skills"
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
if [[ ! -d "$GTM_DIR" ]]; then
  say "  No home at ${GTM_DIR/#$HOME/~} yet. Run scaffold.py, then re-run this."
fi
say "  After git pull in the engine repo, re-run this script to refresh copies."
say "  Tell your agent:  run engine-setup"
say ""

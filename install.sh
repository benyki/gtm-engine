#!/usr/bin/env bash
# gtm-engine one-command install.
#
# Run it from the project you want to grow. It clones the engine somewhere
# durable, creates `workflows/` right here, and links the skills into whichever
# agents you have (Claude Code, Codex, Cursor).
#
#   curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash -s -- --workflow seo,outreach
#
# Already cloned? Run it from the clone and it uses that copy:
#   ~/code/gtm-engine/install.sh --workflow outreach
#
# Options: --workflow, --name, --engine-dir. See usage() below or --help.
# Safe to re-run: it pulls, adds what you name, overwrites nothing you own.

set -euo pipefail

REPO_URL="${GTM_ENGINE_REPO:-https://github.com/benyki/gtm-engine.git}"
ENGINE_DIR="${GTM_ENGINE_DIR:-$HOME/code/gtm-engine}"
WORKFLOW="outreach"
WS_NAME="workflows"

say()  { printf '%s\n' "$*"; }
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }
die()  { printf '\nerror: %s\n' "$*" >&2; exit 1; }
# Paths are for humans: print ~/code/… not /Users/you/code/….
tilde() { case "$1" in "$HOME"/*) printf '~%s' "${1#"$HOME"}" ;; *) printf '%s' "$1" ;; esac; }

usage() {
  cat <<'EOF'
gtm-engine install — run it from the project you want to grow.

  curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
  curl -fsSL .../install.sh | bash -s -- --workflow seo,outreach

Clones the engine somewhere durable, creates `workflows/` in the current
directory, and links the skills into the agents you have installed.

  --workflow NAME    workflow folder(s) to create (default: outreach).
                     Comma list of name[:type], or `all`. Any name works —
                     `newsletter` scaffolds a custom workflow.
  --name NAME        workspace folder name (default: workflows)
  --engine-dir PATH  where the clone lives (default: ~/code/gtm-engine,
                     or $GTM_ENGINE_DIR)
  --help             this text

Writes to: the engine dir, ./<workspace>, ~/.agents/skills, and one symlink
per agent skills folder. It never sends, posts, or reads your secrets.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workflow|-w) [[ $# -ge 2 ]] || die "--workflow needs a value"; WORKFLOW="$2"; shift 2 ;;
    --name)        [[ $# -ge 2 ]] || die "--name needs a value";     WS_NAME="$2";  shift 2 ;;
    --engine-dir)  [[ $# -ge 2 ]] || die "--engine-dir needs a path"; ENGINE_DIR="$2"; shift 2 ;;
    --help|-h)     usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

ENGINE_DIR="${ENGINE_DIR/#\~/$HOME}"
PROJECT="$(pwd -P)"

command -v git     >/dev/null 2>&1 || die "git is not installed — https://git-scm.com/downloads"
command -v python3 >/dev/null 2>&1 || die "python3 is not installed — https://www.python.org/downloads/"

# Running from inside a clone? Use it, don't fetch a second copy.
SELF="${BASH_SOURCE[0]:-}"
if [[ -n "$SELF" && -f "$SELF" ]]; then
  SELF_DIR="$(cd "$(dirname "$SELF")" && pwd -P)"
  [[ -f "$SELF_DIR/skills/engine-setup/scripts/scaffold_workspace.py" ]] && ENGINE_DIR="$SELF_DIR"
fi

# The workspace is your data; the clone is the engine. They never mix.
if [[ -f "$PROJECT/workspace/.gtm-template" || "$PROJECT" == "$ENGINE_DIR" || "$PROJECT" == "$ENGINE_DIR"/* ]]; then
  die "you're inside the gtm-engine clone. cd to the project you want to grow and run this there."
fi
if [[ "$PROJECT" == "$HOME" || "$PROJECT" == "$HOME/Downloads"* ]]; then
  say "warning: $(tilde "$PROJECT") isn't a durable home for a workspace. Ctrl-C and cd"
  say "         somewhere under ~/code (or any folder you keep) if that wasn't deliberate."
fi

step "1/3  Engine  →  $(tilde "$ENGINE_DIR")"
if [[ -d "$ENGINE_DIR/.git" ]]; then
  say "already cloned — pulling"
  git -C "$ENGINE_DIR" pull --ff-only || say "pull skipped (local changes or no network) — using the copy on disk"
elif [[ -e "$ENGINE_DIR" ]]; then
  die "$ENGINE_DIR exists but isn't a git clone. Move it, or pass --engine-dir <path>."
else
  mkdir -p "$(dirname "$ENGINE_DIR")"
  git clone --depth 1 "$REPO_URL" "$ENGINE_DIR"
fi

SCRIPTS="$ENGINE_DIR/skills/engine-setup/scripts"
[[ -f "$SCRIPTS/scaffold_workspace.py" ]] || die "$ENGINE_DIR doesn't look like a gtm-engine clone"

step "2/3  Workspace  →  $(tilde "$PROJECT")/$WS_NAME"
MERGE=""
if [[ -d "$PROJECT/$WS_NAME" ]]; then
  say "$WS_NAME/ exists — merging, nothing you already have is touched"
  MERGE="--merge"
fi
python3 "$SCRIPTS/scaffold_workspace.py" "$PROJECT" --name "$WS_NAME" --workflow "$WORKFLOW" ${MERGE:+"$MERGE"}

step "3/3  Skills  →  ~/.agents/skills  (+ a symlink per agent)"
bash "$SCRIPTS/install_skills.sh" --workspace "$PROJECT/$WS_NAME"

step "Done."
cat <<EOF
Your workspace is $(tilde "$PROJECT")/$WS_NAME — read its AGENTS.md, those are
the house rules every agent working in there follows.

Next:
  1. cp $WS_NAME/shared/.env.example $WS_NAME/shared/.env   (only the keys you need)
  2. Open Claude Code or Codex in $(tilde "$PROJECT") and tell it:  run engine-setup
     — it fills in your brand config and runs the checks.

Update later, from here:
  git -C $(tilde "$ENGINE_DIR") pull && bash $(tilde "$SCRIPTS")/install_skills.sh --workspace ./$WS_NAME
EOF

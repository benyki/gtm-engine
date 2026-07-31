#!/usr/bin/env bash
# gtm-engine one-command install.
#
# Run it from the project you want to grow. Everything lands right here:
# `gtm-engine/` (the clone) and `workflows/` (your workspace) side by side,
# plus every skill linked into whichever agents you have.
#
# You get all four workflows — seo, social, video, outreach — and all six
# skills. Run whichever one you like first; the others cost nothing sitting
# there. Narrow it with --workflow if you'd rather start with one folder.
#
#   curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash -s -- --workflow outreach
#
# Already cloned? Run it from the clone and it uses that copy:
#   ./gtm-engine/install.sh
#
# Options: --workflow, --name, --engine-dir. See usage() below or --help.
# Safe to re-run: it pulls, adds what you name, overwrites nothing you own.

set -euo pipefail

REPO_URL="${GTM_ENGINE_REPO:-https://github.com/benyki/gtm-engine.git}"
PROJECT="$(pwd -P)"
# The clone lands beside the workspace, in the folder you ran this from —
# one self-contained project, nothing to remember the path of.
ENGINE_DIR="${GTM_ENGINE_DIR:-$PROJECT/gtm-engine}"
WORKFLOW="all"
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
  curl -fsSL .../install.sh | bash -s -- --workflow outreach

Creates ./gtm-engine (the clone) and ./workflows (your workspace) side by
side in the current directory, and links every skill into the agents you have.

By default you get all four workflows — seo, social, video, outreach — and
all six skills. Run whichever you like first.

  --workflow NAME    workflow folder(s) to create (default: all four).
                     Comma list of name[:type], or `all`. Any name works —
                     `newsletter` scaffolds a custom workflow.
  --name NAME        workspace folder name (default: workflows)
  --engine-dir PATH  put the clone elsewhere, e.g. ~/code/gtm-engine to share
                     one clone across projects (or set $GTM_ENGINE_DIR)
  --help             this text

Writes to: ./gtm-engine, ./<workspace>, ~/.agents/skills, one symlink per
agent skills folder, and .gitignore if this is a git repo. It never sends,
posts, or reads your secrets.
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

# A clone inside a git repo is somebody else's code sitting in your history —
# ignore it, once, without touching a rule that's already there.
GI="$PROJECT/.gitignore"
if [[ -d "$PROJECT/.git" && "$ENGINE_DIR" == "$PROJECT/gtm-engine" ]] \
   && ! grep -qE '^/?gtm-engine/?$' "$GI" 2>/dev/null; then
  [[ -s "$GI" && -n "$(tail -c 1 "$GI")" ]] && printf '\n' >> "$GI"
  printf '# the gtm-engine clone — the engine, not your code\ngtm-engine/\n' >> "$GI"
  say "added gtm-engine/ to .gitignore"
fi

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
# Show the clone the way you'd type it from here: ./gtm-engine when it's
# inside the project, ~/code/gtm-engine when it's shared.
ENGINE_REL="$(tilde "$ENGINE_DIR")"
[[ "$ENGINE_DIR" == "$PROJECT/"* ]] && ENGINE_REL=".${ENGINE_DIR#"$PROJECT"}"
cat <<EOF
Your workspace is $(tilde "$PROJECT")/$WS_NAME — read its AGENTS.md, those are
the house rules every agent working in there follows.

Every skill is installed and every workflow folder is scaffolded. Run one
first — outreach is the fastest to a real signal — and leave the rest until
you want them. An unused folder costs nothing; delete any you'll never run.

Next:
  1. cp $WS_NAME/shared/.env.example $WS_NAME/shared/.env   (only the keys you need)
  2. Open Claude Code or Codex in $(tilde "$PROJECT") and tell it:  run engine-setup
     — it fills in your brand config and runs the checks.

Update later, from here:
  git -C $ENGINE_REL pull && bash $ENGINE_REL/skills/engine-setup/scripts/install_skills.sh --workspace ./$WS_NAME
EOF

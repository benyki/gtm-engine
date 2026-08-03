#!/usr/bin/env bash
# gtm-engine one-command install.
#
# Three things land, and keeping them apart is the point:
#
#   ~/.gtm-engine    the clone. one per machine, read-only, updated by git pull
#   ~/gtm            YOUR home: brand, keys, assets, insights, and engines.json
#   <somewhere>/     the engine folders. anywhere you like. ~/gtm/engines by
#                    default, or `--at ./engines` to keep a project's engines
#                    with the project
#
# You get all four engines (seo, social, video, outreach) and all six skills.
# Run whichever one you like first; the others cost nothing sitting there.
#
#   curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
#   curl -fsSL .../install.sh | bash -s -- --engine outreach
#   curl -fsSL .../install.sh | bash -s -- --at ./engines --project acme
#
# Already cloned? Run it from the clone and it uses that copy:
#   ~/.gtm-engine/install.sh
#
# Options: --home, --engine, --at, --project, --engine-dir. See --help.
# Safe to re-run: it pulls, adds what you name, overwrites nothing you own.

set -euo pipefail

REPO_URL="${GTM_ENGINE_REPO:-https://github.com/benyki/gtm-engine.git}"
PROJECT="$(pwd -P)"
# One clone per machine, out of the way. Nothing to gitignore in your repos,
# one `git pull` to update however many projects you grow.
ENGINE_DIR="${GTM_ENGINE_DIR:-$HOME/.gtm-engine}"
GTM_DIR="${GTM_HOME:-$HOME/gtm}"
ENGINE="all"
AT=""
PROJECT_NAME=""

say()  { printf '%s\n' "$*"; }
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }
die()  { printf '\nerror: %s\n' "$*" >&2; exit 1; }
# Paths are for humans: print ~/code/... not /Users/you/code/....
tilde() { case "$1" in "$HOME"/*) printf '~%s' "${1#"$HOME"}" ;; *) printf '%s' "$1" ;; esac; }

usage() {
  cat <<'EOF'
gtm-engine install.

  curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
  curl -fsSL .../install.sh | bash -s -- --engine outreach
  curl -fsSL .../install.sh | bash -s -- --at ./engines --project acme

Creates ~/.gtm-engine (the clone) and ~/gtm (your home: brand, keys, assets,
insights, and engines.json). By default the four engine folders go in
~/gtm/engines. Every skill is linked into the agents you have.

  --home PATH        where your shared home lives (default: ~/gtm)
  --engine NAME      engine folder(s) to create (default: all four).
                     Comma list of name[:type], or `all`, or `none` for the
                     home only. Any name works: `newsletter` scaffolds a
                     custom engine.
  --at PATH          where the engine FOLDERS go (default: <home>/engines).
                     `--at ./engines` keeps this project's engines with the
                     project, which is the shape to use once you grow more
                     than one thing.
  --project NAME     the project these engines grow. Recorded in engine.json
                     and used to name folders `engine-<type>-<project>` when
                     they live in the shared home.
  --engine-dir PATH  put the clone somewhere other than ~/.gtm-engine
  --help             this text

Writes to: ~/.gtm-engine, ~/gtm, the engine folders you asked for,
~/.agents/skills, and one symlink per agent skills folder. It never sends,
posts, or reads your secrets.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine|--workflow|-e|-w) [[ $# -ge 2 ]] || die "$1 needs a value"; ENGINE="$2"; shift 2 ;;
    --home)        [[ $# -ge 2 ]] || die "--home needs a path";       GTM_DIR="$2"; shift 2 ;;
    --at)          [[ $# -ge 2 ]] || die "--at needs a path";         AT="$2"; shift 2 ;;
    --project)     [[ $# -ge 2 ]] || die "--project needs a name";    PROJECT_NAME="$2"; shift 2 ;;
    --engine-dir)  [[ $# -ge 2 ]] || die "--engine-dir needs a path"; ENGINE_DIR="$2"; shift 2 ;;
    --help|-h)     usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

ENGINE_DIR="${ENGINE_DIR/#\~/$HOME}"
GTM_DIR="${GTM_DIR/#\~/$HOME}"
[[ -n "$AT" ]] && AT="${AT/#\~/$HOME}"

command -v git     >/dev/null 2>&1 || die "git is not installed: https://git-scm.com/downloads"
command -v python3 >/dev/null 2>&1 || die "python3 is not installed: https://www.python.org/downloads/"

# Running from inside a clone? Use it, don't fetch a second copy.
SELF="${BASH_SOURCE[0]:-}"
if [[ -n "$SELF" && -f "$SELF" ]]; then
  SELF_DIR="$(cd "$(dirname "$SELF")" && pwd -P)"
  [[ -f "$SELF_DIR/skills/engine-setup/scripts/scaffold.py" ]] && ENGINE_DIR="$SELF_DIR"
fi

step "1/3  Engine  ->  $(tilde "$ENGINE_DIR")"
if [[ -d "$ENGINE_DIR/.git" ]]; then
  say "already cloned, pulling"
  git -C "$ENGINE_DIR" pull --ff-only || say "pull skipped (local changes or no network), using the copy on disk"
elif [[ -e "$ENGINE_DIR" ]]; then
  die "$ENGINE_DIR exists but isn't a git clone. Move it, or pass --engine-dir <path>."
else
  mkdir -p "$(dirname "$ENGINE_DIR")"
  git clone --depth 1 "$REPO_URL" "$ENGINE_DIR"
fi

SCRIPTS="$ENGINE_DIR/skills/engine-setup/scripts"
[[ -f "$SCRIPTS/scaffold.py" ]] || die "$ENGINE_DIR doesn't look like a gtm-engine clone"

# `engines/` is also Rails' name for mountable engines. If one is already
# there and it isn't ours, say so rather than scaffolding into it.
if [[ -n "$AT" && -d "$AT" && ! -f "$AT/.gtm-engines" ]] && \
   [[ -n "$(ls -A "$AT" 2>/dev/null)" ]]; then
  say "note: $(tilde "$AT") already exists with files in it. Nothing is overwritten,"
  say "      but if that folder belongs to something else, pass a different --at."
fi

step "2/3  Home  ->  $(tilde "$GTM_DIR")"
say "Everything shared between your engines lives here: brand voice, accounts,"
say "keys, assets, what previous runs taught, and engines.json, which records"
say "where every engine folder is. Nothing in here is touched by an update."
python3 "$SCRIPTS/scaffold.py" --home "$GTM_DIR" --engine "$ENGINE" --merge \
  ${AT:+--at "$AT"} ${PROJECT_NAME:+--project "$PROJECT_NAME"}

step "3/3  Skills  ->  ~/.agents/skills  (+ a symlink per agent)"
bash "$SCRIPTS/install_skills.sh" --home "$GTM_DIR"

step "Done."
cat <<EOF
Your home is $(tilde "$GTM_DIR"). Read its AGENTS.md: those are the house rules
every agent working on your growth follows.

Every engine is listed in $(tilde "$GTM_DIR")/engines.json. Move an engine folder and
you update that file in the same breath, or nothing will find it again.

Next:
  1. cp $(tilde "$GTM_DIR")/shared/.env.example $(tilde "$GTM_DIR")/shared/.env   (only the keys you need)
  2. Open Claude Code or Codex and tell it:  run engine-setup
     It fills in your brand config and runs the checks.

Add an engine to a project later, from that project:
  python3 $(tilde "$ENGINE_DIR")/skills/engine-setup/scripts/scaffold.py \\
    --engine outreach --at ./engines --project <name>

Update:
  git -C $(tilde "$ENGINE_DIR") pull && bash $(tilde "$ENGINE_DIR")/skills/engine-setup/scripts/install_skills.sh
EOF

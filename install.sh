#!/usr/bin/env bash
# gtm-engine install: the five skills, nothing else.
#
#   curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash
#
# Copies skills/gtm and skills/gtm-* into ~/.agents/skills, then links each one
# into every agent skills folder that exists (Claude Code, Codex, Cursor).
# Run from a clone and it uses that copy; piped from curl, it fetches a
# throwaway one. Re-run to update: the copies are refreshed, nothing else on
# your disk changes. It never sends, posts, or reads your secrets.

set -euo pipefail

REPO_URL="${GTM_ENGINE_REPO:-https://github.com/benyki/gtm-engine.git}"
SKILLS_DIR="${GTM_SKILLS_DIR:-$HOME/.agents/skills}"
AGENT_DIRS=("$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.cursor/skills")

say()  { printf '%s\n' "$*"; }
step() { printf '\n\033[1m%s\033[0m\n' "$*"; }
die()  { printf '\nerror: %s\n' "$*" >&2; exit 1; }
# Paths are for humans: print ~/code/... not /Users/you/code/....
tilde() { case "$1" in "$HOME"/*) printf '~%s' "${1#"$HOME"}" ;; *) printf '%s' "$1" ;; esac; }

usage() {
  cat <<'EOF'
gtm-engine install.

  curl -fsSL https://raw.githubusercontent.com/benyki/gtm-engine/main/install.sh | bash

Copies the gtm skills into ~/.agents/skills (or $GTM_SKILLS_DIR) and links
each one into ~/.claude/skills, ~/.codex/skills and ~/.cursor/skills when
that agent is installed. Re-run to update. Takes no options.
EOF
}

case "${1:-}" in
  --help|-h) usage; exit 0 ;;
  "") ;;
  *) die "unknown option: $1 (this installer takes none)" ;;
esac

# Running from inside a clone? Use it, don't fetch a second copy.
SRC=""
SELF="${BASH_SOURCE[0]:-}"
if [[ -n "$SELF" && -f "$SELF" ]]; then
  SELF_DIR="$(cd "$(dirname "$SELF")" && pwd -P)"
  [[ -f "$SELF_DIR/skills/gtm/SKILL.md" ]] && SRC="$SELF_DIR"
fi
if [[ -z "$SRC" ]]; then
  command -v git >/dev/null 2>&1 || die "git is not installed: https://git-scm.com/downloads"
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  git clone --depth 1 --quiet "$REPO_URL" "$TMP/gtm-engine"
  SRC="$TMP/gtm-engine"
fi

step "Skills  ->  $(tilde "$SKILLS_DIR")"
mkdir -p "$SKILLS_DIR"
for skill in "$SRC"/skills/gtm "$SRC"/skills/gtm-*; do
  [[ -f "$skill/SKILL.md" ]] || continue
  name="$(basename "$skill")"
  rm -rf "${SKILLS_DIR:?}/$name"
  cp -R "$skill" "$SKILLS_DIR/$name"
  say "  + $name"
  for dir in "${AGENT_DIRS[@]}"; do
    [[ -d "$(dirname "$dir")" ]] || continue
    mkdir -p "$dir"
    if [[ -e "$dir/$name" && ! -L "$dir/$name" ]]; then
      say "    skipped $(tilde "$dir/$name"): a real folder is there, not a link"
      continue
    fi
    ln -sfn "$SKILLS_DIR/$name" "$dir/$name"
  done
done

old="$(cd "$SKILLS_DIR" && ls -d engine-* 2>/dev/null | tr '\n' ' ' || true)"
if [[ -n "$old" ]]; then
  say ""
  say "note: older engine-* skills are still in $(tilde "$SKILLS_DIR"): $old"
  say "      They belong to the previous layout. Remove them, and their links in"
  say "      your agent skills folders, once you no longer use them."
fi

step "Done."
cat <<'EOF'
In any project, tell your agent:  run gtm
It picks a template (outreach, seo, social, video) or none, makes
workflows/<name>/ in that project, and ships a first piece.
EOF

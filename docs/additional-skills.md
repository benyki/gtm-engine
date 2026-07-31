# Additional skills

Toolbox skills that pair with gtm-engine. `skills/engine-*` stay the product
surface; everything else (ffmpeg, posting APIs, scrapers, …) is opt-in.

---

## Where they live

Each additional skill is a folder in the **`benyki/skills`** repo on GitHub — one
directory per skill:

```
https://github.com/benyki/skills/tree/main/<skill-name>
```

Examples: [`ffmpeg`](https://github.com/benyki/skills/tree/main/ffmpeg),
[`upload-post`](https://github.com/benyki/skills/tree/main/upload-post),
[`elevenlabs`](https://github.com/benyki/skills/tree/main/elevenlabs).

They are **not** shipped inside gtm-engine. The agent downloads only what the
current workflow needs.

---

## How the agent installs one

`~/.agents/skills/` is the **only** place the skill files live. Download there,
then symlink out to each agent that has a skills directory — same pattern as
create-local-skill. Do **not** clone into `~/code/skills` or any other code tree.

1. **Download** the skill folder straight into the canonical store:

```bash
mkdir -p ~/.agents/skills
SKILL=<skill-name>
TMP=$(mktemp -d)
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/benyki/skills.git "$TMP"
git -C "$TMP" sparse-checkout set "$SKILL"
rm -rf ~/.agents/skills/"$SKILL"
mv "$TMP/$SKILL" ~/.agents/skills/"$SKILL"
rm -rf "$TMP"
```

Confirm `~/.agents/skills/<skill-name>/SKILL.md` exists.

To refresh later, run the same download again (replaces the folder).

2. **Symlink into every coding agent directory that already exists.** Skip any
   that don't — do not create them.

```bash
# Claude Code
[ -d ~/.claude/skills ] && ln -sfn ~/.agents/skills/<skill-name> ~/.claude/skills/<skill-name>

# Codex
[ -d ~/.codex/skills ] && ln -sfn ~/.agents/skills/<skill-name> ~/.codex/skills/<skill-name>

# Cursor
[ -d ~/.cursor/skills ] && ln -sfn ~/.agents/skills/<skill-name> ~/.cursor/skills/<skill-name>
```

Use absolute paths in scripts (`$HOME/.agents/skills/...`), not a bare `~`.

3. **Optional workspace link** when a project workspace is in use — link the
   **whole** canonical folder (same as `install_skills.sh`):

```bash
ln -sfn ~/.agents/skills <project>/workflows/skills
```

Never `cp -R` a skill into an agent folder — always symlink from
`~/.agents/skills/<skill-name>`.

---

## Why not dump everything into `skills/`

Toolbox skills are useful, but installing dozens of folders into
`~/.agents/skills` drowns discovery. Keep:

| Layer | Source | Installed when |
|---|---|---|
| Workflows | this repo `skills/engine-*` | `--workflow` / `install_skills.sh` |
| Capabilities | `github.com/benyki/skills` → files in `~/.agents/skills/<name>` | agent downloads only what the run needs |
| Builders / one-offs | `misc/` in this repo | never auto-installed |

Convention: workflow `N` → skill `engine-N` if it exists (`workflows.py`).
Capabilities stay off that map; the agent pulls them when an `engine-*` step
needs a tool it doesn't have yet.

---

## First capabilities (close gaps `engine-*` already documents)

| Capability (`benyki/skills/…`) | Closes the gap in |
|---|---|
| `local-secrets` | every workflow that touches `.env` |
| `ffmpeg` | `engine-video` render |
| `elevenlabs` | `engine-video` voiceover |
| `pexels` (or `pexel-video-downloader`) | `engine-video` footage fallback |
| `ffmpeg-text-overlay` | `engine-video` locked text style — `references/ffmpeg-text-style.md` |
| `yt-dlp` | `engine-video` clip sourcing from YouTube / Pinterest |
| `social-video-downloader`, `pinterest-download-videos` | `engine-video` clip sourcing, per platform |
| `video-duplicate-transformer` | `engine-video` republishing without duplicate collapse |
| `upload-post` | `engine-video` posting |
| `buffer` | `engine-video` posting |
| `bluesky-post-manage` | `engine-social` when posting to Bluesky via API |
| `no-ai-slop-writting` | `engine-seo` + `engine-social` — the full editor behind each skill's `references/anti-slop-writing.md` |
| `clarity-api-seo` | `engine-seo` behavioural analytics **and** `engine-loop`'s "what to make next" — Microsoft Clarity's export API is free at any volume: scroll depth, dead/rage clicks, quick-backs, engaged pages. Needs `CLARITY_API_KEY` |
| `phraser-thread-generate` + `phraser-thread-backstory` | `engine-social` threads — a worked write-then-post thread pipeline (hook → beats → chain, posted to X and Bluesky). Project-specific: read them as the shape and swap the backlog path and brand for the user's |
| one Apify entrypoint | research / metrics at volume |
| `prospect-finder` | `engine-outreach` list building — description → qualified list with one observable per row, deduped against the CRM |
| `apify-ultimate-scraper` | `engine-outreach` lead sourcing at volume — `references/lead-sourcing.md` |
| `agent-browser` | LinkedIn / X / Reddit when there's no API, and hand-built lead lists |
| `video-structure-plan` | `engine-video` script → architecture |
| `video-filter` | `engine-video` post-process look |

Only install a capability when the workflow you're running actually needs it.
Keep the default gtm-engine install small.

### Credits — capabilities adapted from other people's work

Some capabilities were written by adapting open-source skill libraries rather
than from scratch. Where that's true it's stated in the skill's own `CREDITS.md`
with links, and it's worth reading the originals — they go considerably further
than what gtm-engine needs.

| Capability | Adapted from |
|---|---|
| `prospect-finder` | [`growthenginenowoslawski/coldoutboundskills`](https://github.com/growthenginenowoslawski/coldoutboundskills) (MIT) — person-first vs company-first search, hit-rate benchmarks, qualify-before-scaling, the compliance checklist · [`gtmagents/gtm-agents`](https://github.com/gtmagents/gtm-agents) (Apache-2.0) — the signal-first research mindset, signal freshness, the "so what?" test |

---

## Paths stay inside the workspace

Capabilities read and write the **workspace** only:

| Use |
|---|
| `runs/<run_id>/output/` |
| `shared/assets/` |
| `config/` (`.env.example` for names; `.env` sourced at run time, never read into chat) |
| account tables as templates the user fills in |

No hardcoded home-directory media trees. The join key for anything posted stays
the run id / file stem the loop already uses — see `docs/workspace.md`.

---

## Keep `engine-*` as orchestration

`engine-video` still owns arm → script → voice → footage → render → runlog.
Capabilities own the *how* (the ffmpeg flags, the Upload Post call). When a
step needs one, the agent installs it from
`https://github.com/benyki/skills/tree/main/<name>` as above, then follows that
skill's `SKILL.md`.

---

## Posting vs social text

- **Video** — choose manual / Upload Post / Buffer:
  [`skills/engine-video/references/posting-options.md`](../skills/engine-video/references/posting-options.md)
- **LinkedIn / X** — post from the user's logged-in **browser** (no scheduler
  required on day one)
- **Bluesky** — post via the **AT Protocol API** after per-post approval
  (`engine-social`); install `bluesky-post-manage` from
  [`benyki/skills`](https://github.com/benyki/skills/tree/main/bluesky-post-manage)
  when useful

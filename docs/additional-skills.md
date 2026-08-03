# Additional skills

Optional capabilities that pair with gtm-engine. `skills/engine-*` are the
engines; everything below is a tool one of them can reach for. Install only
what the run you're doing actually needs.

They live in **[`benyki/skills`](https://github.com/benyki/skills)**, one folder
per skill. Three layers, and only the first installs itself:

| Layer | Source | Installed |
|---|---|---|
| Engines | this repo, `skills/engine-*` | by `install_skills.sh` |
| Capabilities | `benyki/skills` → `~/.agents/skills/<name>` | on demand, when a step needs one |
| Builders / one-offs | `ui-packs/` in this repo | never |

An engine of type `N` maps to skill `engine-N` if it exists. Capabilities stay
off that map — nothing pulls them but an `engine-*` step that needs a tool it
doesn't have.

## Install one

```bash
mkdir -p ~/.agents/skills
SKILL=<skill-name>
TMP=$(mktemp -d)
git clone --depth 1 --filter=blob:none --sparse https://github.com/benyki/skills.git "$TMP"
git -C "$TMP" sparse-checkout set "$SKILL"
rm -rf ~/.agents/skills/"$SKILL" && mv "$TMP/$SKILL" ~/.agents/skills/"$SKILL" && rm -rf "$TMP"

for d in ~/.claude/skills ~/.codex/skills ~/.cursor/skills; do
  [ -d "$d" ] && ln -sfn "$HOME/.agents/skills/$SKILL" "$d/$SKILL"
done
```

`~/.agents/skills/` holds the real files; everything else is a symlink. Re-run
to update. Never `cp -R` into an agent folder.

## The list

Alphabetical. Each `engine-*` skill points at the ones its own steps can use —
this page is just the inventory.

| Skill | |
|---|---|
| `agent-browser` | Reddit, SERPs, LinkedIn and X when there's no API — research, metrics, hand-built lead lists |
| `apify-ultimate-scraper` | scraping at volume: leads, competitor and audience data |
| `bluesky-post-manage` | posting to Bluesky via the AT Protocol API |
| `buffer` | scheduling posts; needs media at a public URL |
| `buffer-videos` | the video-specific Buffer path |
| `clarity-api-seo` | Microsoft Clarity — free behavioural data on your own pages. Needs `CLARITY_API_KEY` |
| `elevenlabs` | voiceover |
| `ffmpeg` | render, trim, crop, concat |
| `ffmpeg-text-overlay` | the shared text-overlay helper — read `engine-video/references/ffmpeg-text-style.md` first |
| `launch-announcement` | day one: Reddit / HN / Product Hunt / directories, for a product with no audience. **Not in `benyki/skills` yet** |
| `local-secrets` | handling `.env` without leaking values into chat |
| `music-downloader` | music beds |
| `app-video-study` | worked example: a study or finding turned into a vertical explainer |
| `no-ai-slop-writting` | the full editor behind each skill's `references/anti-slop-writing.md` |
| `pexel-video-downloader` | Pexels B-roll by keyword |
| `app-remotion-learn-words` | worked example: a Remotion vocab/teaching format |
| `app-thread-generate` + `app-thread-backstory` | a worked write-then-post thread pipeline — swap the backlog path and brand for yours |
| `pinterest-download-videos` | video pins by keyword |
| `prospect-finder` | description → qualified list, one observable per row, deduped against the CRM |
| `remotion-best-practices` | the Remotion render path — captions, transitions, sync |
| `social-video-downloader` | Reels / TikTok / Pinterest, per-platform handling |
| `tiktok-post-finder` | finding posts and people to reach out to |
| `upload-post` | posting to TikTok / YouTube / Instagram / X via official APIs |
| `video-duplicate-transformer` | re-ship a winner without duplicate collapse |
| `video-factory-floating-text-short` | batch floating-text production from one look |
| `video-filter` | post-process look — makes stock or generated footage read as filmed |
| `video-floating-text` | the full floating-text render engine |
| `video-structure-plan` | concept → segment architecture |
| `x-browser-post` | posting on X from the browser, threads included |
| `yt-dlp` | clips and audio from YouTube, Pinterest and most other sites |

## Credits

Some capabilities were adapted from other people's open-source skills. Each says
so in its own `CREDITS.md` with links — read the originals, they go further than
gtm-engine needs.

`prospect-finder` ← [`growthenginenowoslawski/coldoutboundskills`](https://github.com/growthenginenowoslawski/coldoutboundskills)
(MIT) · [`gtmagents/gtm-agents`](https://github.com/gtmagents/gtm-agents) (Apache-2.0)

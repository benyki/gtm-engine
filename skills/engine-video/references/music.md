# Music / beds

Two levels, and the format decides which (`references/formats.md`):

| | `volume` |
|---|---|
| **No voiceover** — the bed carries the video (viral product, viral vibe) | **0.5** |
| **Under a voiceover** — the bed is texture, nothing more (informative) | **0.03** |

Nothing in between. A bed at 0.15 under a voice is loud enough to muddy the
words and quiet enough to add nothing, and platform loudness normalisation
widens the problem rather than hiding it.

## Rights

- Prefer **licensed** beds you own, or tracks the user has cleared
- Pexels/Pixabay-style libraries and bought packs are fine
- Scraping a trending TikTok sound and shipping it as yours is **not** fine —
  platform audio ≠ a license for your commercial channel

If rights are unclear, ship voice-only.

## Where files live

```
shared/assets/music/<slug>.mp3
```

Reference the path from `inputs.json` → `musicBackground.file`.

## Download helpers (optional)

When the user pastes a **URL they have rights to reuse** (their own upload,
bought track page, etc.):

| Source | Approach |
|---|---|
| YouTube / Shorts / TikTok / X / Pinterest | `yt-dlp -x --audio-format mp3 -o "shared/assets/music/%(title)s.%(ext)s" "URL"` |
| Instagram | often needs a dedicated downloader / Apify — prefer asking the user for a file |
| Spotify | resolve title → search a legal source the user approves; don't pretend Spotify download is licensed |

```bash
mkdir -p shared/assets/music
yt-dlp -x --audio-format mp3 --audio-quality 0 --no-warnings \
  -o "shared/assets/music/%(title)s.%(ext)s" "URL"
```

Then trim/fade with ffmpeg and mix per `references/ffmpeg-recipes.md`.

Full skill: `benyki/skills/music-downloader` (point outputs at `shared/assets/music`).

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

## Offering it (do this every run)

The user is not expected to arrive with a track. **Suggest a mood, then artists
if they want one** — `engine-video` SKILL → step 5b has the wording. Moods that
map cleanly onto the three formats:

| Format | Mood that usually fits |
|---|---|
| Viral product (no voice, bed at 0.5) | driving electronic, upbeat house, clean synth |
| Viral vibe (no voice, bed at 0.5) | calm lo-fi, ambient piano, slow strings |
| Informative (under a voice, bed at 0.03) | minimal texture — sustained pads, no melody competing with the words |

A named artist is a better brief than a genre, so if they have one, ask for it.
"Something like Tycho" gets you closer than "chill".

## Download helpers

Fetch what they name — a song title, an artist, or a URL. The skill route is
better than raw `yt-dlp` when you have a *name* rather than a link:

**`benyki/skills/youtube-song-download`** — takes song + optional artist,
searches YouTube, picks a video inside a duration window (default 90s–10min, so
you don't get a teaser or a two-hour DJ set), downloads and writes a tagged MP3.
Point its output at `shared/assets/music/`. `benyki/skills/music-downloader` is
the broader version. Install:
[`docs/additional-skills.md`](../../../docs/additional-skills.md).

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

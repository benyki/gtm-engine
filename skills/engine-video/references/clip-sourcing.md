# Clip sourcing — where the footage comes from

Hooks, B-roll, screen recordings, the 5 seconds that decide whether anyone
watches the rest. There are five ways to get them and **no single right answer** —
the pick depends on what the user is making, what they can license, how much
they're willing to spend, and how much they care about looking like everyone
else.

Read the table, form a view, then **ask the user** which they want before you
download anything at volume. Their appetite for one option or another is theirs
to set, not yours to assume.

| Source | Cost | Looks like | Best for | Watch out |
|---|---|---|---|---|
| **Their own footage** — product recordings, phone clips, screen captures | free | nobody else | app demos, founder content, anything where the product *is* the story | someone has to record it |
| **Pexels** (`footage-pexels.md`) | free key | stock, and increasingly recognisable as stock | filling a segment your assets can't cover | every competitor draws from the same well |
| **Generated** — fal.ai and similar | credits | uncanny-clean unless you grade it | hooks and impossible shots, fast iteration | costs per clip; needs a look pass (`references/looks.md`) |
| **YouTube / Pinterest** via `yt-dlp` | free | whatever you picked | reference, b-roll from CC or own channels, hook study | rights are per-video; see below |
| **TikTok / Reels / Shorts** via a downloader | free | native to the platform | studying hooks; remixing with permission or under a license you actually have | rights are per-video; reposting someone's clip is a real risk |

## Rights — the part that's on you

There's no blanket ban here, because "downloading a clip" covers everything from
your own back catalogue to somebody's copyrighted upload. What matters is which
of these is true of the specific clip:

- **You own it** — your recordings, your channel, your customer's footage with
  their written OK. No constraints
- **It's explicitly licensed for reuse** — Pexels/Pexels-likes, CC-BY (attribute
  it), CC0, stock you've paid for. Follow the license terms, including
  attribution where required
- **You have permission** — the creator said yes. Keep the message; a DM
  screenshot in `shared/docs/` is worth more than a memory of one
- **None of the above** — then it's someone else's work. Using it as
  *reference* (study the hook, the pacing, the cut, then shoot your own) is
  ordinary practice. Republishing it as your content is a takedown, a strike, or
  a lawyer's letter, and platforms are good at spotting it

**Say which one applies when you hand the clips over.** A one-line note per
source in the run — "own screen recording", "Pexels #4029123", "CC-BY, credit in
caption", "creator gave permission, DM saved" — is the whole discipline. If you
can't name which bucket a clip is in, treat it as reference-only and say so.

If the user asks for something that falls in the last bucket anyway, tell them
the risk once, in a sentence, and let them decide. It's their channel.

## Their own footage

The highest-performing option and the least used. For an app:

- Screen recordings at 9:16 — record at device resolution, trim to the moment,
  no cursor hunting
- Keep them in `shared/assets/screen-recordings/`, named for what they show
  (`onboarding-first-word.mp4`), not `screen-3.mp4`
- One recording usually yields three clips. Cut before you need them

## Generated (fal.ai and similar)

Good for hooks — a shot you can't film, a visual metaphor, five variants of the
same idea in ten minutes.

- Key: `FAL_KEY` in `shared/.env` (add the name to `.env.example` if it's
  missing). Never read `.env` itself
- Model choice moves faster than any doc — check fal.ai's current text-to-video
  models rather than trusting a model id written down here
- Budget per clip is real. Agree a cap with the user before generating a batch
- Generated footage reads as *too clean*. Run `references/looks.md`
  (`soft-downup`, `grain`, `phone-filmed`) or it announces itself
- Platforms increasingly want AI content disclosed — check the channel's rules
  and set the flag when posting

## yt-dlp (YouTube, Pinterest, and most of the rest)

```bash
# a specific video, best quality
yt-dlp -o "shared/assets/hooks-5s/%(id)s.%(ext)s" "<url>"

# top result for a search, without hunting a URL first
yt-dlp -o "shared/assets/hooks-5s/%(title).60s.%(ext)s" "ytsearch1:<query>"

# only the section you need — trim on download instead of fetching 20 minutes
yt-dlp --download-sections "*00:01:12-00:01:17" -o "…" "<url>"
```

Filter by license when you want reusable material — YouTube's Creative Commons
filter (`&sp=EgIwAQ%253D%253D` on a search URL) narrows to CC-BY uploads, which
are reusable with credit.

Then trim, scale and center-crop to 1080×1920 with
`references/ffmpeg-recipes.md`.

## Short-form platforms

TikTok, Reels and Shorts downloads are one command away, and the honest use is
**hook study**: pull twenty openers in your niche, watch the first 1.5 seconds
of each, write down what they do, then build your own from what you learned. The
output of that session belongs in the hook library, not in a render.

Reposting someone else's clip is the case that gets accounts penalised — and if
you do have the rights (your own repost, a creator collab, licensed UGC),
`video-duplicate-transformer` exists because platforms collapse near-identical
re-uploads: see `references/duplicate-safety.md`.

## Naming and where things land

```
shared/assets/screen-recordings/<what-it-shows>.mp4
shared/assets/hooks-5s/<source>-<slug>.mp4
shared/assets/pexels/<query-slug>-<n>.mp4
runs/<run_id>/assets/…            # pulled for one run only
```

Everything reusable goes in `shared/assets/` so sibling video engines don't
re-fetch it. Never a home-directory media tree — those don't travel with the
home.

## Optional skills

Any of these can be installed when the run needs it — download the folder into
`~/.agents/skills/<name>` and symlink it out, per
[`docs/additional-skills.md`](../../../docs/additional-skills.md). Copy the whole
skill; don't cherry-pick a script out of one.

| Skill (`benyki/skills/…`) | What it saves you |
|---|---|
| `yt-dlp` | search syntax, format selection, audio extraction |
| `pexel-video-downloader` | Pexels search → portrait download in one call |
| `pinterest-download-videos` | keyword → first N video pins |
| `social-video-downloader` | Reels / TikTok / Pinterest with per-platform handling |
| `video-filter` | the look pass that makes generated or stock footage read as filmed |
| `video-duplicate-transformer` | stacked transforms for republishing without collapse |
| `ffmpeg` | trimming, cropping, concat when the recipes here aren't enough |

None of them are required. This file is enough to source clips with `curl`,
`yt-dlp` and ffmpeg alone.

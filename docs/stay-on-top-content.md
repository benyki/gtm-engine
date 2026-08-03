# Stay on top — what to follow

The sources worth keeping an eye on, and the shared assets the engines pull
from. Two jobs: keeping your own head current, and **feeding the engines**.

The second one is the reason this file is in the repo rather than in a bookmarks
folder. `engine-social`'s daily job takes 4 of its 12 subjects from RSS
(`social/sources.json` → `rss_feeds`), and this is the starting list to build
that from — a channel you actually watch produces better subjects than a feed
you added because it was popular.

Last checked: 2026-08-01. Links rot; fix them here when they do.

## YouTube

| | What it's good for |
|---|---|
| [Fireship](https://www.youtube.com/@Fireship) | fast, dense takes on whatever just shipped. The 100-second format is a masterclass in hooks — worth studying for `engine-video` as much as for the content |
| [Theo — t3.gg](https://www.youtube.com/@t3dotgg) | long-form opinion on web tooling and the discourse around it. Good source of *arguments*, which make better posts than announcements |
| [Adam Lyttle](https://www.youtube.com/@adamlyttleapps) | indie iOS: ASO, App Store growth, shipping small apps solo. The closest thing here to a direct playbook if the product is an app |
| [Better Stack](https://www.youtube.com/@betterstack) | observability and infra, plus a dev podcast. Also runs one of the better dev-marketing content operations to steal structure from |

**Turning any of these into an RSS feed** — YouTube still publishes one per
channel:

```
https://www.youtube.com/feeds/videos.xml?channel_id=<CHANNEL_ID>
```

The `@handle` isn't the channel id. Get the id from the channel page source
(search for `channelId`), or from the `/channel/UC…` URL when the channel
exposes one. Better Stack's, for example, is `UCkVfrGwV-iG9bSsgCbrNPxQ`.

## Podcasts

| | What it's good for |
|---|---|
| [Syntax](https://syntax.fm) | web dev, twice weekly. The long-running one; good for what practitioners actually argue about |
| [The AI Daily Brief](https://podcasts.apple.com/us/podcast/the-ai-daily-brief-artificial-intelligence-news/id1680633614) · [Spotify](https://open.spotify.com/show/7gKwwMLFLc6RmjmRpbMtEO) | daily AI news and analysis, ~15 min. The one that keeps you current without reading anything |
| [Claude Code Daily](https://podcasts.apple.com/us/podcast/claude-code-daily/id1896883976) | daily briefing on the most useful Claude Code engines, hacks, engineering patterns and community discoveries. Published by Pod Pub |
| [Hacker Newsroom — focus AI](https://podcasts.apple.com/us/podcast/hacker-newsroom-focus-ai/id1890584397) | 5 minutes a day of the top AI stories from Hacker News. Listed on Apple as *"AI Daily: 5-Minute, best of Hacker News"* |

Podcast RSS: most Apple listings expose the feed through
[podcastindex.org](https://podcastindex.org) or the show's own site. Prefer the
show's own feed URL over an aggregator's — aggregator links break when the show
moves host.

## Music bank

Shared bed library for `engine-video`. Level is set by the format — **0.5 with
no voiceover, 0.03 under one** (`engine-video/references/music.md`).

```
gs://amo-assets/music/
```

Objects are publicly readable, so any track also resolves over plain HTTPS:

```
https://storage.googleapis.com/amo-assets/music/<track>.mp3
```

List it, and pull one down:

```bash
gcloud storage ls gs://amo-assets/music/
```

```bash
gcloud storage cp gs://amo-assets/music/<track>.mp3 ~/gtm/shared/assets/music/
```

`gs://` isn't readable by ffmpeg — copy the track down first and point
`inputs.json` → `musicBackground.file` at the local path.

> **Rights are not settled for this bank.** Most of what's in it is commercial
> released music, and none of it carries a named licence. This engine's own rule
> is that every clip and every bed has a nameable rights position — owned,
> licensed, or permitted — and that a downloadable file is not a licence for a
> commercial channel (`engine-video/references/music.md`). Treat these as
> reference/scratch beds: fine for testing a cut, not for anything you publish
> on a monetised account. For published work use a cleared library, a bought
> pack, or your own recordings — and if the rights are unclear, ship voice-only.

## Adding to this file

Keep it short. A list of forty sources is a list nobody reads and a backlog
nobody validates — the daily job only needs enough feeds to produce four decent
candidates. When a source stops earning its place, delete the row rather than
leaving it to rot.

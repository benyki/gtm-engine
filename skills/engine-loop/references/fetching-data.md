# Getting the numbers back

Three routes. Use the cheapest one that works, and always record which it was.

`runlog.py metric` requires `--source` for that reason: a report that can't tell a measured number from a typed-in one is worse than no report, because it looks equally confident either way.

---

## 1. Platform API

Free, exact, and already connected in a few cases:

| Source | Gives you | Setup |
|---|---|---|
| The user's mailbox (Gmail, Outlook, …) | replies | already connected for `engine-outreach` |
| Google Search Console | impressions, clicks, position | verify the property once |
| YouTube Data API | views, watch time, retention | free key |

These are examples, not the list — GA4, PostHog, a data warehouse, whatever the user already has all count. Use whichever exists, name it in `--source`, and don't scrape a number a free API will hand you.

Outreach is the clean case: the metric is replies and the mailbox is the source. A reply in the thread → `--value 1 --source api`, plus `replied_at` in the CRM. Sequence closed with no reply → `--value 0 --source api` — the zero is a real result, and writing it is what marks the run analysed. A late reply overwrites the zero; later information beats earlier.

## 2. Browser — the normal case

TikTok, Instagram, LinkedIn and X all show full analytics behind the user's own login. Reading them off the page works well and needs no API key, no developer account, no approval and no money.

The routine:

1. Open the post's analytics view in the user's browser
2. Read the numbers
3. `runlog.py metric --run <id> --value <n> --source browser`

Notes that matter in practice:

- **Respect the channel's window.** `due_metrics.py` enforces it — 72 hours by default, per-channel via `metric_delay_hours` in `shared/channels.json`. For social it's a real floor: LinkedIn, TikTok, Instagram and X keep distributing a post for days, and an early number mostly tells you what time you posted. Before the window, don't record at all — an empty cell is honest, an early one is wrong and permanent
- **Record the same metric every time.** Switching from views to watch-through rate halfway through an experiment invalidates it
- **Watch-through rate beats views** for video, whenever the platform shows it. Views measure distribution; watch-through measures whether the hook worked
- If a layout changes, adapt — that's exactly the case where a hard-coded scraper breaks and an agent doesn't

This is a first-class route, not a fallback. For someone with forty posts, browser reading is correct and an API integration is over-engineering.

## 2b. Microsoft Clarity — free behavioural data on your own site

Free at any volume, and the one source that says *what people did on the page*
rather than how many arrived. Install `clarity-api-seo`
([`docs/additional-skills.md`](../../../docs/additional-skills.md)), set
`CLARITY_API_KEY`, and pull two windows so you're reading a change, not a
snapshot — recent 7 days against the prior 7, recent 28 against the prior 28.

What it's good for, in order:

- **Scroll depth** — a page with traffic and a shallow average is a rewrite
  brief, not a distribution problem
- **Dead clicks and rage clicks** — people trying to interact with something
  that isn't interactive. Usually a UX fix, sometimes a content one
- **Quick-backs** — arrived, left immediately. The title promised something the
  page didn't
- **Traffic sources and engaged pages** — which channel actually produced
  attention rather than a hit

Its export API is not identical to the dashboard tiles — the skill ships a
truth table for exactly this, so read that before claiming a number matches
what the user sees in the UI.

Turning the findings into the next piece: `engine-seo/references/clarity-rewrite.md`.

## 2b-bis. Public counters without a login — `yt-dlp`

For a video you published at a public URL, `yt-dlp` reads the counters straight
off the page. No login, no extension, no API key — and because it's a script,
this is one of the few metric jobs that can be **deterministic** rather than an
agent session.

```bash
yt-dlp -J --no-warnings "<public url>" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(d.get('view_count'), d.get('like_count'), d.get('comment_count'))"
```

Verified working on both YouTube and TikTok: `view_count`, `like_count`,
`comment_count`, and on TikTok `repost_count` too.

**What it cannot give you, on any platform:** watch-through, average view
duration, retention curves, impressions, traffic source, follower deltas.
Those exist only in the creator dashboard behind the account login — the field
simply isn't in the response, so there's nothing to parse.

That matters because `engine-video`'s default metric is **watch-through**, not
views. Three honest options:

| Route | Gets you | Cost |
|---|---|---|
| `yt-dlp` on the public URL | views, likes, comments | free, scriptable, no login |
| Browser extension on the creator dashboard | watch-through, retention, impressions | needs the extension and a logged-in session |
| **YouTube Analytics API** (OAuth, own channel) | average view duration and percentage — real watch-through | free, but YouTube only |

If the user won't set up the extension, **say plainly that the engine's metric
becomes views** and set `primary_metric` accordingly rather than leaving a
`watch_through_rate` column that never gets filled. Views are a weak signal —
they measure distribution, not whether the hook worked — but a weak measured
signal beats an empty column.

## 2c. Other free APIs worth knowing

All free (or free at the volumes here), all callable with a token and no
browser. Use one when the user already has the account — never sign them up for
something to satisfy a table.

**Their own site**

- **Google Analytics 4** — Data API; sessions, conversions, landing pages
- **Cloudflare Web Analytics** — GraphQL; free with any site on Cloudflare
- **PostHog** — generous free tier; events and funnels rather than pageviews
- **Plausible · Umami · Matomo** — free self-hosted, all with read APIs

**Search and discovery**

- **Google Search Console** — the one that matters for `engine-seo`: queries, positions, clicks
- **YouTube Data API** — views, watch time, subscriber deltas on their own channel
- **Google Trends** — direction of interest, not volume; good for picking subjects
- **Reddit** — public listings and search, for subject mining more than metrics

**Social and channel**

- **Bluesky (AT Protocol)** — open, no approval, posts and engagement
- **Mastodon** — same shape, per instance
- **Discord · Telegram** — community-side numbers
- **GitHub** — stars, traffic and clones, when the audience is developers
- **Buffer · Upload-Post** — whatever they already publish through returns its own stats

**Not on this list on purpose:** Instagram, TikTok, LinkedIn and X. Their APIs
are gated, approval-bound, or paid — which is exactly why the browser path above
exists and is the normal route for those four.

Whatever you use, `--source` names the real system, and two numbers from two
systems are not the same number: a "view" on one platform and a "view" on
another count different things, and neither belongs in the same arm total.

## 3. Apify — when hand-reading is the bottleneck

Paid, structured, precise. Worth it when:

- The volume makes manual reading a chore
- You want competitor or audience data, not just your own numbers
- You need consistent structured history rather than point-in-time reads

**Browser until it hurts, then Apify.** Nobody should be paying for this in week one.

## Nothing available?

`--source manual` and type it in. Recording it honestly is better than an empty row — and the `metric_source` column means it can be discounted later if it needs to be.

---

## What to measure

One primary metric per run: the channel's `primary_metric` override in `shared/channels.json` if set, else the engine's own (`engine.json`). The loop optimises it, so it has to be something real. Common choices:

| Engine | Usually |
|---|---|
| outreach | replies (not opens — opens are noise and increasingly unmeasurable) |
| seo | clicks from Search Console (not impressions) |
| linkedin | impressions early on; profile visits or signups once there's volume |
| video | watch-through rate, then views |

Secondary numbers go in the run's `metrics.json` under `secondary` — the spine holds one primary per run, everything else is welcome there.

Prefer the metric closest to the thing you actually want. Followers are easy to grow and easy to fool yourself with.

## The honesty rules

- **Never invent a number.** A guessed metric poisons every verdict that comes after it, and there's no way to find it later
- **Never mix sources within one experiment** without saying so. Browser-read and API-read numbers rarely agree exactly
- **Never backfill a number you didn't check.** An empty cell is information; a wrong cell isn't
- If most rows have no metric, say that before reporting anything. A verdict on three measured rows out of forty is not a verdict

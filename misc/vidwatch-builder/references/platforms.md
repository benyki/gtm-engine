# Platform Providers: Liveness & Metrics

Layer 5 is where vidwatch touches the network. This file defines the provider
abstraction and documents the working TikTok implementation, including the traps that
were found the hard way.

## The cardinal rule: two verdicts, two sources

A provider answers two different questions, and they must come from **different
endpoints with different trust levels**:

1. **Liveness** — does the post still exist? (`available | removed | unknown`)
   Must come from a *stable, documented-ish* endpoint where status codes are the
   signal. Wrong "removed" verdicts are UI-visible lies (red dots on healthy posts)
   and, because "removed" is cached permanently, they never self-heal.
2. **Metrics** — plays/likes/comments/shares. Usually scraped from an *undocumented*
   page whose shape can change any day. A failed scrape must mean "no numbers this
   time", **never** "the post is gone".

Why this split is non-negotiable, from the TikTok case: removed videos and live
videos both return HTTP 200 on the embed page — a removed one just renders a
stripped page with no stats blob. If liveness were inferred from the scrape, any
change to the page shape would mark every healthy post as removed, permanently, in
cache. Keep the scrape's failure domain limited to missing numbers.

## Provider interface

```ts
interface MetricsProvider {
  id: string;                                   // "tiktok-oembed"
  matches(url: string): boolean;                // is this URL mine?
  checkLiveness(url: string): Promise<"available" | "removed" | "unknown">;
  fetchStats(url: string): Promise<PostStats | null>;  // null = miss, keep old stats
}
```

`availability.ts` iterates configured providers, first `matches()` wins. Per URL:
liveness first; only if `available`, attempt stats; on stats miss **keep the previous
stats** (a blip must not blank the leaderboard).

Cache entry + TTLs (config-driven):

```
{ status, checkedAt, stats? }
removed   → permanent (deletions don't come back; saves requests)
available → stale after statsTtlHours (default 12h — counters move)
unknown   → stale after unknownTtlDays (default 7d)
```

Refresh runs as a worker pool (default concurrency 6, 8–10s timeout per request via
AbortController), persisting every ~10 results.

## Worked provider: TikTok

### Liveness — oEmbed (stable)

```
GET https://www.tiktok.com/oembed?url=<encoded post URL>
User-Agent: Mozilla/5.0            ← any UA works here
200 → available    400 | 404 | 410 → removed    anything else / error → unknown
```

**Trap (real bug):** oEmbed 400s URLs without the `www.` prefix.
`https://tiktok.com/@x/video/123` → 400 (looks removed) while the `www.` form → 200.
**Normalize URLs before checking** (force `www.tiktok.com` host), or live posts get
permanently mislabeled as removed.

### Metrics — embed page scrape (fragile, by design isolated)

```
GET https://www.tiktok.com/embed/v2/<videoId>     videoId = /video\/(\d+)/
User-Agent: <full desktop Chrome UA>              ← REQUIRED; minimal UAs get an
                                                    unrendered shell
```

Parse: find `<script id="__FRONTITY_CONNECT_STATE__" type="application/json">…</script>`,
JSON.parse, read `source.data["/embed/v2/<id>"].videoData.itemInfos`:

```
{ playCount, diggCount (=likes), commentCount, shareCount }   ← directly on itemInfos
```

Return null unless `playCount` is present — it is the engagement denominator; a
stats object without it is worse than none. Expect ~4% transient misses under
concurrency; that is why misses keep old numbers and the TTL retries later.

Private/region-locked posts: oEmbed says available, embed page is stripped → stats
stay null forever. Correct behavior; render "—".

### Cost profile

Both endpoints are public, keyless, and fine at 6-concurrent for a few hundred URLs.
Don't hammer: the once-per-launch auto-check plus a manual button is the right
cadence, not a timer.

## Sketches for other platforms

Same shape everywhere: boring endpoint for liveness, whatever-works for metrics,
strictly quarantined.

| platform | liveness | metrics |
|---|---|---|
| YouTube | `https://www.youtube.com/oembed?url=...` (200/404) | Data API v3 `videos?part=statistics` (needs key, env-var it) — or skip metrics |
| Instagram | HEAD the post URL (redirect-to-login ≠ removed — verify carefully) | no public counters; Graph API only (business accounts) |
| Bluesky | public XRPC `app.bsky.feed.getPostThread` (proper API — one endpoint can serve both) | same call: likeCount/repostCount/replyCount |
| X | oEmbed `https://publish.twitter.com/oembed?url=...` | none public; skip |

When adding one: probe with curl first (below), including a **known-deleted** post —
a provider you can't feed a deleted example is a provider whose "removed" verdict is
untested, and untested-permanent is dangerous. If no reliable removed-signal exists,
return only `available | unknown` and never `removed`.

## Probing checklist (before writing any provider code)

```bash
# 1. liveness endpoint: live post → expect 200
curl -s -o /dev/null -w "%{http_code}\n" -A "Mozilla/5.0" "<liveness-endpoint-for-live-post>"
# 2. liveness endpoint: DELETED post → expect hard 4xx
# 3. metrics source: live post → confirm the numbers are present in the body
curl -s -A "<full chrome UA>" "<metrics-endpoint>" | grep -o 'playCount[^,]*' | head
# 4. metrics source: deleted post → confirm what "stripped" looks like (often 200!)
# 5. re-run 3 five times → gauge transient-miss rate
```

Only after all five behave do you wire the provider in. Then verify end-to-end with
the app's cache file: run a refresh, then spot-check 2–3 cache entries against the
platform's own UI numbers.

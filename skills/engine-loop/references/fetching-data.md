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

- **Respect the channel's window.** `due_metrics.py` enforces it — 72 hours by default, per-channel via `metric_delay_hours` in `config/channels.json`. For social it's a real floor: LinkedIn, TikTok, Instagram and X keep distributing a post for days, and an early number mostly tells you what time you posted. Before the window, don't record at all — an empty cell is honest, an early one is wrong and permanent
- **Record the same metric every time.** Switching from views to watch-through rate halfway through an experiment invalidates it
- **Watch-through rate beats views** for video, whenever the platform shows it. Views measure distribution; watch-through measures whether the hook worked
- If a layout changes, adapt — that's exactly the case where a hard-coded scraper breaks and an agent doesn't

This is a first-class route, not a fallback. For someone with forty posts, browser reading is correct and an API integration is over-engineering.

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

One primary metric per run, resolved from `config/channels.json`: the channel's own `primary_metric` if set, else the workspace-wide one. The loop optimises it, so it has to be something real. Common choices:

| Workflow | Usually |
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

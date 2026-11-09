# Shiplist: <product>

> **Status:** tailoring | roadmap | drafting | launch day | closing | done (<date>)
> **Next:** <the very next action, and who owns it>
>
> This file is the one place progress lives. Read it first, update it as you go, and
> stop when every box under **Done when** is ticked.

**Launch:** <tomorrow (suggested) | in a week | in a month | today, if asked>, <date>  **Flagship:** <Product Hunt | Show HN>  **Founder timezone:** <tz>
**Link everyone gets:** <url>  **Price:** <one line, e.g. "Free, Pro $4.99/mo">  **Traffic sources:** <checked | skipped to move fast>

Legend: `agent` prepares or drafts, `founder` submits or posts. **(today)** marks the rows a same-day launch still needs, for when the founder asks to launch today; then move the rest to Cut. Times are Pacific (PT); the agent rewrites them in the founder's timezone.

---

## The pitch (fill first, every row below reuses it)

- What it does, one sentence:
- Who it's for:
- What they do in the first 60 seconds:
- Tagline, 60 characters max, a benefit not a category:
- What it does not do (yet):
- Why now / the founder story, three lines (goes in maker comments, never in the post):

---

## Roadmap (in a week or in a month only; launching today or tomorrow, move it to Cut)

Dated milestones from today to launch day. The agent fills them from what is not done yet.

- [ ] by <date> `founder` <what still has to ship: the feature, the store review (a few days), the Android closed test (14 days), the landing page>
- [ ] by <date> `founder` Show up in the launch communities (Peerlist, Uneed, Stacker News, DEV, Indie Hackers, the subreddit) a few times a week, so the launch post reads as a regular's
- [ ] by T-7 `founder` Book the dated spots below
- [ ] by T-5 `agent` Assets ready
- [ ] by T-3 `agent` All copy drafted and approved
- [ ] by T-1 `founder` Dry run: every link opens on a phone, every account is logged in

---

## Before the launch

### Product is live

- [ ] `agent` **(today)** Domain and landing page live, one clear button, works on a phone. Skills: `domain-finder`, `gtm-seo` (builds a site if there is none)
- [ ] `founder` App only: store listing approved and live, or a public TestFlight link for a pre-launch. Skills: `appstore-release-planner`, `appstore-review-readiness`, `appstore-build`, `stores-management-expo`
- [ ] `founder` Android only: new personal Play accounts need a closed test with testers for 14 days before production (check the current count in Play Console). Trade testers on <https://www.reddit.com/r/AndroidClosedTesting/>
- [ ] `agent` **(today)** Paid product: buy it once yourself, end to end. Skills: `revenuecat-sdk-react`, `paywall-design`, `stripe-best-practices`

### Traffic sources (about 10 minutes; skip to move fast)

So the Log can say where people came from. Skipped? Move these rows to Cut with "skipped to move fast"; the Log then uses each platform's own stats.

- [ ] `agent` **(today)** The site has analytics: look in the page source for a snippet (PostHog, Plausible, Google Analytics, Umami, Aptabase, Clarity...). None? Add one (`posthog`, `aptabase`, Clarity at <https://clarity.microsoft.com>) or skip
- [ ] `agent` **(today)** It works: open `<url>?utm_source=shiplist-test` on a phone, then find that visit with its source in the dashboard. Not there after 10 minutes means not working
- [ ] `agent` **(today)** One link per channel: `<url>?utm_source=producthunt`, `?utm_source=reddit`, `?utm_source=x`... listed in the Log below. Most analytics read `utm_source` with no setup
- [ ] `founder` App only: App Store Connect campaign links (App Analytics), so installs show per source too

### Assets

- [ ] `agent` Logo, square, 240x240 for Product Hunt
- [ ] `agent` 3 to 5 gallery images: the first states the benefit on a screenshot, the rest show the product working. Skills: `aso-appstore-screenshots`, `app-screenshots-api`, `phone-mockup-scene`
- [ ] `agent` One 30 to 60 s demo, plus a 9:16 cut for TikTok, Reels and Shorts. Skill: `gtm-video`
- [ ] `founder` Maker profile: photo, one-line bio, same on every site

### Accounts, logged in, in the browser the agent drives

- [ ] `founder` **(today)** Product Hunt, Hacker News, Reddit, X, LinkedIn, Bluesky, Threads, Instagram, TikTok
- [ ] `founder` **(today)** Uneed, Peerlist, Stacker News, DEV, Indie Hackers
- [ ] `founder` **(today)** A brand-new HN or Reddit account reads as spam. If yours is new, comment there for a few days first, or pick a different flagship

### Dated spots (these run on schedules)

- [ ] `founder` **(today)** Product Hunt: schedule the launch for 00:01 PT on launch day. Launching today and it's past 00:01 PT: launch now with fewer hours, or schedule tomorrow 00:01 PT as a second wave. <https://www.producthunt.com> (Launch, from your profile menu)
- [ ] `founder` Uneed: free queue or paid date, whichever lands on launch day. <https://www.uneed.best>
- [ ] `founder` Peerlist Launchpad: the week that contains launch day. <https://peerlist.io/launchpad>
- [ ] `agent` Read each site's rules page this week; they change often. Show HN rules: <https://news.ycombinator.com/showhn.html>

### Copy (agent drafts, founder edits, one file per destination in `copy/`)

**(today)** for every destination still on the list.

- [ ] `agent` Product Hunt: tagline, description, maker comment. Template: `launch-announcement/templates/product-hunt.md`
- [ ] `agent` Show HN title and first comment, plain words, no marketing. Template: `launch-announcement/templates/show-hn.md`
- [ ] `agent` Reddit post for one subreddit, written for that subreddit. Template: `launch-announcement/templates/reddit-post.md`, list in `launch-announcement/references/reddit.md`
- [ ] `agent` Uneed, Peerlist, directory listing. Template: `launch-announcement/templates/directory-listing.md`
- [ ] `agent` DEV #showdev and Indie Hackers: the build story, what was hard, what's next
- [ ] `agent` X, LinkedIn, Bluesky, Threads: the launch post and the end-of-day result post. Skill: `gtm-social`
- [ ] `agent` Warm circle: 20 to 50 names (friends, past users, waitlist, people who helped) and one message each, in the founder's voice, as drafts. Skill: `gtm-outreach`
- [ ] `agent` Newsletter or waitlist email, if there is a list
- [ ] `agent` Ready answers: "why not just use X", "is this a wrapper", "what's the moat", the price in one sentence
- [ ] `agent` Every draft through `no-ai-slop-writting` before the founder sees it

---

## Launch day

Launching today: start at the current hour and go down the rows in order; the times are the spacing, not the clock.

| Time (PT) | Do | Where | Who |
|---|---|---|---|
| 00:01 | Launch goes live. Post the maker comment right away | Product Hunt | founder |
| 00:15 | Send the warm circle messages: it's live, here's the link, tell me what's broken. **Never ask for upvotes** | DMs, email, WhatsApp | founder |
| 00:30 | Launch post with the story and the link | X, LinkedIn, Bluesky, Threads | founder (agent posts only on a yes) |
| 01:00 | Newsletter / waitlist email | email tool | founder |
| 02:00 | One subreddit, its own copy, link low in the post | Reddit | founder |
| 02:00 to 05:00 | Day-of submissions on accounts that already exist | Uneed, Peerlist, Stacker News | founder |
| 05:00 | Build story post | DEV #showdev, Indie Hackers | founder |
| 06:00 | 9:16 demo clip | TikTok, Reels, Shorts (`upload-post` or by hand) | founder |
| 07:00 | Promo channel only, in groups the founder really belongs to | Discord, Slack, WhatsApp groups | founder |
| every hour | Answer every comment, first on the flagship, then Reddit | all | founder, agent drafts replies |
| evening, optional | Directory batch: backlinks and search, not traffic. Ranked list in `launch-announcement/references/directories.md` (LaunchIgniter, Micro Launch, Foundrlist, SaaSHub, BetaList, DevHunt, Fazier, TAAFT for AI). Easy profile backlinks (Medium, Crunchbase, DEV, linktr.ee...): `references/backlinks.md` in `gtm-shiplist` | directories, profiles | founder |
| 23:00 | Fill the Log. Post the result: rank, what people said, thanks | X, LinkedIn, Bluesky | founder |

**Show HN as flagship instead:** post a weekday between 08:00 and 10:00 Eastern, stay on it for the first 30 minutes, and move Product Hunt to another day. Never both on one day.

---

## Done when

The end of this shiplist. Tick these and it is finished; nothing more happens in this folder.

- [ ] `founder` Every launch-day row is ticked or moved to Cut with its reason
- [ ] `founder` Result post is out
- [ ] `agent` Day 2: rank, visits per source and signups are in the Log (each platform's own stats if traffic sources were skipped). Rank without traffic tells you little
- [ ] `agent` Best channel named: <channel>. Weekly workflow for it: started with `gtm` in its own folder, or declined
- [ ] `founder` Relaunch date written down (4 to 6 weeks out, a new angle or feature), or "none": <date>
- [ ] `agent` Status above set to `done` with today's date

Later, not part of this shiplist: creators for a consumer product (`creator-discovery`), ads once organic shows a signal (`ads-api`, `appstore-ads-operator`).

---

## Log

| Where | Link used | Posted (time) | Post URL | Rank | Visits | Signups | Note |
|---|---|---|---|---|---|---|---|
| Product Hunt | `?utm_source=producthunt` | | | | | | |
| Reddit r/ | `?utm_source=reddit` | | | | | | |
| X | `?utm_source=x` | | | | | | |

## Cut

Rows removed while tailoring, with the reason, so the founder can bring one back.

-

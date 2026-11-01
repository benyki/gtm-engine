---
name: gtm-shiplist
description: A one-day launch shiplist for a new product. The todo list covers everything needed to ship it and share it everywhere in a single day (Product Hunt or Show HN, one subreddit, Uneed, Peerlist, Stacker News, DEV, Indie Hackers, X, LinkedIn, Bluesky, the founder's warm circle, a short video). It also tells an agent how to tailor that list with the founder, draft every piece beforehand, and walk them through the day row by row, with the project's shiplist.md as the one progress tracker until it is marked done. Use when the founder says "shiplist", "launch checklist", "launch day plan", "we ship tomorrow", "share it everywhere", "help me launch in one day", or names gtm-shiplist.
---

# gtm-shiplist

One file, one day. [`shiplist.md`](shiplist.md) is the template. Your job as the agent:

1. Create the project's `shiplist.md` from it
2. Tailor it with the founder
3. Draft everything before the day
4. Walk the day row by row
5. Close it: numbers in, Status `done`

The founder submits and posts. You prepare, draft, remind and log.

## The project's `shiplist.md` is the one source of truth

It is a todo list, and the only place progress lives, from the first question to the
last number. No side notes, no second tracker: a task list in your chat UI can mirror
it, but the file wins.

- **Start every session by reading it**, its Status and Next lines first. A new agent,
  or the founder on their phone, must know where things stand from that file alone
- **Update it the moment something changes**: tick a box when the thing is really done,
  put the post URL in the Log, move a row that won't happen to Cut with its reason,
  rewrite Status and Next
- **End every session by saving it**, with Next saying the very next action and who
  owns it

This is a one-off, not a recurring workflow: no schedule, and it ends. It is finished
when every box under **Done when** is ticked and Status says `done`. After that, nothing
more happens in this folder; ongoing work moves to a workflow of its own.

---

## 1. Create the project's `shiplist.md`

Copy the template to `<repo>/workflows/shiplist/shiplist.md`, set Status to
`tailoring`, and put the drafts in
`<repo>/workflows/shiplist/copy/<destination>.md`. If `workflows/shiplist/` already
exists from an earlier launch, use `workflows/shiplist-<yyyy-mm>/` next to it; never
move or rewrite one. Outside a git repo, use the folder where the founder keeps this
product's work. If the repo has an `.easignore`, add `/workflows/` to it.

## 2. Tailor it with the founder (about 20 minutes)

**Read before you ask.** README, landing page, `app.json` or `package.json`, the store
listing, brand notes, pricing. Fill the Pitch block yourself from what you find.

**Then ask only what is missing**, three questions at a time at most. Always confirm
these four, because every row depends on them:

| Question | Why it matters |
|---|---|
| What shape is this launch? | It decides which rows stay (table below) |
| Flagship: Product Hunt or Show HN? | Never both on one day |
| Date and timezone? | Tue to Thu is busiest; Mon or Fri ranks easier on Product Hunt with less traffic |
| The one link everyone gets? | Every row and every `?ref=` hangs off it |

| Shape | Keep | Cut |
|---|---|---|
| Pre-launch, waitlist | Reddit, Peerlist, BetaList, warm circle, socials | Product Hunt, Show HN (nothing to try yet) |
| Dev tool | Show HN as flagship, DEV, Reddit, Product Hunt another day | TikTok clip, usually |
| AI product | Product Hunt, Uneed, TAAFT and the AI directories | |
| Consumer app | Product Hunt, Reddit, Uneed, the 9:16 clip, creators after | Show HN, usually |
| Paid tool | Uneed, Product Hunt, the price in every post | |

**Cut rows that do not apply**: move each one to the Cut section with its reason, so
the founder can bring it back. Rewrite every PT time in the founder's timezone
(00:01 PT is 09:01 in Paris for most of the year). Put a real owner on each row.

Show the founder the tailored list and get a yes before you start drafting. Then set
Status to `drafting`.

## 3. Before the day

- **Blockers first**: product live, link works on a phone, accounts logged in, dated
  spots booked. A missing one moves the date; say so early.
- **Draft every copy file** from the templates named in the list, in the founder's
  voice: their brand notes, or a voice skill if they have one. Each destination
  gets its own copy: Hacker News wants no marketing at all, Reddit wants a story with
  the link low, Product Hunt wants a benefit in 60 characters.
- Run each draft through `no-ai-slop-writting` before the founder sees it. When they
  reject one, write down why and apply it to the rest.
- Read each platform's rules page the week of the launch. Rules in
  `launch-announcement/references/platforms.md` are "last known".

## 4. Launch day

Set Status to `launch day`. Walk the table in order. At each row: hand the founder the copy, the exact link with
its `?ref=`, and the page to paste it into. When it is done, tick it and write the
post URL and time in the Log.

- Every hour, remind the founder to answer comments, and draft the replies.
- If you have posting tools (`x-browser-post`, `bluesky-post-manage`, `upload-post`),
  you may post on X, Bluesky or video platforms only after an explicit yes for that
  exact post. Product Hunt, Hacker News, Reddit and directories are always pasted by
  the founder.
- If the flagship stalls, that is normal. Keep going down the list; the rest still
  sends people.

## 5. Close it

Set Status to `closing`. Draft the result post ("#4 on Product Hunt today, here's what
people asked"). On Day 2, once traffic has settled, fill the Log: rank, visits per
`ref`, signups. Then work through **Done when**:

- Name the channel that sent the most people, and offer to make it a weekly workflow
  with `gtm`. That workflow is a new folder, not this one
- Write the relaunch date down, or "none"
- Tick the last box, set Status to `done` with the date, and tell the founder the
  shiplist is finished

---

## Rules

- **Never auto-submit** to Product Hunt, Hacker News, Reddit or directories. They ban
  accounts for it
- **Never ask for upvotes**, anywhere. Product Hunt de-ranks it, Hacker News bans it.
  "Here's the link, tell me what's broken" is fine
- **One subreddit on day one**, with copy written for it
- **Never two flagships** (Product Hunt and Show HN) on the same day
- **Never send or post without an explicit yes** for that message
- **No fake accounts, no bought votes, no invented team**
- **Keys**: read `.env.example` for names, never `.env`

## What it is built from

Skill names in the list are helpers, not requirements. If one isn't installed, do
the row by hand, or install it from
[`benyki/gtm-skills`](https://github.com/benyki/gtm-skills) the way
[`docs/additional-skills.md`](../../docs/additional-skills.md) shows.

| Need | Skill or doc |
|---|---|
| Social posts, video, outreach, site, weekly workflows | `gtm`, `gtm-social`, `gtm-video`, `gtm-outreach`, `gtm-seo` (this repo) |
| Every signup and key | [`docs/useful-links.md`](../../docs/useful-links.md) |
| Platforms, timing, directories, Reddit, templates | `launch-announcement` (gtm-skills) |
| Posting tools | `x-browser-post`, `bluesky-post-manage`, `upload-post`, `buffer` (gtm-skills) |
| Copy | `no-ai-slop-writting` (gtm-skills) |
| Others, if you have them | App Store: `appstore-release-planner`, `appstore-review-readiness`, `appstore-build`, `stores-management-expo`. Assets: `aso-appstore-screenshots`, `app-screenshots-api`, `phone-mockup-scene`. Site and data: `domain-finder`, `posthog`, `aptabase`, `revenuecat-sdk-react`, `paywall-design`. After the day: `creator-discovery`, `ads-api`, `appstore-ads-operator` |

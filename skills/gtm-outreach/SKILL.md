---
name: gtm-outreach
description: Personalised cold outreach that ends in mail drafts, never sends. Takes the user's list in whatever shape it arrives (CSV, spreadsheet, pasted text, screenshot, CRM export), finds missing addresses, researches each person, writes a specific email with the user and tracks everyone in a CRM. Use when the user says "run outreach", "email my list", "write cold emails", "follow up with the people I contacted", or drops a list of leads.
---

# gtm-outreach

Writes outreach worth reading, one person at a time, and stops at the draft.

A template plus a craft guide for one outreach workflow. Copy `template/` into
`<repo>/workflows/<name>/`; every path below is inside that folder. Customers
and investors are two folders, each with its own CRM. Folder rules:
[`../gtm/SKILL.md`](../gtm/SKILL.md).

**It never sends.** Not with permission, not "just this once". Drafts land in
the user's own mail system and a human clicks send.

**No email template ships with this skill, on purpose.** A template with
placeholders produces generic email, so the first one is written *with the
user*, from what they sell and who they write to.

## Start

1. **Copy the folder and find the voice.** Skip the copy if `gtm` already
   made the folder: `cp -R` this skill's `template/` to `workflows/<name>/`,
   then fill the README's first lines (who this writes to, what the email asks
   for, the number). Voice: the project's own notes, else the five questions
   in [`../gtm/SKILL.md`](../gtm/SKILL.md) (Voice)
2. **Connect mail and prove it** with one draft addressed to the user (*Mail*)
3. **Load the list** into `crm.csv` in whatever shape it arrives (*The run*,
   step 1); no list or no addresses, step 2
4. **Write the first email with the user**: three versions, iterate until they'd
   send it unedited, save it as `templates/first-touch.txt`
5. **Research and draft the first ten** (steps 3 to 5). When the user says they
   went out, mark the rows sent and add the batch to `log.csv`

## Mail

Three capabilities, not a vendor: **create drafts** in the user's account, **a
human sends** from their normal client, **replies are readable** later. Gmail
is the default (Claude Code: claude.ai → Settings → Connectors, then it shows in
`/mcp`; Codex: a Gmail MCP server plus `codex mcp login gmail`, which the user
runs). Outlook works the same way. No connector: write each draft to `drafts/`
as a file the user copies over, and ask them to report replies. If an admin
blocks the connector, name the block and offer the file mode; never route
company mail through a personal account.

## The run

### 1. Load the list, in whatever shape it arrives

Converting it is your job; never ask the user to re-export or rename a column.
Any CSV (sniff the delimiter), a spreadsheet (several sheets: ask which), a
Sheet, Airtable or Notion link (open it in the browser), pasted text, JSON, an
email thread, vCards, a 60-column export (keep the five that matter). A
screenshot or PDF: **show what you extracted** before using it.

`crm.csv` is the one format everything downstream reads. Its header is fixed and
**every value is optional**: an empty cell is a normal state, not homework for
the user, and a thin row never blocks the batch.

- **Map their columns** however they're named (`E-Mail` → `email`, `First` +
  `Last` → `name`); ask once, in one message, about what's genuinely ambiguous.
  Fold anything unmappable into `notes`; an observable that came with the list
  goes into `research`, its origin into `research_source`
- **Fill what you own**: `id`, `first_seen`, `status=new`, `outreach_count=0`
- **Fix the ordinary mess**: trim, strip `mailto:`, lowercase, drop `info@` and
  `noreply@` and say so; flag rows with no contact route, don't drop them
- **Dedupe on email**, then LinkedIn URL, then name + company. Never import
  over someone with a `sent_at`

Say in one line what came out (rows, rows with an email, duplicates merged,
what you couldn't map): that's where a bad import gets caught.

### 2. No addresses? Offer to get them, unasked

Names without emails, or no list at all, is the normal start, not a blocked
run; never end on "send me a list with emails". For B2B: search LinkedIn with
the agent driving the user's own session, capture name, role, profile URL and
the observable on the spot, then turn the URLs into addresses with a finder
(Hunter's free tier has the API, `HUNTER_API_KEY`, so it runs unattended). Expect 50 to 70% hits.
`references/lead-sourcing.md` has the tool trade-offs, every source and the
ten-lead test. **The list moves the reply rate more than the copy does.**

### 3. Research each person, into the CRM

A merge field is not personalisation. Look before you write a word about them
and stop at the first real thing: their site (changelog, blog, pricing), their
LinkedIn *activity*, X or GitHub, a talk, their job posts, a Reddit or HN
comment in their own words. About a minute each
(`references/browser-research.md`). Then, **before you draft**, fill the row:
`research` (the observation, one or two plain sentences you could quote back to
them), `research_source` (the URL), `researched_at` (the date).

What they *did*, never what you think of them; no source URL, no claim. Nothing
found in a minute: write `research=nothing found` with the date and flag the row
as a wrong-target candidate. In the row, the follow-up reuses it and the user
can correct it before anything goes out. Voice and banned claims come from the
project's voice notes or `brand.md`.

### 4. Draft

No template yet: write it with the user (`references/first-touch.md`). After
that, render it with the research. The opening proves you looked, the middle is
about them, the ask is small enough to answer on a phone.

**When a finding is strong enough to change the email, offer it first**, one
line per row, in one batch rather than one question per lead:

> **Ana Sørensen (Kitewave)**: shipped v2 last month and posted about their
> onboarding drop-off ([link]). I'd open on the drop-off post rather than the
> launch. Want that, something of your own, or keep it generic?

They know things the internet doesn't, and their name is on the email. Carry on
if they don't bite; what they add goes into `research` or `notes`.

### 5. Cut the slop, then create the draft

`references/anti-slop-writing.md` over **every email, every run**: slop arrives
in the parts filled in per person. Any failure is a rewrite:

- **swap test**: could it go to someone else on the list by changing the name?
- **competitor test**: could a competitor send it with their name in it?
- **read-aloud test**: anywhere you stumble is a line to cut
- **reply test**: is the ask answerable in one sentence, on a phone?

Only then create the draft. Row: `status=drafted`, `template_used`, `drafted_at`.
Show the user ten drafts, not fifty. Ask the user to kill the ones that read like a robot
and say why, then redo the rest. Each reason is one line in the README's "What
we learned", so the next batch starts from it.

## After they send

Each row gets `status=sent`, `sent_at`, `next_followup_at`, and `log.csv` gets
**one row for the batch**. The CRM holds the people, so the log stays free of
personal data and lives in git:

```csv
date,channel,link,what_it_tried,result
2026-11-03,email,templates/first-touch.txt,"open on their changelog, ask for a 10-minute look",
```

**3 to 5 working days later** (longer for people who read mail weekly), read the
mailbox the drafts came from. **Any reply counts, a no included**: set
`replied_at` and stop the sequence; a no also gets `status=closed`. No reply
stays open until the sequence ends. Fill `result`: `4 replies / 20, 1 call
booked`; a late reply updates it.

When a batch clearly won or lost against the ones before, add one line to the
README's "What we learned". Change one thing per batch and name it in
`what_it_tried`, or you won't know what moved the number
(`references/first-touch.md` §6).

## Follow-ups and replies: ask first

At ten emails a week the user's own words beat a draft. Ask: *"Do you want me
to draft follow-ups and replies, or would you rather handle replies yourself?"*
If they want it, keep **a library of short blocks** in their voice
(`templates/followups/blocks.md`), not a decision tree, and add a block every
time a reply arrives that nothing covers (`references/followups.md`). Stop when
someone replies, three touches at most, and every follow-up adds something new:
"bumping this" is worse than nothing.

## Rules

- **Drafts only.** Never send, never schedule a send, warm threads included
- **Never contact anyone twice.** Check the CRM for a `sent_at` before every draft
- **One inbound message gets at most one draft, ever.** A draft doesn't change
  the thread, so a job that trusts the mailbox alone re-drafts the same reply
  daily. Check the CRM row and the existing drafts first
- **Never invent a fact about a person.** Thin research gets said, not filled
- **No key or personal data in a URL**, and no bare URL as link text
  (`references/first-touch.md` §2)
- **Honour unsubscribes and "not interested" permanently**: `status=closed`,
  never re-added by a fresh import

## On a schedule (optional)

A sequence paused for two weeks never gets its follow-up. Once the user would
send the first email unedited, one task on working days is enough: read replies
first, then draft `<n>` new emails and the follow-ups that are due. The README
records when it runs, where, and the exact prompt. `<n>` is a number they'll
actually review (fifty a day is no outreach), the task never sends, and if it
drafts replies its prompt carries the one-draft-per-inbound rule. Refresh the
list weekly or by hand, never alongside drafting: both write `crm.csv`.

## Going further

`references/advanced.md`: Cloudflare Email Routing for inbound, deliverability,
and the sending setup (Resend behind a review gate) a user may build and run
themselves later. This skill still only writes drafts.

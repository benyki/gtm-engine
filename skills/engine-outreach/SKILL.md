---
name: engine-outreach
description: Personalised cold outreach that ends in mail drafts, never sends. Reads the user's audience list, researches each person, writes a genuinely specific email from the workflow's current template (or the assigned A/B arm once one is live), records everything in the CRM, and logs the run. Use when the user says "run outreach", "email my list", "write cold emails", "follow up with the people I contacted", or drops a list of leads.
---

# engine-outreach

Writes outreach worth reading, one person at a time, and stops at the draft.

This skill runs any workflow folder of **type `outreach`**. The default folder
is `outreach/`; paths below (`inputs/audience/`, `crm.csv`, `templates/`,
`runs/`) are inside that folder, while brand, accounts and keys live in
`shared/`. **Multiple outreach workflows are a normal shape** — `outreach/`
for customers and `outreach-investors/` for fundraising are two independent
folders with their own CRMs, templates, experiments and metrics — scaffold one
with `--merge --workflow <name>:outreach`, or copy a folder and empty its
`runs/`, `reports/` and `crm.csv` (history belongs to the original).

**It never sends.** Not with permission, not "just this once". Drafts land in the user's own mail system and a human clicks send. Everything downstream — the CRM, the A/B verdicts, the report — assumes that boundary holds.

**No email template ships with this repo, and that's deliberate.** What makes a
cold email work is specific to what the user sells, who they're writing to and
what that industry finds normal — a generic template with placeholders produces
generic email. The first template is written *with the user*, and
`assign_arm.py` returns `write_template` on an empty folder to say so.

**How (not just what):**

| Step | Reference |
|---|---|
| Where the list comes from | `references/lead-sourcing.md` |
| Writing the first email with the user | `references/first-touch.md` |
| Replies and follow-ups (**optional**) | `references/followups.md` |
| Sending domain, volume, deliverability | `references/advanced.md` |

## Setup

The mail contract is provider-neutral, and it's three capabilities, not a vendor:

1. **create drafts** in the user's own mail account
2. **a human sends** from their normal mail client
3. **replies are readable back** later, to record the metric

**Gmail is the default** because its connector is the least setup — no Google Cloud project, no API keys, no OAuth consent screen. But map the contract onto whatever the user actually has: an Outlook / Microsoft 365 connector satisfies it identically, and much of B2B lives there. If no mail connector is available at all, the degraded mode is honest and workable — write the drafts to `runs/<run_id>/output/` as files the user copies into their mail client, and ask them to report replies; record those with `--source manual`.

If a managed Workspace or tenant blocks the connector at the admin level, that's an IT conversation, not a workaround hunt. Don't steer a company toward routing work mail through a personal account — for an individual using their own address it's a fine fallback, for an organisation it's a data-governance problem. Name the block, offer the file-based degraded mode, and let them take it up with their admin.

## The run

### 1. Load the list

Take whatever they've got in `inputs/audience/` — CSV, spreadsheet export, pasted text — and normalise it into `crm.csv`. Dedupe on email, falling back to LinkedIn URL then name+company.

**No list yet?** Building one is part of this workflow, not a prerequisite —
`references/lead-sourcing.md` covers the sources in the order worth trying, the
ten-lead test that tells you whether a source is any good, and the scraping and
personal-data limits. The list moves the reply rate more than the copy does.

For B2B with nothing to start from, the fastest honest path to the first twenty
is three steps in one afternoon: **search LinkedIn with the agent driving the
browser** (title, headcount, geography, something that changed recently),
capturing name, role, profile URL and the observable → **turn the profile URLs
into verified email addresses** with a finder tool (Dux-Soup, Lusha, Apollo,
Hunter, Prospeo — expect a 50–70% hit rate, so search thirty to land twenty) →
**run this workflow normally**. Full version, including which tool to pick and
the LinkedIn-terms caution to raise with the user, is in
`references/lead-sourcing.md`.

A usable list before normalisation looks like this — the `notes` column is the
part that decides whether the email is worth sending:

```csv
id,name,company,email,linkedin,source,notes
1,Ana Sørensen,Kitewave,ana@kitewave.example,https://linkedin.com/in/example-1,conf-list,shipped v2 last month
2,Marcus Bell,Tinderbox Labs,marcus@tinderbox.example,https://linkedin.com/in/example-2,conf-list,hiring first marketer
```

`crm.csv` adds the tracking columns on top (`status`, `arm`, `template_used`,
`drafted_at`, `sent_at`, `next_followup_at`, `replied_at`) and the three
research columns step 3 fills (`research`, `research_source`, `researched_at`)
— its header is the contract, so keep every column even when a cell is empty.
An observable that arrived with the list goes into `research` on
normalisation, with wherever it came from in `research_source`; `notes` is for
everything else about the person.

**Never contact someone already in the CRM with a `sent_at`.** That's the single most damaging mistake this workflow can make, and it's silent unless you check.

### 2. Get the arm

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --workflow outreach --entity someone@example.com
```

Pass `--entity` every time. It keeps people in the arm they were first assigned, including on follow-ups — otherwise you're measuring noise.

If it returns `action: write_template`, write the template it names using the hypothesis it gives you, then carry on. **Don't fall back to another template and don't stop.** Record the file you actually used.

**On a fresh workflow this returns `use_template` and that's correct** — the
starter experiments ship paused on purpose. Ship one sequence until the user is
happy with the format, then start testing. `engine-loop/references/ab-testing.md`
→ R0 has the three conditions for flipping an experiment live.

When you do flip one live, decide **what** is worth testing before writing a
second template — the wording, or the offer itself. The offer is often the bigger
variable and its answer also changes the landing page, but it isn't always the
right call and it isn't yours to decide alone: recommend one, and let the user
pick. `references/first-touch.md` → §6 has the choice and what to hold constant.

### 3. Research each person — and write what you find into the CRM

This is where the whole thing is won or lost. A merge field is not personalisation and every recipient knows it.

**Go and look before you write a word about them.** Don't work from what's
already in the row — a title and a company name are not research. Search, in
roughly this order, and stop as soon as you have one real thing:

- **their own site** — changelog, blog, pricing page, "what's new"
- **their LinkedIn activity** — what they *posted*, not the profile blurb
- **X / Bluesky / Mastodon**, **GitHub**, a podcast they went on, a talk, a press mention
- **their job posts** — what a company is hiring for is what it's struggling with
- **a Reddit or HN comment** where they described the problem in their own words

The browser is the tool for most of this — `engine-social/references/browser-research.md`
covers reading platforms that have no API. Look for something specific and
recent: what they shipped, what they wrote, what they're hiring for, what they
said publicly. One real observation beats three generic compliments. Budget
about a minute per person; if there's genuinely nothing to find, that's a signal
they're the wrong target, not a reason to write filler.

**Then write it into their CRM row, before you draft.** Three columns:

| Column | What goes in it |
|---|---|
| `research` | the observation itself — one or two plain sentences, a fact you could quote back to them |
| `research_source` | the URL you read it on |
| `researched_at` | the date, so a later pass knows how stale it is |

Putting it in the row and not only in the email is what makes this compound:

- the **follow-up** three weeks later reuses it instead of re-researching from scratch
- the **user can read it and correct you** before anything goes out — they often know the person
- a second workflow, or the same one next quarter, starts warm
- an observation with **no source URL is unverifiable**, and an unverifiable claim in a cold email is the one mistake you can't take back

What goes in the cell: what they *did*, not what you think of them. No adjectives
about them, no inference dressed as fact, no "seems like you're scaling fast".
If a minute of searching turns up nothing, write that — `research=nothing found`
with the date — and flag the row to the user as a wrong-target candidate. An
empty `research` cell and a written "nothing found" mean different things on the
next pass.

Pull the voice and the constraints from `shared/brand.md` — especially the banned claims.

### 4. Draft

**First run of a new workflow?** There's no template yet. Write it with the
user — `references/first-touch.md` walks the interview: ask what the email
absolutely has to say, keep it under 120 words, run the anti-slop pass, then
show them three versions and iterate until they'd send it unedited. That
conversation is the highest-leverage work in this workflow; don't shortcut it.

After that, render the current template (or the assigned arm once an experiment
is live) with the research. Keep it short. The opening line has to prove you
looked, the middle has to be about them and not you, and the ask has to be small
enough to say yes to on a phone.

**When the research turned up something genuinely good, offer the user the
personalisation before you commit to it.** Not for every row — for the ones
where the finding is strong enough to change the email: they shipped the exact
thing the product helps with, they wrote publicly about the problem, they just
raised or just moved, there's a shared connection or a mutual customer. Show the
finding, its source and what you'd do with it, in one line, and give them three
ways out:

> **Ana Sørensen (Kitewave)** — shipped v2 last month and posted about their
> onboarding drop-off ([link]). I'd open on the drop-off post rather than the
> launch. Want that, do you have something of your own to add, or keep it
> generic?

Ask because they know things that aren't on the internet — they met at a
conference, a mutual customer already told them about it, the "recent" post is
two jobs out of date — and because their name is on the email. One line from
them beats your best inference from a profile.

Keep it non-blocking: **one batch, not one question per lead.** Draft everything
with the research you have, list the two or three rows worth a human line, and
carry on if they don't bite. Anything they add goes into the CRM row's
`research` (or `notes`) so the follow-up keeps it.

Create it as a **draft in the user's mail system** (Gmail, Outlook — whatever the connector is).

### 5. Record

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --workflow outreach --channel email \
  --experiment exp-001 --arm partner --template first-touch-partner.txt
```

Then update the CRM row: `status=drafted`, `arm`, `template_used`, `drafted_at`, `next_followup_at`.

## Before you hand over

Show the user ten drafts, not fifty. Ask them to kill the ones that read like a robot and say why — then regenerate the rest with that feedback. The second batch is always better, and the reason is worth writing into `shared/brand.md` so it survives — and if the lesson isn't outreach-specific, add a line to `shared/insights.md` too.

## After they send

Sending happens in the user's mail client, by the user. When they tell you drafts went out, record the moment for each one — it starts the metric clock:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id>
```

No `--url` — an email has none, and `publish` doesn't need one. Update the CRM row at the same time: `status=sent`, `sent_at`, `next_followup_at`.

Skip this and the run stays `draft` forever: `due_metrics.py` never lists it, no number is ever recorded, and the experiment reports "no runs yet" no matter how many replies came in.

## Follow-ups and replies — ask first, it's optional

**Plenty of people should reply themselves.** At ten emails a week the user's
own words beat anything drafted for them, and the reply is where the deal
starts. Ask before building any of it:

> *"Do you want me to draft follow-ups and reply handling, or would you rather
> handle replies yourself?"*

Either way the loop gets its number — a reply is `--value 1` plus `replied_at`
in the CRM. Nothing else is mandatory.

If they do want it: **build a library of optional blocks, not a decision tree.**
Real replies don't sort into interested / not interested — they're "how much?",
"ask me in Q3", "wrong person, talk to X", "we use a competitor", a question
about one feature, a polite no. You answer by combining two or three short
reusable blocks in the user's voice, and **the library grows every time a reply
arrives that nothing covers**. That upkeep is the point, and it's what makes the
workflow smarter in month three than in week one. `references/followups.md`.

The rules that never change:

- Same arm as the first touch, always (`--entity` on every call)
- Stop when someone replies. `replied_at` set means no further sequence mail, ever
- Three touches maximum unless the user asks otherwise
- A follow-up that just says "bumping this" is worse than nothing. Add something new or don't send it
- Drafts only — including replies to warm threads, where a wrong send costs the most

## Getting the numbers back

The metric is replies and the source is the same mailbox the drafts came from — no analytics page, no browser reading. Replies settle faster than social distribution: if the 72h default feels slow here, set `metric_delay_hours` on the email channel in `shared/channels.json` (24–48 is reasonable). On each loop pass, `due_metrics.py` lists the sent runs past that window with no number yet. For each one, check the thread:

- **A reply landed** → `runlog.py metric --run <id> --value 1 --source api`, set `replied_at` in the CRM, stop the follow-ups
- **A decline is a reply.** "Not interested", "wrong person", a polite no — all
  `--value 1` with `replied_at` set, *and* `status=closed` so they're never
  contacted again. The metric asks whether the email made someone write back, not
  whether they said yes. Scoring a no as a zero quietly punishes the arm that
  provoked a real answer, and both arms end up measuring politeness
- **No reply, sequence still open** → leave the cell empty. It stays on the due list and gets checked again next pass
- **No reply, sequence closed** — three touches done and 72h past the last → record the zero: `--value 0 --source api`. A zero is a real result, and writing it is what marks the run analysed

A reply that arrives after a zero was recorded: run `metric` again with `--value 1`. Later information beats earlier.

If the user wants "did they say yes" as well — and they usually do — that's a
second number, not a redefinition of this one: put calls booked or deals opened
in the run's `metrics.json` under `secondary`. An arm can win on replies and lose
on conversations, and you only see that when both are recorded.

**The window is a property of the audience, not just the channel.** 24–48h is
right for people who live in their inbox; it is wrong for anyone who answers mail
weekly. Set `metric_delay_hours` from how fast *these* people actually answer —
if the first cohort's replies are still trickling in on day nine, the window is
too short and every zero written before then is a lead you wrote off early.

**Read the recent slice, not just the running total.** `score_arms.py`'s cohort is
every measured run since the experiment's `started` date, and it only grows — by
week twelve the number is dominated by weeks one to eleven, so a fix made in week
nine barely moves it. Two habits fix that: look at the last ~20 runs next to the
cumulative figure before believing a flat result, and **when the email changes
mid-experiment, bump `started` (or open a new experiment) rather than letting the
old runs vote on the new version.**

## Rules

- **Drafts only.** Never send, never schedule a send
- **Never contact anyone twice.** Check the CRM before every draft
- **One inbound message gets at most one draft, ever.** A draft doesn't change the thread, so a scheduled reply job that trusts the mailbox alone re-drafts the same reply daily. Check the CRM row *and* the existing drafts first — `references/followups.md`
- **Never invent a fact about a person.** If the research is thin, say so — a made-up detail in a cold email is unrecoverable
- **Research lands in the CRM, not only in the email.** An observation that exists only in a sent draft is lost to the follow-up, to the user's review, and to every later pass. With it goes the source URL — an unverifiable claim doesn't go in an email
- **Never put a key or personal data in a URL**, and never a bare URL as visible link text — send an anchor (`references/first-touch.md` → §2)
- Honour unsubscribes and "not interested" permanently — mark them `status=closed` and never re-add them from a fresh import. Closing them doesn't retract the metric: a decline was still a reply

## Make it run without you

Outreach is the workflow where irregularity costs most: a sequence that pauses
for two weeks is a sequence that never gets its follow-up, and the CRM quietly
fills with people mid-thread. Once the first email is one the user would send
unedited:

| Label | When | What |
|---|---|---|
| `engine-metrics-outreach` | daily, working days | read the mailbox: any reply — including a no — is `--value 1` plus `replied_at`, a closed sequence with no reply at all is the zero. Replies settle in 24–48h, so this is the fastest metric clock of any workflow |
| `engine-outreach-daily` | daily, working days | draft `<n>` personalised emails into their mail system, update the CRM |

**Reading replies *is* the metric fetch** — don't add a separate weekly
"check replies" job. Two jobs writing the same `runs/index.csv` and the same
`crm.csv` is how rows get silently lost.

Three things to get right when setting them up. **`<n>` is a number they'll
actually review** — 50 drafts a day is the same as no outreach. **Neither job
sends**, including the follow-ups. And if either job drafts *replies*, its prompt
has to carry the one-draft-per-inbound rule explicitly — that failure is invisible
in a single run and obvious after a week. Catalogue:
[`docs/scheduling.md`](../../docs/scheduling.md); how to create one:
`engine-loop/references/scheduling.md`.

## Going further

`references/advanced.md` — Cloudflare Email Routing for inbound, sending automatically from your own domain via Resend (with the review gate that replaces the human click), and the deliverability rules that decide whether any of it lands.

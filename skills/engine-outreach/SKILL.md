---
name: engine-outreach
description: Personalised cold outreach that ends in Gmail drafts, never sends. Reads the user's audience list, researches each person, writes a genuinely specific email from the assigned A/B template, records everything in the CRM, and logs the run. Use when the user says "run outreach", "email my list", "write cold emails", "follow up with the people I contacted", or drops a list of leads.
---

# engine-outreach

Writes outreach worth reading, one person at a time, and stops at the draft.

**It never sends.** Not with permission, not "just this once". Drafts land in Gmail and a human clicks send. Everything downstream — the CRM, the A/B verdicts, the report — assumes that boundary holds.

## Setup

The only requirement is a Gmail account connected to the agent, with permission to create drafts. No Google Cloud project, no API keys, no OAuth consent screen. If Gmail isn't connected yet, get that working before anything else.

Managed Workspace accounts sometimes block the connector at the admin level. If so, a personal Gmail is the fallback — it takes two minutes and needs no approval.

## The run

### 1. Load the list

Take whatever they've got in `inputs/audience/` — CSV, spreadsheet export, pasted text — and normalise it into `state/crm.csv`. Dedupe on email, falling back to LinkedIn URL then name+company.

**Never contact someone already in the CRM with a `sent_at`.** That's the single most damaging mistake this workflow can make, and it's silent unless you check.

### 2. Get the arm

```bash
python3 ../engine-loop/scripts/assign_arm.py --workflow outreach --entity someone@example.com
```

Pass `--entity` every time. It keeps people in the arm they were first assigned, including on follow-ups — otherwise you're measuring noise.

If it returns `action: write_template`, write the template it names using the hypothesis it gives you, then carry on. **Don't fall back to another template and don't stop.** Record the file you actually used.

### 3. Research each person

This is where the whole thing is won or lost. A merge field is not personalisation and every recipient knows it.

Look for something specific and recent: what they shipped, what they wrote, what they're hiring for, what they said publicly. One real observation beats three generic compliments. Budget about a minute per person; if there's genuinely nothing to find, that's a signal they're the wrong target, not a reason to write filler.

Pull the voice and the constraints from `config/brand.md` — especially the banned claims.

### 4. Draft

Render the assigned template with the research. Keep it short. The opening line has to prove you looked, the middle has to be about them and not you, and the ask has to be small enough to say yes to on a phone.

Create it as a **Gmail draft**.

### 5. Record

```bash
python3 ../engine-loop/scripts/runlog.py new --workflow outreach --channel email \
  --experiment exp-001 --arm partner --template first-touch-partner.txt
```

Then update the CRM row: `status=drafted`, `arm`, `template_used`, `drafted_at`, `next_followup_at`.

## Before you hand over

Show the user ten drafts, not fifty. Ask them to kill the ones that read like a robot and say why — then regenerate the rest with that feedback. The second batch is always better, and the reason is worth writing into `config/brand.md` so it survives.

## After they send

Sending happens in Gmail, by the user. When they tell you drafts went out, record the moment for each one — it starts the 72-hour clock:

```bash
python3 ../engine-loop/scripts/runlog.py publish --run <run_id>
```

No `--url` — an email has none, and `publish` doesn't need one. Update the CRM row at the same time: `status=sent`, `sent_at`, `next_followup_at`.

Skip this and the run stays `draft` forever: `due_metrics.py` never lists it, no number is ever recorded, and the experiment reports "no runs yet" no matter how many replies came in.

## Follow-ups

- Same arm as the first touch, always
- Stop when someone replies. `replied_at` set means no further follow-ups, ever
- Three touches maximum unless the user asks otherwise
- A follow-up that just says "bumping this" is worse than nothing. Add something new or don't send it

## Getting the numbers back

The metric is replies and the source is the same Gmail the drafts came from — no analytics page, no browser reading. On each loop pass, `due_metrics.py` lists the sent runs that are 72h+ old with no number yet. For each one, check the thread:

- **A reply landed** → `runlog.py metric --run <id> --value 1 --source api`, set `replied_at` in the CRM, stop the follow-ups
- **No reply, sequence still open** → leave the cell empty. It stays on the due list and gets checked again next pass
- **No reply, sequence closed** — three touches done and 72h past the last → record the zero: `--value 0 --source api`. A zero is a real result, and writing it is what marks the run analysed

A reply that arrives after a zero was recorded: run `metric` again with `--value 1`. Later information beats earlier.

## Rules

- **Drafts only.** Never send, never schedule a send
- **Never contact anyone twice.** Check the CRM before every draft
- **Never invent a fact about a person.** If the research is thin, say so — a made-up detail in a cold email is unrecoverable
- **Never put a key or personal data in a URL**
- Honour unsubscribes and "not interested" permanently — mark them `status=closed` and never re-add them from a fresh import

## Going further

`references/advanced.md` — Cloudflare Email Routing for inbound, Resend for sending from your own domain at volume, and the deliverability rules that decide whether any of it lands.

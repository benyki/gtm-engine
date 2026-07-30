# Outreach — going further

**Symptom: Gmail drafts don't scale past a few dozen a week, and replies are scattered across addresses.**

---

## The graduation path

Take it in order. Skipping to step 3 on day one is how domains get burned.

1. **Gmail drafts** — you read every one before it sends. Where this workflow starts and where most people should stay for months
2. **Gmail send after review** — same account, batch-approved. Still your reputation, still your rate limits
3. **Your own domain via a sending API** — volume, deliverability, and a sender that isn't your personal inbox

---

## Inbound: Cloudflare Email Routing

Free, and it solves a real problem: you want `hello@`, `sales@` and per-campaign addresses without buying mailboxes for each.

Routing forwards all of them to one inbox you already read. Turn on catch-all and a campaign address exists the moment you use it — no setup per address.

---

## Outbound: Resend (or Postmark, or SES)

Verify your domain, send from it. The worked example below is Resend; Postmark and SES have the same shape and most of it transfers.

Three things that are easy to get wrong:

**Sending and receiving are separate.** A domain verified for sending has no mailboxes at all. There is nothing to "create" — once the domain is verified, any address on it sends the moment you put it in `from`, and `hello@`, `sales@`, `jan-campaign@` all work with zero per-address setup. The flip side is that anything sent *to* those addresses goes nowhere unless you separately configure inbound. So **always set `reply_to`** to an inbox you actually read. This is the single most common mistake with a send-only domain, and you find out about it by losing replies.

**Inbound needs its own MX record**, and adding one at the root of a domain that already has email will outrank the existing provider and stop delivery there. MX priority is lowest-wins, so a new record at priority 0 silently takes over from a mail provider sitting at priority 1. Use a subdomain unless you genuinely mean to move your mail — and if you do mean it, leave the old records in place, because deleting the new one is then your entire rollback.

**Deliverability is earned.** SPF, DKIM and DMARC first, then warm up over weeks — a few a day, climbing slowly. Blasting 500 cold emails from a fresh domain gets it flagged, and a burned domain doesn't recover; you buy a new one.

Send from a subdomain like `mail.yourdomain.com` so a mistake doesn't take your main domain's reputation with it.

---

## Sending automatically

This is the step that removes the human click. Read the next paragraph before you write any code.

### What you give up, and what replaces it

The base workflow's safety property is not "Gmail" — it's that **a person reads each email before it leaves**. A sending API has no drafts. Every call sends, immediately, to a real person. Swapping it in doesn't automate the review step, it deletes it.

So replace it with something, and pick deliberately:

**A review file, then a second command.** The run renders every email and writes them to `runs/<run_id>/output/outbox.json` instead of sending. It reports the count and stops. A separate, explicitly-invoked command posts that file. Nothing sends because a run finished — sending is its own decision, with the batch sitting in a file you can read first.

**A cancel window.** Send with `scheduled_at` set 15–30 minutes out and record the returned id in the CRM. Until it fires you can pull any of it back:

```bash
curl -X POST "https://api.resend.com/emails/<id>/cancel" \
  -H "Authorization: Bearer $RESEND_API_KEY" -H "User-Agent: my-outreach/1.0"
```

Store the ids or you can't cancel. This is worth doing even once you trust the pipeline — it's the difference between "I sent 80 bad emails" and "I cancelled 80 bad emails".

Use both. They cost about twenty lines and they are the reason this stays recoverable.

### Setup

Verify your domain in the Resend dashboard, then create an API key. Put it in `workflows/config/.env` as `RESEND_API_KEY` — the same rules as every other key here: you paste it in yourself, `.env` stays gitignored, your agent reads `.env.example` for the name and never the value.

Load it at run time rather than hardcoding it anywhere:

```bash
set -a; . workflows/config/.env; set +a
```

### The send call

Stdlib only, no dependencies:

```python
import json, os, urllib.request

def send(payload, idempotency_key=None):
    headers = {
        "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
        "Content-Type": "application/json",
        # Required. A missing User-Agent is a 403 with error code 1010,
        # which looks exactly like a bad key and wastes an afternoon.
        "User-Agent": "my-outreach/1.0",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)          # {"id": "..."} — keep this id

result = send({
    "from": "You <you@mail.yourdomain.com>",
    "to": ["them@example.com"],
    "reply_to": "you@yourdomain.com",     # an inbox you actually read
    "subject": "...",
    "text": rendered_body,
    "html": rendered_html,
    "scheduled_at": "in 30 minutes",      # your cancel window
    "tags": [{"name": "arm", "value": arm}],
}, idempotency_key=f"outreach/{email}/touch1")
```

`scheduled_at` takes natural language (`"in 30 minutes"`, `"tomorrow at 9am"`) or ISO 8601, up to 30 days out. `to` accepts up to 50 addresses, but for cold outreach it should always be one — a visible list of strangers is the fastest way to look like spam.

### Idempotency is not optional here

`Idempotency-Key` makes a repeated request return the original result **without sending again**, for 24 hours. Any automation that can retry — a cron that times out, a script you re-run after fixing one row — will double-email people without it, and double-emailing a cold prospect is worse than not emailing them.

Key it on something stable and re-derivable from your own data: `outreach/<email>/touch1`, `outreach/<email>/touch2`. Not a random UUID generated at call time, which changes on the retry and defeats the point.

### Wiring it into the run

The CRM and the loop don't change shape — only the moment `sent_at` becomes true does:

- Draft stage stays identical: `assign_arm.py` for the arm, render, then write to the outbox file rather than a Gmail draft. CRM row: `status=drafted`, `arm`, `template_used`, `drafted_at`
- On send, record the run as published — this starts the metric clock exactly as before:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id>
```

- CRM row: `status=sent`, `sent_at`, `next_followup_at`, and store the returned message id so a cancel or a bounce can be traced back to a person

Set the email channel's `publish` in `config/channels.json` to something other than `draft_only` so the config states what's actually happening. Keep `metric_delay_hours` at 24–48 for email — replies settle faster than social.

### Reading replies back

Two options, and the cheap one is usually right.

**Keep `reply_to` pointed at a mailbox you already read.** Replies land in Gmail, and the existing metric step works unchanged. Nothing to build.

**Or let the sending domain receive.** Add the MX record, enable receiving on the domain, and inbound is then readable over the API — `GET /emails/receiving` lists messages, `GET /emails/receiving/{id}` returns the full body and headers. **No webhook or server is required**; polling on a cron is enough, which is what most guides bury under a serverless tutorial.

Worth knowing before you pick the second: every address at the domain receives, with no per-address configuration, so you get the spam too — filter early. Received emails also count against the same sending quota, one for one.

Don't do both halfway. If replies go to the sending domain, the metric step has to poll the API instead of searching Gmail — otherwise the replies arrive somewhere nothing is watching, and the numbers say the campaign died when it didn't.

### Batch

`POST https://api.resend.com/emails/batch` takes an array of up to 100 of the same objects and cuts request count. Useful once a run is dozens of emails. It is still one personalised email per person — batching is a transport detail, not a mailing list.

### When it breaks

- **403 with error code 1010** and a key you know is good — missing `User-Agent` header
- **403 `invalid_from_address`** — the `from` domain isn't verified, or you typo'd the subdomain
- **429 `rate_limit_exceeded`** — the limit is per team, not per key, so every script you run shares it. Space out sends rather than firing a loop concurrently
- **429 `daily_quota_exceeded` / `monthly_quota_exceeded`** — free tiers are small and inbound counts toward them. Check the plan before blaming the code

---

## What to automate, and what not to

Automate rendering, sending, follow-up scheduling, reply classification and CRM updates.

Don't automate the offer or the personalisation angle. Those are the two things that decide whether any of this works, and they're the two things that most obviously read as machine-written when they aren't thought about.

The A/B loop still applies at volume — arguably it matters more, because at 500 emails a week a 1.2× difference between arms is a lot of meetings.

---

## Rate and reputation notes

- Cold volume from a new domain: start at 10–20/day, double weekly at most
- Keep bounce rate under 2%. Verify addresses before sending — a bounced address costs more than a skipped one
- One unsubscribe mechanism, honoured permanently, across every list you ever import. Above roughly 5,000 messages a day to Gmail or Yahoo they also require one-click unsubscribe headers (`List-Unsubscribe` plus `List-Unsubscribe-Post`, RFC 8058) — set them via the `headers` field
- Reply rate falling while volume rises means the personalisation broke. Check the drafts, not the infrastructure

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

Free, and it solves a real problem: you want `hello@`, `ben@` and per-campaign addresses without buying mailboxes for each.

Routing forwards all of them to one inbox you already read. Turn on catch-all and a campaign address exists the moment you use it — no setup per address.

---

## Outbound: Resend (or Postmark, or SES)

Verify your domain, send from it. Three things that are easy to get wrong:

**Sending and receiving are separate.** A domain verified for sending has no mailboxes at all. Any address on it can send with zero setup, and anything sent *to* those addresses goes nowhere unless you've separately configured inbound. So **always set `reply_to`** to an inbox you actually read. This is the single most common mistake with a send-only domain, and you find out about it by losing replies.

**Inbound needs its own MX record**, and adding one at the root of a domain that already has email will outrank the existing provider and stop delivery there. Use a subdomain unless you genuinely mean to move your mail.

**Deliverability is earned.** SPF, DKIM and DMARC first, then warm up over weeks — a few a day, climbing slowly. Blasting 500 cold emails from a fresh domain gets it flagged, and a burned domain doesn't recover; you buy a new one.

Send from a subdomain like `mail.yourdomain.com` so a mistake doesn't take your main domain's reputation with it.

---

## What to automate, and what not to

Automate rendering, sending, follow-up scheduling, reply classification and CRM updates.

Don't automate the offer or the personalisation angle. Those are the two things that decide whether any of this works, and they're the two things that most obviously read as machine-written when they aren't thought about.

The A/B loop still applies at volume — arguably it matters more, because at 500 emails a week a 1.2× difference between arms is a lot of meetings.

---

## Rate and reputation notes

- Cold volume from a new domain: start at 10–20/day, double weekly at most
- Keep bounce rate under 2%. Verify addresses before sending — a bounced address costs more than a skipped one
- One unsubscribe mechanism, honoured permanently, across every list you ever import
- Reply rate falling while volume rises means the personalisation broke. Check the drafts, not the infrastructure

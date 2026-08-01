# Browser research — finding one real thing about one person

Reading a person's public trail in the browser is the normal path for this
workflow, not a workaround. What you're looking for is small and specific: one
recent, checkable fact you could quote back to them. That's the difference
between an email that gets read and a mail merge.

**Budget about a minute per person.** If a minute turns up nothing, that's a
signal they're the wrong target, not an invitation to write filler
(`engine-outreach` SKILL → step 3).

Requires a browser the agent can drive — the extension from
[`docs/preflight.md`](../../../docs/preflight.md) §2b, or `agent-browser` /
an equivalent browser MCP. Full skill: `benyki/skills/agent-browser`.

## Pattern

```bash
agent-browser open "<url>"
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser get text body > /tmp/page.txt
```

Re-snapshot after every navigation — refs go stale.

## Where to look, in order of what actually yields

Stop at the first real thing. You need **one** observation, not a dossier.

| Source | What you're looking for |
|---|---|
| **Their own site** — changelog, blog, "what's new", pricing page | what they shipped, what they changed, what they charge for now |
| **LinkedIn activity** — the *Activity* tab, not the profile blurb | what they *posted* or commented. A profile says what they claim; activity says what they're thinking about this month |
| **Their job posts** | what a company hires for is what it's struggling with — often the sharpest signal on the page |
| **GitHub** | releases, a README rewrite, a repo they just made public |
| **X / Bluesky / Mastodon** | a complaint, a question, a launch |
| **A podcast, talk or press mention** | they said something in their own words, at length |
| **Reddit / HN comments** | the problem described in their own phrasing — the most quotable of all |

## What counts as an observation

- **It's dated.** "Shipped v2 last month" — not "seems to be growing"
- **It's theirs.** Something they did, wrote, or decided. Not something about
  their industry
- **It has a URL.** No source, no claim — an unverifiable line in a cold email
  is the one mistake you can't take back
- **You could quote it back to them** and they'd recognise it

Not an observation: a job title, a headcount, a funding round everyone
congratulated them on already, a compliment about their "amazing work", or
anything inferred from a logo.

## Write it down before you draft

Into the CRM row, not just the email — `research`, `research_source`,
`researched_at`. The follow-up three weeks later reuses it, the user can correct
you before anything goes out, and next quarter's pass starts warm.
`engine-outreach` SKILL → step 3 has the columns and the reasoning.

## Boundaries

- **Stay signed out where you can.** Most of the above is public. If a page
  walls its content, note that and move on — don't automate account creation and
  don't work around a paywall
- **Their own session, at human pace.** Where a login *is* needed (LinkedIn
  activity, usually), it's the user's own logged-in browser. Automating LinkedIn
  is against its terms and enforcement lands on their account — say that once
  and let them decide
- **Public and professional only.** A home address, a personal phone number, a
  family detail, anything from a private group: not usable, however findable.
  Collect the minimum that justifies the email — `references/lead-sourcing.md`
  has the personal-data limits
- **Never paste what you read straight into the email.** Paraphrase, and never
  invent a quote

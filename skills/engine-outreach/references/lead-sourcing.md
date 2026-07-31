# Lead sourcing — where the list comes from

The list decides more than the copy does. A good email to the wrong 200 people
loses to an average email to the right 20, and no amount of A/B testing rescues
a bad list — it just measures a bad list precisely.

So the first question is never "where do I scrape" but **"who, specifically?"**
Pull that from `shared/brand.md`; if the answer there is "businesses" or
"founders", stop and fix that first. A source can only be as targeted as the
description you're sourcing against.

## Sources, in the order most people should try them

| Source | Cost | Quality | Use when |
|---|---|---|---|
| **People they already know** — inbox, LinkedIn connections, past customers, waitlist, churned users | free | highest | always first, and almost always skipped |
| **Communities where the ICP posts** — subreddits, Discords, Slack groups, forums | free | high, if you read before you write | the ICP is defined by a behaviour rather than a job title |
| **Platform search** — LinkedIn, X, GitHub, TikTok, Product Hunt, job boards | free | good, slow by hand | you can describe the person by something they *did* |
| **Directories and marketplaces** — app stores, agency lists, conference attendee pages, funding announcements | free | mixed | the ICP is a company type |
| **Scraping a platform** at volume (Apify and similar) | paid | as good as your filter | hand-collection is the bottleneck and the filter is proven |
| **Bought lists** | paid | usually poor | rarely — see below |

**Bought lists deserve their reputation.** They're stale, they're sold to
everyone in your category, and the addresses often carry spam traps that damage
your sending domain. If someone insists, sample fifty and check the bounce rate
before touching the rest.

## The signal that makes a list good

Whatever the source, prefer people you can describe by something **recent and
observable**: they shipped a thing, they wrote a thing, they're hiring for a
thing, they asked a question in public, they just raised, they just migrated off
a tool. That observable is what fills `{{OBSERVATION}}` in the email — so a list
where you can't find one per person is a list that will produce filler.

Test it before scaling: **take ten**, research each for a minute, and see how
many yield a real observation. Eight or more, scale the source. Three, the
source is wrong and no amount of volume fixes it.

## Doing it by hand first

Hand-build the first 20–50, even when a scraper is available. It's an hour, and
it's the hour where you learn what the filter should actually be — which
titles are decoys, which company sizes never reply, what the observable looks
like in this niche. Automating before that just produces wrong leads faster.

## The fastest honest path to the first 20 (B2B)

Three steps, one afternoon, no list to buy. Works because LinkedIn is where the
filter lives and the email is a separate problem you solve afterwards.

**1. Search on LinkedIn with the agent driving the browser.**
Build the search with real filters — title, industry, headcount, geography, and
ideally something that changed recently (hiring, a new role, a recent post). The
agent reads the results and writes name, company, role and **profile URL** into
`inputs/audience/`. Capture the observable while you're on the profile: it's
right there, and coming back for it later doubles the work. This needs the
browser extension — [`docs/preflight.md`](../../../docs/preflight.md) §2b — and
it uses the user's own logged-in session, so nothing is scraped anonymously.

**2. Turn profiles into email addresses.**
The profile URL is the input; a finder tool returns the address. Options, all
paid, all freemium enough to test twenty rows before committing:

| Tool | Shape |
|---|---|
| **Dux-Soup** | Chrome extension that works *through* your own LinkedIn session — visits, scrapes and enriches profiles as you browse. Closest to "I already have the search open" |
| **Lusha · Apollo · Hunter · Clearbit Connect** | extension or API; paste or upload profile URLs, get verified addresses back |
| **Prospeo · Findymail · Dropcontact** | API-first, built for exactly the URL-in-address-out step, and easier to script |

Pick on two things: whether it **verifies** the address (a bounce costs sender
reputation, and a fresh domain can't afford many), and whether it can take a
**list** rather than one profile at a time. Expect a 50–70% hit rate on
professional audiences — that's normal, not a failed run, and it's why you
search for thirty to land twenty.

**3. Run the outreach flow.**
Normalise into `crm.csv`, then the ordinary run: `assign_arm.py` →
research → `references/first-touch.md` → drafts. Nothing about this path is
special downstream; it just fills the audience folder faster.

**Two cautions, both worth saying once to the user:**

- **Automating LinkedIn is against its terms**, and enforcement lands on the
  account — the restriction is theirs to accept, so name it and let them decide.
  Tools driving your own session at human pace are the lower-risk end of this;
  bulk connection-request automation is the high-risk end and a different
  activity entirely
- **A found address is still cold outreach.** The consent, opt-out and
  minimum-data rules further down apply exactly the same way, and a verified
  address is not a relationship

## Scraping, when you get there

- **Describe the filter precisely first**, then find the tool. A scraper is a
  faster version of a search you already know how to run
- **Cap what you collect.** Name, company, one contact route, one observable,
  the source URL. A row with 40 enrichment fields is a row nobody reads
- **Keep the source URL per lead.** It's how the next agent verifies the
  observable instead of re-researching from scratch
- **Respect the obvious limits.** Public profile data is one thing; a login-
  walled page, a scraped private group, or a platform whose terms forbid it is
  a different thing, and the account risk lands on the user
- **Personal data has rules that vary by country** — GDPR-style regimes require
  a lawful basis and a working opt-out for B2B cold mail, and some jurisdictions
  are stricter about individuals than companies. Say this out loud once, put an
  opt-out line in the email, and honour it permanently. Don't play lawyer beyond
  that; flag it and let the user decide

**`prospect-finder`** is the capability that does all of this end to end —
description → search shape → ten-lead test → qualified list with one observable
per row, deduped against the CRM. Install it when list-building is the step
you're spending real time on;
[`docs/additional-skills.md`](../../../docs/additional-skills.md) has the steps.

Other optional capabilities: `apify-ultimate-scraper` for platform scraping at
volume, `agent-browser` for reading platforms that have no API,
`tiktok-post-finder` for creator-style outreach.

## Landing it in the CRM

Normalise into `crm.csv` — the header is the contract, keep every column even
when a cell is empty (`engine-outreach` SKILL step 1 has the shape).

- **Dedupe on email**, falling back to LinkedIn URL, then name + company
- **Never import over someone with a `sent_at`.** That's the one silent mistake
  this workflow can make, and it costs the relationship, not just the row
- **Keep `source` and `notes` populated.** In two months "where did these 300
  people come from and were they any good?" is a question you'll actually ask,
  and `runs/index.csv` can answer it per source once the column is there
- **A `status=closed` row is permanent.** Unsubscribes and "not interested"
  survive every future import

## Credits

Parts of this page were adapted from open-source sales skill libraries, and the
`prospect-finder` capability draws on them more heavily — its `CREDITS.md` has
the full attribution. Specifically:

- The **person-first vs company-first** distinction, the **hit-rate benchmarks**,
  and the **qualify-a-sample-before-scaling** check come from
  [`growthenginenowoslawski/coldoutboundskills`](https://github.com/growthenginenowoslawski/coldoutboundskills)
  (MIT), built from patterns across 1,000+ real B2B campaigns
- The **signal-first research mindset** — look for what's happening in their
  world now, not for fields to fill a template with — comes from
  [`gtmagents/gtm-agents`](https://github.com/gtmagents/gtm-agents) (Apache-2.0)

Both go far beyond what this workflow needs — sequencing, deliverability,
campaign grading, CRM sync. Worth reading in full if outreach becomes your main
channel.

## Reading it back

Once a few sources have run, compare reply rate **by source**, not just by
template. Sourcing usually moves the number more than copy does, and it's the
cheaper thing to change: add a `source` column to `runs/index.csv` (the spine
preserves extra columns) and the weekly report can split on it.

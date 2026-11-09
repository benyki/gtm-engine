# <workflow name>

<One or two lines: what this workflow writes, for which site, for whom.
Example: articles for example.com/blog answering the invoicing questions
freelancers ask on Reddit, one a week.>

**The number:** <Search Console clicks a month on these articles, or signups
from them>

Articles generated locally as markdown. Nothing here publishes: a person moves
every article live.

## Run it

Ask your agent to run this workflow with the `gtm-seo` skill.

## Schedule

Manual.

<!-- Or, once it runs on its own:
When: every Monday, 09:00
Where: <the scheduler this project uses>
Prompt: "<the exact prompt, e.g. Run the seo-articles workflow with gtm-seo:
top up the backlog, draft the next article into drafts/, fill in results
that are due. Never publish.>"
-->

## Files

| Path | What | In git |
|---|---|---|
| `inputs/backlog.csv` | real questions, validated and scored; the next article comes from the top | yes |
| `inputs/query-patterns.md` | the query grid filled in for this product, written on the first pass | yes |
| `templates/article-default.md` | the article skeleton | yes |
| `drafts/` | the agent's drafts. Nothing here is live | yes |
| `site/` | the site, if this workflow built one. Only a person copies a draft into it | source yes, builds no |
| `log.csv` | one row per published article, with its result | yes |
| `brand.md` | voice notes, only if the project has none elsewhere | yes |

## Keys

None for the default path. Optional, set in the project's own env, by name:
`CLARITY_API_KEY` (Clarity export, for rewrites once there's traffic),
`AHREFS_API_KEY` or `SEMRUSH_API_KEY` (only if already paid for). Delete the
ones this workflow doesn't use.

## Sources

- **Primary:** Reddit
- **Subreddits:** <none yet: the agent finds where the audience posts; list
  them here once known>
- **Competitor URLs:** <pages to outrank; when listed, they come before Reddit>
- **Ahrefs / Semrush:** off. Only if already paid for, never bought for this

## What we learned

<!-- One line each time something clearly won or lost, with the date of its
log.csv row. Example: 2026-12-01: answer-first openings held twice the clicks
of story openings. -->

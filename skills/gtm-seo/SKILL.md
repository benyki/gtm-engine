---
name: gtm-seo
description: Writes search-led articles and landing pages by mining the questions real people ask (Reddit by default, competitor pages when supplied), drafting in the project's voice, and building a simple markdown site when there is none. Sets up a workflow folder from its template. Generates locally, publishing stays manual. Use when the user says "write an article", "SEO", "blog post", "what should I write about", "make a landing page", or asks for written content that should rank.
---

# gtm-seo

Finds a question people actually asked, answers it better than what ranks now,
and writes the piece in the project's voice. Output is markdown, generated
locally. Nothing goes live until the user says so.

This skill is a template plus a craft guide. The workflow folder it fills
follows [`../gtm/SKILL.md`](../gtm/SKILL.md); every path below is inside it.

## Start

1. **Copy** (skip if `gtm` already made the folder): `cp -R` this skill's `template/` to `<repo>/workflows/<name>/` (`seo-articles` is fine) and fill in the README's first lines, the number included.
2. **Voice.** The project's own voice or brand notes, plus a few things they wrote and like. None? The five questions in [`../gtm/SKILL.md`](../gtm/SKILL.md) (Voice), answers saved to `brand.md` here.
3. **Ask where articles go**: an existing site or CMS, or none yet (see Publishing).
4. **Find five real questions** (see Where topics come from), validate and score them into `inputs/backlog.csv`, show the top three. The user picks.
5. **Outline, write, cut the slop** (see The writing), save to `drafts/<slug>.md` and hand it over.

| How | Reference |
|---|---|
| Reddit and search results in the browser | `references/browser-research.md` |
| Find, validate and score subjects | `references/subject-finding.md` |
| Cut AI slop, keep the voice (every draft) | `references/anti-slop-writing.md` |
| Build the site, the publishing gate, metadata | `references/publishing-site.md` |
| Rewrites from Clarity once there's traffic | `references/clarity-rewrite.md` |
| Internal linking, content in a database | `references/advanced.md` |

## Where topics come from

The README's Sources section says where to look. The default is Reddit, and it needs no account. No API for something? Read it in the browser: that's the normal path here, not a workaround.

**Reddit.** Find the subreddits where the audience actually posts, then look for questions asked repeatedly, questions with long comment threads, and questions where the top answer is bad. That last one is the opportunity: a real question with no good answer is the whole game.

**Competitor URLs.** If the README lists any, read them and find what they left out, got wrong, or let age badly. Beat the page that exists; don't write a worse copy of it.

**Ahrefs or Semrush.** Only if they already pay. The free path is enough.

The first article doesn't wait for a full backlog. After it, run `references/subject-finding.md` weekly and keep at least twenty rows at `status=validated`: a thin backlog is how a site fills up with articles nobody searched for.

## The writing

**Show the outline first.** It costs a minute, saves an hour, and it's the last cheap moment to catch a wrong angle.

Then write from `templates/article-default.md`. Voice comes from their own writing, not from adjectives in a brief.

- Answer the question in the first hundred words. Nobody scrolls for it
- Specifics over hedging: real numbers, real examples, real product names
- No throat-clearing intro, no "in today's fast-paced world", no summary of what the article will cover
- Length is whatever the question needs
- Respect the banned words and claims in the voice notes

**Cut the slop before the user reads it.** `references/anti-slop-writing.md` over every draft, in edit mode by default (detect mode when they want the patterns named). If a paragraph could appear on a competitor's blog with the product name swapped, rewrite it in their voice or cut it. Sanding off their edge is the failure, not the goal. If `no-ai-slop-writting` is installed, use it instead.

## Publishing

Ask which route applies before the first article.

**They already have a site.** They paste the markdown into their CMS. Don't automate WordPress, Webflow or Ghost: every setup is different, and it's a bad problem to solve on day one.

**They don't.** Then building one is part of the job, because thirty good articles in a folder are worth nothing. The contract: content stays in plain markdown an agent can read and fix, and publishing is a git push. If they already run a Next.js site or a company host, publish into that. From nothing, the default is Astro plus local markdown in `site/`, deployed to Cloudflare Pages or Railway (free at this size, deploy on push). `references/publishing-site.md` has the build: the gate (the agent writes to `drafts/`, a human copies into the built folder, and that copy is the approval), the frontmatter, the six metadata pieces and the checks that prove they're live.

## Log and learn

When an article is live, add a row to `log.csv` (`date,channel,link,what_it_tried,result`): channel `blog` or `landing`, the live URL, the one thing the piece tried (angle, opening, length), `result` empty. Set its backlog row to `status=published`.

Search is slow. After three or four weeks, read the URL's clicks, impressions and position in Search Console and write them into `result` (`28d: 41 clicks, 1.9k impr, pos 8.2`). When something clearly won or lost, add one line to the README's "What we learned". A page with traffic gets its next rewrite from `references/clarity-rewrite.md`; a clear winner is worth multiplying (`references/subject-finding.md`, section 6).

## Schedule (optional)

One weekly or fortnightly task in whatever scheduler the project uses: top up the backlog, draft the next article into `drafts/`, fill in results that are due. It never publishes. The README records when it runs, where, and the exact prompt.

## Rules

- **Never publish without a yes.** Deploying is a git push, easy to do by accident and hard to undo from a search index. The agent never writes into the built folder
- **Never invent a statistic, study or quote.** If a claim needs a source, find one or cut the claim
- **Every article traces to a real question**: a backlog row with a `source_url`. Flag the ones that don't
- One good piece, published and measured, beats ten in a folder. Don't batch
- An objection that keeps coming back in the project's other workflows (their READMEs' "What we learned", outreach replies) is your next article

Optional toolbox skills: `clarity-api-seo` and `agent-browser` from `benyki/gtm-skills` ([`docs/additional-skills.md`](https://github.com/benyki/gtm-engine/blob/main/docs/additional-skills.md)).

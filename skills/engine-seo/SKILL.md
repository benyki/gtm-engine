---
name: engine-seo
description: Writes search-led articles and landing pages by mining the questions real people ask (Reddit by default, competitor pages when supplied), drafting in the user's voice, and logging the run. Generates locally — publishing stays manual. Use when the user says "write an article", "run the SEO workflow", "what should I write about", "make a landing page", or asks for written content.
---

# engine-seo

Finds a question people actually asked, answers it better than what currently ranks, and writes the piece in the user's voice.

This skill runs any workflow folder of **type `seo`**. The default folder is
`seo/`; paths below (`sources.json`, `inputs/`, `templates/`, `runs/`, `site/`)
are inside that folder, while brand, accounts and keys live in `shared/`.
**Two seo workflows are fine** — e.g. `seo/` for the product blog and
`seo-docs/` for a docs/comparison site, each with its own sources, site and
metric — scaffold with `--merge --workflow seo-docs:seo`, or copy a folder
and empty its `runs/` and `reports/` (history belongs to the original).

Output is markdown, generated locally. Where it goes depends on whether they already have a site — see **Publishing** below. Either way nothing goes live without them saying so.

**How (not just what):**

| Step | Reference |
|---|---|
| Reddit / SERPs in the browser | `references/browser-research.md` |
| Cut AI slop / keep voice | `references/writing.md` |
| After publish (Clarity → rewrites) | `references/clarity-rewrite.md` |
| Static site / CMS tradeoffs | `references/advanced.md` |

## Where topics come from

Read this workflow's `sources.json`. The default is Reddit, and it needs no account.

**Reddit (default).** Find the subreddits where the audience in `shared/brand.md` actually posts, then look for questions asked repeatedly, questions with long comment threads, and questions where the top answer is bad. That last one is the opportunity — a real question with no good answer is the whole game. How to read threads without an API: `references/browser-research.md`.

**Competitor URLs.** If they're listed in `sources.json`, read them and find what they left out, what they got wrong, and what's aged badly. Beat the page that exists; don't write a worse copy of it.

**Ahrefs / Semrush.** Only if they already pay. Never suggest buying one.

No API for something? Read it in the browser. That's the normal path here, not a workaround.

## The run

### 1. Pick the question

One question, phrased the way a human would ask it. Show the user the shortlist with why each one is worth writing, and let them choose. Note the source — the queue in `inputs/queue/` may already have one waiting from the loop.

### 2. Get the arm

```bash
python3 ~/.agents/skills/engine-loop/scripts/assign_arm.py --workflow seo
```

For articles the variants are usually structural — how it opens, whether it leads with the answer or the context, how long it runs. If it returns `write_template`, write that template from the hypothesis and use it.

### 3. Outline, then check

Show the outline before writing the draft. It costs a minute and saves an hour, and it's the last cheap moment to catch a wrong angle.

### 4. Write

Voice comes from `inputs/best/` — their own best-performing pieces — not from adjectives in a brief. Read those first, every time.

- Answer the question in the first hundred words. Nobody scrolls for it
- Specifics over hedging. Real numbers, real examples, real product names
- No throat-clearing intros, no "in today's fast-paced world", no summary of what the article will cover
- Length is whatever the question needs
- Respect the banned words and claims in `shared/brand.md`

Before the user reviews, run `references/writing.md` over the draft (edit or detect).

### 5. Log it

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py new --workflow seo --channel blog \
  --experiment exp-002 --arm default --template article-default.md
```

Write the draft to `runs/<run_id>/output/`.

## Publishing

Two routes. Ask which one applies before the first run — it changes where the markdown ends up.

### They already have a site

Generate locally, they paste it into their CMS. Don't try to automate WordPress, Webflow or Ghost — every setup is different and it's a bad problem to solve on day one.

### They don't have a site, or want to start fresh

Then building one is part of this workflow, because thirty good articles in a folder are worth nothing.

The **contract** is: content stays in plain markdown files an agent can read and fix, publishing is a git push, and each page carries its `run_id` back to the spine. Any stack that satisfies it works — if they already have a Next.js site or a company-standard host, publish into that rather than building a parallel one. The **default**, when starting from nothing, is Astro + local markdown + a simple host:

1. Scaffold an Astro site once, into this workflow's own `site/` folder (e.g. `seo/site/`) — self-contained like everything else here
2. Define a content collection with the `glob` loader pointing at your articles:

   ```ts
   // src/content.config.ts
   import { defineCollection, z } from 'astro:content';
   import { glob } from 'astro/loaders';

   const blog = defineCollection({
     loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
     schema: z.object({
       title: z.string(),
       description: z.string(),
       pubDate: z.coerce.date(),
       run_id: z.string().optional(),   // ties the page back to runs/index.csv
     }),
   });

   export const collections = { blog };
   ```
3. On publish, copy the finished article into `site/src/content/blog/<slug>.md` with that frontmatter
4. Deploy — **Cloudflare Pages** or **Railway** by default; both are free at this size and deploy on git push. Any host that deploys from git is equivalent here

Then the standard SEO set, which Astro gives you cheaply: sitemap (`@astrojs/sitemap`), canonical URLs, per-page meta and Open Graph tags, JSON-LD, RSS. **Check the current Astro docs when you set this up** — the content APIs changed in Astro 5 and older tutorials will send you wrong.

Keeping the content as markdown files is deliberate: when something breaks, an agent opens the file and fixes it. That stops being true once the content lives in a database — see `references/advanced.md`, which covers when that trade is worth making.

### Either way

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish --run <run_id> --url https://...
```

The URL matters — `engine-loop` needs it to fetch Search Console numbers later.

One timing note: search is slow. The 72-hour default window in `due_metrics.py` is a social-media number; Search Console data on a new article takes weeks to mean anything. Set `metric_delay_hours` on the blog channel in `shared/channels.json` (336 = two weeks is a sane floor) so the loop doesn't ask for numbers that don't exist yet.

### After it has traffic

If Clarity is set up, turn behavior into the next rewrite with
`references/clarity-rewrite.md` — don’t guess from vanity metrics alone.

## Rules

- **Never publish without a yes.** Deploying is a git push, which is easy to do by accident and hard to undo from someone's index
- **Never invent a statistic, study or quote.** If a claim needs a source, find one or cut the claim. A fabricated number in a published article is the kind of mistake that outlives the article
- **Never write about a question nobody asked.** If it didn't come from a real thread, a real competitor gap or the queue, it's guesswork
- Don't write ten pieces in a batch. One good piece, published, measured, beats ten in a folder
- An objection or question that keeps appearing in other workflows' replies is your next article — check `shared/insights.md` and the siblings' `reports/latest.json` when picking topics, and add a line back when an article's numbers teach something general

## Going further

- `references/advanced.md` — site that generates from `runs/`
- Optional: `benyki/skills/clarity-api-seo`, `benyki/skills/agent-browser` —
  `docs/additional-skills.md`

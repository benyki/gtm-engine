# Publishing — the gate, the metadata, the deploy

`SKILL.md` decides *whether* the workflow builds a site. This file is what
"published" has to mean once it does: a human moved the file, the page carries
its metadata, and the URL is back in the run log.

The stack is Astro + local markdown by default, but nothing here is
Astro-specific. Any generator that reads markdown and deploys from git
satisfies it.

---

## The gate — the builder reads one folder, you fill it

Two folders, and the difference between them is the entire safety model:

```
seo/
├── runs/<run_id>/output/<slug>.md      ← the agent writes here. Always.
└── site/
    └── src/content/blog/<slug>.md      ← only a human puts a file here
```

The site builds from `site/src/content/blog/` and **nothing else**. An agent
never writes into it. Publishing is one deliberate copy:

```bash
cp seo/runs/<run_id>/output/<slug>.md seo/site/src/content/blog/<slug>.md
```

Why a folder and not a flag: a `draft: true` in frontmatter is one character
away from live, and the mistake is invisible in a diff full of prose. A file
that isn't in the built folder cannot be published by accident, by a broken
build script, or by an agent that misread an instruction. The copy is the yes.

If the user wants a review step *inside* the site folder instead — some people
prefer everything in one tree — the equivalent is a `blog/` collection that
globs `published/**` only, with drafts sitting in `blog/pending/`. Same
property: the build has one input directory and a human moves files into it.

**Deploying is a `git push`.** That's easy to do by accident and hard to undo
from someone's search index. Never push without an explicit yes, per run.

## Frontmatter — the contract

Every published file carries this. `run_id` is the one people forget, and it's
what lets the loop tie a Search Console number back to the arm that earned it:

```yaml
---
title: "How to track billable hours without a timer"
description: "The three methods that survive a real week, and when each breaks."
pubDate: 2026-08-04
updatedDate: 2026-09-11        # only when you actually revise it
run_id: 2026-08-04-002-seo     # ties this page to runs/index.csv
canonical: ""                  # set only when this page duplicates another URL
image: "/og/billable-hours.png"  # optional; falls back to a site default
---
```

The collection schema enforces it — an article missing `title` or `pubDate`
fails the build rather than shipping a page with a blank `<title>`:

```ts
// src/content.config.ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string().max(60),
    description: z.string().min(50).max(160),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    run_id: z.string().optional(),
    canonical: z.string().optional(),
    image: z.string().optional(),
  }),
});

export const collections = { blog };
```

Those length limits aren't pedantry: a title over ~60 characters and a
description over ~160 get truncated in the result, and the truncation lands
mid-sentence.

## The metadata set

Six things. All of them are cheap, and all of them are invisible until they're
missing.

| | What | Where it shows up |
|---|---|---|
| **`<title>` + meta description** | from frontmatter, per page | the search result itself |
| **Canonical** | self-referencing on every page; points elsewhere only for a genuine duplicate | stops the same article competing with itself across `/`, `/?ref=`, and a trailing slash |
| **Open Graph + Twitter card** | `og:title`, `og:description`, `og:image`, `og:url`, `og:type=article`, `twitter:card=summary_large_image` | every share on LinkedIn, X, Slack, WhatsApp |
| **JSON-LD** | `Article` (or `BlogPosting`) with `headline`, `datePublished`, `dateModified`, `author` | rich results, and how some assistants read the page |
| **Sitemap** | generated at build from the collection, never hand-maintained | what you submit to Search Console |
| **RSS** | `/rss.xml` from the same collection | readers, aggregators, and your own newsletter later |

In Astro that's `@astrojs/sitemap` plus `@astrojs/rss` plus a head partial;
`astro-seo` handles OG/Twitter/canonical if you'd rather not write the tags.
**Check the current Astro docs when you wire it up** — the content APIs changed
in v5 and older tutorials will send you wrong.

Two details that catch people:

- **`site` must be set in `astro.config.mjs`.** Without it the sitemap has no
  absolute URLs and the canonical tags are relative — both silently useless
- **`og:image` needs an absolute URL**, including the domain. A relative path
  renders a blank card, and the card is cached by the platform for weeks

## Verify on the live URL, not locally

A local build proves the template. It doesn't prove what the host serves:

```bash
URL=https://example.com/blog/billable-hours

# metadata actually present in the served HTML
curl -sL "$URL" | grep -oE '<(title|link rel="canonical"|meta property="og:[^"]+")[^>]*>'

# JSON-LD parses
curl -sL "$URL" | python3 -c "import sys,re,json; [json.loads(m) for m in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', sys.stdin.read(), re.S)] and print('ld+json ok')"

# the page is in the sitemap
curl -sL https://example.com/sitemap-index.xml
curl -sL https://example.com/sitemap-0.xml | grep -c "$URL"

# feed is valid XML
curl -sL https://example.com/rss.xml | head -5
```

Then, once: submit the sitemap in Search Console and request indexing on the
first article. Nothing else in this file matters if Google never fetches the
page.

## Log it

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish \
  --run <run_id> --url "$URL"
```

The URL is not optional here — `engine-loop` needs it to pull Search Console
numbers later, and a published article with no URL in the spine is invisible to
every verdict that follows.

Set `metric_delay_hours` on the `blog` channel in `shared/channels.json` before
the first article lands. The 72-hour default is a social number; Search Console
data on a new page needs weeks (`336` is a sane floor). Reading early doesn't
just mislead you — it writes a wrong number into `index.csv` permanently.

## Rules

- **Never push without an explicit yes.** Per run, not once for the project
- **The agent never writes into the built folder.** The copy is the human's
- **Never publish a page with no `description`** — the search result then shows
  whatever sentence Google picks, usually the worst one
- **Never set a cross-page `canonical` to "consolidate" two articles** you
  should have merged. Merge them
- **A revision updates `updatedDate` and keeps the `run_id`.** The run that
  earned the traffic is the run that keeps it; a rewrite that erases the link
  breaks the only trail back to the arm

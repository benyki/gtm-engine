# SEO — going further

The base engine already builds a site: Astro, local markdown, deployed to Cloudflare Pages or Railway. This is what comes after that.

**Symptom: the markdown files have become the bottleneck.** Two machines writing the same folder, content you want to reuse across a site and an app, or a hundred-plus articles where "find the one about pricing" means grepping a directory.

---

## Move the content into a database

Astro and Next.js can both build static pages from a remote source at build time. You keep static output — the DB is a build input, not a runtime dependency.

**Astro.** Write a custom loader against the Content Loader API. It runs at build time, pulls rows, and puts them in the content store:

```ts
// src/loaders/supabase.ts
import type { Loader } from 'astro/loaders';
import { createClient } from '@supabase/supabase-js';

export function supabaseLoader(): Loader {
  return {
    name: 'supabase-articles',
    async load({ store, renderMarkdown, logger }) {
      const db = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!);
      const { data, error } = await db
        .from('articles').select('*').eq('status', 'published');
      if (error) throw error;

      store.clear();
      for (const row of data) {
        store.set({
          id: row.slug,
          data: row,
          rendered: await renderMarkdown(row.body),
        });
      }
      logger.info(`loaded ${data.length} articles`);
    },
  };
}
```

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { supabaseLoader } from './loaders/supabase';

export const collections = { blog: defineCollection({ loader: supabaseLoader() }) };
```

`renderMarkdown` is what makes `render()` work on the entry, so the page component doesn't care where the content came from.

**Next.js.** Same shape: fetch in `generateStaticParams` and the page component, export statically. Keep it SSG — there's no reason to render per-request for content that changes when you publish.

**Check the current docs before you build this.** Astro's content APIs changed in v5 and Next's data-fetching story changes most major versions. Anything you remember about either is probably a version behind.

## The SEO features are the reason to use a framework

Don't hand-roll these — both frameworks give you them for a few lines:

- **Sitemap** — `@astrojs/sitemap`, or Next's `sitemap.ts`
- **Open Graph and Twitter cards** per page, generated from the row's title and description. Astro can render **OG images at build time**, so every article gets its own social preview instead of one shared banner
- **Canonical URLs** — matters as soon as you have tag or pagination routes
- **JSON-LD** — `Article`, and `FAQPage` where the piece answers a question
- **RSS** — `@astrojs/rss`
- **Internal linking** — with everything in a DB this becomes a query rather than a chore, and it's the highest-leverage thing most content sites never do

Read the framework's current SEO guide when you set this up. These integrations move.

---

## The trade you're making

Worth being explicit, because it cuts both ways and most write-ups only mention the upside.

**What you gain: agents can run anywhere.** Once content is in Supabase rather than a folder on your laptop, a cron on a VPS or a cloud agent can write an article, insert a row, and trigger a rebuild. Nothing depends on your machine being awake or on files being in the right place. That's the real unlock — it's what makes the whole loop survivable when you're travelling, and it pairs with the cloud-cron section in `engine-setup/references/advanced.md`.

**What you lose: agents can no longer just fix it.** With markdown files, a broken page is a file an agent opens, reads and edits — the whole state is visible in the repo, and `git diff` shows what changed. With a database, the content is behind a network call and a schema. To debug, the agent needs credentials, a working client, and permission to write, and when something looks wrong there's no diff to read. A malformed row that breaks the build is meaningfully harder to find than a malformed file.

So the honest ordering:

| | Local markdown | Database |
|---|---|---|
| Agent can read and fix directly | yes | needs credentials and a client |
| History and rollback | `git log`, free | you build it |
| Runs headless in the cloud | awkward | natural |
| Multiple machines / writers | conflicts | fine |
| Query across content | grep | SQL |
| Debugging a broken build | open the file | inspect the row |

**Stay on files until you actually need the cloud.** Most people don't, for a long time. When you do move, keep a periodic export of the table back to markdown in git — you get the cloud execution without giving up the thing that made it debuggable.

---

## The honest caveat

None of the infrastructure above changes what ranks.

A site of AI-generated pages ranks like a site of AI-generated pages. What ranks is content that answers a real question better than the page currently answering it — which is why the base engine mines real questions rather than keyword lists. A hundred thin pages will do more damage to a domain than ten good ones will do good.

If you wouldn't send a page to a customer, don't publish it. Moving it into Postgres first doesn't help.

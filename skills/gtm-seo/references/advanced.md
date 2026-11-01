# SEO — going further

Next steps once the markdown site from `publishing-site.md` is live and articles are landing. Not before.

## Internal linking

The highest-leverage thing most content sites never do. Every new article links to two or three older ones in the same cluster, and they link back. By hand while there are a dozen articles; a query once there are a hundred.

## Two more metadata pieces

- **OG images at build time.** Astro can render one per article from its title, so every share gets its own preview instead of one shared banner
- **`FAQPage` JSON-LD** next to `Article`, where the piece answers a question

These integrations move: read the framework's current SEO guide when you add them.

## Move the content into a database

**Symptom: the markdown files have become the bottleneck.** Two machines writing the same folder, content reused across a site and an app, or a hundred-plus articles where "find the one about pricing" means grepping a directory.

Keep static output: the DB is a build input, not a runtime dependency. In Astro, a custom loader against the Content Loader API pulls rows at build time:

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
        store.set({ id: row.slug, data: row, rendered: await renderMarkdown(row.body) });
      }
      logger.info(`loaded ${data.length} articles`);
    },
  };
}
// src/content.config.ts: collections = { blog: defineCollection({ loader: supabaseLoader() }) }
```

In Next.js, same shape: fetch in `generateStaticParams` and the page component, export statically. **Check the current docs first**: Astro's content APIs changed in v5, and Next's data fetching changes most major versions.

**The trade.** Writers can run anywhere, but an agent can no longer just open the file and fix it:

| | Local markdown | Database |
|---|---|---|
| Agent can read and fix directly | yes | needs credentials and a client |
| History and rollback | `git log`, free | you build it |
| Runs headless in the cloud | awkward | natural |
| Multiple machines / writers | conflicts | fine |
| Debugging a broken build | open the file | inspect the row |

Stay on files until you actually need the cloud. When you move, keep a periodic export of the table back to markdown in git.

## The honest caveat

None of this changes what ranks. What ranks is content that answers a real question better than the page answering it now. A hundred thin pages do more damage to a domain than ten good ones do good. If you wouldn't send a page to a customer, don't publish it.

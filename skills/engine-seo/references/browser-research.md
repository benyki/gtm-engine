# Browser research — Reddit / SERPs when there’s no API

No Reddit or search API? Read the page in the browser. That is the normal path
for topic mining in `engine-seo`, not a workaround.

Requires `agent-browser` (or an equivalent browser MCP). Prefer a few durable
commands over memorizing the whole CLI — full skill: `benyki/skills/agent-browser`
or `agent-browser skills get core --full`.

## Pattern (every research session)

```bash
agent-browser open "<url>"
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser get text body > /tmp/page.txt
```

Re-snapshot after every navigation or click — refs go stale. Use `@eN` refs from
`snapshot -i` for clicks/fills.

## 1. Google SERP for a question

```bash
# URL-encode the query yourself or type into the box after open
agent-browser open "https://www.google.com/search?q=how+to+X+without+Y"
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser get text body > /tmp/serp.txt
```

From the snapshot/text: note the top titles, People Also Ask phrasing, and which
URLs actually answer the question. Those are your competitors to beat.

Open a result:

```bash
agent-browser click @e12          # link ref from snapshot
agent-browser wait --load networkidle
agent-browser get text body > /tmp/competitor.txt
```

## 2. Reddit — find the thread, then mine it

```bash
agent-browser open "https://www.reddit.com/r/<sub>/search/?q=<question>&restrict_sr=1&sort=comments"
agent-browser wait --load networkidle
agent-browser snapshot -i
```

Open a promising thread, then pull the body (title + comments):

```bash
agent-browser click @e5
agent-browser wait --load networkidle
agent-browser get text body > /tmp/thread.txt
```

What to extract into the shortlist:

- Question phrased the way a human asked it
- Long threads / repeated asks across posts
- Top answers that are thin, outdated, or wrong (the gap to fill)

## 3. Stay signed out unless you must

Topic mining does not need a login. If a page walls content, note it and pick
another thread — don’t automate account creation.

## Don’t

- Dump the entire accessibility tree into the draft — summarize into 3–5
  candidate questions with *why* each is worth writing
- Invent comment quotes; paste or paraphrase only what you read
- Rely on one SERP screenshot; open at least one competing page and one thread

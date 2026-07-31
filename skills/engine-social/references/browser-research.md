# Browser research — reading platforms and threads when there's no API

No API for the platform you're mining? Read the page in the browser. That is the
normal path for `engine-social` research, not a workaround: LinkedIn and X show
what you need behind your own login, and Reddit needs no account at all.

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

## 1. The platform's own search

The first validation step in `references/subject-finding.md` — has this claim
landed before, and who said it. Search inside the platform, sort by top, and
read the replies rather than the like count: an argument in the comments is a
stronger signal than a big number.

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

What to extract into the backlog:

- The claim, phrased the way a human said it
- The friction people keep describing — that's the post
- Threads where the top answer is thin: their disagreement is your angle

## 3. Stay signed out unless you must

Topic mining does not need a login. If a page walls content, note it and pick
another thread — don’t automate account creation.

## Don’t

- Dump the entire accessibility tree into the draft — summarize into 3–5
  candidate questions with *why* each is worth writing
- Invent comment quotes; paste or paraphrase only what you read
- Rely on one SERP screenshot; open at least one competing page and one thread

# Threads, and posting them on X

Two things: how to **write** a thread (transfers to X, Bluesky, LinkedIn), and
how to **post** one from the user's logged-in browser.

---

# Part 1 — writing a thread

## First: does this need to be a thread?

Usually not. A single post that lands beats a mediocre thread, and a thread that
exists because the draft ran long is the most common bad post on any platform.

Thread when the idea genuinely has **stages** — a sequence, a story, a
before/after, a list where each item earns its own beat, a claim that needs
evidence built up. Don't thread a single idea with three supporting sentences;
that's one post.

## The rules that make one work

**A thread is not a long post cut into pieces.** Each post is read on its own,
in a feed, by someone deciding whether to keep going. That changes how it's
written:

1. **The first post stands alone and earns the second.** Most people read only
   this one. It has to make sense with no context, say something concrete, and
   leave a reason to continue — a tension, a number, a claim that begs a "how".
   Never open with "a thread on…" or "1/"; that's a table of contents, not a hook
2. **One idea per beat.** If a post contains two, it should be two posts. If it
   contains half of one, merge it back
3. **Each post should be quotable alone.** People screenshot and quote single
   posts out of a thread — every one should survive that
4. **The last post lands.** A conclusion, the takeaway restated with the specific
   detail, or a real invitation. Not "that's it!", not a follow-beg, and not
   trailing off because the material ran out
5. **Front-load.** The strongest three beats go first. Anyone who leaves at post
   four should still have got the value
6. **4–7 beats is the working range.** Under 4, it's a post. Over ~8, read-through
   collapses and you're writing an article that belongs on the blog with a link

**Numbering:** only when the thread has 3+ posts, and only if it helps —
`1/`, `2/`. For two posts, skip it; the reply carries the continuation visually.
Numbering a 2-post thread reads as ceremony.

**Voice is unchanged.** Same `inputs/best/` voice, same anti-slop pass
(`references/anti-slop-writing.md`) — run it over the whole thread at once, not
post by post, so repetition across beats shows up.

## Splitting something long into a thread

When you have a long draft (an article section, a written answer) rather than a
thread written as one:

1. **Count characters, not words.** URLs count as their full typed length in the
   composer even though the platform shortens them server-side
2. **Target ~270 characters** against a 280 limit — headroom for numbering and
   off-by-one rejections
3. **Break on sentence or paragraph boundaries first**, then clauses (`, ` `; `
   ` — `), then words. Never mid-word
4. **Never straddle a URL, an @handle or a code block** across two posts — move
   the whole token to the next one
5. **Rewrite the first post.** The original opening was written to be read with
   the rest visible; as a standalone hook it almost never works unedited

**Assume a free account: 280 characters.** Premium allows far more in a single
post, but the connected session may not be Premium, and an over-length caption
gets silently truncated or rejected. Split by default; only ask when the user
explicitly wants one oversized post.

---

# Part 2 — posting on X from the browser

The user's own logged-in browser, driven by a browser MCP (Claude-in-Chrome or
equivalent). **Do not use the X API** unless the user already has it and asks.
This flow does not log in — the target account must already be signed in.

## Single post

1. **Confirm the session** — open `https://x.com/<handle>` and check it's the
   right account. Posting from the wrong logged-in account is unrecoverable
2. **Open the composer** — the control matching *"compose new post"*
   (`href="/compose/post"`)
3. **Focus the text box** — *"What's happening"* / *"Post text"*
4. **Type the caption.** Multi-line works. Stay ≤280 characters
5. **Optional image** — see below
6. **Click Post**, then confirm the *"Your post was sent"* toast
7. **Record the URL** → `runlog.py publish --run <id> --url <url>`

## Thread

Every post is **staged before publishing** — they ship together, not one at a
time:

1. Type post 1
2. For each remaining post: click **Add post** (`+`) → focus the new empty
   textbox → type
3. Click **Post all** — the label switches from *Post* to *Post all* as soon as
   the first `+` is clicked
4. Confirm the *"Your posts were sent"* toast (plural)

Three things that break agent runs here:

- **Re-find elements between every step.** The DOM changes as posts are staged,
  so a cached reference points at something that no longer exists — including
  the publish button, whose label and identity change after the first `+`
- **The new-textbox query returns the newest empty box.** Re-run it per post
  rather than assuming an index
- **Long threads need a beat between clicks.** At 8+ posts, give the DOM a
  moment after each `+` or the next textbox isn't there yet

## Images and alt text

The composer's file input is typically **blocked** for agent browsers. The
reliable path on macOS is the clipboard: copy the image, click inside the
**composer body** (below the typed text, not on the toolbar), and paste
(`cmd+v`).

Then add alt text — every attached image, every time:

1. Open **Add description**
2. Confirm the prompt if one appears
3. Describe **what is in the image**, not "image" or "screenshot"
4. Save

## LinkedIn — same contract

Logged-in browser, native composer, human approval, record the URL. Don't build
API posting on day one. Draft into the run's output folder, then either hand it
over to paste or drive the UI the same way.

LinkedIn threads aren't a native format — a long LinkedIn post is one post, and
the "…see more" break replaces the first-post job described above. The writing
rules still apply to the opening two lines, which is all anyone sees before
clicking.

## The boundary

**Nothing publishes without the user's yes.** A logged-in browser is not
consent, and neither is a queued draft. Ask per post, then record the URL so
`engine-loop` can fetch the number later.

---

## Going further

`benyki/skills/x-browser-post` is the full operational skill, worth installing
if you post to X often. It adds what's deliberately not duplicated here: a
frozen element map with fallback queries for every control, the clipboard-paste
image script, the staged-thread loop as runnable pseudocode, and a quirks file
covering what fails and why (including why it never logs in).

For Bluesky, `references/bluesky-post.md` — its API posts chains natively, so
none of the browser mechanics above apply.

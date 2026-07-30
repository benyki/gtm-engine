# X via browser — single post, thread, alt text

LinkedIn and X: the user (or the agent driving their logged-in browser) posts.
This is the X checklist. Do **not** use the X API unless the user already has it
and asks for it.

Prerequisites: browser MCP / Claude-in-Chrome (or equivalent) connected; target
account **already signed in**. This flow does not log in.

## Single post

1. Confirm session — open `https://x.com/<handle>`
2. Open composer — control matching “compose new post” / `href="/compose/post"`
3. Focus the tweet textbox (“What’s happening” / “Post text”)
4. Type the caption (newlines ok). Stay ≤ **280 characters** on free accounts
5. Optional image — see Alt text / images below
6. Click **Post**
7. Confirm the “Your post was sent” toast
8. Copy the post URL → `runlog.py publish --run … --url …`

## Thread

If text is longer than ~280 chars, **split into a thread** (don’t ask first unless
they explicitly want one oversized Premium post).

Splitting:

1. Count characters (URLs count as typed length in the composer)
2. Target ~270 chars/post for headroom
3. Break on sentence → clause → word; never mid-word, mid-URL, or mid-@handle
4. First post is the hook — rewrite so it stands alone
5. Number `1/N`, `2/N` only when N ≥ 3

Staging:

1. Type post 1
2. For each remaining post: **Add post** (`+`) → focus the new empty textbox → type
3. Click **Post all** (label switches from Post → Post all after the first `+`)
4. Re-find elements between steps — don’t cache refs across DOM changes

## Images + alt text

File-upload inputs are often blocked in agent browsers. Reliable path on macOS:
copy image to clipboard, click in the **composer body** (not the toolbar), paste
(`cmd+v`).

Then:

1. Open **Add description** (alt)
2. Confirm the prompt if shown
3. Write real alt text (what’s in the image, not “image” / “screenshot”)
4. Save

Every attached image needs alt text before publish.

## LinkedIn (same idea)

Same contract: logged-in browser, human approval, then record URL.
Use LinkedIn’s native composer in the connected browser; don’t invent API posting
on day one. Draft in the run output; paste or drive the UI; `runlog.py publish`.

## Optional full skill

`benyki/skills/x-browser-post` — element maps, image clipboard script, quirks.

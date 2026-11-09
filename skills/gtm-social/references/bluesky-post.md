# Bluesky — AT Protocol post (after approval)

Agent may post **only after** an explicit per-post yes. App password, never the
account password.

## Credentials

- Create: bsky.app → Settings → Privacy and Security → **App Passwords**
  (`xxxx-xxxx-xxxx-xxxx`)
- Keys come from the project's own env setup: add `BSKY_HANDLE` /
  `BSKY_APP_PASSWORD` to its `.env.example` (or `BSKY_ACCOUNT_<NAME>_HANDLE` /
  `_APP_PASSWORD` for multi-account), and the user pastes the values into the
  project's `.env` themselves
- Load at run time the way the project loads its env; never read `.env` into
  chat; never commit

```bash
set -a; . "$(git rev-parse --show-toplevel)/.env"; set +a   # a root .env
```

## Constraints

- **300 graphemes** max per post (thread for longer)
- Up to **4 images**, ~1 MB each — **alt text on every image**
- Mentions / links / hashtags need facets — use `RichText.detectFacets()`, don’t
  hand-compute byte offsets

## Minimal post (Node 18+)

```bash
npm install @atproto/api   # once, in a scratch dir or the project
```

```js
import { AtpAgent, RichText } from "@atproto/api";

const agent = new AtpAgent({ service: "https://bsky.social" });
await agent.login({
  identifier: process.env.BSKY_HANDLE,
  password: process.env.BSKY_APP_PASSWORD,
});

const rt = new RichText({ text: process.argv[2] });
await rt.detectFacets(agent);

const res = await agent.post({
  text: rt.text,
  facets: rt.facets,
  createdAt: new Date().toISOString(),
});
console.log(res.uri);
```

Public post URL shape (approx):
`https://bsky.app/profile/<handle>/post/<rkey>` — derive from the returned
`uri` / CID, or open the profile and copy the link after posting.

Then add the row to `log.csv` with that URL.

Results: likes/reposts/replies via the API, into the row's `result`. Bluesky
settles faster than LinkedIn/X; a day or two is often enough.

## Optional full skill

`benyki/gtm-skills/bluesky-post-manage` — threads, images, multi-account, delete,
timeline. Prefer it when installed.

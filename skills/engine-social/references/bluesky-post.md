# Bluesky — AT Protocol post (after approval)

Agent may post **only after** an explicit per-post yes. App password, never the
account password.

## Credentials

- Create: bsky.app → Settings → Privacy and Security → **App Passwords**
  (`xxxx-xxxx-xxxx-xxxx`)
- Store in home `shared/.env` as `BSKY_HANDLE` / `BSKY_APP_PASSWORD`
  (or `BSKY_ACCOUNT_<NAME>_HANDLE` / `_APP_PASSWORD` for multi-account)
- Source at run time; never read `.env` into chat; never commit

```bash
set -a; . ~/gtm/shared/.env; set +a
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

Then:

```bash
python3 ~/.agents/skills/engine-loop/scripts/runlog.py publish \
  --run <run_id> --url https://bsky.app/profile/...
```

Metrics: likes/reposts/replies via API → `runlog.py metric … --source api`.
Shorter `metric_delay_hours` than LinkedIn/X is often fine.

## Optional full skill

`benyki/skills/bluesky-post-manage` — threads, images, multi-account, delete,
timeline. Prefer it when installed.

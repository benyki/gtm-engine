# images/ : your images, for posts that want one

Drop files in here. Your agent reads this folder and **never writes to it**.

What earns its place, best first:

- **screenshots of the actual thing** : the feature, the dashboard, the error
  you fixed, the run log
- **charts from your own numbers** : exported, not redrawn
- **photos you took** : the office, the talk, the whiteboard, the product
- product shots, and the logo if you post it often

Rough naming helps the agent pick well: `dashboard-signups-jul.png` beats
`Screenshot 2026-07-31 at 14.22.png`. Anything reused by *every* engine (the
logo, a house background) belongs in `shared/assets/` instead.

**Before you drop something in, look at what's in the frame** : customer names,
real revenue, an inbox, a browser tab bar. Your agent flags what it spots, but
it's your screen.

Empty is fine. A text-only post is not a worse post.

## Editing one

Optional, and it costs money per image: the agent can send an image from here
to Gemini ("nano banana") or OpenAI to crop it, swap a background, or make
aspect-ratio variants. Add `GEMINI_API_KEY` or `OPENAI_API_KEY` to
`shared/.env` first : keys from
[aistudio.google.com/apikey](https://aistudio.google.com/apikey) or
[platform.openai.com/api-keys](https://platform.openai.com/api-keys).

Edits are written to `runs/<run_id>/output/`, so your originals stay as they
are. Nothing that functions as proof : a metrics screenshot, a revenue chart :
gets generated: if the number is real, screenshot the real thing.

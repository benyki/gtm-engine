# <workflow name>

<One line: what this workflow posts, on which channel, from which account, for
whom.>

**The number:** <profile visits or link clicks a week, or signups from posts>

## Run it

Ask your agent to run this workflow with the `gtm-social` skill, for example
"draft this week's posts in workflows/<name>".

## Schedule

Manual.

<!-- Once scheduled, replace "Manual." with:
When: <every weekday at 08:00>
Where: <the scheduler this project uses>
Prompt: "<the exact prompt the task runs>"
-->

## Files

| Path | What | In git |
|---|---|---|
| `brand.md` | voice notes, only when the project has none of its own | yes |
| `inputs/best/` | your own posts that did well | yes |
| `inputs/swipe/` | posts by others you wish you'd written | no: not yours |
| `inputs/images/` | your screenshots and photos; the agent reads them, never edits them | no: heavy |
| `inputs/backlog.csv` | subjects, scored | yes |
| `templates/` | post templates; `templates/blocks/` holds the parts that rotate | yes |
| `posts/` | one dated file per batch of drafts, edited images next to it | text yes, images no |
| `log.csv` | one row per shipped post | yes |

## Keys

Names only. The values live in the project's own env setup (`.env.example`
lists the names); you paste them in yourself.

- `BSKY_HANDLE`, `BSKY_APP_PASSWORD`: Bluesky only, an app password
- `GEMINI_API_KEY` or `OPENAI_API_KEY`: image edits only

## Sources

- **Subreddits:** none yet. The agent finds where the audience actually posts;
  list them here once you know
- **RSS feeds:** none yet. Ten to fifteen: trade press, the newsletters you
  actually read, competitor blogs, release notes from tools your audience uses,
  a subreddit's `.rss`. Built with the agent the first time the daily twelve
  runs
- **Rating criteria:** none yet. What makes a subject worth posting for you, in
  your words. Until then the agent uses the 0 to 9 score (attention, proof,
  proximity) and says so

## What we learned

<!-- One line per clear win or loss: the date, what it tried, what happened. -->

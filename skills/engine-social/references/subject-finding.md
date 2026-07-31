# Subject finding — twenty things worth posting

`SKILL.md` says *posts come from the queue, their own material, an article, or
a real question*. This is how you keep twenty of them ready, so no writing
session ever starts with "what should we post about today".

Run it weekly. The output is `inputs/backlog.csv`; the writing run takes the
top rows and drafts a batch.

Scoped to this workflow. `engine-seo` has its own version — same shape, but it
mines for search demand and this one mines for feed attention. Don't merge
them: an article subject and a post subject are validated against different
evidence, and the two workflows have to be able to change independently.

The loop:

```
sources → collect → validate on the platform → score → kill the weak → multiply
```

---

## 1. Where subjects come from

Ranked by what actually performs. The first two beat the rest by a distance,
and they're the two people skip because they feel too obvious.

**1. What they did this week.** A feature they shipped, a bug that taught them
something, a decision and the reasoning, a number they can share, a customer
conversation, something they changed their mind about. This is the only source
nobody else has, and it's why the founder account outperforms the brand
account.

**2. The queue** — `inputs/queue/`, written by `engine-loop` from what already
performed. When it isn't empty, start here.

**3. Their own published work.** One `engine-seo` article is three or four
posts: the counterintuitive claim, the specific example, the number, the
objection it answers. Check the seo workflow's `reports/latest.json` for which
articles earned something before mining them.

**4. Questions the audience actually asks.** Replies to their posts, support
threads, sales objections, the same Reddit mining `engine-seo` does — but read
for *phrasing and friction*, not for search volume.

**5. What's moving in the niche right now.** A launch, a price change, a bad
take with traction. Timely posts decay fast, so cap this: one or two rows in
the backlog at a time, never a strategy on its own.

## 2. Collect

For each source, write down **the claim, not the topic**. "Onboarding" is a
topic and it will produce a vague post. "We deleted the onboarding tour and
activation went up" is a claim, and the post writes itself.

Every row needs three things or it isn't ready:

- **The claim** — one sentence, arguable, specific
- **The proof** — the number, the screenshot, the story, the named example.
  A claim with no proof is an opinion post, and opinion posts need a much
  stronger voice to survive
- **Who it's for** — which slice of the audience nods at it

If you can't fill the proof, the subject isn't dead: it's a *question* to ask
the user, and asking is usually faster than inventing an angle.

## 3. Validate on the platform

Search is a library; a feed is a room. Validation happens where the post will
actually run:

| Check | How | What it tells you |
|---|---|---|
| **Has this landed before?** | Search the platform for the claim, sort by top | If similar posts have real engagement, demand exists. If everything on it is flat, the room doesn't care |
| **Who said it already?** | Read the top few | Same claim from a bigger account, said well = skip, or take the opposite side with evidence |
| **Is there a fight in the replies?** | Open the comments | Disagreement is the strongest signal here. A claim people argue about outperforms one they agree with |
| **Does it fit `inputs/best/`?** | Compare against their own top posts | A subject that doesn't fit their voice will read as borrowed, whatever the demand |

Don't validate with a search-volume tool. Nobody searches for a LinkedIn post.

## 4. Score

Three factors, `0–3` each, summed into `potential` (0–9):

**Attention (0–3)** — will the first line stop a scroll
`0` generic advice · `1` mildly interesting to insiders · `2` specific and
unexpected · `3` a claim people will argue with, or a number nobody else has

**Proof (0–3)** — how concrete the evidence is
`0` opinion only · `1` a plausible story · `2` a named example or real
screenshot · `3` a number from their own work

**Proximity (0–3)** — how close the reader is to being a customer
`0` broad relatable content · `1` adjacent to the problem · `2` the problem the
product solves · `3` the moment someone chooses a solution

High attention with zero proximity is the classic trap: the post that gets 200
likes and no signups. Post those deliberately and sparingly, not by accident —
and note in `notes` that that's what you're doing.

## 5. Kill the weak

- **`potential < 5` → `status=killed`**, score kept in the row
- **No proof and no way to get it** → killed. Don't upgrade an opinion into a
  fake anecdote; that's the one mistake in this workflow that's unrecoverable
- **Timely rows expire.** Anything tied to a moment gets a kill date in
  `notes`; if it's still sitting there next week, it's gone
- **Two rows making the same claim** → keep the one with better proof
- **Anything that reads as a competitor's post rephrased** → killed

Killed rows stay in the file, so the same weak idea doesn't come back in a
month wearing a new title.

**The bar: ≥20 rows at `status=validated`.** Short-form burns through subjects
— a batch is five to seven posts — so a thin backlog shows up as generic
content within two weeks.

## 6. Multiply what worked

When a post performs, it has told you something about the *format or the
claim*, and both are reusable:

- **Same claim, new proof.** The point landed; give it a different example next
  month. This is not repetition — it's the only way a position becomes known
- **Same format, new claim.** If the "we deleted X and Y improved" shape works,
  it will work for the next three things they deleted
- **Zoom in.** One line from a post that got replies is a whole post. The
  replies themselves are subjects
- **Cross-post the finding, not the post.** A hook that wins here usually says
  something about the video hook — that belongs in `shared/insights.md`, not in
  a copy-paste to another channel

Variants enter the backlog as ordinary rows with `source=variant-of` and the
parent `run_id`, and get scored like anything else. Multiply winners only;
multiplying a guess just gives you five guesses.

## The output

```csv
title,claim,source,source_url,proof,audience,attention,proof_score,proximity,potential,status,validated_at,parent_run_id,notes
```

| Column | |
|---|---|
| `title` | working label, for finding the row later |
| `claim` | the arguable sentence. The durable part |
| `source` | `own-material` · `queue` · `article` · `audience-question` · `niche-news` · `variant-of` |
| `source_url` | the thread, the article, the run. Empty only for their own material |
| `proof` | the number, example or story that backs it |
| `audience` | which slice nods at it |
| `attention` `proof_score` `proximity` | 0–3 each, per §4 |
| `potential` | their sum, 0–9 |
| `status` | `candidate` → `validated` → `queued` → `drafted` → `published` · or `killed` |
| `validated_at` | ISO date. Timely rows also carry a kill date in `notes` |
| `parent_run_id` | for variants, the post that earned them |
| `notes` | the angle, the format, or "reach play, low proximity — on purpose" |

Add columns freely. Nothing parses this file but you and the next agent.

## Weekly, in order

1. Expire the timely rows that didn't get used
2. Ask the user what happened this week — the single highest-yield step here
3. Mine the queue, the seo reports and the replies for anything new
4. Score, kill everything under 5
5. Multiply any post whose numbers justify it
6. Confirm ≥20 validated rows, then move the top ones into `inputs/queue/`

Automating it: `engine-loop/references/scheduling.md`. It needs the user's
logged-in browser, so it's an agent job.

## Rules

- **Never invent proof.** No fabricated anecdotes, no numbers the user didn't
  give you. One invented story is unrecoverable on a personal account
- **Never post a claim the user hasn't actually made.** When in doubt, ask
- **Never validate short-form with search volume.** Wrong room
- **Score before you fall for a hook.** A great first line makes a hollow
  subject feel like a good one
- Read `shared/insights.md` and the sibling workflows' `reports/latest.json`
  before mining — an objection that keeps coming back in outreach replies is a
  validated subject you got for free

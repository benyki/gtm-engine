# Writing — cut AI slop, keep their voice

Run this over every draft before the user sees a batch. Voice still comes from
`inputs/best/` first; this only removes patterns that make copy sound generic.

## Mode

- **Edit (default):** minimum changes; return the draft
- **Detect:** name each pattern + quote the line; don’t rewrite unless asked

## Preserve

Vocabulary, cadence, bluntness, humor, uncertainty, digressions from
`inputs/best/`. Don’t make every post equally tidy. Don’t invent claims, stats,
or anecdotes the user didn’t provide.

## Cut these words

delve, foster, leverage, utilize, facilitate, empower, streamline, robust,
cutting-edge, paradigm shift, game changer, tapestry, realm, beacon,
multifaceted, meticulous, intricate, paramount, transformative, elevate,
embark, supercharge, harness, ever-evolving.

Empty openers/phrases: “here's the thing,” “let me be clear,” “in today's
world,” “at the end of the day,” “it's worth noting,” “let's dive in.”

## Cut these patterns

| Pattern | Fix |
|---|---|
| “Not X — it's Y” / “The question isn't X” | State Y |
| “What nobody tells you” / “the part everyone misses” | State the claim |
| Colon reveal (“The best part: it learns”) | Plain sentence |
| Trailing “highlighting/underscoring/showcasing…” | Say the concrete effect |
| “Experts agree” / “studies show” | Name the source or cut |
| “In conclusion” / mic-drop metaphor kicker | End on the last concrete line |
| Engagement bait (“Agree?”, fake vulnerability) | Delete |
| Synonym cycling for style | Repeat the clear word |

## Short-form extras (LinkedIn / X / Bluesky)

- First line is the only line most people read — no throat-clearing
- One idea per post
- Match formatting in `inputs/best/` (line breaks, length, punctuation)
- Specific > clever: a real number or named moment beats a polished abstraction

## Before ship

If a sentence could appear on any brand's account after swapping the product
name, rewrite it from `inputs/best/` or cut it.

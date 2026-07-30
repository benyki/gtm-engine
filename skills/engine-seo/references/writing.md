# Writing — cut AI slop, keep their voice (articles)

Run this over every draft before the user reviews. Voice still comes from
`inputs/best/` first; this only removes patterns that make long-form sound
generic.

## Mode

- **Edit (default):** minimum changes; return the draft
- **Detect:** name each pattern + quote the line; don’t rewrite unless asked

## Preserve

Vocabulary, cadence, bluntness, humor, uncertainty, digressions from
`inputs/best/`. Don’t make every section equally tidy. Don’t invent claims,
stats, quotes, or studies — name a source or cut the claim.

## Cut these words

delve, foster, leverage, utilize, facilitate, empower, streamline, robust,
cutting-edge, paradigm shift, game changer, tapestry, realm, beacon,
multifaceted, meticulous, intricate, paramount, transformative, elevate,
embark, supercharge, harness, ever-evolving.

Empty openers/phrases: “here's the thing,” “let me be clear,” “in today's
world,” “in this article,” “at the end of the day,” “it's worth noting,”
“let's dive in,” “when it comes to.”

## Cut these patterns

| Pattern | Fix |
|---|---|
| “Not X — it's Y” / “The question isn't X” | State Y |
| “What nobody tells you” / “the part everyone misses” | State the claim |
| Colon reveal (“The best part: it learns”) | Plain sentence |
| Trailing “highlighting/underscoring/showcasing…” | Say the concrete effect |
| “Experts agree” / “studies show” | Name the source or cut |
| “In conclusion” / “Ultimately” / summary-recap ending | End on the last concrete point or next action |
| Throat-clearing intro that restates the title | Answer in the first hundred words |
| Synonym cycling for style | Repeat the clear word |
| Emoji headings / bold sprinkled mid-sentence | Format follows content |

## Long-form extras (articles / landing pages)

- Answer the question in the first hundred words
- Specifics over hedging: real numbers, named products, real mechanisms
- Active voice with human subjects — “The team shipped it Tuesday” beats
  “the decision emerged”
- Every sentence earns its place; cut empty qualifiers
- Keep edge and opinion from `inputs/best/` — don’t sand it into safe prose
- Respect banned words and claims in `shared/brand.md`

## Before ship

If a paragraph could appear on any competitor’s blog after swapping the product
name, rewrite it from `inputs/best/` or cut it.

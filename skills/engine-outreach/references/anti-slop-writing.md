# Anti-slop writing — cut the patterns, keep their voice (cold email)

Run this over **every draft, every run**, before the user sees it. Not only over
the template when it's first written — a template can be clean and forty
rendered emails still read like a robot, because the slop arrives in the parts
you filled in per person.

This is the **short version, tuned for email**. The full editor lives in
`benyki/skills/no-ai-slop-writting` (complete banned-word list, ~20 named
patterns with worked rewrites, a detect mode, an eval set). If it isn't
installed, install it and use it instead of this page — it's one download and
it's better:

```bash
mkdir -p ~/.agents/skills
TMP=$(mktemp -d)
git clone --depth 1 --filter=blob:none --sparse https://github.com/benyki/skills.git "$TMP"
git -C "$TMP" sparse-checkout set no-ai-slop-writting
rm -rf ~/.agents/skills/no-ai-slop-writting
mv "$TMP/no-ai-slop-writting" ~/.agents/skills/no-ai-slop-writting && rm -rf "$TMP"
[ -d ~/.claude/skills ] && ln -sfn ~/.agents/skills/no-ai-slop-writting ~/.claude/skills/no-ai-slop-writting
```

Full install pattern, including the other agent folders:
[`docs/additional-skills.md`](../../../docs/additional-skills.md).

## Mode

- **Edit (default):** minimum changes; return the draft
- **Detect:** name each pattern + quote the line; don't rewrite unless asked

## Preserve

The user's vocabulary, bluntness, humour and register — from the template they
approved and from `shared/brand.md`. A cold email that has been sanded smooth
is worse than one with edges: smooth is what everyone else sends.

## The openers that get deleted unread

Cold email has its own slop, and it's concentrated in the first line — the one
part that shows in the preview pane:

| Cut | Why |
|---|---|
| "I hope this email finds you well" | the single most-deleted sentence in B2B |
| "I'm reaching out because…" / "Just wanted to…" | says nothing; the email starts after it |
| "I came across your profile and was impressed by…" | reads as mail-merge flattery, because it usually is |
| "Quick question" as a subject when it isn't one | the oldest trick; everyone knows it |
| "I'll keep this brief" / "I know you're busy" | be brief instead of announcing it |
| "Hope you don't mind me reaching out" | apologising for the email you chose to send |
| "circle back", "touch base", "leverage", "solutions", "synergies", "game-changing" | filler that survives from a different company's email unchanged |

## Cut these words

delve, foster, leverage, utilize, facilitate, empower, streamline, robust,
cutting-edge, paradigm shift, game changer, seamless, transformative, elevate,
supercharge, harness, unlock, ever-evolving, best-in-class, holistic.

## Cut these patterns

| Pattern | Fix |
|---|---|
| "Not X — it's Y" | State Y |
| Colon reveal ("The best part: it learns") | Plain sentence |
| Three-adjective stacking ("fast, reliable and scalable") | Pick the one that's true and specific |
| Trailing "…, helping you scale/streamline/unlock" | Say the concrete effect, or cut |
| A compliment with no object ("love what you're building") | Name the thing, or drop the line |
| Rhetorical question opener ("Ever wondered why…?") | Make the claim |
| "Let me know if you'd like to learn more" | One small, concrete ask |
| Signature with six links and a banner | Name, one line, one link |

## The email-specific tests

Four checks, in this order. Any failure is a rewrite, not a tweak:

1. **The swap test.** Could this email be sent to a different person on the list
   by changing the name? Then the personalisation is a merge field and the first
   line has to be rewritten from `research`
2. **The competitor test.** Could a competitor send this same email with their
   product name in it? Then it says nothing specific about what the user does
3. **The read-aloud test.** Read it out. Anywhere you stumble or hear a phrase
   you'd never say to someone at a bar is a line to cut
4. **The reply test.** Is the ask small enough to answer in one sentence, on a
   phone, without opening a calendar? "Worth a look?" gets replies; "do you have
   30 minutes on Thursday?" doesn't

## Before it becomes a draft

Under 120 words. One link, as an anchor, never a bare URL
(`references/first-touch.md` → §2). No tracking pixel. If the observation in the
first line isn't something you could quote back with a source URL, it doesn't go
in the email at all — `references/first-touch.md` has what to do instead.

# Hook and overlay copy — what the text actually says

Three files decide the text on screen and they don't overlap:

| File | Decides |
|---|---|
| `references/structure-plan.md` | **where** it goes — which segment, how long it holds |
| **this file** | **what it says** — the wording, the tone, the punctuation |
| `references/ffmpeg-text-style.md` | **how it looks** — font, size, position |

The copy this file governs ends up in exactly one place: `runs/<run_id>/inputs.json`
→ `segments[].textOverlay.lines`. Write it here, not in the render command.

Applies to every overlay in a video, with a stricter set of rules for the first
one. Everything below assumes short-form vertical — TikTok, Reels, Shorts —
watched muted, at speed, by someone who has not decided to watch anything yet.

## 1. Core philosophy

Five principles apply to every overlay, hook or not:

- **One idea per screen.** If two ideas are fighting for the same overlay, split them or cut one.
- **Visual + text must match the same moment.** Overlays should comment on what's on screen, not describe an unrelated benefit.
- **Readable on first scan.** People watch with sound off, in bed, at 0.7x attention. If they have to reread, the line has already failed.
- **Emotionally clear, even when playful.** Meme phrasing is fine. Confusing phrasing is not.
- **Native-feeling, not translated.** The line should sound like something a real person in that language would caption their own video with.

## 2. The hook (first overlay)

The hook is the scroll-stopper. Its only job is to create curiosity, tension,
identification, or payoff fast enough that the viewer stays for the second beat.

It is also **the A/B variable** for this engine — question versus claim, face
versus text, first-second payoff versus slow build. Hold everything else
constant across arms or the verdict means nothing (`references/formats.md`,
`engine-loop/references/ab-testing.md`).

### Hard rules

- Communicate **one sharp idea**, not a feature list.
- Be understandable from the first two lines alone.
- Start from a **moment, problem, or reaction** before explaining anything.
- Sound like a native caption or meme, **not a translated slogan**.
- If the clip is event-driven, name the event or situation early.
- Slang only if it sounds natural in that language.
- A hook can be chaotic, but the **payoff must still land clearly**.

### Hook priorities (ranked by typical performance)

**Highest priority**

1. **Concrete scene + social curiosity** — a specific place or moment combined with a question about what other people are doing, listening to, watching, etc.
2. **Chaos prevention / utility payoff** — naming a friction point that the viewer already fears (losing people in a crowd, missing a deadline, getting lost) and implying it's solved.

**Medium priority**

3. **Competitive or behavioral switch** — borrowing attention from an existing habit, app, or behavior and reframing the new option as the upgrade.
4. **Identity / obsession bit** — leaning into a character trait or fandom-style behavior the audience already shares.

This ranking came from consumer social apps. It is a starting order, not a law —
once this engine has 5–10 videos with numbers, the ranking that matters is the
one in your own `runs/`.

### Recommended hook formats

**POV scene-setter** — use when the clip shows a recognizable moment or place.
- Open with `POV:` only if the visual really supports a mini-scene.
- Make the scene hyper-specific, not generic.
- End the hook with the surprise, reveal, or social payoff.
- Templates:
  - `POV: you're in [specific place] and [payoff happens]`
  - `POV: your [person] says [excuse] but [reality]`
  - `POV: [small action] and then [unexpected realization]`

**"me when" confession** — use when the hook is driven by a relatable guilty-pleasure or self-aware behavior.
- Keep it playful and friend-coded.
- Confession beats explanation.
- Never let it tip into creepy or malicious.
- Templates:
  - `me when I realize I can [benefit]`
  - `me when [person] says [thing] but [contradiction]`
  - `me pretending I don't care while [doing the thing]`

**"wdym / wait / hold up" discovery** — use when the clip reveals one strong feature or insight.
- The surprise has to be instantly legible.
- One reveal per hook, not stacked.
- Best when the final line contains the practical benefit.
- Templates:
  - `wdym I can [benefit] at [situation]`
  - `wait so I can [benefit] without [usual pain]`
  - `hold up, [thing A] and [thing B] in one place?`

**Direct-address PSA** — use for seasonal, event-based, or advice-shaped clips.
- Speak to the viewer directly.
- Anchor in a real situation, not generic talk.
- Make it sound saveable or shareable.
- Templates:
  - `if you're going to [event], do this first`
  - `before you [action], set this up`
  - `quick PSA: [mistake] + [fix]`

**Minimalist punchline** — use only when the visual already tells the story.
- The shorter the line, the stronger the visual must be.
- Treat as a verdict, chant, or ironic punchline.
- Never use this for a new or complex concept.
- Templates:
  - `[one word].`
  - `[short chant]`
  - `[dramatic reaction caption]`

### Hook structure

- **Lines:** 1–3
- **Words:** 3–12
- Break **before** the payoff line.
- Let the **final line** carry the benefit, reveal, or joke.
- Don't split names or key nouns across lines.
- If the hook needs rereading to make sense, simplify it.

The hook segment is ≤ 5s (`references/structure-plan.md`). Three lines of twelve
words do not fit in four seconds — count the words against the duration before
you render, not after.

## 3. General overlay rules (all clips)

### Line structure

- Follow the structure of the example line you're working from. Don't reshape it.
- Surprise, reveal, or payoff goes on the **last line** when there is one.

### Length

- **Words per overlay:** 4–14
- **Words per line:** 1–7
- **Max ideas per overlay:** 2
- Denser copy is allowed only when the visual is simple and the phrasing is naturally easy to read.

These are editorial limits. `references/ffmpeg-text-style.md` has a separate
mechanical reflow limit per script (30 chars/line Latin, 13 CJK) — staying inside
the word counts here keeps you well clear of it.

### Capitalization

- Match what feels native on the platform in the target language.
- **Lowercase the whole line by default**, including the first letter.
- Use ALL CAPS only for deliberate hype, warnings, or punchline emphasis.
- If the reference text has a word in all caps, keep it in caps.

### Punctuation and symbols

- **No commas, periods, or hyphens.**
- Allowed: `?`, `!`, and `:` for dry short setups.
- Ellipses (`...`) are fine when they help the rhythm.
- **No emoji by default** — only include emoji if the reference text already has one.

### Tone families

Pick the family that fits the clip, then write within it.

- **Playful confessional** — the line admits something mildly nosy, obsessive, or embarrassing in a cute way.
- **High-energy hype** — there's a strong reveal, surprise, update, or event payoff.
- **Utility lifesaver** — the scenario has real friction (festivals, travel, deadlines, getting lost).
- **Competitive flex** — contrasting the new behavior with an old habit or competitor.
- **Minimalist absurdist** — visual carries the story, text is seasoning.

Whichever family you pick, the voice constraints in `shared/brand.md` still win.

### Generic overlay patterns

Each shows the *shape*, not the wording:

- **Social curiosity** — `at [specific place]` / `checking what everyone [is doing]`
- **Chaos prevention** — `going to [event]` / `and NOT [bad outcome]`
- **Gamified progress** — `not [normal reason]` / `[real, sillier reason]`
- **Reassurance** — `[obstacle]` / `but [tool/habit] keeps us [state]`

## 4. Tone — what to avoid

- Corporate or polished brand-copy voice.
- Literal translations of US slang into another language.
- Overexplaining the feature list in one overlay.
- Fear-based, controlling, or surveillance-flavored phrasing.
- Generic motivational tone that could fit any product.

## 5. Localization

The job of localization is **transcreation**, not translation.

- Preserve the **emotional job** of the line, even if the literal wording changes.
- Replace culture-specific slang when it feels imported or unnatural.
- Preserve product names, event names, and clearly branded terms exactly.
- If a phrase reads as ad copy in the target language, rewrite it into friend-to-friend phrasing.
- Keep the same overlay count and order as the source.
- Apply the hook rules specifically to the first overlay.

A localized cut is **a different video, not a different arm**. It gets its own
run and its own row — never fold two languages into one A/B verdict.

### Language-by-language posture

Written from real posting in these markets. A language missing here isn't a
language to avoid; it's one nobody has learned the posture for yet — add it once
you have.

**English**
- Lowercase often beats sentence case.
- Short slangy setups work if the line still reads instantly.
- Surprise openers (`wait`, `hold up`, `wdym`) only when the payoff is genuinely clear.

**Italian**
- Use spoken disbelief, social drama, and strong scene-setting.
- Questions and reactions usually land harder than literal feature explanations.
- Don't force English meme words when a natural Italian reaction is stronger.

**Brazilian Portuguese**
- Stay warm, colloquial, friend-group-coded.
- Playful, slightly dramatic setups outperform direct translation.
- Avoid anything that sounds like a product explainer.

**Romanian**
- Expressive reactions and hype punctuation work when they still feel native.
- Update reveals, school/campus context, and social curiosity perform well.
- Hype is welcome, but the payoff still needs to be readable.

**Vietnamese**
- Emotion-first hooks (reassurance, teasing, closeness) land well.
- Modern, natural syntax beats anything that mirrors English structure.
- Slightly longer lines are okay when the rhythm sounds like a real caption.

**Polish**
- Short, punchy, lightly ironic lines tend to win.
- Meme energy is welcome when the wording stays native.
- Use absurd or emphatic phrasing sparingly, only for standout moments.

**Ukrainian**
- Keep phrasing confessional and conversational.
- Soft drama beats stiff explanatory wording.
- Preserve emotional clarity even when the sentence is casual or fragmented.

Non-Latin scripts need a font that covers them — `references/ffmpeg-text-style.md`
→ *Rules*. libass substitutes silently, so a Hebrew or Thai overlay that renders
"fine" without a Noto face in the fonts dir is not fine.

### Localization verification pass

Before accepting localized text, check:

1. Every line is in the correct local language.
2. Every line sounds natural to locals.
3. Source meaning and tone are preserved.
4. Brand tokens and event names remain exact.
5. The first overlay still follows the hook rules and hasn't drifted into a different angle.

If any check fails, reject the localized array and regenerate the full array in
one pass, keeping the exact same length and order.

## 6. Hard don'ts

- Don't capitalize the first letter of the line. Caps only follow the reference text.
- No commas, periods, or hyphens. Only `?`, `!`, and `:`.
- Don't open with a generic product claim (`best app ever`, `the only tool you need`, etc.).
- Don't explain multiple features in one overlay.
- Don't carry slang across languages literally.
- Don't make the line sound creepy, controlling, or invasive.
- Don't use a minimalist hook when the visual is ambiguous.
- Don't invent claims, features, CTAs, or angles that weren't in the source.
- Don't change overlay count or order during localization.

## 7. Quick checklist

Before shipping any overlay:

- [ ] One idea per screen
- [ ] Matches the visual moment
- [ ] Readable on first scan
- [ ] Within 4–14 words (overlay), 1–7 words (line)
- [ ] Lowercase by default
- [ ] Only `?`, `!`, `:` for punctuation
- [ ] Sounds like a real caption in the target language
- [ ] If it's the first overlay: passes the hook rules too
- [ ] Words fit the segment duration

## Keeping this current

This file is the *default*. What earned watch-through on your account beats it.

- The weekly `engine-video-app-hooks` job reads the numbers and rewrites the
  engine's own hook library from them (`docs/scheduling.md`)
- A hook finding that outlives this engine — a length, an angle, an audience
  truth — goes in `shared/insights.md`, because the social engine is writing
  first lines against the same audience
- When a rule here is contradicted by your own numbers twice, change the rule

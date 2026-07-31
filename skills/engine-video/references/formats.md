# The three formats this workflow makes

Short-form is not one thing. This workflow ships **three** default formats, and
picking the wrong one is the most expensive mistake available — a demo cut like a
vibe video sells nothing, and a vibe video cut like a demo gets scrolled.

| | **Viral product** | **Viral vibe** | **Informative** |
|---|---|---|---|
| Job | show the thing working | make someone feel something, brand adjacent | teach something worth saving |
| Length | ~16s — 4s hook + ~12s demo | ~8–15s, one clip | 30–60s, as long as the content needs |
| Footage | hook clip + real screen recordings | one meditative clip, no cuts | b-roll per beat, or a rendered template |
| Voiceover | usually none | never | **yes** — ElevenLabs, the spine of the video |
| Music | **50%** | **50%** | **3%** (optional) |
| Product | the whole point | one subtle mention, or only in the caption | in the outro / CTA |
| Metric to watch | signups, watch-through | reach, saves | watch-through, follows |

**The music rule underneath the numbers:** 50% is a *no-voice* level — the bed is
carrying the video. The moment a voiceover exists it drops to ~3%, because
anything louder fights the voice and the platform's loudness normalisation makes
it worse. If you add a VO to a product video, drop the bed to 3% too.

Worked examples, ready to copy: `examples/` in this skill. Each is a real
config, generalised — every project-specific value replaced with a placeholder
that says what belongs there.

---

## These are proven starts, not the ceiling

All three have earned real views for real products — which is the only reason
they're the defaults. It is **not** a claim that they're right for you.

Audiences differ more than formats do. The same 4s hook that sells a consumer
app dies in front of a B2B ops audience; a vibe video that works for a calm,
aesthetic product looks evasive in front of people who want the spec sheet. A
format is a bet about what a specific audience will stop for, and yours hasn't
voted yet.

So the honest instruction is: **start from one of these because it saves you the
first ten failures, then let your numbers move you off it.**

**Tweaking is expected.** Change the hook length, the number of cuts, the music
level, the reveal timing, whether the product appears at second 4 or second 12.
Every value in the examples is a starting point someone else's audience agreed
with. The only discipline is the one the loop needs: **change one thing per
experiment**, or the verdict tells you nothing about which change did it.

**Inventing a fourth format is encouraged, not a deviation.** Talking head,
green-screen reaction, before/after, carousel-of-stills, POV, split-screen,
comment-reply, silent-tutorial — none of these are here, and any of them might
be the format your audience actually rewards. If you have a strong instinct
about how your people watch, that instinct is worth more than this table.

How to run a new format without losing the thread:

- **Give it its own workflow folder** (`--merge --workflow video-<name>:video`)
  with its own goal, metric and experiments. Formats aren't arms of each other —
  they have different watch patterns, and pooling them into one folder makes
  every verdict mush
- **Ship five or six before you judge it.** One video tells you about that
  video. Short-form is heavy-tailed, and a format's first attempt is also your
  worst attempt at it
- **Write down what it is** — a `formats.md`-style note in the workflow folder
  saying the structure, the durations, the rules. A format nobody wrote down
  drifts into a different format by run four, and then the numbers span two
  things wearing one name
- **Keep what it teaches.** When a new format wins, the reason usually
  generalises — a hook style, a length, an audience truth. One line in
  `shared/insights.md`, and the other workflows get it too

A format that loses isn't waste either: the reason it lost is information about
your audience, and it belongs in `shared/insights.md` next to the wins.

**One caveat on timing.** Running a new format *because you have an instinct* is
free and encouraged from day one. Running one as a **measured A/B against a
format that's already working** is a different, slower exercise with entry
conditions — chiefly that you freeze the champion while it runs.
`references/advanced.md` → *A/B testing whole formats* has the mechanics. Until
a format is working, the hook is still the variable worth testing.

---

## 1. Viral product — `examples/viral-app-demo.json`

The volume format. One hook, one thing the product does, done.

**Structure**

| Beat | Seconds | What |
|---|---|---|
| Hook | 4 | The scroll-stopper. A face, a result, a question, a mess |
| Demo | ~12 total, 3–4 cuts | The product doing the thing. Real screen recordings |

- **The hook does not show the product.** It earns the next second; the product
  is the payoff, not the opener
- Cut the demo into 3–4 segments of 3–5s. One idea each: the tap, the result,
  the second result. A single 12s take reads as a tutorial
- Screen recordings beat everything else here — `references/clip-sourcing.md`
- The hook is the A/B variable. Hold the demo constant across arms or you're
  testing two things at once

**With a voiceover instead** (the shape the example uses): keep the 4s hook
silent-but-loud, then let the VO carry the demo, burn captions, and drop the
music to 3%. Match the voice to whoever is on screen in the hook — a woman on
screen and a male narrator is the kind of mismatch viewers can't name but do feel.

---

## 2. Viral vibe — `examples/viral-vibe.json`

One clip. One line of text. No cuts, no voice, no CTA on screen.

**Structure**

- **8–15 seconds, a single clip**, slow and meditative. Someone alone, reading,
  walking, working somewhere beautiful. Nothing that moves fast
- **Two text blocks**: the setup and the turn. The turn is where the product
  lives — *subtly*. Name the category the product belongs to, never the product:
  a line ending on what your app is *for* sells it without saying it
- The explicit mention, if you want one, goes **in the caption**, not on screen
- Music at 50% *is* the video. Pick a bed with a clean first note and fade the
  tail 0.5s
- Serif, white, centred, no outline unless the clip is bright. This format is
  quiet — the loud text style from `references/ffmpeg-text-style.md` is the
  wrong instrument here, and that's a deliberate exception, not a drift

**The duration rule that keeps it from breaking**: clip under 8s → loop it once;
8–15s → use as-is; over 15s → trim. Never pad with black or a freeze frame.

**It runs out of clips before it runs out of ideas.** Track which clip each run
used (that's what `inputs.json` is for) and never repeat one — when the folder is
exhausted, generate variations rather than re-using
(`references/duplicate-safety.md`).

---

## 3. Informative — `examples/informative-vocab.json`, `examples/informative-recap.json`

Turn text you have — an article, a dataset, a list, a week of research — into
something watchable. The slowest format to build and the one that compounds:
these get saved and followed.

**Structure**

- **Voiceover is the spine.** Write the script first, let the visuals follow it
- Music at **3%**, or none
- Beats of 4–8s, each with one idea and one on-screen element
- Ends on a follow/CTA line

**Two shapes, two examples:**

**a) Repeatable template** — `examples/informative-vocab.json`. The same
composition every time, new content each run: a prompt, a beat of suspense, a
reveal. Built once as a Remotion or ffmpeg template, then fed configs forever.
This is what you want if the content is a series.

**b) Data recap** — `examples/informative-recap.json`. A weekly or monthly
digest: one config drives the script, the on-screen numbers, the durations and
the footage per scene. Scene *kinds* (counter, bar chart, chips, big number) do
the visual work.

**The rules that make either one good**, learned the expensive way:

- **Never write a comma-list in a voiceover line.** "phones, apps, software, AI"
  is read by TTS as four clipped fragments with the pauses in the wrong places.
  Unfold it into a sentence a person would say aloud. On-screen text can stay
  terse; the spoken line never can
- **One concept per video.** A food video is all food. Mixing themes reads as
  a list of facts, and nobody saves a list of facts
- **The first beat is the hook and it must be the easiest one.** Whatever is
  most instantly recognisable goes first — if beat one makes a casual viewer feel
  behind, they're gone before beat two
- **Match the background to the beat.** Food content over a food scene. A
  mismatched backdrop looks broken even when nobody can say why
- **Never hand-type numbers into a config.** Numbers are only right for one run:
  keep the copy in a tokenised template, the numbers in a vars file derived from
  the source data, and compile the two. A number that's right this week and wrong
  next week is worse than no number
- **Re-author the surprising parts every run.** The template is a scaffold. The
  bit that makes it worth watching — the standout finding, the weird example —
  is written fresh each time by reading the actual content

---

## Which one to start with

**One format until it works.** Three half-built formats produce no verdict on
any of them; the loop needs runs in one place. Product demo if you have an app
and no audience, vibe if you have a look and no product story yet, informative
if you already have written content you're proud of.

Two formats = two workflow folders (`video/` and `video-vibe/`), not one folder
with two kinds of run — they have different metrics, different experiments and
different queues.

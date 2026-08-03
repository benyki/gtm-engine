# Writing the first-touch email

**This repo ships no outreach template, on purpose.** A cold email that works
is made of things only the user knows — what they sell, who they're writing to,
what that industry finds normal, what proof they can point at. A generic
template filled with placeholders produces generic email, and generic email is
what everyone's inbox is already full of.

So the first template is **written for this user, with this user**, and
`assign_arm.py` tells you so: an empty `templates/` folder returns
`action: write_template`. That's the normal first run, not an error.

## 1. Ask them what it has to contain

Before drafting anything, get the non-negotiables out of their head. Ask
directly:

> *"If you had to send this yourself, what are the things this email absolutely
> has to say? And what would make you delete it if you received it?"*

Then push on the parts that are vague:

| Ask | Why it matters |
|---|---|
| **The one sentence of value** — what changes for the recipient | Everything else is packaging |
| **The proof they're allowed to use** — a customer name, a number, a result | Specifics are the only defence against sounding like everyone |
| **The ask** — reply, call, trial, intro? | Decides the whole shape. A big ask needs a different email, not a longer one |
| **What their industry expects** — formal or blunt, first names or not, how long is normal | A perfectly good email in the wrong register reads as an outsider |
| **What must never appear** — claims, competitor names, regulated language | Cheaper to hear now than after 200 sends |

Take the answers into `shared/brand.md` if they're not already there. They're
not outreach-specific — every engine needs them.

## 2. Write it short

The constraints that survive contact with real inboxes:

- **Under 120 words.** It's read on a phone, in a list, with a thumb hovering
  over archive
- **The first line proves you looked.** Not a compliment — an observation. If
  the first line would work for anyone on the list, it's not personalisation,
  it's a mail merge and every recipient can tell
- **The middle is about them.** Their situation, their problem. Not your
  founding story, not your feature list
- **One ask, small enough to answer on a phone.** "Worth a look?" gets replies.
  "Do you have 30 minutes on Thursday?" gets ignored by people who'd have said
  yes to the small version
- **No preamble.** "I hope this finds you well", "I'll keep this brief", "I'm
  reaching out because" — cut all of it, the email starts at the second
  paragraph anyway
- **Plain text.** No images, no tracking pixels, no signature block with six
  links. It should look like a person typed it

Placeholders that stay in the template are fine — `{{FIRST_NAME}}`,
`{{OBSERVATION}}`, `{{OFFER}}` — but never render one empty or half-filled, and
never invent a value to fill one. **Every field on the person is optional; the
email has to survive any of them being blank.** No first name means the greeting
changes ("Hi there", or no greeting at all), not that the row is unusable.
`{{OBSERVATION}}` is the one that carries weight: if a minute of looking turns
up nothing real and recent, don't write filler — cut the line and send the
shorter email, or flag them to the user as a wrong-target candidate. Which of
those two is right is the user's call, not a rule.

### The link — one, and never a bare URL

Most first-touch emails carry at most one link. How it's rendered matters more
than it should:

- **Never put a bare URL in as visible text.** Gmail auto-linkifies it and
  rewrites what the reader sees into `google.com/url?q=…&source=gmail&ust=…`.
  It looks like tracking spam, and it's the reader's first impression of the
  sender
- **Send an anchor instead** — `<a href="https://the.real/url">the actual thing,
  named</a>` in the HTML body, with the raw URL kept in the plain-text part. The
  visible text is a phrase, the `href` is untouched
- **Build it in one place.** A small renderer that takes the lead's row and emits
  `to` / `subject` / `body` / `htmlBody` is worth writing on day one: every draft
  goes through it, so the anchor can't be hand-assembled wrong on run forty.
  It's also where the per-language template lookup and the link constant live
- **One link.** Two links in a cold email is a newsletter

### Opens are noise; clicks are signal

The "no tracking pixels" rule above is not squeamishness, it's that **open rates
stopped meaning anything**: privacy-protecting mail clients prefetch remote
images, so a large share of "opens" are machines. Don't report them, and don't
let the user make decisions on them.

A **click** is different — a person chose to go somewhere. If the user wants one
extra signal beyond replies, a self-hosted redirect on the single link is the one
worth having: it's cheap, and *clicked but hasn't replied* is a real state that
changes what you do next (`references/followups.md`). Say the trade-off out loud
before adding it — a redirect domain is visible to the recipient and is one more
thing that can hurt deliverability — and if they'd rather stay clean, replies
alone are a complete metric. The primary metric doesn't change either way.

## 3. Run the anti-slop pass

Every draft, before the user sees it. The patterns that make writing sound
machine-made are the same ones that make a cold email get deleted —
`references/anti-slop-writing.md` is the list, tuned for email, and
`benyki/skills/no-ai-slop-writting` is the deeper editor if it's installed.

The ones that kill cold email specifically: "I hope this finds you well",
"reaching out", "just wanted to", "circle back", "leverage", "solutions",
"game-changing", and any sentence that could appear in a different company's
email unchanged.

## 4. Iterate with the user — this is the actual work

**Do not ship the first version.** Show them **three** drafts of the same email
and ask which one they'd send *and what they'd change*. Then:

1. Rewrite from their edits, not from your own preference
2. Show it again. Two rounds is normal; three is fine
3. **Write down every reason they rejected something** — one line each in
   `shared/brand.md` under "What I've learned". That section is what stops the
   same argument happening next month
4. Stop when they say they'd send it unedited. That sentence is the gate

Keep nudging until they engage with it properly. A user who shrugs and says
"looks fine" hasn't read it, and you'll find that out 200 emails later when
nobody replies. It's worth saying plainly: *this email is the whole engine —
ten minutes on it now is worth more than anything downstream.*

## 5. Save it and record it

Write the agreed version into `templates/first-touch.txt` with a header comment
saying what it's trying to do, then record it as `template_used` on every run
that renders it.

**One template.** Not two, not an A/B — `engine-loop/references/ab-testing.md`
→ R0: testing starts once the user is happy with the format and 5–10 emails
have numbers on them. Until then, changing the template by hand from what you
learn beats splitting a thin stream between two versions that both need work.

## 6. When testing does start: the offer, or the wording?

The default first experiment is two phrasings of the same email. Sometimes
that's right. Often the bigger variable is **what's being offered**, and it's
worth raising before defaulting to copy.

The difference is what the result is good for. A wording test tells you about
that email. An **offer** test answers a question the user also has to answer on
the landing page, on the pricing page, and out loud on the first call:

> **Which true half of what we're offering makes the right person answer?**

That finding outlives the experiment that produced it.

**Which one to run is a judgement call, and the user gets the final say.** Put
the choice to them in one sentence with a recommendation — they know things
about their market that aren't in the home. Roughly:

| Test the **offer** when | Test the **wording** when |
|---|---|
| There are genuinely two true propositions and nobody knows which this audience wants | The offer is fixed — a set price, a role with agreed terms, one thing you do |
| It's a new audience or a new channel | The offer is settled and replies are coming, but the user winces at how it reads |
| The user is still deciding how to position the thing | The gap is getting opened at all — subject line, first line, length |
| Both previous attempts got replies, and you want to know *why* | The wording carries a specific risk: register, jargon, a claim that lands badly |

If the honest answer is "we only have one offer", that settles it — test the
wording, and note in `experiments.json` that the offer wasn't testable rather
than inventing a second one to have a test.

### If it's the offer

Splits that work:

| Arm A leads with | Arm B leads with |
|---|---|
| free access to the paid tier, no strings | a revenue split with one launch partner |
| speed — a result in days, not a quarter | reach — the work in front of a much bigger audience |
| independence and credit for the work | the platform handling the part they don't want to do |

Design them by writing down **every genuine upside** of the thing first, then
splitting that list: each arm leads with a different one, everything else
identical.

### What gets held constant — either way

Both kinds of test are easy to run badly, and a badly-run one is worse than no
test: it produces a confident number that means nothing. Four rules, whichever
variable you picked:

- **One dimension.** Same skeleton, same length within about fifteen words, same
  voice, same single ask, same sign-off. If arm B is also warmer and longer, a
  win tells you nothing about the thing you meant to test
- **The subject line belongs to the arm.** It carries the same headline as the
  body. A subject shared across arms mutes the variable; an unrelated one adds a
  second variable
- **The personalised hook is not part of the test.** The observation about that
  specific person is researched and written just as hard for both arms. It's
  what earns the read — holding it constant is what leaves the tested variable
  as the only real difference
- **Both arms have to be true** (offer tests especially). They describe the same
  thing the user actually does. An arm that promises what they can't deliver
  wins the test and loses the call — and now there's a number telling you to
  send more of it

Put what each arm is leading with in the template's header comment *and* in the
experiment's hypothesis. In six weeks that sentence is the only reason anyone
will remember what the two files were for.

**A won offer test doesn't stay in this engine.** If leading with the revenue
split beat leading with free access, that's a claim about what this audience
wants — it belongs in `shared/insights.md`, and it should change the landing
page the emails point at, not just the next template.

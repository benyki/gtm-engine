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
not outreach-specific — every workflow needs them.

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
`{{OBSERVATION}}`, `{{OFFER}}` — but `{{OBSERVATION}}` must be filled per person
with something real and recent. If it can't be filled honestly, that person is
the wrong target: skip them rather than writing filler.

## 3. Run the anti-slop pass

Every draft, before the user sees it. The patterns that make writing sound
machine-made are the same ones that make a cold email get deleted —
`engine-seo/references/anti-slop-writing.md` is the full list, and
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
nobody replies. It's worth saying plainly: *this email is the whole workflow —
ten minutes on it now is worth more than anything downstream.*

## 5. Save it and record it

Write the agreed version into `templates/first-touch.txt` with a header comment
saying what it's trying to do, then record it as `template_used` on every run
that renders it.

**One template.** Not two, not an A/B — `engine-loop/references/ab-testing.md`
→ R0: testing starts once the user is happy with the format and 5–10 emails
have numbers on them. Until then, changing the template by hand from what you
learn beats splitting a thin stream between two versions that both need work.

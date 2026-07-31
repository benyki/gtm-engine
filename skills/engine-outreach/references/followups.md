# Follow-ups and replies — optional, and built out of blocks

## This layer is opt-in

**Plenty of people should skip it.** If the volume is ten emails a week, the
user reading their own inbox and replying in their own words beats anything an
agent drafts — it's faster, it's better, and the reply is where a deal actually
starts. Ask before building any of this:

> *"Do you want me to draft the follow-ups and reply handling, or would you
> rather handle replies yourself?"*

If they'd rather reply themselves, the workflow is complete without this file.
The only thing still owed to the loop is the metric: when a reply lands, the
run gets `--value 1` and the CRM row gets `replied_at`. Everything else here is
optional machinery.

Two things make it worth turning on: volume they can't keep up with, and the
same three answers arriving over and over.

---

## Don't write a decision tree. Build a block library.

The obvious design — *interested → template A, not interested → template B* —
breaks in week one, because real replies don't sort into two buckets. What
actually arrives:

- interested, but wants a price first
- interested, but "ask me in Q3"
- not the right person, here's who is
- already using a competitor
- a single word: "how much?"
- a question about one specific feature
- a polite no with a reason
- a polite no with no reason
- "who gave you my email?"
- an out-of-office
- something none of the above covers

So keep **a library of optional blocks**, not a set of finished emails. Each
block is one short, reusable move:

| Block | When it goes in |
|---|---|
| acknowledge the specific thing they said | always — it's what proves a person read it |
| price / how it works | they asked, or the reply implies it |
| one proof point | they're weighing it up |
| the small next step | they're warm |
| defer to a date they named | "later" replies |
| redirect / ask for the right person | wrong person |
| honest comparison to what they use | competitor mentioned |
| how they got the email + opt-out | asked, or any irritation at all |
| clean close, no pitch | a clear no |

A reply is answered by **picking two or three blocks and joining them in the
user's voice** — not by finding the matching template. That's why this is a
library: the combinations are the point, and there are more of them than you'd
ever pre-write.

Keep it as one file per workflow — `<workflow>/templates/followups/blocks.md`
— with each block a short titled section. It sits alongside the templates but
isn't an A/B arm: blocks are components, and the spine tracks the first-touch
template that started the thread.

---

## The library has to grow — that's the maintenance loop

The first version will be wrong, and that's fine as long as it's updated. **Every
reply that doesn't fit an existing block is the signal**:

1. Answer it — with the user, in their words, however it needs answering
2. **Add what you wrote back to the library** as a new block, or as a variant
   note on an existing one, with one line on what triggered it
3. When a block stops being used, mark it stale rather than deleting it

Do this on the weekly pass, next to reading the numbers. Six weeks in, the
library is a real map of what this audience actually says — which is worth more
than the original template, and is exactly the thing a new agent picking up the
workspace can't reconstruct.

When a reply theme keeps recurring, it has stopped being a follow-up problem:

- Three people asking the same objection → that objection belongs in the
  **first-touch email**, answered before it's raised
- The same question over and over → that's an article
  (`engine-seo/inputs/queue/`) and a line in `shared/insights.md`
- The wrong people replying → the list is the problem, not the copy
  (`references/lead-sourcing.md`)

---

## Rules that don't change

- **Drafts only.** Replies to real people go out when a human clicks send. Same
  boundary as the first touch, and it doesn't relax because the conversation is
  warm — this is the point where a wrong send costs the most
- **Same arm as the first touch, always.** `assign_arm.py --entity <email>`.
  Switch someone mid-thread and you no longer know which message earned the reply
- **Stop when someone replies.** `replied_at` set means no further sequence
  mail, ever. A follow-up that arrives after a reply reads as a machine, and it
  undoes the credit the reply just earned
- **Three touches maximum** unless the user asks otherwise
- **A "bumping this" follow-up is worse than nothing.** New information, a
  different angle, or don't send it
- **Honour a no permanently.** `status=closed`, and never re-added by a future
  import

## What the loop needs from all this

Unchanged, whoever writes the replies: a reply is `runlog.py metric --value 1`
plus `replied_at` in the CRM; a closed sequence with no reply is `--value 0`.
The zero is a real result — writing it is what marks the run analysed, and
skipping it leaves the experiment reporting "no runs yet" forever.

# Running gtm-engine as a bootcamp

For the **organiser's agent**: you're helping someone run a session where a room
of people install gtm-engine and ship something real before they leave. Most of
them will be new to coding agents. Your job is the logistics and the room, not
the install itself, which each participant's own agent handles from
[`onboarding.md`](onboarding.md).

The one measure of a good session: **every participant leaves with one piece
they'd actually send or publish**, and a machine that will still work on Monday.

---

## Before the session

Give the organiser something to send participants a day or two ahead. It should
be short, and everything in it is a thing that costs ten minutes at home and
half an hour in the room.

What they need to have working:

- **A coding agent they're signed into.** Claude Code (Claude Desktop → Code
  tab, Pro or higher) or Codex (ChatGPT desktop → Codex, Plus or higher).
  Worth having them test it once: ask it to create a file and see it appear.
- **Browser control** installed and connected, since it's the piece nobody has
  by default and the one that blocks the most. *Claude in Chrome* or the
  ChatGPT extension. `engine-social` is effectively dead without it.
- **A Gmail their agent can reach**, if they're doing outreach. Personal
  accounts are safer here: managed Workspace accounts often block the
  connector, and finding that out at 10am costs the morning.
- **Admin rights on the laptop.** Managed work machines that block installs are
  the single most common dead end, and there's no fix in the room.
- **A charger**, and 10 GB free if anyone is doing video.

What to ask them to bring, in whatever shape they already have it:

- **who they'd reach**: a list, a CRM export, a spreadsheet, a pasted block of
  addresses, even a screenshot. Tell them explicitly not to reformat it
- **what they sell** and the promise they make
- **the one number that matters** to them: replies, signups, demos
- **three pieces of content** they wish they'd made, as raw material for voice

Collect the answers to the middle two before the session if you can. They're the
slowest part of `brand.md`, and they're much better answered at a desk than
under time pressure.

## The shape of a session

Roughly ninety minutes to a first shipped piece, if the prep landed:

1. **Install**, ten minutes. Each participant tells their agent to follow
   `onboarding.md`. The agent checks the machine, creates `~/gtm`, scaffolds the
   engines, installs the skills.
2. **One engine, configured properly**, twenty minutes. Outreach unless they
   have a reason otherwise: it needs no keys and no website, and a reply is a
   real signal inside a week. The brand interview is the substance here.
3. **Ship one thing**, the rest. A draft they'd actually send, ten researched
   people, one post. Whatever it is, it gets a run row, so next week's numbers
   have somewhere to land.
4. **Schedulers**, five minutes at the end. One metric job for the engine they
   ran, one weekly job. Without these the loop never has anything to say, and
   the session was a demo rather than a start.

Resist a second engine in the room. Four half-configured engines produce no
verdict anywhere, and the folders are already there for whenever they want one.

## What eats the time

- **A managed laptop that won't install.** No fix. Pair them with someone else
  and let them watch, or have them work in a cloud environment for the day.
- **A Workspace Gmail that won't connect.** Personal account, or draft into a
  local file and move on.
- **The browser extension not connected**, or the participant logged into
  LinkedIn in a different browser profile from the one the agent drives.
- **Video keys.** ffmpeg not installed, fal.ai credit at zero, upload-post
  profile not created. Anyone doing video needs the prep done beforehand.
- **A blank `brand.md`.** Thin answers are fine, invented ones are not. If
  someone genuinely can't say who they sell to, that's the real session.

## Guiding beginners

- **Take the defaults out loud.** Say which one you took and keep going. Nobody
  in their first hour benefits from a folder-layout decision.
- **Don't teach the architecture.** They don't need to know what `engines.json`
  is to send an email. It's there when they ask.
- **Show them a draft they'd actually send** as early as possible. That's the
  moment the thing becomes real; everything before it is setup.
- **Let them reject things.** Telling the agent why a draft is wrong is most of
  the work, and it's the habit that makes month three better than week one.
- **Be honest about the loop.** It needs about three weeks of runs before its
  verdicts mean anything. A session produces the first run, not the answer.

## Afterwards

[`goals.md`](goals.md) is the completion checklist, written as things that
exist on a machine rather than intentions: a file that opens, a scheduler that
fires, a run row with a number in it. Worth sending round a week later, when the
first metrics are due, along with a nudge to record them.

If a participant's setup looks broken, their agent can run
`python3 ~/.gtm-engine/skills/engine-setup/scripts/doctor.py`, which reports
what's missing and repairs the registry with `--fix`.

# Blocks : the pre-built parts of a post

**Optional.** A template in `templates/` can be written entirely free-form; this
folder exists for when part of a post is settled and only part of it changes.

The idea: a post is made of slots. Some slots you want written fresh every time
(the claim, the story, the number : the part that's actually about today). Other
slots you've already got right and only want to *rotate*: how you sign off, how
you frame a CTA, the one-line way you describe what you do. Those live here, as
named files with several variations each.

```
templates/
├── post-default.txt        a whole-post template
└── blocks/                 this folder : parts, never a whole post
    ├── README.md           you're reading it
    ├── closers.md          e.g. 4 ways you end a post
    └── bio-line.md         e.g. 3 ways you say what you do
```

Keep them in this subfolder, not loose in `templates/`: a file directly in
`templates/` reads as a whole-post template.

## Format

One file per slot. A heading, then one variation per list item. Plain markdown,
because a human edits this far more often than an agent does.

```markdown
# closers

Ends the post. Never a question, never "agree?".

- Anyway : that's the version that worked. The other three didn't.
- Still figuring out the rest of it.
- If you're doing the same thing and it's going worse, tell me how.
- (no closer : end on the last concrete line)
```

`(no closer …)` is a legitimate variation and often the winning one. Write it
down rather than leaving it implicit.

## Using them from a template

Name the block-fed slots in the template's header. Everything else is free:

```
# tries: A flat, specific claim in line one stops the scroll.
# blocks: CLOSE -> blocks/closers.md
# free:   CLAIM, BODY

{{CLAIM}}

{{BODY}}

{{CLOSE}}
```

Two rules when filling them:

- **Never the same variation twice in one batch.** Five posts that end
  identically read as one automated account, which is exactly what they are at
  that point
- **Rotate across batches too.** Check the last few batches in `posts/` before
  picking; prefer the least recently used

## Where they come from

**Not from an agent's imagination.** Blocks are extracted from `inputs/best/`
(their own posts that worked) and `inputs/swipe/` (posts they admire) : the
structures, never the words. The `gtm-social` skill's "Voice comes from their
best work" has the interview
that produces them, and it's worth doing before any of this: an invented closer
library is just slop with a folder around it.

Start with one block file. Two or three is plenty; a post assembled entirely
from pre-built parts is a mail merge, and readers can tell.

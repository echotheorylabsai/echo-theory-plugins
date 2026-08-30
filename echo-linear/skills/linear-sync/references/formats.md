# Formats

Written for a non-engineer. Plain language, short lines, no jargon, no long paragraphs.

**Word caps are hard.** If a section will not fit, the content is wrong — not the cap.

The `~` means one thing only: **do not count words to three decimal places.** Under the
number is fine, a little over is fine, half again as long is not. The review check fails a
description that is visibly padded or visibly over, not one at 265 words. Dated callouts do
not count toward it at all.

**Do not write `**Label:**` immediately before a link** — Linear's parser renders it as
`**Label: **[link]`, with the space inside the bold. Use `**Label** · [link]` instead.

| Artifact | Cap |
|---|---|
| Issue description | ~250 words |
| Project description | ~300 words |
| Milestone description | ~120 words |

---

## Issue

```markdown
**Order:** Phase A.2 · Blocked by ECH-41
**Context** · [Spec](link) §3 · [Plan](link) §Phase A

## What we're building
≤40 words, plain language. What exists after this ships.

## Why it matters
≤40 words. Customer value and product value.

## User story
As a <who>, I <do this> so that <outcome>.

## Scope
- 3–6 bullets, ≤15 words each

## Acceptance criteria
- 3–6 checkable bullets

## Out of scope
- only when something is genuinely at risk of being misread
```

**Add `## What the user sees`** — 2–4 bullets, directly after `## User story` — whenever the
work changes anything a person interacts with: a screen, a flow, a message, an email, a
state a user can land in. Describe what they see and do, never how it is built.

```markdown
## What the user sees
- A "Marketing" item in the left nav, one sub-page per capability
- Each page shows the latest numbers with the date they were collected
- Where there is no data yet, the page says so instead of showing a zero
```

Omit the section entirely for work with no user-facing surface.

For a simple (non-phased) project the Order line reads `**Order:** 2 of 5 · Blocked by ECH-41`.

**Optional:** `## How it fits` with a mermaid diagram — **only** when three or more
components interact or the sequence is non-obvious. Never as decoration.

### Implementation detail

Belongs in the linked spec, not here. No file paths, function names, table names or
schema in the prose.

**One exception:** a technical constraint a PM must understand to judge the work — a
dated third-party API retirement, a hard platform limit. State it in one plain sentence.

---

## Project

```markdown
## Goal
≤40 words — what changes for the customer.

## Why now
≤40 words.

## Who it's for
1 line.

## What ships
- 3–6 bullets

## How we'll know
- 3–5 measurable bullets

## Context
- [Spec](link)
- [Implementation plan](link)
```

Also set the Linear `summary` field: one sentence, ≤255 characters.

---

## Milestone

Name per `conventions.md`. Body:

```markdown
**Accepted when**
- 3–5 checkable bullets

**Why now** · one sentence
```

---

## Writing rules

- Short sentences. One idea each.
- No paragraph longer than three lines.
- Bold only the few words that carry the decision.
- Prefer a bullet to a sentence, a table to a list of trade-offs.
- Never restate the same point in two sections.
- If a PM would have to ask "what does that mean?", rewrite it.

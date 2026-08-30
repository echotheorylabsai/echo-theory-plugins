# Linear conventions

Workspace facts verified 2026-08-29. Re-check with the Linear MCP if anything looks stale.

## Workspace

- **One team:** `Echotheorylabs`, key `ECH`. Never ask which team.
- **No templates exist.** This skill carries its own format.
- **States:** `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate`.
- **Labels — type:** `Bug`, `Feature`, `Improvement`.
- **Labels — area:** `platform`, `echo-hq`, `content-agent`, `support-agent`,
  `research-agent`, `outreach-agent`, `mcp-connector`, `context-layer`.

**Never invent a new label, state or template.**

## Titles and sequencing

| Project kind | Milestone name | Issue title |
|---|---|---|
| **Complex** — phased roadmap, major code changes | `Phase A · Short name` | `[Phase A.1] Title`, `[Phase A.2] Title`, `[Phase B.1] Title` |
| **Simple** — minor tasks done in order | none | `1. Title`, `2. Title` |

Letters for phases, numbers for order within a phase — so the two are never confused when
a title is read out of context.

**Adding to an existing project: do not restart the numbering.** List that project's
issues first, detect the prefix convention already in use, and continue the sequence.

## Write order

The saves depend on each other. Out of order, they fail partway and leave Linear half-built.

```
1  project        a milestone save requires its project
2  milestones     an issue is matched to a milestone BY NAME — it must already exist
3  issues, one at a time, in sequence
                  a blocked issue needs its predecessor's identifier, both for the
                  blockedBy relation and for the "Blocked by ECH-41" line in its body
```

Never batch issue creates. You cannot write an Order line that names an identifier you do
not have yet.

## Milestones

**Create every milestone before creating any issue.** An issue is assigned to a milestone
by name, so the milestone must already exist or the save fails partway through the run.

**Reuse before you create.** List the project's milestones first. If one already carries the
name a plan phase maps to, **use it** — do not create a second milestone with that name, and
do not shift the phase to the next free letter. New letters are only for phases the project
does not already have.

**One plan phase = one milestone.** Nothing else becomes a milestone.

- If the plan has no phases, the project has no milestones. **Never invent phases the plan
  does not have** — a made-up roadmap is worse than a flat issue list.
- If a phase is too small to hold at least one issue, it was not a phase. Merge it.

**Target dates.** Set `targetDate` only when the plan states a date or a deadline. Never
infer one from effort estimates, and never invent one to make the project look planned.

**Adding a phase to a project that already has milestones.** List the existing milestones
first, then continue the letter sequence from the last one — a project holding `Phase A`
and `Phase B` gets `Phase C`, never a second `Phase A`.

## Fields on every issue

| Field | Value |
|---|---|
| team | `Echotheorylabs` |
| project | the tier's project |
| milestone | the phase this issue belongs to; omit when the project has no milestones |
| labels | exactly two — one type + one area |
| state | `Backlog` |
| title | per the table above |
| links | spec and plan URLs as link attachments |
| blocks / blockedBy | per **Dependencies** below |

Set `priority` only when the source material states urgency. Leave assignee, estimate,
cycle and due date unset.

## Dependencies

- Chain `blocks` / `blockedBy` sequentially **within** a phase.
- Across phases: link the first issue of Phase B as blocked by the last issue of Phase A
  **only when the plan says the phases are sequential**. If they can run in parallel,
  leave them unlinked.
- Never chain issues that are genuinely independent. Numbering conveys reading order;
  blocking conveys a real constraint.

## File links

Prefer a GitHub blob URL — but **only if the file is committed and pushed**. Verify with
git; do not assume.

Otherwise use the repo-relative path (`docs/superpowers/specs/…`), which a local coding
agent can still open.

**Never link a path that does not exist.**

### A repo path cannot be a link attachment

Link attachments need a URL. A repo-relative path is not one, so an unpushed file goes in
the description's Context line instead, as plain text:

```
**Context** · Spec `docs/superpowers/specs/2026-08-20-content-v2-design.md` §3
```

This is the **one** sanctioned exception to "no file paths in the prose". Say in the confirm
table which sources are unpushed, so the user can push them and get real links instead.

## Updates must never clobber hand-written text

Descriptions get edited by hand. A full-description rewrite destroys that work.

- **Never** send a whole replacement `description` on an update. Use `patch` operations.
- **New information** → `prepend` a dated callout, matching the house convention:

  ```
  > **UPDATE 2026-08-29** — one-line summary.
  >
  > The detail.
  ```

- **A specific wrong statement** → anchored `replace` on that exact text.

### Milestones have no safe update — read before you write

`save_issue` and `save_project` accept `patch`. **`save_milestone` does not.** Its
description is full-replace only, so a careless update silently destroys a hand-written
milestone body, and milestone bodies are often the longest hand-written text in the
workspace.

**The only safe procedure:**

1. `get` the milestone and read its **complete** current description.
2. Build the new body: your dated callout, a blank line, then **the existing body verbatim**.
3. Save that whole string as `description`.

You are reproducing by hand what `patch` does for issues. There is no shortcut.

**Stop and ask instead of guessing** when the existing body is long, was truncated in the
response you received, or contains anything you cannot reproduce exactly. Losing it is
irreversible. Asking costs one message.

### Keep the cap when updates accumulate

**A dated callout does not count toward the word cap.** The cap governs the description a
reader is meant to absorb; the callouts sit above it. Without this, every update to a
cap-sized issue or milestone would be impossible — trimming to fit destroys hand-written
text, which is the one thing these rules exist to prevent.

What is capped instead is the **number** of callouts, because the description degrades into
a changelog long before it degrades into a long one.

**Before prepending a new callout, count the ones already there.**

- Two callouts at most stay at the top.
- When adding a third, move the **oldest** one into a Linear comment on that issue, then
  delete it from the description with an anchored `replace`.
- The description stays a description. The comment thread carries the history.
- **A milestone has no comment thread.** At a third callout on a milestone, fold the oldest
  into a comment on the project instead, and say you did.

### Traps

| Field | Behaviour |
|---|---|
| `labels` | **Replaces the entire set.** `get` the issue and read its current labels *before* writing any, then send the full intended set — otherwise existing labels are silently dropped. |
| `links`, `blocks`, `blockedBy`, `relatedTo` | Append-only. Safe to add to. |
| `patch` | Each anchor must match **exactly once**. One failing op aborts the whole save — nothing changes, which is safe but silent. |
| `patch` anchors | Must match what Linear **stored**, not what you sent. Its parser rewrites markdown on save. **Always `get` the issue first and copy the anchor from the stored text.** |
| `save_milestone` | **No `patch` support.** `description` replaces the whole body. Read the existing body first and re-send it, or it is gone. |
| milestone assignment | An issue's `milestone` is matched by name against milestones that already exist on that project. Create milestones first. |

## Harness portability

This skill runs in Claude Code and Codex. Both have the Linear MCP configured, under
different tool names.

- Refer to operations by capability: "list issues", "get the project", "save the issue".
- Never hardcode a harness-specific tool name.
- Assume subagents may not exist.
- Use plain file reads and git commands, not repo-specific tooling.

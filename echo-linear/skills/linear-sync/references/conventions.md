# Linear conventions

## Workspace — discover it, do not assume it

This plugin is installed in workspaces other than the one it was written for. **List the
teams, states and labels from Linear before the confirm gate**, and shape the plan against
what you actually find.

The values below are Echo Theory Labs' workspace, verified 2026-08-29. Treat them as the
expected case, not as fact.

| | Echo Theory Labs |
|---|---|
| Team | `Echotheorylabs`, key `ECH` — the only one, so never ask which |
| Templates | none; this skill carries its own format |
| States | `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate` |
| Labels — type | `Bug`, `Feature`, `Improvement` |
| Labels — area | `platform`, `echo-hq`, `content-agent`, `support-agent`, `research-agent`, `outreach-agent`, `mcp-connector`, `context-layer` |

**What to do when the workspace differs:**

- **More than one team** → ask which, once. Do not guess.
- **No `Backlog` state** → use the workspace's own unstarted state and say which you picked.
- **No type/area label pair** → say so in the confirm table and file with the labels that do
  exist, or none. Do not force issues into a scheme this workspace has not got.

**Never invent a label, state or template.** Use what exists, or state plainly that it does
not.

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

**Same intent, different name** — an existing `Phase A · Instrument` against a plan phase
called `Instrumentation` — is not yours to decide. Show both in the confirm table and ask
whether to reuse or add a new phase.

### Adding issues to a milestoned project (tier 1)

Every issue in a project that has milestones needs one. Which milestone the new issues take
depends on what they are:

- **Continuing existing work** → the milestone that work belongs to, numbering on from its
  last issue.
- **A new phase of work** → a new milestone, continuing the letter sequence.

If it is not obvious which, **put both options in the confirm table and ask.** Attaching
issues to the wrong phase silently corrupts the roadmap.

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
| team | the workspace's team — `Echotheorylabs` here; ask when there is more than one |
| project | the tier's project |
| milestone | the phase this issue belongs to; omit when the project has no milestones |
| labels | one type + one area where both exist. Fewer only when the workspace has no such scheme — say so in the confirm table |
| state | the workspace's unstarted state — `Backlog` here |
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

Use a GitHub blob URL — **only if the file is committed and pushed**. Verify with git; do
not assume. Check `git check-ignore` too: a gitignored file can never be pushed, so it can
never get a URL.

**Never link a path that does not exist.**

### An unreachable source is a stop, not a fallback

Link attachments need a URL. A repo-relative path is not one — and worse, it only resolves
on the machine that has the file. The issue looks complete and is unusable to everyone else.

**So an unpushed source stops the run.** Name the files, ask the user to commit and push
them, and wait. Pushing costs one command; a project of issues pointing at nothing costs a
lot more.

Only after the user explicitly says to proceed without pushing, put the path in the
description's Context line as plain text:

```
**Context** · Spec `docs/superpowers/specs/2026-08-20-content-v2-design.md` §3 · local only
```

This is the **one** sanctioned exception to "no file paths in the prose", and the confirm
table must say the link is local-only.

### When the source is a Linear comment, not a file

`linear-implement` hands back mid-run when an approved change needs an issue that does not
exist. Its source is then an **approval-record comment** on an existing issue — not a spec
file, and not a branch anyone can reach.

That is a legitimate source and it does **not** trip the unpushed-source stop: a comment in
Linear is reachable by everyone who can see the issue, which is the whole test.

- Link the parent issue as a **related issue**, not as a file link.
- Context line: `**Context** · Approved on ECH-42 · see the approval record of 2026-08-30`.
- Never push a half-built phase branch to manufacture a URL for it.

### Where specs live must be committable

If the repo gitignores the directory specs are written to, every issue this skill files will
hit the stop above. Fix the ignore rule rather than working around it — a spec nobody but
you can open is not a link.

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
3. Save that whole string as `description` — **and send `project` too.** It is required even
   on an update, and omitting it fails validation.

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
- At a third callout on a milestone, fold the oldest into a **comment on that milestone** and
  say you did. Milestone comments exist — they render as description comments — so history
  stays with the artifact it belongs to. **A comment needs the milestone's UUID**, not its
  name: list the project's milestones to resolve it first. (A milestone *save* accepts the
  name; a comment does not.)

### Traps

| Field | Behaviour |
|---|---|
| `labels` | **Replaces the entire set.** `get` the issue and read its current labels *before* writing any, then send the full intended set — otherwise existing labels are silently dropped. |
| `links`, `blocks`, `blockedBy`, `relatedTo` | Adding is safe — these do not replace the set. Removing needs the explicit remove operation, so a wrong dependency **can** be corrected; it just is not undone by omitting it. |
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

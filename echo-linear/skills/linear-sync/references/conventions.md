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

## Fields on every issue

| Field | Value |
|---|---|
| team | `Echotheorylabs` |
| project | the tier's project |
| milestone | tier 3 only |
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

### Traps

| Field | Behaviour |
|---|---|
| `labels` | **Replaces the entire set.** Always re-send the full intended set, or existing labels are silently dropped. |
| `links`, `blocks`, `blockedBy`, `relatedTo` | Append-only. Safe to add to. |
| `patch` | Each anchor must match **exactly once**. One failing op aborts the whole save. |

## Harness portability

This skill runs in Claude Code and Codex. Both have the Linear MCP configured, under
different tool names.

- Refer to operations by capability: "list issues", "get the project", "save the issue".
- Never hardcode a harness-specific tool name.
- Assume subagents may not exist.
- Use plain file reads and git commands, not repo-specific tooling.

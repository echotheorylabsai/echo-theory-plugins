# linear-sync — design

**Date:** 2026-08-29
**Status:** Design approved, ready for implementation
**Deliverable:** new `echo-linear` plugin in `echo-theory-plugins`, containing one skill: `linear-sync`
**Harnesses:** Claude Code and Codex CLI (both installed; both have the Linear MCP configured)

---

## 1. Problem

After a working session — sometimes a plain discussion and agreement, sometimes a full
`superpowers:brainstorming` spec plus a `superpowers:writing-plans` implementation plan — the
agreed work has to reach Linear by hand. Two things go wrong when it does:

1. **The writing drifts technical.** Descriptions end up as implementation notes, so a PM
   reading the issue cannot tell what is being built or why it matters.
2. **The context is lost.** A coding agent starting a fresh session on that issue has no route
   back to the spec or plan that justified it.

## 2. Goal

One skill, invoked at the end of such a session, that turns what was **approved** into Linear
projects, milestones and issues written in product language, each linking back to the source
documents, and each independently actionable by a coding agent in a clean session.

## 3. Non-goals (v1)

- No status syncing back from Linear into the repo.
- No cycles, estimates, assignees, releases, or initiatives.
- No new Linear labels, statuses, or templates — reuse only what the workspace already has.
- No Linear document creation. Specs stay in git; Linear links to them.
- No automatic archiving or deletion of anything.

---

## 4. Deliverable layout

Follows the existing `echo-marketing` convention in this repo.

```
echo-linear/
├── .claude-plugin/plugin.json
├── README.md
└── skills/linear-sync/
    ├── SKILL.md                 the 5-step loop; deliberately thin
    └── references/
        ├── formats.md           project / milestone / issue templates + word caps
        ├── conventions.md       workspace facts, labels, wiring, safe-update rules
        └── review-rubric.md     the adversarial read-back checklist
```

`SKILL.md` holds only the loop and the decision rules. Everything a future edit is likely to
touch — a template, a label, a check — lives in a reference file, so the logic and the content
can evolve separately.

---

## 5. The loop

```
1  READINESS GATE   do I actually have enough? → if not, STOP and ask
2  SHAPE            pick the tier, decide the MINIMUM issue set, say it out loud
3  CONFIRM          show the plan table in chat, wait for an explicit yes
4  WRITE            create/update via the Linear MCP
5  REVIEW           fresh read-back from Linear vs rubric → fix → re-verify → report
```

Steps 1, 3 and 5 are gates. None of them may be skipped, including on a single-issue run.

### 5.1 Step 1 — readiness gate

Collect the source of truth first: approved spec/plan files referenced in the conversation
(or found under `docs/superpowers/specs/` and `docs/superpowers/plans/`), what was explicitly
agreed in chat, and the relevant parts of the codebase.

Then reflect critically against this checklist:

- Is the scope **agreed**, or still under discussion? A proposal is not an approval.
- Do I know the goal, who it is for, and how we would know it worked?
- Can I write acceptance criteria that are **checkable**, rather than vague?
- Do the components, surfaces or products I would name actually exist in the repo?
- Is this a create or an update — and if an update, of exactly which project/issue?
- If linking files: do they exist, and are they committed?

**Any gap → stop. Ask clarifying questions. Write nothing to Linear.**
Proceed only when the skill can state in one line why it has enough.

Rationale: an issue built on a guess is worse than no issue, because it looks authoritative
and is already live in a shared workspace.

### 5.2 Step 2 — shape

Three tiers. The skill picks one and states which, with a one-line reason.

| Tier | Input | Creates |
|---|---|---|
| 1 | A chat agreement, or a single change | Issues only, on an existing project. If the user has not named one, ask — do not guess, and do not create a project. |
| 2 | A spec/PRD, no phased plan | New project + flat issues |
| 3 | A spec + a phased implementation plan | New project + milestones (from phases) + issues |

**Minimum-issue discipline** — the rule that prevents sprawl:

- One issue = one shippable outcome a developer can verify on its own.
- Merge anything that cannot be reviewed independently.
- Never create a separate issue for "write tests", "update docs" or "refactor". Fold that work
  into the issue whose acceptance criteria it serves.
- Target **1–4 issues per milestone**. If a plan phase yields more than 6, that is a signal to
  re-group, not to create twelve issues.

### 5.3 Step 3 — confirm

Print a compact plan table and wait. Format:

```
WILL CREATE
  Project  Content Intelligence v2
  Phase A · Instrument
    [Phase A.1] Record the baseline   Feature/platform
    [Phase A.2] Seal Day 0            Feature/platform
  Phase B · Report
    [Phase B.1] Change log            Feature/echo-hq

WILL UPDATE
  ECH-44   prepend dated callout

Proceed?
```

Nothing is written until the user says yes. If they amend, re-print and wait again.

### 5.4 Step 4 — write

Create/update through the Linear MCP, following §6–§8. Record the identifier and URL of every
artifact touched — the review step needs the list.

### 5.5 Step 5 — review

§9. Runs before any answer is returned to the user.

---

## 6. Naming and sequencing

Decided by whether the work is a phased roadmap or a short sequence of minor tasks.

| Project kind | Milestone name | Issue title |
|---|---|---|
| **Complex** — phased roadmap, major code changes | `Phase A · Short name` | `[Phase A.1] Title`, `[Phase A.2] Title`, `[Phase B.1] Title` |
| **Simple** — minor tasks done in order | none | `1. Title`, `2. Title` |

Letters for phases, numbers for order within a phase, so the two can never be confused when a
title is read out of context.

**Tier 1 exception — do not restart the numbering.** When adding issues to an existing project,
first list that project's issues, detect the prefix convention already in use, and continue the
sequence. Starting again at `1.` next to an existing `[Phase B.2]` breaks review check 4.

---

## 7. Content formats

Written for a non-engineer. Plain language, short lines, no jargon. Word caps are hard: if a
section will not fit, the content is wrong, not the cap.

### 7.1 Issue — cap ~250 words

```markdown
**Order:** Phase A.2 · Blocked by ECH-41          (complex)
**Order:** 2 of 5 · Blocked by ECH-41            (simple)
**Context:** [Spec](url or path) §3 · [Plan](url or path) §Phase A

## What we're building
≤40 words, plain language.

## Why it matters
≤40 words. Customer value and product value.

## User story
As a <who>, I <do this> so that <outcome>.

## Scope
- 3–6 bullets, ≤15 words each

## Acceptance criteria
- 3–6 checkable bullets

## Out of scope
- only when genuinely at risk of being misread
```

Optional `## How it fits` with a mermaid diagram — **only** when three or more components
interact, or a sequence is non-obvious. Never as decoration.

Implementation detail belongs in the linked spec, not here. The exception is a technical
constraint a PM must understand to judge the work (for example, a dated third-party API
retirement) — those may be stated in one plain sentence.

### 7.2 Project — cap ~300 words

```markdown
## Goal                ≤40 words — what changes for the customer
## Why now             ≤40 words
## Who it's for        1 line
## What ships          3–6 bullets
## How we'll know      3–5 measurable bullets
## Context             links to spec and plan
```

Also set the Linear `summary` field: one sentence, ≤255 characters.

### 7.3 Milestone — cap ~120 words

Name per §6. Body:

```markdown
**Accepted when**
- 3–5 checkable bullets

**Why now** · one sentence
```

This matches the milestone style already used across the workspace.

---

## 8. Linear wiring and safe updates

### 8.1 Workspace facts (verified 2026-08-29)

- One team: `Echotheorylabs`, key `ECH`. Never ask which team.
- No templates exist. The skill carries its own format.
- Statuses: `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate`.
- Labels — type: `Bug`, `Feature`, `Improvement`.
  Area: `platform`, `echo-hq`, `content-agent`, `support-agent`, `research-agent`,
  `outreach-agent`, `mcp-connector`, `context-layer`.

### 8.2 Fields set on every issue

| Field | Value |
|---|---|
| team | `Echotheorylabs` |
| project | the tier's project |
| milestone | tier 3 only |
| labels | exactly two — one type + one area. **Never invent a new label.** |
| state | `Backlog` |
| title | per §6 |
| links | spec and plan URLs as link attachments |
| blocks / blockedBy | per §8.3 |

Priority is set only when the source material states urgency. Assignee, estimate, cycle and
due date are left unset in v1.

### 8.3 Dependency chaining

- Chain `blocks` / `blockedBy` sequentially **within** a phase.
- Across phases: link the first issue of Phase B as blocked by the last issue of Phase A
  **only when the plan states the phases are sequential**. If phases can run in parallel, leave
  them unlinked.
- Do not chain issues that are genuinely independent, even when numbered — numbering conveys
  reading order, blocking conveys a real constraint.

### 8.4 File links

Prefer a GitHub blob URL, but **only if the file is committed and pushed** — verify, do not
assume. Otherwise use the repo-relative path (`docs/superpowers/specs/…`), which a local coding
agent can still open. Never link a path that does not exist.

### 8.5 Updates must never clobber hand-written text

The user edits Linear descriptions by hand. A full-description rewrite destroys that work.

- **Never** send a whole replacement `description` on an update. Use the MCP `patch` operations.
- New information → `prepend` a dated callout, matching the existing house convention:
  `> **UPDATE 2026-08-29** — one-line summary.` followed by the detail.
- A specific wrong statement → anchored `replace` on that exact text.
- Known traps, to be stated explicitly in `conventions.md`:
  - `labels` **replaces the entire label set** — always re-send the full intended set.
  - `links`, `blocks`, `blockedBy`, `relatedTo` are **append-only** — safe to add to.
  - `patch` anchors must match exactly once, and the whole patch aborts if one op fails.

---

## 9. Adversarial review

Runs after writing and before the final answer. It must re-fetch every artifact from Linear —
it may never trust what it believes it wrote.

| # | Check |
|---|---|
| 1 | **Coverage** — every approved item maps to exactly one artifact; nothing was invented, nothing dropped |
| 2 | **No leakage** — no file paths, function names, table names or schema in the prose (links excepted) |
| 3 | **Readable** — a PM understands it unaided; word caps respected; no verbosity |
| 4 | **Wiring** — project, milestone, labels, state, title prefixes, order and blocking chain all consistent |
| 5 | **Links resolve** — every referenced spec/plan exists; GitHub URLs point at pushed files |
| 6 | **Codebase alignment** — components and surfaces named in the issue actually exist in the repo |

Failures are fixed in Linear and re-verified before reporting. The review also serves as the
**recovery path**: it compares Linear against the confirmed plan table from step 3, so anything
missing after a partial failure is created then, with no extra machinery.

**Independence.** Where the harness provides subagents (Claude Code), run this in a
clean-context subagent so it cannot inherit the writer's assumptions. Where it does not
(Codex), run it as an explicit fresh read-back pass against the same rubric. The rubric is the
mechanism; the subagent is an upgrade.

---

## 10. Cross-harness constraints

The same `SKILL.md` must work in Claude Code and Codex.

- Refer to Linear operations by **capability** — "list issues", "save an issue", "get a project"
  — never by harness-specific tool names such as `mcp__claude_ai_Linear__save_issue`.
- Assume no subagents (see §9).
- Assume no repo-specific tooling; use plain file reads and git commands.

---

## 11. Rollout

The skill existing in the repo loads in neither harness. Installation is part of the work.

1. Add `echo-linear` to `.claude-plugin/marketplace.json`.
2. Create `echo-linear/.claude-plugin/plugin.json` at version `1.0.0`, matching the
   `echo-marketing` shape.
3. Install/refresh the plugin in **Claude Code**.
4. Install/refresh in **Codex**. Note Codex's `[[skills.config]]` entries point at versioned
   cache paths (`…/echo-marketing/1.0.0/skills/…`), so a version bump requires a refresh.
5. Confirm `linear-sync` appears in both harnesses' skill lists and invokes.

**Task acceptance criterion:** the skill is listed and invocable in both tools — not merely
present on disk.

---

## 12. Verification plan

Linear is a live shared workspace, so verification must not pollute it.

1. Run the skill on a small real spec into a **scratch Linear project** named
   `zz-linear-sync-test`.
2. Inspect by eye against §7 and §9: language, caps, labels, order, blocking, links.
3. Run an **update** against one scratch issue and confirm the hand-written body survives and
   a dated callout was prepended.
4. Run the same flow once from **Codex** to prove the harness-agnostic wording holds.
5. Archive the scratch project.

---

## 13. Decisions on record

| Decision | Choice |
|---|---|
| Where it lives | `echo-theory-plugins` repo, new `echo-linear` plugin |
| Shape selection | Three tiers, skill picks and announces |
| Sequencing | Numbered/phased title prefixes + native Linear blocking relations |
| Title prefixes | `Phase A · Name` / `[Phase A.1] Title` complex; `1. Title` simple |
| Confirm gate | Always, including single-issue runs |
| Word caps | Issue ~250, project ~300, milestone ~120 |
| Updates | `patch` only; dated prepended callout; never a full rewrite |
| Review | 6-check rubric, fresh read-back, subagent where available |

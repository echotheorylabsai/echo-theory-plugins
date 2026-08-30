# Keeping Linear authoritative

Linear is the record. The ledger is a local cache. When they disagree, Linear wins.

## States, truthfully

The tables below name Echo Theory Labs' states — `Backlog`, `Todo`, `In Progress`,
`In Review`, `Done`, `Canceled`, `Duplicate` — restated so this file stands alone. **Step 0
lists the actual workspace's states**; where they differ, use its equivalents and read
`In Review` below as "the state meaning finished but not merged". **Never invent one**, and
note there is no `Blocked` state here. Full workspace notes:
`../../linear-sync/references/conventions.md`.

| Situation | State |
|---|---|
| Actively working the issue | `In Progress` — set after the re-read, before the first edit |
| Its work is committed to the phase branch and independently reviewed, but the phase PR has not merged | `In Review` — this is where most finished issues sit until the checkpoint |
| Stopped mid-work: blocked, awaiting a decision, or grind limit hit | **Leave `In Progress`** and say why in a comment. Moving it back reads as abandoned; moving it to `In Review` claims work that is not finished |
| Stopped **after** its work was committed and the phase PR opened — post-PR review feedback, a pending decision | **Leave `In Review`.** The work is committed and reviewed; the decision is about what happens next, not about whether it is finished |
| The phase PR merged and was confirmed from the remote | `Done` — set for every issue in that phase at the checkpoint |
| Unstarted | `Backlog` / `Todo` — leave as found |
| Found `Canceled` or `Duplicate` at step 0 | Skip it. Do not resurrect it; say so in the delivery plan |
| Found already `In Progress`, `In Review` or `Done` at step 0 | Resume if the ledger — read or rebuilt from Linear per `ledger.md` § Resuming — accounts for it. Stop and ask only when Linear shows work no record can explain: an issue `In Progress` with no evidence comment and no branch means someone else is in there |

**A blocked issue is never Done.** State is a claim about reality, not a courtesy to the
run's tidiness. Never move an issue to Done to make a report look finished.

## Never without approval

- Create, rename, reorder, regroup or delete a project or milestone.
- Change an issue's description, acceptance criteria, order or dependencies for anything
  the material-change gate calls material.
- Change scope, labels, milestones or the roadmap.

Creating Linear artifacts is `linear-sync`'s job, not this skill's.

## Evidence comment

**One per issue**, written when its work is committed to the phase branch — before the PR
exists. Concise.

```markdown
**Complete** · committed to `feat/phase-a-instrument` · ships with the Phase A PR

**Verification** — 14 tests passing (`pytest tests/ingest`), full suite green
**Review** — independent review passed; one finding fixed (unhandled empty response)
**Decision** — retry budget set to 3, per plan §Phase A
**Gate** — none outstanding
```

**The PR does not exist yet when this is written, and that is fine.** Naming the branch and
the phase is enough. At the checkpoint the PR link goes in the **project** status update —
never as a second comment on every issue, and never by patching this one.

Include `Decision` and `Gate` lines only when there is one. Omit rather than pad.

## Discrepancy comment

Posted the moment evidence shows an approved source is wrong, incomplete or unsafe —
**before** any approval, and without waiting.

```markdown
**Blocked — decision needed**

**What we found** — the plan's sealing step rewrites rows in place; 2,400 existing rows
have no `sealed_at` and would be overwritten.
**Evidence** — `SELECT count(*) … WHERE sealed_at IS NULL` returns 2,400; plan §Phase A.2
assumes the column is always populated.
**Affects** — ECH-42's acceptance criterion 2, and any later read of pre-seal history.
**Options** — (a) backfill first, one extra step; (b) seal forward only, losing history;
(c) plan is right and the data is stale — needs confirming.
```

State facts and options. **Never announce a decision, a new plan, or a changed criterion.**

### Approval record

```markdown
**Approved 2026-08-30 by the user in session** — backfill the 2,400 unsealed rows before
sealing forward.

**Asked** — see the discrepancy comment above; three options given.
**Answer** — option (a), backfill first.
**Changes** — plan §Phase A.2 gains a backfill step; this issue's criterion 2 is patched.
**Replaces** — plan §Phase A.2 previously read "seal each row in place as it is read".
```

**Quote the superseded text** in `Replaces`. Once the doc is updated, that wording exists
nowhere else, and the close pass needs it to audit what actually changed.

**Name who approved**, in the first line: the user, or a named human reviewer on the PR. A
reviewer subagent cannot approve anything — it reports. "Approved" with no approver is not a
record, and across a session boundary it is indistinguishable from something you decided
yourself.

Post it **before** acting on the approval, on the issue the change affects. Reconciliation
cites this comment; nothing else counts as provenance.

### Why it has to be here

When the user approves a change — in chat, in a review, anywhere — **write it to the issue as
a comment before acting on it**, quoting what was approved and dating it. Mirror it in the
ledger.

Reconciliation later has to distinguish an approved deviation from an unapproved one, and its
test is whether you can name where approval happened. A chat transcript is not something a
resumed session can open. If the approval is not in Linear, a later run cannot tell drift
from agreement.

## Project status updates

Post one:

- after the start gate — goal, order, dependencies, risks, next issue
- at each milestone start and end
- for a material risk, blocker, scope change or external gate

Say what completed, what is next, and what decision or gate is needed. **An update per issue
is noise.**

A status update may **report** a risk. It may never **announce** a decision that was not
approved.

## When blocked

1. Post the discrepancy comment above on the issue.
2. Post a non-decisional project risk update, only if it warrants one.
3. Commit the work in progress to its branch so nothing is lost.
4. **Leave dependent work untouched.** Do not start the next issue to stay busy.
5. Request direction and stop.

## Never in a comment

A secret, token, credential, customer record or any sensitive data. Comments are permanent
and visible to the whole workspace.

---

## The lethal update traps

These apply on the **non-material patch path** and after an approved material change — the
only times this skill edits a description. Full safe-update rules:
`../../linear-sync/references/conventions.md`.

### 1. `patch` anchors must match Linear's *stored* text

Linear's parser rewrites markdown on save, so the text you sent is not necessarily the text
it holds. **Always `get` the issue first and copy the anchor from the stored text.**

Each anchor must match exactly once. One failing operation aborts the whole save — nothing
changes, which is safe but gives no error you will notice.

### 2. `labels` replaces the entire set

**`get` the issue and read its current labels before writing any.** Send the complete
intended set, or the existing ones vanish silently.

`links`, `blocks`, `blockedBy` and `relatedTo` behave the opposite way: adding is safe and
does not replace the set. A wrong dependency **can** still be corrected — it just needs the
explicit remove operation, not omission.

Whenever an update replaces a collection, send the complete intended collection.

### 3. A milestone save has no `patch`

Its `description` is **full-replace**, so a careless update destroys a hand-written body.
This skill does not edit milestones without approval — but if an approved change requires
it: `get` it, read the **complete** body, build callout + blank line + existing body
verbatim, save the whole string — **and send `project` too**, which is required even on an
update. If the body is long, was truncated in the response, or
contains anything you cannot reproduce exactly — **stop and ask.** Losing it is
irreversible.

### Patching without clobbering

Use anchored patches; use **comments** for progress, never a description rewrite. A dated
callout does not count toward the description's word cap — but at most two stay at the top,
and the oldest moves into a comment before a third is added.

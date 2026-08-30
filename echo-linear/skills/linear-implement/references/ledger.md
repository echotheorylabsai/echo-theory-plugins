# The execution ledger

A multi-issue run outlives a context window. The ledger is what survives it.

## Where it lives

`.linear-implement/<slug>.md` in the **primary checkout** of the repo being worked on.

The **slug is the Linear project identifier**, not its name — stable, unique, and the same
every session. Fall back to the name lowercased with non-alphanumerics collapsed to `-` only
if the project has no identifier, and record which you used in the header.

- **Not in a worktree** — per-phase worktrees are removed at the end of each milestone and
  would take the ledger with them.
- **Never committed.** On first use, create the directory *and* confirm `.linear-implement/`
  is ignored by the target repo.

  If it is not, **make and commit that `.gitignore` edit inside the first phase's worktree**,
  so it rides along in that phase's PR. Never edit `.gitignore` in the primary checkout: a
  later `git pull --ff-only` aborts there the moment anyone upstream touches the same file,
  and it is untracked work nothing will ever carry. Never commit it straight to the
  integration branch either — that skips review and fails outright on a protected branch. Mention it in the step-1 plan so an unrelated line in that PR is not a surprise.

  Until that PR merges, the ledger directory is untracked in the primary checkout. That is
  expected, and it is the only uncommitted thing step 0 tolerates. An untracked directory
  does not block a pull.

**Created only after the step-1 gate passes.** Nothing reaches disk while the user is still
being asked.

## What it is not

**Not authoritative.** Linear is the record: issue states and evidence comments carry the
same facts. Where the two disagree, Linear wins and the ledger is corrected.

If the ledger is lost, rebuild it from Linear rather than from memory. That is the whole
reason evidence goes into Linear comments and not only here.

## Format

```markdown
# Content Intelligence v2 — execution ledger

Project      <Linear project identifier>
Baseline     docs/superpowers/plans/2026-08-20-content-v2-plan.md @ abc1234
Integration  main
Started      2026-08-30
Checkpoints  after Phase A · after Phase B

## Order

| # | Issue | Title | Phase | State | Phase PR |
|---|---|---|---|---|---|
| 1 | ECH-41 | [Phase A.1] Record the baseline | A | IN REVIEW | not opened |
| 2 | ECH-42 | [Phase A.2] Seal Day 0 | A | IN PROGRESS | — |
| 3 | ECH-43 | [Phase B.1] Change log | B | Backlog | — |

## Phase A · Instrument

Worktree   ../echo-hq-phase-a
Branch     feat/phase-a-instrument
PR         not opened — opens at the checkpoint
Retained   —

## ECH-42 — Seal Day 0

Outcome    The Day 0 snapshot is written once and cannot be overwritten.
Cycles     1 of 3

Criteria
- [x] A second seal attempt is rejected with a clear error
- [ ] The seal is recorded with its timestamp and source commit
- [ ] The existing daily job keeps passing

Decisions
- Retry budget 3, per plan §Phase A — no source change needed

Findings
- [ ] Review flagged: empty-response path untested

Stopped
- Awaiting a decision on row backfill — see the discrepancy comment on ECH-42

## Carried forward

- Nothing outstanding from Phase A.
```

Keep it terse. It is a working record, not a report — the report is written fresh at the
close.

## When to update it

| Point | Write |
|---|---|
| Immediately after the step-1 gate | Header, order table, checkpoints |
| Start of a phase | Its section: worktree, branch |
| Start of an issue | Its section: outcome, criteria |
| A decision made | Under `Decisions`, with the evidence |
| A review finding | Under `Findings`, unchecked |
| A finding resolved | Check it off |
| A failed verification cycle | Increment `Cycles` |
| Blocked, or the grind limit hit | `Stopped` — what happened, what is awaited, and any `WIP (unreviewed)` commit left on the branch |
| An approval given in chat | Under `Decisions`, verbatim, dated — **and mirrored to a Linear comment**. A transcript is not a citation a later session can open |
| End of an issue | State `IN REVIEW`, criteria all checked |
| Each checkpoint | Phase PR number, every issue to `DONE`, retained artifacts, `Carried forward` |

## Resuming

After any interruption — a new session, a context reset, a stopped run:

1. Read the ledger. **If there is none** — a different machine, a cleared checkout — rebuild
   it from Linear rather than stopping. Issue states, evidence comments, **approval-record
   comments and discrepancy comments** carry the facts; the approval records repopulate
   `Decisions`, so read every issue's comments, not just its description. Say that you
   rebuilt it, and what did not survive.
2. Take the rebuilt ledger as the account of any issue already `In Progress` or `Done`.
   Only stop and ask if Linear shows work the rebuilt record cannot explain — for example an
   issue `In Progress` with no evidence comment and no branch.
3. **Re-read the project and every issue from Linear.**
4. Where they differ, trust Linear and correct the ledger.
5. Rebuild what the ledger does not carry: the model, the security invariants, the external
   gates, the repo instructions. The ledger records progress, not understanding.
6. **Re-print the delivery plan for what remains and wait for a yes.** The gate belongs to
   the session, not to the project — the earlier approval was given to a session that is
   gone.
7. Resume at the first issue that is **neither Done nor already finished**. An issue sitting
   `In Review` with an evidence comment and its commit on the phase branch is finished —
   **do not re-implement it.** Verify the commit is there, and move on. Only an issue with no
   evidence comment and no commit is genuinely unstarted.
8. If the phase branch and worktree still exist, reuse them. Cut a new worktree only when
   starting a phase that has none.
9. Then continue from step 2. **Re-run the phase's pre-flight if the phase has not started or
   a phase boundary was crossed**; if you are resuming mid-phase and it already ran against
   this same merged code, only the resumed issue's own re-read is needed.

Never resume from the ledger alone. It records what you intended; Linear records what
happened.

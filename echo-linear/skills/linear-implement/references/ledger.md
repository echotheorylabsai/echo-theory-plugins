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
  so it rides along in that phase's PR. Never edit `.gitignore` in the primary checkout: an
  uncommitted change there makes the next `git pull --ff-only` abort, and never commit it
  straight to the integration branch — that skips review and fails outright on a protected
  branch. Mention it in the step-1 plan so an unrelated line in that PR is not a surprise.

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
| Blocked, or the grind limit hit | `Stopped` — what happened, what is awaited |
| End of an issue | State `IN REVIEW`, criteria all checked |
| Each checkpoint | Phase PR number, every issue to `DONE`, retained artifacts, `Carried forward` |

## Resuming

After any interruption — a new session, a context reset, a stopped run:

1. Read the ledger. **If there is none** — a different machine, a cleared checkout — rebuild
   it from Linear rather than stopping: issue states plus evidence comments carry the same
   facts. Say that you rebuilt it, and that the pre-`In Review` detail is gone.
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
7. Then resume at the first issue that is not Done, from step 2, including its pre-flight
   and its re-read.

Never resume from the ledger alone. It records what you intended; Linear records what
happened.

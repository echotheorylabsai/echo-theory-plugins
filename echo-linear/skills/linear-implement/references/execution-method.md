# Execution method

Method serves the approved plan. It never overrides it. If a method here conflicts with the
approved sources, the sources win and you stop and say so.

## Isolation — one milestone, one worktree, one branch, one PR

**The unit is the milestone, not the issue.** Every issue in a phase is built in the same
worktree, each as its own commit, and the whole phase ships as one PR at the checkpoint.

Why: a PR per issue multiplies CI runs and merges — six issues means six PR pipelines plus
six merge pipelines. Per milestone that is two. The phase is also already the unit the user
approves at step 3, so the merge and the checkpoint gate land together.

**Cut the worktree once per milestone**, after the previous milestone's PR merged. Update
the local integration branch first — your local copy does not know about that merge yet, and
skipping it cuts the phase from stale code.

```
git fetch origin
git checkout <integration-branch> && git pull --ff-only
git worktree add ../<repo>-phase-a -b feat/<phase-slug> <integration-branch>
```

**Do not reach for `git branch -f`.** Git refuses to force-update a branch that is checked
out in any worktree — including the primary checkout, which is where this runs — and fails
with exit 128 before anything is cut. `checkout` + `pull --ff-only` is the working form.

If `pull --ff-only` refuses, read *why* before concluding anything — the two causes need
opposite responses:

| Message | Cause | Do |
|---|---|---|
| `Your local changes to <file> would be overwritten` | The primary checkout has uncommitted edits | Find out whose. If they are yours, you put them in the wrong place — move them to a worktree. If they are not, **stop and ask**. Never discard them |
| `Not possible to fast-forward` / divergent branches | The local branch has commits the remote does not | **Stop and ask** — do not merge, rebase or reset past it |

**Branch names.** The repo's own convention wins wherever it has one — check recent branches
and any contributing guide first, and follow what you find. Absent a convention:

- with milestones: `feat/<phase-slug>`, e.g. `feat/phase-a-instrument`
- without: the checkpoint boundaries confirmed at step 1 are the branch boundaries, and each
  branch is named for the issues it carries — `feat/<project-slug>-ech-41-ech-42`, or
  `feat/<project-slug>-batch-1` when that is unwieldy

Either way, put the chosen names in the step-1 plan so they are approved with everything else.

**Commit per issue.** Each issue gets its own commit or commits on the phase branch, with
the issue key in the message, so the phase PR stays reviewable issue by issue.

Work happens inside that worktree only. The **primary checkout** holds the ledger and is
where you run worktree removal from — not from inside the worktree you are removing.

### What this costs

Issues inside a phase see each other's work immediately — no fetch, no merge between them.
But recovery is coarser: if a phase PR is rejected, **all of its issues roll back together.**
Keep phases small enough that this is acceptable; `linear-sync` already targets 1–4 issues
per milestone.

## `origin/<integration-branch>` is a moving target

**Assume other agents and people are merging into it while you work.** A phase that takes an
hour is an hour of other people's commits you have not seen. Treat every fetch result as
current only at the instant you fetched it.

### Re-sync at three points, not one

| When | Why |
|---|---|
| Before cutting the phase worktree | The obvious one |
| **Immediately before opening the phase PR** | Otherwise you open a PR against a base that moved |
| **Immediately before merging** | It can move again between opening and merging |

At each of the last two: `git fetch origin`, and if the integration branch advanced,
integrate it into the phase branch — merge or rebase, whichever the repo already uses.

### Re-verify after every re-sync

**A green test run from before an integration proves nothing about the code after it.** Once
you have pulled someone else's commits in, run the relevant suite again. A clean textual
merge can still be semantically broken: another agent may have changed a function signature,
a schema, or a default your work depends on, with no conflict marker anywhere.

This is the failure this whole section exists to prevent. Merging on stale green is how two
correct branches produce a broken integration branch.

### When that re-verification fails

There is no conflict to look at — someone else's merged change broke your work silently.
**Treat it exactly like a conflict: stop and ask.** Their change is in the integration branch
and yours is not, so theirs is the one that stands; whether yours adapts, or theirs was
wrong, is not yours to decide alone.

Report what broke, the commit that broke it, and what each side appears to be doing. The
grind limit does not apply — it counts attempts at one issue's own criteria, and this failure
belongs to no issue.

**The one exception:** a purely mechanical adaptation with no behaviour change — a renamed
import, a moved constant, a signature that gained a defaulted parameter. Make it, re-verify,
and say in the PR what you adapted and to whose commit. Anything that changes what your code
*does* is the material gate.

### A conflict is a stop

If integrating produces a conflict, **stop and ask.** Someone else's change collided with
yours and their intent is not yours to guess. Report both sides, the files, and what each
appears to be doing.

The one exception: a conflict with no semantic content — an append-only list, an import
block, a lockfile the repo regenerates. Resolve those, say in the PR that you did, and say
which.

### Never rewrite a shared branch

No force-push to a branch that has been pushed. No rebase of the integration branch. No
`git reset` to get past a divergence. If your local integration branch has commits the
remote does not, that is a stop — see above.

### If it keeps moving

If the integration branch advances more than twice during one phase, the phase is too long
for how busy this repo is. Say so at the checkpoint and offer to shorten the remaining
boundaries. Repeated re-syncs are a signal, not just a chore.

### Someone else may be running this too

At step 0, note any other worktrees or recent branches that suggest concurrent work, and say
so in the delivery plan. An issue `In Progress` that no record can explain — no evidence
comment, no branch — means someone else is in there: stop and ask, do not take it over. An
issue your ledger *or* a ledger rebuilt from Linear accounts for is your own earlier run
(`ledger.md` § Resuming).

## Test first

For any behaviour change:

1. Write the test that proves the requirement.
2. Run it. **Confirm it fails, and fails for the right reason** — a test that errors on a
   missing import proves nothing.
3. Write the smallest change that makes it pass.
4. Run it again and confirm it passes.

A non-code deliverable gets an equally falsifiable check — a command whose output you can
read, a file whose content you can diff, a link that resolves. "I looked at it" is not a
check.

Prove an ordering or concurrency claim with **explicit observable boundaries** — a recorded
event, a lock, a barrier. Never with a timing sleep or an unconstrained parallel call.

**Skipping test-first needs the user's approval, not your own.** If you believe it is
genuinely inapplicable for an issue, say which issue and why, and ask. Record the answer as
an **approval-record comment** (`linear-updates.md`) — the same format as any other approval,
so reconciliation can find it — and note it in the ledger.

**Passing tests are evidence about code.** They are never proof of deployment, provider
state, or production authorization.

## Delegation

v1 runs issues **sequentially**. Parallelism applies only *within* an issue, and only to
read-only investigation and independent reviews. Keep everything that touches shared
mutable state, security, migrations, rollout or integration in one sequence.

### The subagent brief

Narrow and self-contained. Give it:

- the specific issue or task, and nothing else's history
- links to the authoritative sources
- the constraints and the interfaces it may touch
- the evidence it must return
- where to report

**Never** hand over the whole project history, and never let it redefine scope. Use a fresh
implementer per independent task and a **separate, read-only** reviewer after each.

**Do not trust a completion claim.** Read the diff and the verification output yourself.

## Independent review

After each issue's implementation passes verification, **before committing it** to the phase
branch. Not once per phase — once per issue.

Give the reviewer the current code, the tests, the approved acceptance criteria and the
evidence — **not your reasoning**. The point is to find the gap between what you meant and
what is there.

- **Harness with subagents:** run it in a clean-context subagent.
- **Harness without:** run an explicit fresh-context pass that separates verified facts,
  assumptions, and external gates.

Fix **significant** findings, re-run verification, and re-review after a significant change.
Carry unresolved findings into the ledger — never past the close.

**"Significant" here is not "material."** A significant review finding is one worth fixing
before shipping. *Material* is the term reserved for the gate that halts the run and asks the
user, and it applies only to the categories listed in `SKILL.md`. A review nit is not a
reason to stop and ask.

## Grind limit

A **verification cycle** is one implement-then-verify attempt *after* the first
deliberately-failing test. The red test itself is not a failure, and neither is a re-run
after fixing a review finding — the counter tracks failures to satisfy the issue's own
criteria, nothing else.

**The counter resets** when the user reviews a stop and says continue, and at the start of
each issue. Record it in the ledger so a resumed session does not inherit a stale count.

If the user's answer to a stop is itself a change — "do it this other way" — that is a
material change, not a continuation. Take it through the gate and record it.

Three failed cycles on one issue is the stop. Commit the work in progress to its branch so
the evidence survives — prefix the message `WIP (unreviewed):` and record it in the ledger,
because it has not been through independent review and must not ride into the phase PR
unexamined. Record what failed, what you tried and what you believe is wrong, then report and
ask. Before the phase PR opens, every `WIP (unreviewed)` commit must be finished and reviewed,
or dropped from the branch. Grinding past this burns hours and usually means the issue or the
source is wrong.

## Post-merge cleanup

Runs **once per milestone**, and only after the phase PR's merge is confirmed — that it
merged into the intended integration branch and that the branch contains the result.

Nothing is cleaned up mid-phase. The worktree stays until its whole phase has landed.

**Under a squash or rebase merge, commit ancestry will say the branch is unmerged even
though the content landed.** Confirm by content — the PR shows merged on the remote and the
change is present on the integration branch — not by `git branch --contains`. That is a
successful merge, not an unverifiable one.

If a merge, a required deployment, or another required external gate is genuinely pending,
failed or unverifiable: **report that and retain the worktree and branch** unless told
otherwise. A merged PR alone is not deployment proof; verify deployment against the
project's approved release evidence.

Then:

1. Confirm the exact dedicated feature-worktree path — **never the primary checkout** — the
   feature branch, the integration branch, and that no remaining worktree has the feature
   branch checked out.
2. Confirm each issue's record is accurate — the states were already set to `Done` at
   checkpoint step 5; do not set them again. Re-read them. Add a comment **only** if
   something new is true: the merge landed differently, or an artifact is being retained. Do
   not post second "done" comments — the phase PR link lives in the project status update.
3. From the primary checkout, remove **only that exact worktree** — `git worktree remove
   <path>`. If it refuses because of untracked build artifacts (`__pycache__`,
   `.pytest_cache`, coverage output), delete those files and retry. **Never
   `--force`** — it discards uncommitted work irreversibly, and there is no way to tell from
   outside whether that work mattered. If it still refuses, retain the worktree and report.
4. Delete **only that exact local branch**, non-force: `git branch -d <branch>`.

   **`-d` is a weaker safety net than it looks.** After a squash merge it succeeds — verified,
   exit 0 — printing only `warning: deleting branch 'x' that has been merged to
   'refs/remotes/origin/x', but not yet merged to HEAD`. It is satisfied by the
   *remote-tracking ref*, not by the integration branch actually containing the work. So it
   will cheerfully delete a branch whose commits never landed.

   **Therefore: confirm the merge by content first (item 0 above), and treat that as the
   safety check — not `-d`'s exit code.** Read the warning; if it names a remote ref rather
   than your integration branch, you have only proved the branch reached the remote.

   If `-d` does refuse — the remote branch was deleted and pruned, so git can no longer see it
   as merged — retain the branch and report why. **Never force-delete.** `git branch
   --contains` will correctly call a squashed branch unmerged; that is expected and is not a
   reason to force anything.
5. Prune stale remote-tracking references only if authorized. **Never** delete a remote
   branch, tag, release or deployment resource unless explicitly asked.

At the **end of a milestone**, not per issue, update the Linear project record with what
landed. Per-issue project updates are noise (`linear-updates.md`).

If audit, rollback or an active review requires retention, preserve the worktree and branch
and record why in the ledger and on the issue.

## Harness portability

This skill runs in Claude Code and Codex.

| Capability | How to treat it |
|---|---|
| git worktrees, branches, test runners | Universal. Use directly. |
| PR creation and merge | Assume nothing. Detect the host's CLI (`gh` or equivalent) and whether it is authenticated. If there is none, or the branch is protected, say so in the step-1 plan and route through `In Review` instead of merging. |
| Superpowers skills — worktrees, TDD, subagent-driven development, code review, verification | Use **where present**. The discipline is the requirement; the skill is the upgrade. |
| Subagents | Claude Code has them; assume Codex may not. Fall back to an explicit fresh-context pass with the same brief. |
| Linear operations | Name by capability, never by harness-specific tool name. |

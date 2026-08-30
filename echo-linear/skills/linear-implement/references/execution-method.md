# Execution method

Method serves the approved plan. It never overrides it. If a method here conflicts with the
approved sources, the sources win and you stop and say so.

## Isolation — one issue, one worktree, one branch, one PR

**Update the local integration branch before every worktree.** The previous issue merged on
the remote; your local copy does not know that yet. Skipping this cuts the next issue from
stale code and its PR will conflict with or revert the last one.

```
git fetch origin
git checkout <integration-branch> && git pull --ff-only
git worktree add ../<repo>-ech-41 -b feat/ech-41-<slug> <integration-branch>
```

**Do not reach for `git branch -f`.** Git refuses to force-update a branch that is checked
out in any worktree — including the primary checkout, which is where this runs — and fails
with exit 128 before anything is cut. `checkout` + `pull --ff-only` is the working form.

If `pull --ff-only` refuses, the local branch has commits the remote does not. **Stop and
ask** — do not merge, rebase or reset your way past it.

Branch name: `feat/<issue-key-lowercased>-<short-slug>`. Use the repo's own convention if it
has one — check recent branches and any contributing guide first.

Work happens inside that worktree only. The **primary checkout** holds the ledger and is
where you run worktree removal from — "not from inside the worktree you are removing".

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
genuinely inapplicable for an issue, say which issue and why, and ask. Record the approval
in the ledger and the evidence comment.

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

After each issue's implementation passes verification, before the PR.

Give the reviewer the current code, the tests, the approved acceptance criteria and the
evidence — **not your reasoning**. The point is to find the gap between what you meant and
what is there.

- **Harness with subagents:** run it in a clean-context subagent.
- **Harness without:** run an explicit fresh-context pass that separates verified facts,
  assumptions, and external gates.

Fix material findings, re-run verification, and re-review after any material change. Carry
unresolved findings into the ledger — never past the close.

## Grind limit

A **verification cycle** is one implement-then-verify attempt *after* the first
deliberately-failing test. The red test itself is not a failure.

Three failed cycles on one issue is the stop. Commit the work in progress to its branch so
the evidence survives, record what failed, what you tried and what you believe is wrong,
then report and ask. Grinding past this burns hours and usually means the issue or the
source is wrong.

## Post-merge cleanup

Runs per issue, and **only after the merge is confirmed** — that it merged into the intended
integration branch and that the branch contains the result.

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
2. Confirm the issue's Linear record is accurate — the evidence comment from step 2.9 names
   the merged PR and any deployment evidence. Re-read it. Add a comment here **only** if
   something new is true: the merge landed differently, or an artifact is being retained.
   Do not post a second "done" comment.
3. From the primary checkout, remove **only that exact worktree** — `git worktree remove
   <path>`. If it refuses because of untracked build artifacts (`__pycache__`,
   `.pytest_cache`, coverage output), delete those files and retry. **Never
   `--force`** — it discards uncommitted work irreversibly, and there is no way to tell from
   outside whether that work mattered. If it still refuses, retain the worktree and report.
4. Delete **only that exact local branch**, non-force: `git branch -d <branch>`. A squash or
   rebase merge will make this refuse — retain the branch and report why. **Never
   force-delete.**
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

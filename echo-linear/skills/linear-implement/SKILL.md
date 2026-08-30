---
name: linear-implement
description: Use when an approved Linear project whose issues already exist needs to be built end to end — issue by issue, test-first, each independently reviewed and merged. Triggers include "implement the Linear project", "execute the Linear plan", "build the issues in this Linear project", "continue implementing <project>", or approving a linear-sync run and wanting the work actually done. Does not create Linear projects, milestones or issues — that is linear-sync.
---

# linear-implement

You are the execution owner for one Linear project. Deliver its **goal**, not merely its
closed issues.

All Linear work goes through the **Linear MCP**. Refer to its operations by capability —
get project, list issues, save issue, save comment — never by harness-specific tool names,
because this skill runs in more than one harness.

**Reference paths below are relative to the file they appear in.** `references/…` from this
file; `../../linear-sync/…` from inside `references/`.

## The loop

```
0  ADOPT       read the whole project + approved sources → state the model
1  GATE        show the delivery plan → wait for an explicit yes
2  PHASE       PRE-FLIGHT: are this phase's issues and docs still true? → then
               per issue: re-read → test-first → implement → independent
               review → commit → In Review
3  CHECKPOINT  reconcile docs into the phase branch → re-sync → PR → merge →
               issues Done → reconcile Linear → clean up → report → wait
4  CLOSE       full reconciliation, whole-project review, honest report
```

Step 1 and step 3 are gates. So is the **material-change decision** inside step 2.
**None may be skipped — not even on a one-issue project, and not on a resume.**

**The docs are a deliverable.** A project that ships correct code and leaves a spec
describing something else has failed. Reconciliation runs before every phase and after every
phase: `references/reconciliation.md`.

This skill never creates a Linear project, milestone or issue. It executes what is already
approved.

**Hand back to `linear-sync` whenever the work needs a Linear artifact that does not exist**
— no project yet, an approved change that needs a new issue, work that has to be re-scoped
across issues, or a phase that needs a milestone. Say what is needed and why, then stop. Do
not improvise around the missing artifact, and do not create it yourself.

**Handing back mid-phase, and coming back.** The current phase keeps its worktree, its branch
and its `In Review` issues; nothing is cleaned up and nothing is reverted.

- Tell `linear-sync` the source is the **approval-record comment and the discrepancy comment**
  on the affected issue, not a file. Those are reachable, so its source gate is satisfied —
  say so, rather than pushing the phase branch to manufacture a URL.
- Say whether the new issue joins this phase or waits for the next. Joining an in-flight
  phase means it ships in that PR; if unsure, ask.
- On return, this is a **resume**: re-read from Linear, add the new issue to the ledger's
  order table, re-print the delivery plan for what remains, and get a yes. Then continue
  **within the phase** at the next unfinished issue. The phase's pre-flight already ran and
  the phase has not merged since, so re-run only the part that changed: the new issue's own
  premise. `ledger.md` § Resuming covers the general case, where the pre-flight does re-run
  because a phase boundary was crossed.

### Source precedence

The **issue** defines the immediate outcome. The **approved sources** define behaviour,
constraints, sequence and acceptance criteria. Where an issue is silent, the sources
govern. Where they conflict, that is a material change — stop and ask.

---

## 0. Adopt the project

Identify the project from the invocation — an identifier, a URL or a name. If you were
given an **issue** key, resolve it to its parent project and confirm which project you are
about to execute. **If none was named, ask.** Never guess, never take the most recent
project.

Read it **whole** from Linear: overview, milestones, every issue, attachments, links,
**comments**, relations, dependencies and states. Comments carry the approval records
everything downstream depends on.

**Then decide whether this is a resume — from Linear, not from disk.** If any issue is
already `In Progress`, `In Review` or `Done`, **it is**, whether or not a ledger exists
locally. A ledger is a convenience; a different machine or a cleared checkout has none, and
keying off the file would silently start a fresh run over live work.

Follow `references/ledger.md` § Resuming — read the ledger, or rebuild it from Linear when
there is none. A resume still passes through the step-1 gate.

**On a resume, check the last completed phase's reconciliation ran.** If a phase is `Done`
but the plan, its issues or its milestone still describe something else, the previous session
died between the merge and its reconciliation.

**Do not fix it here** — step 1 forbids writing anything before the gate. Say so in the
delivery plan as work to be done first, and carry it out immediately after the yes, before
the next phase's pre-flight. Its approval records are what that pre-flight has to read. Doc
edits ride in the next phase's PR; Linear edits happen straight away.

Then follow every link and read the **approved sources themselves**, not the issue's
summary of them. Identify the authoritative baseline — prefer a committed, pushed, pinned
link. Confirm each source is **readable**: a pushed URL is best; a repo-relative path is
acceptable when the file is present and its content matches what the issue was written from.
Where you cannot tell — an uncommitted or gitignored source has nothing to pin against — say
so in the delivery plan rather than asserting it is current.

**Determine the integration branch.** The repo's default branch, unless its instructions
name another. State which you picked. If there is no clear default, ask.

**Check now whether `.linear-implement/` is already gitignored**, so the delivery plan can say
whether a `.gitignore` line rides in the first phase's PR. Nothing is written that the plan
did not show, so this cannot wait until the ledger is created.

**List the workspace's states.** This plugin runs in workspaces other than the one it was
written for. The whole per-milestone model rests on there being a state meaning *finished
but not merged* — `In Review` in the expected workspace. Find the equivalent and name it in
the delivery plan. If the workspace has no such state, say so and ask which to use; do not
invent one, and do not fall back to marking issues `Done` before they merge. Full workspace
notes: `../linear-sync/references/conventions.md`.

Then read the repo: its instructions, **its docs**, the code this work touches, its tests,
its deployment context.

Build the model, out loud and briefly: goal, boundaries, data and request flows,
authorization and security invariants, rollout and external gates, dependencies,
acceptance criteria.

Derive execution order from explicit dependencies, milestones and issue ordering. Where
issues carry no blocking relation, **numbering is reading order, not a constraint** — say
so, and execute in numbered order unless the sources give a reason not to. **Never invent
phases, issues, scope, labels or dependencies.**

### Stop conditions

Any of these ends step 0. Report it and ask — write nothing.

- Sources conflict, are mutable, or none is identifiably the approved one.
- A source cannot be read at all, or its link does not resolve.
- An issue has no acceptance criteria you could actually check.
- A component the work **depends on** does not exist in the repo. (A component the work
  **creates** is expected to be absent — that is not a stop.)
- The primary checkout has **any** uncommitted change. The untracked ledger directory is the
  one exception; its `.gitignore` line is edited in a worktree, never here.
- No Linear project exists for this work — that is `linear-sync`'s job, not yours.

Do not synthesize a plan to fill a gap. A confident wrong execution is worse than a
stopped one.

## 1. Start gate

Print the delivery plan and wait. **Nothing is written to code, to disk or to Linear before
the yes** — the ledger included.

```
DELIVERY PLAN — Content Intelligence v2
Baseline     docs/superpowers/plans/2026-08-20-content-v2-plan.md @ abc1234 (pushed)
Integration  main · clean · one worktree, branch and PR per milestone

Phase A · Instrument            branch feat/phase-a-instrument
  ECH-41  [Phase A.1] Record the baseline    Backlog
  ECH-42  [Phase A.2] Seal Day 0             Backlog  ← blocked by ECH-41
Phase B · Report                branch feat/phase-b-report
  ECH-43  [Phase B.1] Change log             Backlog  ← blocked by ECH-42

Checkpoints  after Phase A · after Phase B
Gates        PR review — say who merges
Also in PR   one .gitignore line for .linear-implement/  (Phase A)
Risks        ECH-42 touches the production data export

Start implementation?
```

**Everything that will be written appears here.** Branch names, the checkpoint boundaries,
who merges, and any incidental change riding in a PR — such as the ledger's `.gitignore`
line. Nothing is written that this table did not show.

**Checkpoint boundaries are the project's milestones.** A project with no milestones
proposes boundaries **of size, not of phase** — every second issue, or every issue for
risky work — and has them confirmed here, along with a branch name for each. That is a
run-length decision, not an invented roadmap; nothing is written to Linear.

```
Batch 1  ECH-41, ECH-42        branch feat/content-v2-batch-1
Batch 2  ECH-43, ECH-44        branch feat/content-v2-batch-2
```

**Name who merges — and default to *not you*.** Ask in the plan. **If the answer is anything
other than an explicit "you may merge it", a human merges.** A bare `yes` to the gate approves
the plan, not merge authority.

This is deliberate. Merging into a shared branch is irreversible and outward-facing, and the
reader of this plan is agreeing to a build, not to an unattended merge. Detecting a PR tool
and an unprotected branch is capability, not permission.

**Say if the repo is busy.** If other worktrees or recent branches suggest concurrent agents
or people, note it: the integration branch will move under this run, and phases may need to
be shorter.

Only after the yes: open the ledger (`references/ledger.md`) and post **one** concise
project status update — goal, order, dependencies, material risks or gates, next unblocked
issue. Not a restatement of the plan.

## 2. Execute a phase

**"Phase" means a milestone, or — in a project with none — one of the batches confirmed at
the step-1 gate.** Everything below applies to both: the worktree, the pre-flight, the
post-flight, the PR, and the rule that an in-phase blocker is satisfied at `In Review`.

### Pre-flight — before the first issue of every phase

Earlier phases changed the codebase; this phase's issues were written before that happened.

**Refresh the primary checkout first** — `git fetch origin && git checkout <integration> && git
pull --ff-only`. Without it the pre-flight judges this phase's issues against a working tree
that predates the previous phase's merge, which is exactly what it exists to catch. Any
catch-up reconciliation carried over from step 0 happens here too, in the phase worktree once
it is cut.

Re-read this phase's issues from Linear and the sources they link, and check them against
the code **as it now stands**: are the acceptance criteria still achievable and still
meaningful, do the components each issue depends on now exist, does the plan's approach
still fit what it will build on, do the dependencies still hold?

**An issue whose premise the last phase invalidated stops the phase.** Report and ask before
writing code — building against a stale criterion produces work that passes its issue and
misses the goal. Full procedure: `references/reconciliation.md`.

### Then, one issue at a time

Work the phase's issues in order, one at a time, skipping any already Done.

**What "unblocked" means here.** A blocker inside the same phase is satisfied when its work
is **committed and `In Review`** — not when it is `Done`. Issues in a phase all reach `Done`
together when the phase PR merges, so waiting for `Done` would deadlock on the second issue
of every phase. A blocker in an **earlier** phase must be `Done`, which it is, because that
phase merged before this one started.

Before setting an issue In Progress, re-read its current Linear record and every linked
source — either may have changed since step 0.

Method for steps 2–7 is in `references/execution-method.md`. **Read it before step 2.**

1. **Restate** the smallest shippable outcome and its acceptance criteria in the ledger.
2. **Isolate** — work in **this milestone's** worktree. One milestone, one worktree, one
   branch, one PR; one commit per issue inside it. At the *first* issue of a phase, fetch
   and update the local integration branch, then cut the worktree from it; later issues in
   the same phase reuse it. **Other agents merge into that branch while you work** — it is
   re-synced again before the PR and before the merge, never assumed still current. Never
   implement on the integration branch. Commands and naming: `execution-method.md`.
3. **Inspect** the owning code, tests, repo instructions and established patterns. Keep the
   design minimal — no speculative abstraction, no unrelated cleanup.
4. **Set state** `In Progress`.
5. **Test first** — a failing test that proves the requirement, confirmed failing for the
   right reason, then the smallest change that makes it pass. Skipping test-first needs the
   user's approval, not your own. Details: `execution-method.md`.
6. **Verify** — focused checks while iterating, then the relevant broader suite. **Passing
   tests are evidence about code — never proof of deployment or production state.** Prove
   ordering or concurrency with observable boundaries, never with timing sleeps.
7. **Review independently** — read-only, clean context, given the diff, the tests, the
   approved acceptance criteria and the evidence, never your reasoning. Harness fallbacks:
   `execution-method.md`.
8. **Land it on the phase branch** — commit, with the issue key in the message.
9. **Record** — one evidence comment on the issue, then set it `In Review`: the work is done
   and reviewed, but nothing has merged yet.
10. **Next issue in this phase**, from step 1. The last issue of the phase goes to step 3.

Implement **only approved scope**. Take no destructive, irreversible, production, provider
or external-account action without explicit authorization and satisfied gates.

Move on only when the current issue is complete and its real dependencies permit it.

**States, evidence comments and status updates:** `references/linear-updates.md`. In short —
`In Progress` while working, `In Review` once its work is committed to the phase branch,
`Done` only when the phase PR has merged and been confirmed. Blocked or stopped stays
`In Progress` with a comment. **A blocked issue is never Done.**

**Descoping an issue.** If the user answers a stop with "skip it and carry on", that is a
scope change: take it through the material gate, post the approval record, and hand back to
`linear-sync` if the issue must be re-scoped rather than dropped. Then set the skipped issue
to the workspace's unstarted state with a comment saying it was descoped and why, revert or
drop its `WIP (unreviewed):` commits, and treat its blocker as satisfied for the issues after
it. It is **not** `Done`, and checkpoint item 6 must not sweep it there.

**Grind limit.** A *verification cycle* is one implement-then-verify attempt after the
first red test. Three failed cycles on one issue **stops the run**: commit the work in
progress so the evidence survives, **prefixed `WIP (unreviewed):`**, record what failed and
what you believe is wrong in the ledger and on the issue, leave the state as it is, report,
and ask. Do not keep grinding.

**No `WIP (unreviewed):` commit may be in the phase PR.** Before opening it, every one must
be finished and independently reviewed, or dropped from the branch. If the PR is *already*
open — feedback stopped mid-fix — you cannot drop it without a force-push, which is
forbidden: finish and review it, or revert it with a new commit that says why.

### The material-change gate

When evidence shows an approved source is wrong, incomplete or unsafe, **stop at that
decision boundary.** Do not silently implement a different design. Commit whatever is
half-built as `WIP (unreviewed):` so it cannot reach a PR unexamined.

Two things you may do immediately, without approval:

- a factual issue comment — discrepancy, evidence, affected outcome, options (template in
  `linear-updates.md`)
- a non-decisional project status update reporting a risk or blocker

Neither may claim a decision or alter the approved roadmap. Commit the half-built work to
its branch so nothing is lost, leave the issue `In Progress`, and do not start the next
issue.

**The default is material.** A change is non-material only when **all five** hold:

- no observable behaviour changes
- no acceptance criterion changes
- no scope, sequence, dependency or milestone changes
- no security, authorization, data, rollout or external-authority impact
- the code itself forces it, and you can point at the evidence

**If you have to argue it, it is material.**

| | What happens |
|---|---|
| **Material** | Get explicit approval. **Then post an approval-record comment on the issue** — quoting what was approved, dated — *before* acting on it. Then update the authoritative source, then the affected Linear records under the safe-update rules. Re-read both before resuming. |
| **Non-material** | Post the same record comment, saying what the code forced and why it meets all five conditions. Update the implementation plan before coding. Then patch every affected issue with an anchored patch, attach the current source link if needed. Re-read the changed sources and records before resuming. |

**The approval-record comment is not optional, and it is not paperwork.** Reconciliation
later has to tell an approved deviation from an unapproved one, and its only test is whether
you can name where approval happened. Approval given in chat dies with the session. If it is
not in Linear, the next run cannot distinguish agreement from drift — and the plan you
rewrote afterwards is circular evidence for itself. Template: `linear-updates.md`.

A specification change that alters requirements or behaviour is **always** material.

## 3. Milestone checkpoint — ship the phase

Every issue in the phase is committed and `In Review`. Now the phase lands.

**Reconciliation happens on both sides of the merge, and the split is not arbitrary.** Files
tracked by git — the plan, the spec, repo docs — must be edited **in the worktree and
committed to the phase branch, before the PR opens**, so they ship with the code they
describe. There is no legal place to commit them afterwards: the branch has merged, the
primary checkout must stay clean, and the integration branch is barred. Linear records are
edited after the merge, because they cite the merged PR.

1. **Reconcile the docs, in the worktree.** Update the plan's section for this phase, and the
   spec where an **approved** change altered behaviour. Commit to the phase branch. An
   unapproved difference is the material gate, not an edit. `references/reconciliation.md`.
2. **Re-sync.** Fetch; if the integration branch moved while you worked, integrate it into the
   phase branch and **re-run verification** — green from before the integration proves
   nothing. A conflict is a stop. See `references/execution-method.md`.
3. **Open the PR** for the phase branch, listing each issue and its evidence. It carries the
   code *and* the doc updates.
4. **If a human must approve or merge it, say so, report, and wait** — hand back with the PR
   link and "tell me when it has merged, or what to change." Do not start the next phase;
   its worktree would be cut from a branch that does not contain this one.

   **When they say it merged:** skip item 5 — the merge has happened, so there is nothing to
   re-sync before it. **Confirm from the remote** that it landed (by content, under a squash
   or rebase). Then **re-run verification against the merged integration branch** before
   continuing at item 6: it may have moved for days while the PR sat, and a clean merge can
   still be semantically broken. Do not re-run pre-flight and do not restart the phase.

   **When they bring back review feedback:** apply it on the phase branch, re-verify, re-run
   the independent review for each issue the change touches, re-reconcile the docs if the
   change moved them, push, and return to **item 4** — the PR already exists; never open a
   second one. Name the issue in each commit; if the change spans two issues, split the
   commits and post an approval record on **each**.

   Feedback that changes behaviour, acceptance criteria or scope is a **material change** —
   take it through that gate first, even though a human asked for it. In this post-PR state
   the gate's "leave the issue `In Progress`" does not apply: the work is committed and
   reviewed, so issues **stay `In Review`** while the decision is pending.

   **If you cannot merge at all** — no PR tooling, or a branch you may never merge — this is
   an unsatisfied external gate, not a failure. Say so, leave the issues `In Review`, and stop
   at this checkpoint. Do not close the project behind it (step 4).
5. **Merge — only if the step-1 plan said you may.** Re-sync first; it can move between
   opening and merging. Then merge, and **confirm from the remote** that it landed on the
   intended integration branch — by content under a squash or rebase, not commit ancestry.
   If the plan did not grant merge authority, you are not here: item 4 is where you wait.
6. Move every issue in the phase from `In Review` to **`Done`**, and update the Linear
   project record. This is the only place issues become Done.
7. **Reconcile Linear.** Patch any issue whose description no longer describes what landed,
   fix the milestone body if its "accepted when" moved, and patch **remaining** issues this
   phase changed the premise of. No git is involved, so this belongs after the merge.
   `references/reconciliation.md`.
8. **Clean up** the worktree and branch per `references/execution-method.md`.
9. Report: issues shipped with their evidence, **what you reconciled on each side**, findings,
   risks, what comes next.

**Wait for a yes before starting the next milestone.**

If the run stops mid-phase — grind limit, a blocked decision, a rejected PR — the phase
branch is retained with its completed issues on it, and they stay `In Review`. Say plainly
which issues are on an unmerged branch; none of them has shipped.

## 4. Close honestly

Re-read the project and every issue from Linear. Never close from memory of what you
built.

**Run the full reconciliation pass** (`references/reconciliation.md`): read the spec, the
plan, the project, every milestone and every issue against the code that now exists.

Confirm that every required **outcome** — not merely every task — meets its approved
acceptance criteria; that required verification and independent reviews passed; and that
every external gate is satisfied or explicitly accepted as a separate follow-up.

Then run the final relevant repository verification and **one final independent
whole-project review**. "Significant" means worth fixing before shipping, not the
material-change gate.

**Fixing a close-time finding needs its own worktree.** Every phase worktree is gone by now.
Cut one from the integration branch — `feat/<project-slug>-close` — fix there, re-verify,
re-review, and ship it as a final PR under the same rules as a phase: the plan said who
merges, and that still holds. Report it as a distinct PR, not folded into a phase.

If the finding is a scope change rather than a defect, it is the material gate and probably a
hand-back — not something to slip in at the close.

Report: verified results, external assumptions, completed issues, remaining gates, gaps —
and state plainly **either** that every document and Linear record describes what was built,
naming the commit or PR you checked against, **or** exactly which ones do not and why.

**A project that ships correct code and leaves a misleading spec has failed a required
outcome.** The next person to read it builds on the lie.

**Setting the project's own state is the user's call, not yours.** At the close, report that
every outcome is met and **ask** whether to mark the project complete. Never set it while a
required outcome sits behind an unsatisfied external gate, even if asked — say what the gate
is instead.

---

## Red flags — stop and go back

| Thought | Reality |
|---|---|
| "The project is clear enough, I'll just start" | Step 1 gates hours of work and a shared workspace. Print the plan, wait. |
| "It's a resume, the gate already happened" | It happened in a session that is gone. Re-print, re-confirm. |
| "It's a small fix, no need for a worktree" | The integration branch is not a workspace. One phase, one branch. |
| "This issue is finished, I'll mark it Done" | Nothing has merged yet. `In Review` until the phase PR lands. |
| "This change is obviously what they meant" | If you have to argue it is non-material, it is material. Stop and ask. |
| "The source is wrong, I'll implement it properly" | That is the drift this skill exists to prevent. Comment the evidence, then ask. |
| "Tests pass, so it's Done" | Done needs criteria, review and a merged PR. Tests are evidence about code, nothing more. |
| "I'll mark it Done and note the gap in a comment" | A blocked issue is never Done. State is a claim, not a courtesy. |
| "I'll write the test after — it's faster" | The failing test is what proves the requirement exists. First, or not at all. |
| "The reviewer said it was done" | Read the diff and the evidence yourself. A claim is not a verification. |
| "I'll tidy the rest of this file while I'm here" | Unrelated cleanup is scope nobody approved. |
| "The phase PR is up, I'll start the next phase" | The next worktree branches off a merge that has not happened. Wait. |
| "I fetched at the start of the phase, so I am current" | Other agents have merged since. Re-fetch before the PR and before the merge. |
| "The merge was clean, so the tests still pass" | A clean merge can still be semantically broken. Re-run them. |
| "This conflict is obviously mine to resolve" | It is someone else's change. Stop and ask unless it carries no meaning. |
| "The code is right, so I'll update the doc to match" | Only if the change was approved. Otherwise you are erasing evidence that something drifted. |
| "I'll tidy the docs at the end" | By then nobody remembers why. Reconcile at each boundary. |
| "Nothing changed this phase" | Say that only after re-reading both sides. |
| "It mostly works — I'll report success" | Report the gap plainly. A false completion claim costs more than the gap. |

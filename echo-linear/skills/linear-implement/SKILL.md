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
3  CHECKPOINT  phase ships: re-sync → PR → re-sync → merge → issues Done →
               POST-FLIGHT: make the docs and Linear match what shipped →
               clean up → report → wait
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

**Then check for a resume.** Look for a ledger under `.linear-implement/` matching that
project. If one exists, this run is a resume: follow `references/ledger.md` § Resuming, and
treat its record as the explanation for any issue already `In Progress` or `Done`. A resume
still passes through the step-1 gate.

Read it **whole** from Linear: overview, milestones, every issue, attachments, links,
comments, relations, dependencies and states.

Then follow every link and read the **approved sources themselves**, not the issue's
summary of them. Identify the authoritative baseline — prefer a committed, pushed, pinned
link. Confirm each source is **readable**: a pushed URL is best; a repo-relative path is
acceptable when the file is present and its content matches what the issue was written from.
Where you cannot tell — an uncommitted or gitignored source has nothing to pin against — say
so in the delivery plan rather than asserting it is current.

**Determine the integration branch.** The repo's default branch, unless its instructions
name another. State which you picked. If there is no clear default, ask.

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
- The primary checkout has uncommitted changes other than the ledger and its `.gitignore`
  entry.
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

Phase A · Instrument
  ECH-41  [Phase A.1] Record the baseline    Backlog
  ECH-42  [Phase A.2] Seal Day 0             Backlog  ← blocked by ECH-41
Phase B · Report
  ECH-43  [Phase B.1] Change log             Backlog  ← blocked by ECH-42

Checkpoints  after Phase A · after Phase B
Gates        PR review — say who merges
Risks        ECH-42 touches the production data export

Start implementation?
```

**Checkpoint boundaries are the project's milestones.** A project with no milestones
proposes boundaries **of size, not of phase** — every second issue, or every issue for
risky work — and has them confirmed here. That is a run-length decision, not an invented
roadmap; nothing is written to Linear.

**Name who merges.** If PRs need human approval, say so in the plan — it changes the flow at
the checkpoint.

**Say if the repo is busy.** If other worktrees or recent branches suggest concurrent agents
or people, note it: the integration branch will move under this run, and phases may need to
be shorter.

Only after the yes: open the ledger (`references/ledger.md`) and post **one** concise
project status update — goal, order, dependencies, material risks or gates, next unblocked
issue. Not a restatement of the plan.

## 2. Execute a phase

### Pre-flight — before the first issue of every phase

Earlier phases changed the codebase; this phase's issues were written before that happened.

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

**Grind limit.** A *verification cycle* is one implement-then-verify attempt after the
first red test. Three failed cycles on one issue **stops the run**: commit the work in
progress to the branch so the evidence survives, record what failed and what you believe is
wrong in the ledger and on the issue, leave the state as it is, report, and ask. Do not
keep grinding.

### The material-change gate

When evidence shows an approved source is wrong, incomplete or unsafe, **stop at that
decision boundary.** Do not silently implement a different design.

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
| **Material** | Get explicit approval first. Then update the authoritative source, then the affected Linear records under the safe-update rules. |
| **Non-material** | Update the implementation plan before coding. Then patch every affected issue with an anchored patch, attach the current source link if needed, comment explaining the change. Re-read the changed sources and records before resuming. |

A specification change that alters requirements or behaviour is **always** material.

## 3. Milestone checkpoint — ship the phase

Every issue in the phase is committed and `In Review`. Now the phase lands:

1. **Re-sync first.** Fetch; if the integration branch moved while you worked, integrate it
   into the phase branch and **re-run verification** — green from before the integration
   proves nothing. A conflict is a stop. See `references/execution-method.md`.
2. **Open the PR** for the phase branch, listing each issue and its evidence.
3. **If a human must approve or merge it, say so, report, and wait** — hand back with the PR
   link and "tell me when it has merged, or what to change." Do not start the next phase;
   its worktree would be cut from a branch that does not contain this one.

   **Re-entry.** When the user says it merged, resume at step 4 — do not restart the phase
   and do not re-run pre-flight. If they bring back **review feedback** instead: apply it on
   the phase branch, re-verify, push, and return here. Feedback that changes behaviour,
   acceptance criteria or scope is a **material change** — take it through that gate before
   implementing it, even though a human asked for it.
4. **Re-sync again before merging** — it can move between opening and merging. Once merged,
   **confirm from the remote** that it landed on the intended integration branch. Under a
   squash or rebase merge, confirm by content, not commit ancestry.
5. Move every issue in the phase from `In Review` to **`Done`**, and update the Linear
   project record. This is the only place issues become Done.
6. **Post-flight — make the record match what shipped.** Update the plan's section for this
   phase, patch any issue whose description no longer describes what landed, fix the
   milestone body if its "accepted when" moved, and patch **remaining** issues this phase
   changed the premise of. Only for changes that were approved — an unapproved difference is
   the material gate, not an edit. `references/reconciliation.md`.
7. **Clean up** the worktree and branch per `references/execution-method.md`.
8. Report: issues shipped with their evidence, **what you reconciled**, findings, risks, what
   comes next.

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
whole-project review**. Fix and re-review material findings before claiming anything.

Report: verified results, external assumptions, completed issues, remaining gates, gaps —
and state plainly **either** that every document and Linear record describes what was built,
naming the commit or PR you checked against, **or** exactly which ones do not and why.

**A project that ships correct code and leaves a misleading spec has failed a required
outcome.** The next person to read it builds on the lie.

**Never mark the project Done while a required outcome sits behind an unsatisfied external
gate**, unless the approved workflow explicitly reclassified it as a separate follow-up.

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

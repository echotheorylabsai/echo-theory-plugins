# linear-implement — design

**Date:** 2026-08-30
**Status:** Design approved, ready for implementation
**Deliverable:** second skill in the existing `echo-linear` plugin: `linear-implement`
**Harnesses:** Claude Code and Codex CLI (both installed; both have the Linear MCP configured)

---

## 1. Problem

`linear-sync` ends where the work begins. It leaves a Linear project whose issues are
written for a person to read and a coding agent to act on — and then someone has to open
each one and build it by hand.

Three things go wrong when a coding agent is pointed at that project without structure:

1. **It closes issues instead of delivering the goal.** Tasks get marked Done while the
   outcome the project existed for is still missing.
2. **It drifts from the approved plan.** Faced with a source that looks wrong, it quietly
   implements something better rather than stopping at the decision boundary.
3. **It runs out of context mid-project.** Six issues in, the model of the goal, the
   decisions made, and the unresolved findings are gone.

## 2. Goal

One skill that takes an approved Linear project and delivers its **goal** — issue by
issue, test-first, each independently reviewed, shipping a phase at a time — pausing for approval
before it starts and at every milestone boundary, and reporting honestly at the end.

## 3. Non-goals (v1)

- No parallel issue execution. Sequential only; dependencies are the point.
- No deployment automation and no rollback. Deployment can be a *gate* it verifies, never
  an action it performs.
- No creating Linear projects, milestones or issues. That is `linear-sync`'s job.
- No multi-project runs. One project per invocation.
- No new Linear labels, states or templates.
- No re-planning. If the plan is wrong, it stops and asks.

---

## 4. Why a skill, not an agent

| Option | Verdict |
|---|---|
| **Skill** | The only component that can pause and ask the user mid-run. Loads in Claude Code *and* Codex. Matches the plugin's existing convention. **Chosen.** |
| Subagent (`agents/`) | Cannot converse with the user, so every approval gate fails. Claude-Code-only, breaking the portability constraint in §10 of the `linear-sync` design. |
| Slash command | A viable thin entry point later. Not a home for the logic. |
| Hook | Fires on events, not on judgment. Wrong shape entirely. |

The skill still *uses* subagents internally — a fresh implementer per independent task, a
separate read-only reviewer after each — with an in-session fresh-context fallback where
they do not exist. This is the pattern `review-rubric.md` already establishes: the
discipline is the mechanism, the subagent is the upgrade.

---

## 5. Deliverable layout

```
echo-linear/skills/linear-implement/
├── SKILL.md                    the gated loop; deliberately thin
└── references/
    ├── execution-method.md     isolation, test-first, delegation, review, cleanup
    ├── linear-updates.md       truthful states, evidence comments, safe-update traps
    ├── reconciliation.md       keeping specs, plans and Linear true to the code
    └── ledger.md               the durable execution record
```

Same principle as `linear-sync`: `SKILL.md` carries only the loop and the decision rules.
Anything a future edit is likely to touch lives in a reference file.

---

## 6. The loop

```
0  ADOPT       read the whole project + approved sources → state the model
1  GATE        show the delivery plan → wait for an explicit yes
2  ISSUE       next unblocked issue only, in this phase's worktree: re-read →
               test-first → implement → independent review → commit → In Review
3  CHECKPOINT  phase ships: re-sync → PR → re-sync → merge → all its issues Done
               → clean up → report → wait
4  CLOSE       whole-project review, final verification, honest report
```

Step 1 and step 3 are gates. So is the **material-change decision** inside step 2. None
may be skipped, including on a single-issue project.

### 6.1 Step 0 — adopt

**Check for a resume first.** An existing ledger under `.linear-implement/` means this is a
resumed run: follow the ledger's resume protocol, then rejoin at step 1. A resume does not
skip the gate — the gate belongs to the session, not to the project.

Identify the project from the invocation (ID, URL or name). An issue key is resolved to its
parent project and confirmed. If none was named, ask. Never guess and never pick the most
recent project.

Read it whole from Linear — overview, milestones, every issue, attachments, links,
comments, relations, dependencies and states — then follow every link and read the
**approved sources themselves**, not their summaries in the issue.

Identify the authoritative baseline, preferring a committed, pushed, pinned link. Confirm
each source is **readable and stable** — a pushed URL is best, a repo-relative path is
acceptable when the file is present and unchanged. This must not be stricter than
`linear-sync`, which links unpushed repo paths by design; requiring sources to be committed
on the integration branch would dead-end the handoff between the two skills.

**Determine the integration branch** — the repo's default unless its instructions name
another. State which. If there is no clear default, ask.

Then read the repo: instructions, docs, the code the work touches, its tests, deployment
context. Build the model — goal, boundaries, data and request flows, authorization and
security invariants, rollout and external gates, dependencies, acceptance criteria.

Derive execution order from explicit dependencies, milestones and issue ordering. Where no
blocking relation exists, numbering is reading order, not a constraint. **Never invent
phases, issues, scope, labels or dependencies.**

**Source precedence.** The issue defines the immediate outcome; the approved sources define
behaviour, constraints, sequence and acceptance criteria. Where the issue is silent, the
sources govern. Where they conflict, that is a material change.

**Stop conditions.** Any of these ends step 0 without writing anything:

- sources conflict, are mutable, or none is identifiably approved
- a source cannot be read at all, or its link does not resolve
- an issue has no checkable acceptance criteria
- a component the work **depends on** does not exist in the repo — a component the work
  **creates** is expected to be absent, and is not a stop
- the primary checkout has uncommitted changes other than the ledger
- no Linear project exists for this work — that is `linear-sync`'s job

### 6.2 Step 1 — start gate

Print a delivery plan and wait for an explicit yes. Nothing is written to code **or to
Linear** before it.

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

Only after the yes: open the ledger and post **one** concise project status update — goal,
order, dependencies, material risks or gates, next unblocked issue. Not a restatement of the
plan. Nothing reaches disk before the yes, the ledger included.

Checkpoint boundaries are the project's milestones. A project with no milestones proposes
boundaries **of size, not of phase** — every second issue, or every issue for risky work.
That is a run-length decision confirmed in chat, not an invented roadmap, and nothing about
it is written to Linear; it therefore does not collide with "never invent phases".

The plan also **names who merges.** If PRs need human approval, the flow in step 2.8 routes
through `In Review` rather than merging.

### 6.3 Step 2 — execute, one issue at a time

Work only on the next unblocked issue. Before setting it In Progress, re-read its current
Linear record and every linked source — either may have changed since step 0.

1. **Restate** the smallest shippable outcome and its acceptance criteria in the ledger.
2. **Isolate** — **update the local integration branch from the remote first**, then cut a
   worktree and branch from it. Without the fetch, every issue after the first branches off
   code that does not contain the previous merge. One issue, one worktree, one branch, one
   PR. Never implement on the integration branch.
3. **Inspect** the owning code, tests, repo instructions and established patterns. Keep
   the design minimal. No speculative abstraction, no unrelated cleanup.
4. **Set state** `In Progress`.
5. **Test first** — a failing test that proves the requirement, confirmed failing for the
   right reason, then the smallest change that passes it. Non-code deliverables get an
   equally falsifiable check.
6. **Verify** — focused checks while iterating, then the relevant broader suite. Passing
   tests are evidence about code, never proof of deployment or production state.
7. **Review independently** — read-only, clean context, given the diff, the tests, the
   approved acceptance criteria and the evidence, never the writer's reasoning. Fix
   material findings, re-verify, re-review after material changes.
8. **Land it** — commit to the phase branch, with the issue key in the message.
9. **Record** — **one** evidence comment on the issue, then set it `In Review`.
10. **Next issue in this phase.** The last one goes to step 3, where the phase ships.

**Truthful states.** `In Progress` while working. `In Review` once the issue's work is
committed to the phase branch and reviewed — nothing has merged yet, so this is where most
finished issues sit until the checkpoint. A blocked or stopped issue **stays `In Progress`
with a comment** — the workspace has no `Blocked` state and inventing one is forbidden.
`Done` only when the phase PR has merged and been confirmed, set for every issue in the
phase at once. A blocked issue is never Done.

**Grind limit.** A *verification cycle* is one implement-then-verify attempt **after** the
first deliberately-failing test; the red test is not a strike. Three failed cycles on one
issue stops the run, commits the work so the evidence survives, records it, and reports.

**Never `--force`.** Not on a branch delete, and not on a worktree removal — the asymmetry
of forbidding one and not the other reads as permission. A worktree that refuses removal
because of build artifacts gets those files deleted and one retry; then it is retained and
reported.

### 6.4 The material-change gate

When evidence shows an approved source is wrong, incomplete or unsafe, **stop at that
decision boundary.** Do not silently implement a different design.

Two things may be done immediately, without approval:

- a factual issue comment recording the discrepancy, the evidence, the affected outcome
  and the options
- a non-decisional project status update reporting a risk or blocker

Neither may claim a decision or alter the approved roadmap.

**The default is material.** A change is non-material only when *all* of the following
hold:

- no observable behaviour changes
- no acceptance criterion changes
- no scope, sequence, dependency or milestone changes
- no security, authorization, data, rollout or external-authority impact
- the code itself forces it, and the evidence can be pointed at

If it has to be argued, it is material.

| | Path |
|---|---|
| **Material** | Get explicit approval first. Then update the authoritative source, then the affected Linear records under the safe-update rules. |
| **Non-material** | Update the implementation plan before coding. Then patch every affected issue with an anchored patch, attach the current source link if needed, and comment explaining the change. Re-read the changed sources and records before resuming. |

A specification change that alters requirements or behaviour is always material.

### 6.5 Step 3 — milestone checkpoint, where the phase ships

The checkpoint gate and the merge are the same moment. Every issue in the phase is committed
and `In Review`; now:

1. **Re-sync.** Fetch; if the integration branch moved, integrate it into the phase branch
   and **re-run verification** — green from before the integration proves nothing. A
   conflict is a stop.
2. Open the phase PR, listing each issue and its evidence.
3. If a human must approve it, say so, report and wait. Do not start the next phase — its
   worktree would be cut from a branch that does not contain this one.
4. **Re-sync again before merging** — it moves between opening and merging too. Once merged,
   confirm from the remote. Under a squash or rebase merge, confirm by content, not commit
   ancestry.
5. Move every issue in the phase to `Done`; update the project record.
6. Clean up the worktree and branch.
7. Report, and **wait** for a yes before the next milestone.

If the run stops mid-phase, the branch is retained with its completed issues on it and they
stay `In Review`. The report must say which issues sit on an unmerged branch — none of them
has shipped.

**The cost of this choice.** Recovery is coarser than per-issue: a rejected phase PR rolls
back all of its issues together. `linear-sync` already targets 1–4 issues per milestone,
which keeps that blast radius small.

### 6.5b Reconciliation — the docs are a deliverable

Coding agents pivot mid-build; blockers appear and approaches get replaced. A project that
ships correct code and leaves a spec describing something else has failed a required
outcome, because the next person to read it builds on the lie.

So reconciliation runs **twice per milestone and once at the close**:

| When | What |
|---|---|
| **Pre-flight**, before a phase's first issue | Are this phase's issues still achievable and still meaningful against the code earlier phases produced? An invalidated premise stops the phase before any code is written |
| **Post-flight**, after the phase merges | Update the plan's section, patch any issue whose description no longer matches what landed, fix the milestone body, and patch remaining issues this phase changed the premise of |
| **Close** | Full pass over spec, plan, project, milestones and every issue against the code that exists |

**The rule that keeps it honest: reconciliation is descriptive, never decisional.** It
records changes that were already approved. It never rewrites a document to match code that
deviated without approval — that would turn drift into fact and erase the record of what was
agreed. An unapproved difference is the material-change gate, not a doc edit. *If you cannot
name where a change was approved, it was not approved.*

Full procedure: `references/reconciliation.md`.

### 6.6 Step 4 — close honestly

Re-read the project and every issue from Linear. Confirm that every required **outcome** —
not merely every task — meets its approved acceptance criteria; that implementation and
documentation are current; that required verification and independent reviews passed; and
that every external gate is satisfied or explicitly accepted as a separate follow-up.

Then run the final relevant repository verification and one final independent
whole-project review. Fix and re-review material findings before claiming completion.

Report verified results, external assumptions, completed issues, remaining gates and gaps.

**Never mark the project Done while a required outcome sits behind an unsatisfied external
gate**, unless the approved workflow explicitly reclassified it as a separate follow-up.

---

## 7. The ledger

Context exhaustion is the primary failure mode of a multi-issue run, so the execution
record has to be concrete rather than "a ledger or equivalent".

- **Path:** `.linear-implement/<slug>.md` in the primary checkout of the **target** repo.
  The slug is the **Linear project identifier**, not its name — a derived slug differs
  between sessions and a resume then finds nothing.
- **Gitignored in the target repo.** The rollout's `.gitignore` entry protects only this
  repo. On first use the skill confirms the entry exists in whatever repo it is running
  against and adds it if not — otherwise the ledger dirties the checkout and trips step 0's
  own stop condition.
- **Not in the worktree** — per-phase worktrees are removed at the end of each milestone
  and would take the ledger with them.
- **Created after the step-1 gate**, never before. Nothing reaches disk while the user is
  still being asked.
- **Not authoritative.** Linear is the record. If the ledger is lost, rebuild it from
  Linear: issue states plus evidence comments carry the same facts. Where the two differ,
  Linear wins.

The ledger records **progress, not understanding.** A resumed session rebuilds the model,
the security invariants and the external gates from Linear and the repo — the ledger does
not carry them.

Format, update points and the resume protocol: `references/ledger.md`.

---

## 8. Harness portability

Same constraint as `linear-sync` §10, and the same solution.

- git worktrees, branches and test runners are universal — use them directly.
- **PR creation and merge assume nothing.** The skill detects the host's CLI and whether it
  is authenticated. No CLI, or a protected branch, routes through `In Review` instead.
- Superpowers skills (worktrees, TDD, subagent-driven development, code review,
  verification) are used **where present**. The discipline is the requirement; the skill
  is the upgrade.
- Subagents exist in Claude Code and may not in Codex. Fallback: an explicit fresh-context
  pass with the same brief and the same rubric.
- Linear operations are named by capability, never by harness-specific tool name.
- **The workspace state names are restated inline** in `linear-updates.md`, not only behind
  the `../../linear-sync/` path, so a packaging that copies one skill directory cannot leave
  the skill unable to check a state it is forbidden to invent.

---

## 9. Handoff from `linear-sync`

`linear-sync`'s reporting step gains one line offering the handoff, naming the project so
the next skill does not have to ask:

> Ready to build it? Invoke `linear-implement` on **Content Intelligence v2**.

The reverse direction is a stop condition, not a line: `linear-implement` invoked where no
project exists hands back to `linear-sync`.

Each skill's `description` carries an explicit negative clause pointing at the other. The
boundary is **creation**, not updating — `linear-implement` updates issue states, comments
and, on the approved non-material path, descriptions.

The skills stay independently invocable. `linear-implement` never creates Linear artifacts,
and `linear-sync` never writes code.

---

## 10. Rollout

1. Bump `echo-linear/.claude-plugin/plugin.json` to `1.1.0`.
2. Update the plugin README and the marketplace description to cover delivery, not only
   planning.
3. Add `.linear-implement/` to `.gitignore`.
4. Reinstall/refresh the plugin in **Claude Code** and in **Codex** — Codex caches skills
   under versioned paths, so a version bump requires a refresh.
5. Confirm both `linear-sync` and `linear-implement` appear in both harnesses' skill lists
   and invoke.

**Acceptance criterion:** both skills are listed and invocable in both tools — not merely
present on disk.

---

## 11. Verification plan

Linear is a live shared workspace and the repo is real, so verification must not pollute
either.

1. **Trigger check** — confirm `linear-implement` fires on "implement the Linear project"
   and that `linear-sync` still fires on "put this in Linear", with no collision.
2. **Dry run to the gate** — invoke on a scratch project and stop at step 1. Nothing should
   be written to Linear or to git before the yes.
3. **Stop-condition check** — invoke on a project with a deliberately broken source link.
   It must stop in step 0.
4. **Single-issue run** — a scratch project with one trivial issue, executed end to end,
   inspected for: worktree isolation, a failing-test-first commit, an evidence comment, a
   truthful state transition, and cleanup that leaves no stray worktree or branch.
5. **Codex pass** — repeat step 2 from Codex to prove the harness-agnostic wording holds.

---

## 12. Decisions on record

| Decision | Choice |
|---|---|
| Component | Second skill in `echo-linear`, not an agent — approval gates need the main session |
| Branch model | One worktree, branch and PR **per milestone**; one commit per issue inside it. Chosen over per-issue: six issues in two phases is two PR pipelines and two merge pipelines instead of twelve, and the merge lands on the checkpoint gate that already existed. Cost: a rejected phase PR rolls back all its issues together |
| Autonomy | Autonomous within a milestone; a gate at every milestone boundary |
| Start gate | Always, including a single-issue project |
| Material change | Default is material; non-material requires all five conditions |
| Ledger | Gitignored file in the target repo's primary checkout, named by Linear project identifier, rebuildable from Linear |
| Grind limit | Three implement-then-verify cycles after the first red test |
| Parallelism | None in v1 — sequential execution only |
| Deployment | Verified as a gate, never performed |
| Resume | Re-prints the plan and re-asks; the gate belongs to the session |
| Merge authority | Named in the step-1 plan; a human-approval repo routes through `In Review` |
| Force | Never — on a branch, a worktree, or a push |
| Doc hygiene | Reconciliation before every phase, after every phase, and at the close. Descriptive only: it records approved changes, and an unapproved difference is a stop, never a doc edit |
| Concurrency | `origin/<integration-branch>` is a moving target: re-sync before the worktree, before the PR and before the merge, and re-verify after each. A conflict with another agent's work is a stop |
| Blocked state | Stays `In Progress` with a comment; the workspace has no `Blocked` |

---

## 13. Review record

Three independent read-only reviews ran against the first draft of these files, simulating
the loop end to end plus nine branch variants. They surfaced defects in both skills,
including several in the already-shipped `linear-sync`:

| Fixed in `linear-implement` | Fixed in `linear-sync` |
|---|---|
| Stale integration branch between issues | Greenfield work blocked by the "component must exist" gate |
| Resume skipped the gate and was unreachable | Reviewer given nothing to run checks 4 and 7 or recovery against |
| Step 0 stop condition dead-ended the handoff | Pushed-vs-unpushed contradiction; repo paths cannot be link attachments |
| `--force` forbidden on branches, open on worktrees | Milestone update mathematically unsatisfiable under the word cap |
| Ledger created on either side of the gate | No rule for reusing an existing milestone by name |
| `execution-method.md` routed to only at step 10 | `labels` full-replace with no read-before-write |
| Up to three Linear writes where one was specified | Existing-project reads happening after the confirm gate |
| Human PR approval entirely unhandled | Write order never stated |
| Undefined slug, verification cycle, blocked state | Tier-to-title mapping, named-existing-project override |

A fourth pass re-checked every fix against the files. **26 of 30 closed outright.** Four
needed a second round, and one of those was a defect the fix itself introduced:

| Re-opened | Resolution |
|---|---|
| `git branch -f <branch> origin/<branch>` — the prescribed way to refresh the integration branch | **Fails, exit 128**, whenever that branch is checked out in any worktree, including the primary checkout this runs in. Confirmed empirically. Replaced with `git checkout <branch> && git pull --ff-only`, and `pull` refusing is now a stop, not something to merge past. |
| The skill's own `.gitignore` edit tripped its "checkout is dirty" stop condition on the next run | The one-line entry is committed to the integration branch, and the stop condition exempts it |
| `linear-sync` check 7 still had no guaranteed input | Step 4 now requires keeping a verbatim copy of every description and milestone body before overwriting it |
| A resume finds its own issues `In Progress` and stops as if a human were mid-work | The ledger accounts for them; the resume check runs after the project is identified, not before |

Two further wording fixes: an unverifiable claim that an uncommitted source is "unchanged
since planning" became an explicit uncertainty stated in the delivery plan, and the resume
check was reordered after project identification, which it depends on.

**Not yet done.** Design §11's live verification plan is outstanding — nothing has been run
against a real Linear workspace, and neither skill has been installed or invoked from Codex.
The acceptance criterion in §10 ("invocable in both tools, not merely present on disk") is
**unmet**.

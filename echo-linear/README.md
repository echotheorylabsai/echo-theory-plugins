# echo-linear

Turn what was **approved** in a working session into Linear artifacts a product manager
can read and a coding agent can act on alone — then build them.

## Requirements

- **The Linear MCP server**, configured and authenticated. Both skills stop without it.
- **A git repository** for `linear-implement`, with a remote it can push to.

Written to work in Claude Code and Codex — no harness-specific tool names, and a stated
fallback wherever subagents are assumed. The packaged install path is Claude Code's; on Codex,
point at the skill directory directly and keep the plugin folder intact, since the two skills
reference each other's files.

## Install

```bash
claude plugin marketplace add echotheorylabsai/echo-theory-plugins
claude plugin install echo-linear --scope project     # or --scope user
```

Session-local, without installing:

```bash
claude --plugin-dir /path/to/echo-linear
```

```
discussion / spec / plan  ──linear-sync──▶  Linear project  ──linear-implement──▶  merged PRs
```

## Skills

### `linear-sync` — plan into Linear

Invoke it after you and an agent have agreed what to build — whether that was a plain
discussion, a `superpowers:brainstorming` spec, or a `superpowers:writing-plans`
implementation plan.

It runs five steps, three of which are gates:

1. **Readiness gate** — reflects critically on whether it has enough. Any gap, it stops
   and asks rather than guessing.
2. **Shape** — picks a tier (issues only / project + issues / project + milestones +
   issues) and the *minimum* set of issues that covers the work.
3. **Confirm** — shows you a plan table and waits for a yes. Always, even for one issue.
4. **Write** — creates or updates via the Linear MCP.
5. **Adversarial review** — re-fetches everything from Linear and checks it against a
   seven-point rubric before reporting.

### What the output looks like

Descriptions are written in product language — goal, user story, customer value,
acceptance criteria — under hard word caps (issue ~250 words, project ~300, milestone
~120). Implementation detail stays in the spec, which is attached as a link so a coding
agent in a fresh session can still reach it.

Issue titles carry the sequence: `[Phase A.1] Title` for a phased roadmap, `1. Title` for
simple sequential work. Dependencies are set as real Linear blocking relations.

### Safety

Updates to **issues and projects** never rewrite a description — new information is prepended
as a dated callout, so anything you wrote by hand survives. Linear supports partial edits on
both, and the skill uses them.

**Milestones are the exception, and it matters.** Linear has no partial edit for a milestone
description; saving one replaces the whole body. The skill therefore reads the complete body
first and re-sends it verbatim beneath the new note — and **stops and asks** if that body is
long, came back truncated, or contains anything it cannot reproduce exactly. Losing it is not
recoverable.

**Example prompts**:
```
"Put this in Linear"
"Create the Linear issues for what we just agreed"
"We've finished the spec — file it in Linear"
"Add these two issues to the Content Intelligence project"
"Update ECH-42 — we decided to backfill before sealing"
"Turn this implementation plan into a Linear project with milestones"
```

**Before you start**: **commit and push your spec or plan.** Issues link to their sources, and
a link only your machine can open is useless to a teammate — and unreadable to
`linear-implement` later. An unpushed source stops the run and asks you to push. If the
agreement lives only in the conversation, it writes it into the project description instead, so
there is still something reachable to point at.

**What happens next**: it reflects on whether the scope is actually agreed, picks a shape,
then prints a `WILL CREATE` table and waits. Nothing reaches Linear before you say yes.

---

### `linear-implement` — Linear into merged code

Invoke it on an approved Linear project whose issues already exist. It delivers the
project's **goal**, not merely its closed issues.

Five steps. Two are gates that wait for you, and a third fires whenever the approved plan
turns out to be wrong:

0. **Adopt** — reads the whole project and the approved sources it links to, checks the
   repo, and builds the model. Any gap — conflicting sources, uncheckable criteria, a
   missing dependency — and it stops.
1. **Start gate** — prints a delivery plan and waits. Nothing reaches code, disk or Linear
   first.
2. **Execute** — the next unblocked issue only, in the current phase's worktree: a failing
   test first, an independent review, its own commit, a truthful Linear state.
3. **Checkpoint** — the docs are brought up to date *inside* the phase's branch so they ship
   with the code, then the phase goes up as one PR. **A human merges unless you said
   otherwise.** Once merged, every issue in the phase goes Done, the Linear records are
   reconciled, and it waits before the next phase.
4. **Close** — re-reads everything from Linear, reconciles every doc against the code, runs
   a final whole-project review, and reports the gaps plainly.

### Docs stay true

Agents pivot mid-build — blockers appear, assumptions turn out wrong. So before every phase
it checks that the phase's issues and docs still describe reality, and after every phase it
updates the spec, the plan and the Linear records to match what actually shipped.

**It only records changes that were approved.** A difference nobody agreed to is a stop, not
a doc edit — otherwise reconciliation just launders drift into fact.

When the project closes, the report says either "every doc matches the code, checked against
this commit" or names exactly which ones don't.

### The third gate

When the code shows an approved source is wrong, it stops there. It posts the evidence as a
comment and asks — it never quietly implements something better.

**The default is material.** A change only proceeds without asking when it changes no
behaviour, no acceptance criterion, no scope or sequence, and nothing about security or
data — and the code forces it. If it has to be argued, it is material.

### What it will not do

| Never | Why |
|---|---|
| Re-plan | Drift from the approved source is the failure this exists to prevent. |
| Create Linear artifacts | That is `linear-sync`. |
| Mark work Done early | Done needs criteria, verification, review *and* a confirmed merge. A blocked issue is never Done. |
| Grind | Three failed verification cycles on one issue stops the run. |
| Merge past a human | If a PR needs approval, it opens one, hands you the link, and waits for you to say it merged or what to change. |
| Deploy | Deployment is a gate it verifies, never an action it takes. |
| Force-delete anything | A branch that resists a safe delete is kept and reported. Never a force-push either. |
| Assume the branch stood still | Other agents merge while it works. It re-syncs before the PR and before the merge, and re-runs the tests each time — a clean merge can still be semantically broken. |
| Resolve someone else's conflict | A collision with another agent's change is a stop, unless the conflict carries no meaning. |

**Example prompts**:
```
"Implement the Linear project Content Intelligence v2"
"Execute the Linear plan for ECH project Content Intelligence v2"
"Build the issues in <linear project URL>"
"Start building ECH-41"                    ← resolves to its parent project first
"Continue implementing Content Intelligence v2"
```

Those start or resume a run. **"The Phase A PR merged — carry on"** and **"skip ECH-42"** are
answers to something it asked you, not ways to begin — see the table below.

**Before you start**: commit or stash anything in progress. A dirty working tree in your main
checkout stops the run — it needs a clean base to cut worktrees from. It will also ask to add
one `.gitignore` line for its own progress notes, and will tell you so in the plan.

**What happens next**: it reads the whole project and the sources it links, then prints a
`DELIVERY PLAN` and waits. It stops again at every phase boundary, and whenever the code
shows the approved plan is wrong.

**Name the project.** If you don't, it asks rather than guessing — it will never pick the
most recent one for you.

### Answering it mid-run

Things it will ask, and what a useful answer looks like:

| It says | You say |
|---|---|
| "Start implementation?" | `yes` — or amend the plan first |
| "Phase A shipped. Start Phase B?" | `yes`, or `hold, I want to look at the PR` |
| "The plan's approach would overwrite 2,400 rows. Options: (a) backfill first…" | `go with (a)` — it records that as a dated approval on the issue |
| "PR #12 is open and needs your approval" | merge it, then `it's merged` |
| "Three failed attempts on ECH-42" | `skip it and carry on`, or `here's what's wrong: …` |

### Surviving a long run

Progress, decisions and open findings go to `.linear-implement/<slug>.md` — gitignored, kept
outside the per-phase worktrees. It is a cache, not the record: if it is lost, it rebuilds
from Linear. A resumed run re-prints its plan and asks again; the gate belongs to the
session, not the project.

## A full run, end to end

The two skills chain, but they do **not** need the same session. Linear carries everything
between them — so a plan filed on Monday can be built on Thursday, on a different machine.

```
Session 1   discuss and agree
            "put this in Linear"              → project + milestones + issues

Session 2   "implement Content Intelligence v2"
            → DELIVERY PLAN → yes
            → Phase A builds, ships as one PR
            → "Phase A shipped. Start Phase B?"

Session 3   "continue implementing Content Intelligence v2"
            → notices Phase A is Done, resumes at Phase B
            → re-prints the plan for what remains → yes
```

Session 3 re-asks because **the approval belongs to the session, not the project.** Consent
given three days ago is not consent for what happens now.

If you lose the thread, say *"continue implementing Content Intelligence v2"*. It reads the
project fresh, works out where things stand, and re-prints the plan for what remains — so the
answer to "where are we?" arrives before it asks to carry on.

## Design

- `../docs/design/2026-08-29-linear-sync-skill-design.md`
- `../docs/design/2026-08-30-linear-implement-skill-design.md`

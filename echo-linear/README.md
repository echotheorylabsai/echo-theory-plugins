# echo-linear

Turn what was **approved** in a working session into Linear artifacts a product manager
can read and a coding agent can act on alone — then build them.

Works in Claude Code and Codex. Both need the Linear MCP configured.

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

Updates never rewrite a description. New information is prepended as a dated callout, so
anything you wrote by hand survives.

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
2. **Execute** — the next unblocked issue only: its own worktree, a failing test first, an
   independent review, a PR, a merge, a truthful Linear state, then cleanup.
3. **Checkpoint** — stops at every milestone boundary and waits before the next phase.
4. **Close** — re-reads everything from Linear, runs a final whole-project review, and
   reports the gaps plainly.

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
| Merge past a human | If PRs need approval, it opens one, sets `In Review`, and waits. |
| Deploy | Deployment is a gate it verifies, never an action it takes. |
| Force-delete anything | A branch that resists a safe delete is kept and reported. |

### Surviving a long run

Progress, decisions and open findings go to `.linear-implement/<slug>.md` — gitignored, kept
outside the per-issue worktrees. It is a cache, not the record: if it is lost, it rebuilds
from Linear. A resumed run re-prints its plan and asks again; the gate belongs to the
session, not the project.

## Design

- `../docs/design/2026-08-29-linear-sync-skill-design.md`
- `../docs/design/2026-08-30-linear-implement-skill-design.md`

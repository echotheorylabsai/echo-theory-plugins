# echo-linear

Turn what was **approved** in a working session into Linear artifacts a product manager
can read and a coding agent can act on alone.

Works in Claude Code and Codex. Both need the Linear MCP configured.

## Skill

### `linear-sync`

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
   six-point rubric before reporting.

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

## Design

`docs/design/2026-08-29-linear-sync-skill-design.md`

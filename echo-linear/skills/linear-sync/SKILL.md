---
name: linear-sync
description: Use when work agreed in this conversation needs to reach Linear as projects, milestones or issues, or when existing Linear artifacts need updating from newly approved decisions. Triggers include "put this in Linear", "create the Linear issues", "update the Linear project", or finishing a spec, PRD, design doc or implementation plan that someone now has to build.
---

# linear-sync

Turn what was **approved** in this session into Linear artifacts a product manager can
read and a coding agent can act on alone.

All Linear work goes through the **Linear MCP**. Refer to its operations by capability —
list issues, get project, save issue, save milestone — never by harness-specific tool
names, because this skill runs in more than one harness.

## The loop

```
1  READY?     do I actually have enough? → if not, STOP and ask
2  SHAPE      pick the tier, decide the MINIMUM issue set, say it out loud
3  CONFIRM    show the plan table, wait for an explicit yes
4  WRITE      create/update via the Linear MCP
5  REVIEW     fresh read-back vs the rubric → fix → re-verify → then answer
```

Steps 1, 3 and 5 are gates. **None may be skipped — not even on a single-issue run.**

---

## 1. Readiness gate

Collect the source of truth first: approved spec/plan files named in the conversation
(else look under `docs/superpowers/specs/` and `docs/superpowers/plans/`), what was
explicitly agreed in chat, and the relevant code.

Then reflect critically. Answer each, out loud, before going further:

- Is the scope **agreed**, or still being debated? A proposal is not an approval.
- Do I know the goal, who it is for, and how we would know it worked?
- Can I write acceptance criteria that are **checkable**, not vague?
- Do the components, surfaces or products I would name **actually exist** in the repo? Verify.
- Create or update — and if update, exactly which project or issue?
- If linking files: do they exist? Are they committed and pushed?

**Any gap → STOP. Ask clarifying questions. Write nothing to Linear.**

Proceed only when you can state in one line why you have enough. An issue built on a
guess is worse than no issue: it looks authoritative and it is already live.

## 2. Shape

Pick one tier and say which, with a one-line reason.

| Tier | Input | Creates |
|---|---|---|
| 1 | A chat agreement, or one change | Issues only, on an existing project. If none is named, **ask** — never guess, never create a project to dodge the question. |
| 2 | A spec or PRD, no phased plan | New project + flat issues |
| 3 | A spec + a phased implementation plan | New project + milestones from phases + issues |

**Minimum-issue discipline.** Think hard about the fewest issues that cover the work:

- One issue = one shippable outcome a developer can verify on its own.
- Merge anything that cannot be reviewed independently.
- **Never** a separate issue for "write tests", "update docs" or "refactor" — fold that
  into the issue whose acceptance criteria it serves.
- Aim for **1–4 issues per milestone**. More than 6 from one plan phase means re-group,
  not create twelve.

## 3. Confirm

Print the plan and wait. Nothing is written until the user says yes.

```
WILL CREATE
  Project  Content Intelligence v2
  Phase A · Instrument
    [Phase A.1] Record the baseline   Feature/platform
    [Phase A.2] Seal Day 0            Feature/platform
  Phase B · Report
    [Phase B.1] Change log            Feature/echo-hq

WILL UPDATE
  ECH-44   prepend dated callout

Proceed?
```

If they amend, re-print and wait again.

## 4. Write

Follow `references/formats.md` for what goes in each description, and
`references/conventions.md` for titles, labels, **milestones**, links, relations and the
**safe-update rules**. Record the identifier and URL of every artifact you touch — step 5 needs the list.

## 5. Adversarial review

**Mandatory. Runs before you answer.** Follow `references/review-rubric.md`.

Re-fetch every artifact from Linear. Never review from memory of what you meant to write —
the whole point is to catch the gap between the two.

Where the harness has subagents, run the review in a clean-context subagent so it cannot
inherit your assumptions. Where it does not, run it as an explicit fresh read-back pass
against the same rubric. The rubric is the mechanism; the subagent is an upgrade.

---

## Red flags — stop and go back

| Thought | Reality |
|---|---|
| "The plan is obvious enough, I'll skip the readiness check" | Obvious to you is a guess about the user. Run the checklist. |
| "It's one issue, no need to confirm" | The gate is about writing to a live shared workspace, not about size. |
| "I know what I wrote, the review is a formality" | You are reviewing Linear's copy, not your intent. Re-fetch. |
| "Better to over-cover with more issues" | Issue sprawl is the failure mode. Fewest that cover the work. |
| "I'll include the file paths so it's precise" | That is the technical drift this skill exists to prevent. Link the spec instead. |
| "I'll rewrite the description to be cleaner" | Full rewrites destroy hand-written text. Patch only. |
| "Scope is fuzzy but I'll write something reasonable" | Stop and ask. A plausible wrong issue is worse than none. |

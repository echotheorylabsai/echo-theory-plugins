# Adversarial review

Runs after writing, **before any answer is returned**. Its job is to find the gap between
what you meant to write and what is actually in Linear.

## Rule one

**Re-fetch every artifact from Linear.** Get each project, each **milestone** and each issue
fresh.

Reviewing from memory defeats the entire exercise — the failures this catches are exactly
the ones you cannot see from your own intent.

## Independence

- **Harness with subagents (Claude Code):** run this in a clean-context subagent. It must
  not inherit the writer's reasoning.
- **Harness without subagents (Codex):** run it as an explicit fresh read-back pass
  against the same rubric.

The rubric is the mechanism. The subagent is an upgrade, not a requirement.

### What the reviewer must be given

Checks 4 and 7 and the recovery pass cannot run without these. Withholding them is not
independence — it is a broken review.

| | Why |
|---|---|
| Artifact identifiers, including milestones | Rule one, and check 4 |
| The source spec/plan paths | Checks 1, 5 and 6 |
| This rubric | All of it |
| **The plan table the user confirmed at step 3** | Recovery — it is the only statement of what should exist |
| **A verbatim copy of any description or milestone body that existed before this run** | Check 7 — there is nothing to compare against otherwise |

Give it those and nothing else. Never the writer's reasoning about why a choice was made.

### The reviewer is read-only. Always.

**It reports. It never writes to Linear** — no patch, no create, no milestone save, no
recovery. Not even an obvious one-line fix, and not even when it has read the pre-write
bodies.

Everything in *What to do with a failure* and *Recovery* below is the **writer's** work,
performed after the reviewer's report comes back.

This is not ceremony. A milestone save has no patch operation — it replaces the whole body.
A clean-context subagent performing one is the single irreversible destruction available in
this workspace, and it is precisely what check 7 exists to catch. A reviewer that can write
can destroy the evidence of its own check.

## The seven checks

| # | Check | Fails when |
|---|---|---|
| 1 | **Coverage** | An approved item has no artifact, an artifact has no basis in the approved material, or one item is split across two issues |
| 2 | **No leakage** | File paths, function names, table names or schema appear in the prose. Links are fine, and so is the Context-line path for an unpushed source — that exception is in `conventions.md` |
| 3 | **Readable** | A PM could not follow it unaided; jargon; padding; the description body over its cap. Dated callouts do not count toward the cap; more than two of them do fail |
| 4 | **Wiring** | Wrong project, missing or wrong milestone, a duplicate milestone name, a milestone that no plan phase justifies, labels not matching what the confirm table said, a dropped label, an invented label or state, broken title sequence, or a blocking chain that contradicts the plan |
| 5 | **Links resolve** | A referenced spec or plan does not exist, or a GitHub URL points at a file that was never pushed |
| 6 | **Codebase alignment** | A component the work **depends on** cannot be found in the repo. A component the work **creates** is expected to be absent — never fail an issue for naming what it is about to build |
| 7 | **Nothing was destroyed** | A milestone or description that existed before this run lost text. Compare against what you read before writing. Anything gone that is not an intentional, stated correction is a failure. |

## What to do with a failure — **the writer, not the reviewer**

1. Fix it in Linear, using the safe-update rules in `conventions.md`.
2. Re-fetch and re-check that artifact against the rubric.
3. Only then continue.

If a fix does not hold after **two** attempts, stop trying. Report the artifact, what is
wrong, and what you tried.

**Never report success with a known unfixed failure.** If something cannot be fixed, say
so plainly in the answer, with the artifact identifier and what is wrong.

## Recovery — **also the writer**

This review is also the recovery path for a partial failure.

Compare Linear against the plan table the user confirmed at step 3. Anything in the table
that is missing from Linear gets created then, by the writer. No separate retry machinery.

## Reporting

After the review passes, report:

- Each artifact — identifier, title, URL.
- What was created vs updated.
- Anything the review fixed.
- Anything still outstanding, stated plainly.

Then offer the handoff, on its own line, **naming the project** so the next skill does not
have to ask for it:

> Ready to build it? Invoke `linear-implement` on **Content Intelligence v2**.

Offer it only when nothing is outstanding. Do not invoke it yourself — it has its own
approval gate.

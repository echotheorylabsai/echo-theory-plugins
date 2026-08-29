# Adversarial review

Runs after writing, **before any answer is returned**. Its job is to find the gap between
what you meant to write and what is actually in Linear.

## Rule one

**Re-fetch every artifact from Linear.** Get each project and each issue fresh.

Reviewing from memory defeats the entire exercise — the failures this catches are exactly
the ones you cannot see from your own intent.

## Independence

- **Harness with subagents (Claude Code):** run this in a clean-context subagent, given
  only the artifact identifiers, the source spec/plan paths and this rubric. It must not
  inherit the writer's reasoning.
- **Harness without subagents (Codex):** run it as an explicit fresh read-back pass
  against the same rubric.

The rubric is the mechanism. The subagent is an upgrade, not a requirement.

## The seven checks

| # | Check | Fails when |
|---|---|---|
| 1 | **Coverage** | An approved item has no artifact, an artifact has no basis in the approved material, or one item is split across two issues |
| 2 | **No leakage** | File paths, function names, table names or schema appear in the prose (links are fine) |
| 3 | **Readable** | A PM could not follow it unaided; jargon; a word cap exceeded; padding |
| 4 | **Wiring** | Wrong project, missing or wrong milestone, a milestone that no plan phase justifies, not exactly two labels, wrong state, broken title sequence, or a blocking chain that contradicts the plan |
| 5 | **Links resolve** | A referenced spec or plan does not exist, or a GitHub URL points at a file that was never pushed |
| 6 | **Codebase alignment** | A component, surface or product named in the issue cannot be found in the repo |
| 7 | **Nothing was destroyed** | A milestone or description that existed before this run lost text. Compare against what you read before writing. Anything gone that is not an intentional, stated correction is a failure. |

## What to do with a failure

1. Fix it in Linear, using the safe-update rules in `conventions.md`.
2. Re-fetch and re-check that artifact.
3. Only then continue.

**Never report success with a known unfixed failure.** If something cannot be fixed, say
so plainly in the answer, with the artifact identifier and what is wrong.

## Recovery

This review is also the recovery path for a partial failure.

Compare Linear against the plan table the user confirmed at step 3. Anything in the table
that is missing from Linear gets created now. No separate retry machinery.

## Reporting

After the review passes, report:

- Each artifact — identifier, title, URL.
- What was created vs updated.
- Anything the review fixed.
- Anything still outstanding, stated plainly.

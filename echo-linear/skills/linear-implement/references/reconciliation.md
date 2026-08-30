# Reconciliation — keeping the docs true

Coding agents pivot. Blockers appear, assumptions turn out wrong, an approach gets replaced
mid-phase. That is normal. What is not acceptable is finishing a project where the spec, the
plan and the Linear issues describe something nobody built.

**Reconciliation runs twice per milestone** — before the phase starts, and after its PR
merges — and once more at the close.

```
before phase ──▶ build ──▶ ship ──▶ after phase ──▶ … ──▶ close
   PRE-FLIGHT                        POST-FLIGHT          FULL PASS
   is the plan still                 does the doc say     does everything
   true for what is                  what actually        describe what
   about to be built?                shipped?             was built?
```

---

## The rule that keeps this honest

**Reconciliation is descriptive, never decisional.**

It records changes that were **already approved**. It never rewrites a document to match
code that deviated without approval — that turns drift into fact and destroys the record of
what was actually agreed.

So every difference you find gets classified before anything is written:

| What you found | What you do |
|---|---|
| An approved change the doc has not caught up with | **Record it.** Patch the doc and the Linear record, dated, citing where the approval happened |
| The doc was vague, the code is now specific | **Record it.** State the behaviour as built, cite the PR |
| A difference **nobody approved** | **Stop.** This is the material-change gate. Report it, do not update the doc to match |
| Remaining work whose premise the last phase invalidated | **Stop before starting it.** That is the whole point of the pre-flight |

**If you cannot name where a change was approved, it was not approved.**

---

## Pre-flight — before a phase starts

Previous phases changed the codebase. This phase's issues were written before that happened.

Re-read, fresh: this phase's issues from Linear, and the sources they link. Then check
against the code as it now stands:

- Are the acceptance criteria **still achievable**, and do they still mean anything? A
  criterion satisfied incidentally by the last phase is not a criterion any more.
- Do the components each issue **depends on** now exist? Do the ones it **creates** still
  not exist?
- Does the plan's approach for this phase still fit the code it will build on?
- Do the stated dependencies and ordering still hold?
- Has anything in the spec been superseded by an approved change made during an earlier
  phase?

**Any issue whose premise is void stops the phase.** Report it and ask before writing code.
Building against a stale criterion produces work that passes its issue and fails the goal.

---

## Post-flight — after a phase merges

What shipped is now fact. Make the record match it.

1. **The implementation plan** — update the phase's section to describe what was actually
   done: the approach taken, anything replaced, anything deferred. Date it.
2. **Each shipped issue** — if what landed differs from what its description said, patch the
   description with an anchored edit and a dated note. Never a rewrite.
3. **The milestone body** — if its "accepted when" no longer matches what was accepted, fix
   it. Milestones have no patch operation: read the complete body first, prepend, re-send
   the whole thing (`linear-updates.md`).
4. **The spec** — only where an **approved** change altered behaviour. An unapproved
   difference is a stop, not an edit.
5. **The project description** — only if the goal or what-ships list is now wrong.
6. **Remaining issues** — if this phase changed what a later issue must do, patch it now,
   while the reason is fresh. Do not leave it for the agent that picks it up.

Say in the checkpoint report what you reconciled and what you left alone.

---

## Full pass — at the close

Before declaring the project complete, read the spec, the plan, the project, every milestone
and every issue against the code that exists.

The closing report must state, in plain words, **either**:

- every document and Linear record describes what was built — naming the last commit or PR
  you checked against, **or**
- these specific places do not, and here is what is wrong with each.

**Never report a project complete with a document you have not re-read.** A project that
ships correct code and leaves a misleading spec behind has failed a required outcome — the
next person to read it will build on a lie.

---

## Rules that still apply

- **Safe updates only.** Anchored patches; never a full description rewrite; read a milestone
  body completely before replacing it. See `linear-updates.md`.
- **Word caps hold.** A reconciliation note is a dated callout and does not count toward the
  cap, but at most two stay at the top — fold the oldest into a comment.
- **Approval before the source changes.** Editing the authoritative spec or plan follows the
  material-change gate, not this file.
- **Comments carry history, descriptions carry the current truth.** If a description is
  becoming a changelog, the history belongs in comments.

## Red flags

| Thought | Reality |
|---|---|
| "The code is the truth, I'll just update the doc to match" | Only for approved changes. Otherwise you are erasing the evidence that something drifted. |
| "I'll reconcile everything at the end" | By then nobody remembers why. Reconcile at each boundary, while the reason is fresh. |
| "The issue is Done, its description doesn't matter now" | It is what the next person reads to understand what exists. |
| "Nothing changed this phase" | Say that only after re-reading both sides. Assuming it is how drift accumulates. |
| "The spec is close enough" | Close enough is what the next agent builds on. |

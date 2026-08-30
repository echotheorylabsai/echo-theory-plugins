# Reconciliation — keeping the docs true

Coding agents pivot. Blockers appear, assumptions turn out wrong, an approach gets replaced
mid-phase. That is normal. What is not acceptable is finishing a project where the spec, the
plan and the Linear issues describe something nobody built.

**Reconciliation runs twice per phase** — before it starts, and after its PR merges — and
once more at the close. A project with no milestones uses the batches confirmed at the step-1
gate as its phases; it does not skip reconciliation for want of a roadmap.

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
| An approved change the doc has not caught up with | **Record it.** Patch the doc and the Linear record, dated, **citing the approval-record comment** |
| The doc was silent on a detail the code had to settle — a variable name, an error string, a log line | **Record it.** State it as built, cite the PR |
| The doc was **wrong, incomplete or unsafe** about behaviour, and the code went the other way | **Stop.** Incompleteness about behaviour is the material gate's own trigger, not something to write down |
| A difference **nobody approved** | **Stop.** Report it; do not update the doc to match |
| Remaining work whose premise the last phase invalidated | **Stop before starting it.** That is the whole point of the pre-flight |

**Row 2 versus row 3 is the line to get right.** If the doc's silence made a *decision* for
you — about behaviour, an interface, data, or anything a reader would want to have agreed —
that is an incomplete source, and it stops. Row 2 is only for detail nobody would have
specified.

**If you cannot name the approval-record comment, the change was not approved.** Not the
chat, not your memory, not the plan section a previous phase already rewrote — that last one
is circular, and it is exactly how drift becomes permanent and invisible. A comment on the
issue, or nothing.

---

## Pre-flight — before a phase starts

Previous phases changed the codebase. This phase's issues were written before that happened.

**On the very first phase there are none**, and step 0 read everything minutes ago. Say so and
move on — do not re-fetch the project to satisfy the form. From the second phase onward it is
not optional.

Re-read, fresh: this phase's issues from Linear — **including their comments**, which is where
approval records and discrepancies live — and the sources they link. Citing an approval you
have not fetched is not citing it. Then check against the code as it now stands:

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

**Classify every difference against the table above first.** Only differences that landed in
its two *Record it* rows get written; the rest stop. Nothing below is unconditional.

1. **The implementation plan** — update the phase's section to describe what was actually
   done: the approach taken, anything replaced, anything deferred. Date it, citing the
   approval-record comment. The plan is an authoritative source, so an unapproved difference
   never reaches this step — it stopped at the table.
2. **Each shipped issue** — if what landed differs from what its description said, patch the
   description with an anchored edit and a dated note. Never a rewrite.
3. **The milestone body** — if its "accepted when" no longer matches what was accepted, fix
   it, **and only with an approval you can cite**: a milestone save has no patch operation, so
   this is a full replace of hand-written text. Read the complete body first, prepend, re-send
   the whole thing, and send `project` too (`linear-updates.md`). If you cannot reproduce the
   existing body exactly, stop and ask.
4. **The spec** — only where an **approved** change altered behaviour. An unapproved
   difference is a stop, not an edit.
5. **The project description** — only if the goal or what-ships list is now wrong.
6. **Remaining issues** — if this phase changed what a later issue must do, patch it now,
   while the reason is fresh. Do not leave it for the agent that picks it up.

Say in the checkpoint report what you reconciled and what you left alone.

### When post-flight finds something unapproved

Awkward by construction: the phase has merged and its issues are `Done`. **Do not revert, do
not re-open the issues, and do not write the difference into the docs.**

1. Post it as a discrepancy comment on the issue it affects — what shipped, what the approved
   source says, and that it shipped without approval.
2. Say it in the checkpoint report, plainly, as an outstanding item.
3. Leave the doc showing what was **approved**, not what shipped, until the user decides
   which is right.
4. Do not start the next phase. Its pre-flight would be reading a record you have just found
   untrustworthy.

The code is already live; the honest record of that is the point, not a tidy doc.

---

## Full pass — at the close

Before declaring the project complete, read the spec, the plan, the project, every milestone
and every issue — **with its comments** — against the code that exists.

**And against the baseline the ledger pinned.** Comparing docs to code only proves they agree
now; a deviation that post-flight already normalised leaves no difference to find. Diff the
plan and spec against their state at the pinned baseline commit, and for every change, name
the approval record that licensed it. A change with no record is drift that reconciliation
wrote in — report it.

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
  cap, but at most two stay at the top — fold the oldest into a comment on that same artifact.
  Milestones take comments too.
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

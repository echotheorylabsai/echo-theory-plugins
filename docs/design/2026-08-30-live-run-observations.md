# echo-linear — first live run, observations

**Date:** 2026-08-30
**Purpose:** first end-to-end execution of `linear-sync` → `linear-implement` against a real
Linear workspace and a real git repo. Nothing in this plugin had ever been executed before
this run; eight review rounds were all static reading.

**Method.** Fresh Opus subagents act as the "new sessions". They get the repo path, the task,
and one line describing the async harness — nothing about the plugin's design history. The
monitoring session (this one) plays the human at every gate. A subagent that stops at a gate
is resumed with its context intact once the gate is answered.

---

## Setup and environment

| Check | Result |
|---|---|
| Linear MCP reachable | ✅ one team, `Echotheorylabs` |
| Workspace states | ✅ `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`, `Duplicate` — exactly as `conventions.md` documents, including the load-bearing `In Review` |
| Workspace labels | ✅ type (`Bug`/`Feature`/`Improvement`) + 8 area labels — exactly as documented |
| GitHub auth | ✅ `echotheorylabsai`, scopes `gist, read:org, repo` |

**O-1 — `conventions.md`'s workspace table is accurate.** Every team, state and label it
claims exists, with the same names. The discovery-and-fallback machinery added in review was
therefore never exercised in this run; it remains untested.

**O-2 — a plugin update does not reach the running session.** The installed plugin was still
`1.0.3` (pre-merge) at the start. `claude plugin marketplace update` + `claude plugin update`
moved it to `1.1.0`, and the CLI said verbatim: *"Restart to apply changes."* Verified: the
`1.0.3` cache directory contains no `linear-implement` at all, so this session cannot invoke
it by name.

**Consequence, and a real limit on this run:** the subagents load each skill **by file path**
from the merged `main`, not by trigger. **The `description` / trigger-matching mechanism is
therefore NOT tested here.** Whether "implement the Linear project X" actually fires the skill
remains unverified. The cached `1.1.0` files were confirmed byte-identical to `main`, so the
*content* under test is the shipped content.

**O-3 — token scope cannot delete a repo.** `repo` is present, `delete_repo` is not. The
scratch repo created for this run must be deleted by hand afterwards.

---

## Run log

### Stage 0 — scratch repo

`echotheorylabsai/zz-agent-budget-guard`, private. Seeded with a working `RunMeter` that
accumulates token usage, a passing 3-test suite, and a README stating that nothing is
enforced. Deliberately leaves a real gap for the feature to close.

**Feature under test:** a per-run budget guard — hard cap, warning threshold, run report.
Two phases, three issues, ~30 lines each. Small on purpose; the workflow is what is being
tested, not the feature.

### Stage 1 — spec and plan (fresh Opus session, superpowers skills)

Produced `docs/specs/…-budget-guard-design.md` and `docs/plans/…-budget-guard-plan.md`,
committed and pushed at `67ba987`.

**O-4 — the input the plugin was designed for is easy to produce.** Two phases, three tasks,
9–10 assertable acceptance criteria each, 13 numbered decisions pinned so a stranger need not
re-derive them. Verified independently: both files on `origin/main`, working tree clean, seed
suite still green.

Worth noting the agent validated the plan's code blocks out-of-tree before committing, and
wrote no feature code into the repo — so `linear-sync` receives exactly the situation it
specifies: agreed docs, pushed, nothing built.

### Stage 2 — `linear-sync` (fresh Opus session)

Invoked with: *"We've agreed on the budget guard work — the spec and the implementation plan
are both written and pushed. Put this in Linear."* Skill loaded by file path (see O-2). The
only instruction added beyond the skill was to prefix the project name with `zz-`.

**O-5 — the confirm gate held, verified independently.** The session printed a plan table and
stopped. The workspace was then listed from the monitoring session: 8 projects, none of them
the new one. **Nothing was written before approval.** This is the promise the whole design
rests on and it is the first time it has been observed rather than asserted.

**O-6 — six rules written the same day all fired correctly on first execution.** None had
ever run:

| Rule | Evidence from the run |
|---|---|
| SHA-pinned source links | *"Real GitHub URLs pinned to commit `67ba987`"* — not `blob/main/…` |
| List existing projects before creating | *"None of the 8 existing projects covers per-run token enforcement"* — and there are exactly 8 |
| Discover the workspace before the gate | *"on team Echotheorylabs (the only team)"*, *"State Backlog (exists in this workspace)"* |
| Disclose incidental repo changes in the plan | *"ALSO adds `.linear-sync/` to the repo's .gitignore"* |
| Confirm table names everything the review audits | team, state, labels, blocking chain, dates, link reachability — all present |
| Tier keys on the shape of the work | Tier 3 chosen from a two-phase plan into a project that does not exist |

**O-7 — minimum-issue discipline held without prompting.** Three issues for three plan tasks,
and the README update inside Task 3 was folded into that issue rather than split into a
fourth. This is the sprawl the rule exists to prevent.

**O-8 — it surfaced its own judgement calls for correction.** Unprompted, it flagged the
project name and the rationale for blocking A.2 on A.1, inviting a correction on each. Not
required by the skill; a good emergent property of "the table is the user's only chance to
correct it".

**O-9 — the dependency chain was justified from the source, not from numbering.** *"a real
constraint, not just reading order: the plan has Task 2 insert its check into the sequence
Task 1 establishes."* The rule distinguishing reading order from real constraints worked.

#### Result — every artifact verified against Linear from the monitoring session

Project `zz-Per-Run Budget Guard`, milestones `Phase A · Enforce the budget` and
`Phase B · Report the run`, issues ECH-125/126/127.

| Wiring check | Result |
|---|---|
| Titles | `[Phase A.1]`, `[Phase A.2]`, `[Phase B.1]` — sequence correct |
| Milestones | Both, from the plan's own two phases; none invented |
| Labels | `Feature` + `platform` on all three — exactly one type, one area |
| State | `Backlog` on all three |
| Blocking | 126 blocked by 125, 127 blocked by 126 — chain intact |
| Links | `blob/67ba9870d3e2…/docs/specs/…` — **full commit SHA**, not a branch |
| Dates | none set |

**O-10 — its own adversarial review ran, and demonstrably re-fetched.** A subagent cannot
spawn a subagent, so the fallback path was exercised for real. The reviewer cited
`stateHistory`, relation edges, per-artifact timestamps and an empty comment list — none of
which were in its brief, so it genuinely read Linear rather than the prompt. 7/7 checks
passed. It also verified the links via git rather than HTTP: the pinned commit *is* the
remote's `main` HEAD, and both paths exist at that exact commit.

**O-11 — the review produced advisories, not just pass/fail, and they were acted on.** Three
phrases a PM would stumble over were patched with anchored replacements against Linear's
stored text, then re-fetched to confirm nothing else moved. The "anchors must match stored
text, not what you sent" rule held under real use.

---

### 🔴 DEFECT 1 — `linear-sync` leaves the repo dirty, and `linear-implement` stops on exactly that

**The most valuable finding of the run, and it is an integration bug no review round caught.**

`linear-sync` step 4 requires a recovery file under `.linear-sync/` and says to add that
directory to `.gitignore`. It does — and leaves the change **uncommitted**:

```
 M .gitignore        +.linear-sync/
```

The recovery file itself was correctly deleted after the review. But the `.gitignore` edit
survives, and `linear-implement`'s step 0 stops on **"any uncommitted change"** in the primary
checkout, with only its own ledger directory exempted.

So `linear-sync`'s final line — *"Ready to build it? Invoke `linear-implement` on
zz-Per-Run Budget Guard"* — hands directly into a skill that will refuse to start, because of
a file the first skill just modified.

Eight rounds of static review missed it. One live handoff surfaced it immediately, because
static review examined each skill's rules and this bug lives only in the *state one leaves
for the other*.

**Fix options:** have `linear-sync` restore `.gitignore` when it deletes the recovery file;
or write the recovery file somewhere already ignored; or exempt it in `linear-implement`'s
stop condition. The first is cleanest — the file is transient, so the ignore line need not
outlive it.

**Left unfixed deliberately**, to observe whether `linear-implement` actually stops as
specified.

### Stage 3 — `linear-implement` (fresh Opus session)

Invoked with exactly *"Implement the Linear project zz-Per-Run Budget Guard."*

**O-12 — DEFECT 1 confirmed end to end, and the stop condition worked.** It refused to start,
named the cause correctly — *"Left behind by the linear-sync run"* — and did not proceed. The
step-0 clean-checkout rule fired exactly as specified. Both halves of the defect are now
observed: `linear-sync` creates the condition, `linear-implement` correctly stops on it.

**O-13 — it reasoned forward to the downstream failure the docs only warn about abstractly.**
Unprompted: *"`.linear-implement/` is **not** ignored, so Phase A's PR has to touch
`.gitignore` too — and after that merges, the next `git pull --ff-only` in this checkout
aborts on exactly this file."* That is the precise failure mode `execution-method.md` describes,
derived here from first principles about the actual repo.

**O-14 — it refused a bare "yes" for a destructive action.** Verbatim: *"I won't revert a
tracked-file edit in your checkout on a bare 'yes'."* It offered three options and demanded an
explicit pick. Nothing in the skill says this in so many words; it generalised from the
"never discard them" rule in the pull-failure table. The disposition the whole design aims at
appeared without being spelled out.

**O-15 — the merge-authority default worked, first time.** This was the most dangerous finding
of the final review round: a bare `yes` could once have been read as permission to merge to a
shared branch. The run produced, unprompted:

> *"`gh` is authenticated as `echotheorylabsai`, but that's capability, not permission.
> **Default: you merge**, and I wait at each checkpoint with the PR link."*

That is the fix, in the skill's own words, behaving correctly on its first execution.

**O-16 — the delivery plan carried everything the fixes require.** Baseline with pinned
commit and pushed status; integration branch confirmed equal to `origin/main`; per-phase
branch names; checkpoints; the `Also in PR` disclosure of incidental `.gitignore` lines; the
ledger path; the "finished but not merged" state named and *confirmed present in this
workspace*; expected test counts at each step; and a risk note. The concurrency check ran too
— *"Repo quiet — one worktree, no branches but main, no concurrent agents."*

**O-17 — it escalated a conflict between the plan and the skill rather than deciding.** The
plan named `superpowers:subagent-driven-development` as a required sub-skill; the session
proposed satisfying it with the skill's own per-issue loop and asked to have that ratified.
Source-precedence tension surfaced, not silently resolved.

#### Phase A — shipped. Everything below verified from the monitoring session.

PR #1 merged as `d9d01b4`. Commit graph on `main`:

```
d9d01b4  Merge pull request #1
1f843e9  docs: reconcile the plan with what Phase A built
b8e74ed  feat: warn before a run reaches its token budget (ECH-126)
c6bcd56  feat: halt a run when it exceeds its token budget (ECH-125)
7fc78ee  chore: ignore agent ledger directories
67ba987  docs: design spec and phased plan
```

**O-18 — the doc-reconciliation fix worked, and it is visible in the graph.** `1f843e9` sits
*inside* the merged PR, below the merge commit. This was BLOCKER B3 from the final review:
doc edits had nowhere to be committed because the reference put them after the merge. The
split — git-tracked files into the phase branch before the PR, Linear records after — is what
actually happened.

**O-19 — the `.gitignore` fold-in worked.** `7fc78ee`, its own commit, in the phase PR, not on
the integration branch and not left dirty.

**O-20 — one commit per issue, issue-keyed.** `c6bcd56` (ECH-125), `b8e74ed` (ECH-126). It
chose a merge commit over a squash *specifically* to preserve them, stating the reason: the
repo had no convention, and per-issue commits are the point.

**O-21 — the state machine behaved exactly as specified, on the clock.**

| Event | Time |
|---|---|
| ECH-125 → In Progress | 22:11:06 |
| ECH-126 → In Progress | 22:16:59 |
| PR merged | 22:26:00 |
| ECH-125 → Done | 22:26:29 |
| ECH-126 → Done | 22:26:32 |

Issues went In Progress **one at a time**, and both flipped to Done **only after the merge,
three seconds apart** — the "all issues in a phase reach Done together at the checkpoint" rule,
observable in timestamps. ECH-127 untouched at `Backlog`.

**O-22 — verification ran against merged `main`, not the branch.** Its own words: *"a clean
merge can still be semantically broken."* 18 tests pass on the merged result. Confirmed here
independently.

**O-23 — the seed-test regression guard held, claim checked precisely.** It claimed the three
seed tests were unmodified "byte-for-byte". Verified: all three bodies hash identical to the
seed commit; the only removed line in the file is the import, extended to add `BudgetExceeded`.
The claim was exact.

**O-24 — cleanup was correct and complete.** Worktree removed, local branch deleted non-force,
primary checkout clean on `d9d01b4`, only `main` remains. Remote branch left in place — not
deleted, per the rule about never removing remote resources unasked.

**O-25 — it refused to let a casual approval skip the material gate.** It found two minor
defects and fixed neither, because both would mean editing code the approved plan prescribes
verbatim. On one it wrote, unprompted: *"fixing the pickle one is a material change — it
alters observable behaviour the spec doesn't specify, so it needs the spec updated and an
approval record first. A casual 'sure, fix it' shouldn't skip that gate."*

**O-26 — it left the README knowingly stale, and said so.** Enforcement now exists, so the
README is false. The approved plan schedules that rewrite inside Phase B, so it stayed there.
*"Disclosed, not skipped."* Source precedence beat the obvious tidy-up.

**O-27 — emergent rigour beyond the skill.** It ran mutation testing per issue (22 of 23
injected mutants killed) and reported the survivor. Nothing in the skill asks for this.

**O-28 — it would not touch the user's stash.** *"It's your edit, so I won't drop it."*

#### Phase B — merge authority withheld

**O-29 — the withheld-merge path works.** This is the fix for the most dangerous finding of
the final review, and the path with the most churn across rounds and zero prior verification.
Verified from the monitoring session at the moment it stopped:

- PR #2 **OPEN**, `mergedAt: null`
- `origin/main` still at `d9d01b4` — untouched by Phase B
- ECH-127 `In Review`, not `Done`
- Phase B worktree and branch **retained**, as required until a merge

It had `gh` authenticated, an unprotected branch, and the technical ability to merge. It did
not, because permission was not granted. Capability ≠ permission held under real conditions.

**O-30 — it caught a false red.** *"The initial red was just an `ImportError` at collection,
which proves nothing. I added the dataclass and export first so the five tests then failed on
`report()` genuinely being absent."* The "confirm it fails for the **right reason**" rule is
the sort of instruction that is usually decorative. It was applied.

**O-31 — it tested a documentation claim by executing it.** The README carries a worked
example, so it ran the example verbatim and compared the output to spec §6.4 field by field.

**O-32 — the Phase B diff was purely additive**: 27 production insertions, 0 deletions, so no
Phase A behaviour could have moved. All 18 earlier tests passed with byte-identical bodies.

**O-33 — pre-flight ran at the second phase and was reported.** Dependencies existed, what
the phase creates was still absent, no criterion had been satisfied incidentally by Phase A,
nothing in the spec superseded. This is the check that only has meaning from the second phase
onward, and it ran there.

**Squash trap armed deliberately.** The monitoring session merged PR #2 with `--squash`
(`f23b3f7`). Ancestry now reports **2 commits on the branch as not in `main`**, though the
content landed. This is the exact trap `execution-method.md` describes — confirm by content,
not `git branch --contains` — and it is now live for the session to handle on re-entry.

**O-34 — the squash trap was handled correctly, including the part I originally got wrong.**
On re-entry it confirmed the merge *by content*, and reported: *"`git branch -d` then
'succeeded' with a warning naming only the **remote-tracking ref**, not `main`. The content
check was the real safety net."*

That is precisely the correction made after a reviewer empirically disproved my original claim
that `-d` would refuse after a squash. The rule was wrong, was fixed, and the fix was then
confirmed by an independent session hitting the real case unprompted.

#### Close

**O-35 — 🔴 the whole-project review found a real correctness bug that no per-issue review
could have found.** Reproduced independently from the monitoring session against merged
`main`:

```
RunMeter("run-x", budget_tokens=100, warn_tokens=80, on_warn=<raises>)
m.record(500, 0)   → RuntimeError escaped; the halt was skipped
m.report()         → total=500  budget=100  halted=False
```

**A run five times over budget reports that it was not halted.** If a single call crosses both
thresholds and the warning callback raises, the halt never happens and the report lies about
it — in exactly the case the report exists for.

This is the single strongest justification for the close-time whole-project review in the
whole design. Both issues passed their own reviews and all 23 tests. **The defect lives in the
integration between them**, which is by construction invisible to a per-issue check.

**O-36 — and it owned the miss.** Unprompted: *"I recorded this mechanism on ECH-126 during
Phase A and called it 'informational, not a defect.' That judgement was made before `report()`
existed. It's the integration that makes it matter, which is precisely what a per-issue review
can't see."*

**O-37 — it changed nothing, correctly.** *"That's the material gate, and your 'do not fix'
covered the four known items, not this."* It refused to extend a previous approval to a new
decision — the exact failure the approval-record mechanism exists to prevent.

**O-38 — the close diffed against the pinned baseline, not just against the code.** *"comparing
docs to code only proves they agree now."* Result, verified here: the **spec is byte-for-byte
unchanged** from `67ba987` — zero drift across the whole project. The plan carries 50
insertions / 16 deletions, all ticked boxes and dated "Built" notes; no requirement, criterion,
interface or approach was rewritten. That is descriptive reconciliation behaving as specified.

**O-39 — it verified project-level outcomes, not just issue criteria.** It exercised *"the
warning fires exactly once, however long the run continues"* across 500 calls — a project-level
claim no single issue's tests covered. Deliver the goal, not the closed issues.

**O-40 — it reported its own imprecision.** It flagged that its Phase 2 "Built" note overstated
a README claim, and that spec §5 omits `on_warn` from its attribute list — neither corrected,
because fixing them needs a PR someone must merge. *"That imprecision is mine."*

**O-41 — it declined to set the project state and recommended against completing.** *"Hold,
don't mark it Completed yet. Every approved acceptance criterion is met and no gate is
outstanding, so completing it is defensible — but finding #5 deserves the same eyes-open
decision the other four got."*

**Final verified state.** 23 tests passing on merged `main` @ `f23b3f7`. All three issues Done,
both milestones complete. One worktree, one branch, clean tree. Remote branches left in place —
never deleted unasked.

---

## Defect log — where the skill left the executing session guessing

Collected from the session itself at the end of the run, asked bluntly and answered bluntly.
Ordered by what it cost.

### 🔴 D2 — a minor finding whose fix would edit plan-prescribed code

Came up **four times**; the skill does not determine it. `execution-method.md` says "fix
significant findings" and "carry unresolved findings", and says nothing about a finding that is
minor *and* whose fix would deviate from an approved source. Two readings: a one-line test
assertion is non-material, just add it; or the plan prescribes that test verbatim, so touching
it is deviation. It picked the conservative one every time and disclosed — *"but I was
inventing that policy, not following one."*

**Fix:** state it. A finding whose fix would alter text an approved source prescribes verbatim
is carried and disclosed, never fixed unilaterally, however small.

### 🔴 D3 — the close is written as terminal, but it is a gate

Step 4 says to fix a close-time finding in a `-close` worktree and ship a final PR. It has no
branch for what actually happened: the finding was **significant** *and* fixing it was a
**material change** needing approval. The close then cannot complete in one pass. Worse, merge
authority was granted **per phase**, and the close is not a phase — so authority there was
undefined. It stopped and asked; nothing told it to.

### 🔴 D4 — the anchored-patch discipline does not extend to git-tracked docs, and it caused a near-miss

"Anchored patches, never blunt rewrites" is stated only for **Linear** descriptions. For the
plan file the session reached for a blanket string replace and **corrupted the plan's header
prose** — it rewrote the sentence *describing* checkbox syntax. It caught this in the diff,
*"but only because I looked."*

**Fix:** the discipline is about not destroying hand-written text. That applies to a markdown
file in git exactly as much as to a Linear description.

### 🟡 D5 — merge method is never specified, and my own squash proved the cost

The skill covers merge-vs-rebase for *re-syncing*, and covers confirming a squash landed. It
never says which method to **use**. That matters: "one commit per issue, so the phase PR stays
reviewable issue by issue" is an explicit design principle, and a squash destroys it.

The session chose a merge commit for Phase A and said why. **I then squash-merged Phase B** —
silently discarding exactly the property the skill was built to preserve. Neither of us was
wrong by the text, which is the point.

### 🟡 D6 — agent-directed instructions embedded inside approved sources

The plan's header carried `REQUIRED SUB-SKILL: use superpowers:subagent-driven-development`.
Source precedence says the sources govern, so by the letter that binds the executor — but it is
an instruction about *method*, aimed at an agent, not about the product. The skill never says
to look for such instructions or how to treat them. The session surfaced it at the gate.

Its own note: *"A malicious or careless plan could use that channel."* This is a
prompt-injection surface in a skill designed to follow documents.

### 🟡 D7 — the ledger exception versus "any uncommitted change"

The one uncommitted change was `.gitignore` adding `.linear-sync/` — arguably the very category
the ledger exception carves out, but belonging to the *sibling* skill. It stopped and asked;
safe, but potentially needless friction on **every** run that follows a sync. Interacts with
DEFECT 1.

### ⚪ D8 — reverting is undefined, and the safe form is ambiguous

The skill never discusses reverting a stray edit. `git checkout --` was blocked by a safety
net suggesting stash. *"Stash and checkout are semantically different — one is recoverable, one
is not."* It chose stash and disclosed, leaving a stash the user then had to clear.

### ⚪ D9 — are plan checkboxes "reconciliation"?

`reconciliation.md` says update the phase's *section* to describe what was done. Checkboxes are
tracking state, not description. It ticked them and added dated notes.

### ⚪ D10 — a discrepancy spanning two issues has one home

Finding #5's mechanism lives in ECH-126 and its harm in ECH-127. `linear-updates.md` says "on
the issue the change affects" — singular. It posted on ECH-127 and cross-referenced. A guess.

### ⚪ D11 — the ledger slug clause anticipates the wrong failure

*"The slug is the Linear project identifier, not its name."* This MCP exposes a UUID and a URL
slug, but no `PROJ-123`-style identifier. The fallback clause anticipates *no* identifier, not
an identifier *in an unexpected shape*. It used the UUID and recorded the choice.

---

## Verdict

**The plugin works.** Both skills ran end to end against a live workspace and a real repo,
produced correct artifacts and working code, and stopped at every gate they were supposed to
stop at — verified independently at each one, not taken on report.

**The design's two most contested mechanisms both earned their place on first contact:**

- The **merge-authority default** — the most dangerous finding of the final review round —
  held under conditions where the session had every technical means to merge and no permission.
- The **whole-project close review** found a real correctness bug that two per-issue reviews
  and 23 passing tests had missed, because the defect lived in the integration between them.

**Eight rounds of static review missed an integration bug that one live handoff exposed in
seconds** (DEFECT 1). Static review examined each skill's rules; that bug lives only in the
state one skill leaves for the other. That is the strongest argument in this document for
running things rather than reading them.

**Eleven defects for the next round**, one of them a near-miss that corrupted a file (D4), one a
prompt-injection surface (D6), and one caused by the monitoring session's own choice (D5).

**Untested by this run:** trigger/description matching (O-2), workspace discovery fallbacks
(O-1), context-loss resume, the material-change approval path end to end, and Codex.

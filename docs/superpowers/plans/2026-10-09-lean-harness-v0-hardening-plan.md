# Lean Harness v0 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every harness defect that real tasks proved would give a wrong record, block a task, or
clash with project rules, before the harness is used for production work and before Codex (Slice 2).

**Architecture:** Small, generic changes to the existing CLI and instruction files. The event log
becomes the only source of a task's phase; `harness pr` separates "PR open" from `ready`; timing gains
one pause rule and one span rule; instruction files gain a few lines. No new commands, no new event
kinds, no project-specific code.

**Tech Stack:** Python 3.12 standard library only; `unittest` (run with `python3 -m pytest -q`); git;
`gh`.

**Spec:** `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md` (this repo). Evidence:
`~/Desktop/src/echo-official/harness-tasks/testing-notes.md` (gap rows #1–#44) and
`~/Desktop/src/echo-official/harness-tasks/project-clashes.md` (G1–G5, P1–P10, W1–W3, E1–E2).

**Code:** `~/Desktop/src/echo-official/lean-harness` (GitHub `echotheorylabsai/lean-harness`), branch
`v0-hardening` from `main` (`235cf61`). All file paths below are relative to that repo unless they start
with `docs/superpowers/` (this repo).

**Execution:** Native (one implementer in one session; the tasks share `pr.py`, `phase.py` and
`gate.py` and are small), then the user's review protocol on the PR: independent adversarial reviews by
Fable (`fable-reviewer`) and GPT Astra (`codex:codex-rescue`, `--model gpt-6-astra --effort xhigh
--fresh`).

## Global Constraints

- Python 3.12 stdlib only; tests are `unittest` classes; the suite must stay green after every task.
- No new `harness` commands and no new event kinds (spec §6.7 schema v1 unchanged).
- Nothing project-specific in code or instruction files (no `mvp`, `echo-wiki`, `npm`, `preflight`).
- Scoring stays idempotent over raw events (§6.12): re-scoring old tasks is allowed to change their
  cards only where this plan changes a rule, and each such change is listed in Task 9.
- Instruction files stay terse: one line per rule; `AGENTS.md` is read by every task session.
- Agent-agnostic: every rule reads only fields both adapters emit (`session_end`, `prompt`, `stop`,
  CLI events), so Slice 2 (Codex) stays additive.
- Default behavior for already-installed projects is unchanged unless a gap requires it
  (`project.json` without `merge` means `user`).

## What this plan fixes, and why each is in

| Gap | Evidence (testing-notes / clashes) | Fix | Task |
|---|---|---|---|
| #35 gate reads only the first id after `Check:` | prereqs-table card stays not-done after `close --done`; `planfile.DECISION_CHECK_RE` | Parse a comma list | 1 |
| #26 `state.json` trusted for the phase | M1 s2 hand-edited `phase` to `verify`; `phase.py`, `pr.py` read it | Phase comes from the event log; `state.json` keeps only `task_id`, `branch`, `created_at` | 2 |
| #28 plan rewritten without checks | M1 s2 dropped `## Acceptance checks`; nothing noticed until `pr` | Every `phase` command (except `triage enter`) refuses an unusable `plan.md` | 3 |
| #41 observed check that needs the PR | E2 C8 ("CI passes on this PR") could not be recorded before `harness pr`; agent had to drop and restore it | Runnable checks gate opening the PR; observational checks gate `ready` | 4 |
| P2/W3, #6 PR titles | mvp `main`: `Fix ECH-200: … must emit the (#553)` breaks conventional commits | `harness pr --title`; default cut at a word | 5 |
| #37 `pr` needs the task id | E4 s2's first `harness pr --refresh` failed on usage | Task id optional, resolved from the branch like `phase`/`check` | 5 |
| Q1, #29/P1 merge rule | User wants agents able to merge when mandated (cloud); mvp's skill says `--auto` | `project.json` `merge: user\|agent`, printed by `harness pr` at `ready` | 5 |
| #2/P4 pre-push hook runs twice | M3 `ready` push took ~2 min more (preflight again) | The bookkeeping-only second push skips hooks | 5 |
| #40 clock runs with no agent alive | M1 wall 2.26 h, about 17 min of it worked | The controlling session's end pauses the clock until the task's next `harness` command | 6 |
| #43 agent time drops a span | M3 lost 207 s and its whole triage: a queued message fired a second prompt with no stop | A prompt that arrives before a stop closes the open span at that prompt | 6 |
| #27 agent works without the harness | M1 s2 carried on after `harness start` was denied | Bootstrap: stop if `harness start` fails in a harness project | 7 |
| #24 note times made up | 6 of 6 tasks wrote clock times that disagree with events | Notes carry the date only (deletion; no metric reads the time) | 7 |
| #32 checks pinned to a fixed SHA | prereqs-table C6/C7 broke after `harness pr` rebased | `triage.md`: diff against `git merge-base HEAD <remote>/<branch>` | 7 |
| #7/#31 S plans have no Decisions | E3 silently turned the requested observed check into a runnable one | S plans may add `## Decisions` | 7 |
| G1, P1, P7, #42 clashes | superpowers "must use skills"; mvp `--auto`; M3 posted a PR comment | `AGENTS.md`: harness alone plans, opens PRs, sets the merge rule, rebases; write to GitHub only through `harness pr`; never enable auto-merge | 7 |
| Clash record | User asked that project rules complement the harness | `docs/project-setup.md` in the harness repo (generic) | 8 |

## Deferred (not in this plan), with the reason

| Gap | Why it waits |
|---|---|
| #36 conflicts/revisions not recorded | Derivable already: revisions = number of `ready` events; refresh failures = handoff `build exit` after a `ready`. No new event kind |
| #8 extra review sessions counted | Topology is observe-only (§5.4); count-or-exclude is a scoring decision for Slice 3, not a defect |
| #38 `harness check` runs any plan command | Inherent: the agent writes its checks and could run the same command through any allowed tool. Documented in `docs/project-setup.md` |
| #4 rebase-merge with an extra commit passes | Only rebase merges; squash and merge commits are caught. Recorded in `docs/project-setup.md` (prefer squash or merge commits) |
| #3 `/clear` identity, #20 Codex fixtures, #21 desktop hooks, cloud spool | Slice 2 / later, per the roadmap (§11) |
| #11/#25 triage depth and tier under-calls | Product decisions about the workflow, not defects |
| #1, #5, #9, #10, #12–#19, #22, #23, #30, #33, #34, #39, #44 | Low severity, by design, or covered by a fix above (#33 is the gate working; #34/#39 by the `AGENTS.md` lines) |

## Review Focus

1. **A task folder created before this change** (its `state.json` still has `phase`, `phase_open`,
   `controlling_session`): every command must ignore those keys and use the event log. Pinned by
   Task 2's hand-edited `state.json` test, which writes exactly those keys.
2. **A later session that continues an open phase without `phase … enter`** after the controller
   ended (E2 s1 → s2): the clock must restart at that session's first `harness` command (`resume`).
   Pinned by Task 6's controller-end test.
3. **New commits after a PR opened "not ready"**: an observation recorded on an older code tree is
   stale, so `harness pr` must stay not-ready. Pinned by Task 4's stale-observation assertion.
4. **An invalid `merge` value in `project.json`** must fail loudly at load, not print a wrong rule.
   Pinned by Task 5's `load_project` test.
5. **`harness pr --refresh` run by the user with observational checks** must hand control back (exit
   1, `build exit --handoff`) instead of emitting `ready` or crashing. Pinned by Task 4's refresh test.

---

### Task 0: Branch

- [ ] **Step 1: Create the branch and confirm a green baseline**

```bash
cd ~/Desktop/src/echo-official/lean-harness
git fetch -q origin && git switch -c v0-hardening origin/main
python3 -m pytest -q
```
Expected: `108 passed`.

---

### Task 1: A Decision may name several checks (#35)

**Files:**
- Modify: `harness/planfile.py:9` (`DECISION_CHECK_RE`) and `harness/planfile.py:52-53` (`decision_refs`)
- Test: `tests/test_planfile.py`, `tests/test_gate.py`

**Interfaces:**
- Produces: `planfile.decision_refs(text: str) -> set[str]` (unchanged signature; now reads lists).

- [ ] **Step 1: Write the failing tests**

Append to `PlanfileTest` in `tests/test_planfile.py`:

```python
    def test_decision_refs_read_every_id_in_a_list(self):  # gap #35
        extra = ("- 2026-10-09 · claude · build — Rebased C6/C7. Why: main moved. [Check: C6, C7]\n"
                 "- 2026-10-09 · claude · build — Allow versions. Why: #15 merged. Check: C5, goal\n")
        self.assertEqual(planfile.decision_refs(PLAN + extra), {"C3", "C5", "C6", "C7", "goal"})
```

Append to `GateTest` in `tests/test_gate.py`:

```python
    def test_a_decision_naming_several_checks_covers_each(self):  # gap #35
        approved = PLAN.replace("exit 0.", "exit zero.")  # C1 was rewritten after approval
        named = PLAN.replace("[Check: C3]", "[Check: C3, C1]")
        self.assertNotIn("C1 changed since approval without a Decision naming it",
                         gate.evaluate(named, approved, PASSING, "T1").reasons)
        self.assertIn("C1 changed since approval without a Decision naming it",
                      gate.evaluate(PLAN, approved, PASSING, "T1").reasons)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_planfile.py tests/test_gate.py`
Expected: 2 failures (`{"C3", "C5", "C6", "goal"}` missing `C7`; the gate still lists C1).

- [ ] **Step 3: Implement**

In `harness/planfile.py` replace line 9 with:

```python
_REF = r"(?:C\d+|goal)"
DECISION_CHECK_RE = re.compile(rf"\bCheck:\s*({_REF}(?:\s*,\s*{_REF})*)")
```

and replace `decision_refs` with:

```python
def decision_refs(text: str) -> set[str]:
    """Every check id (or `goal`) a Decision names; `Check: C6, C7` names both (gap #35)."""
    refs = set()
    for group in DECISION_CHECK_RE.findall(sections(text).get("Decisions", "")):
        refs.update(part.strip() for part in group.split(","))
    return refs
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m pytest -q tests/test_planfile.py tests/test_gate.py`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add harness/planfile.py tests/test_planfile.py tests/test_gate.py
git commit -m "fix(gate): a Decision's Check: may name several checks (#35)"
```

---

### Task 2: The event log is the only source of a task's phase (#26)

**Files:**
- Modify: `harness/gate.py` (add `open_phase`), `harness/commands/phase.py` (`enter`, `exit_phase`,
  `_write`), `harness/commands/pr.py:53-55` and `:100-102`, `harness/commands/start.py:45-47` and
  `bootstrap`
- Test: `tests/test_gate.py`, `tests/test_phase.py`, `tests/test_start.py:32-34`,
  `tests/test_pr.py:68` and `:135`

**Interfaces:**
- Produces: `gate.open_phase(events: list[dict]) -> str | None`: the phase name the task's last phase
  event left open, in log order; `None` when the last phase event is an exit or there is none.
- `state.json` written by `start --new` becomes `{"task_id", "branch", "created_at"}`; nothing reads
  phase fields from it.
- `harness start` (bootstrap) prints a `phase: …` line after the task id.

- [ ] **Step 1: Write the failing tests**

Append to `GateTest` in `tests/test_gate.py`:

```python
    def test_open_phase_follows_the_last_phase_event(self):  # gap #26
        self.assertIsNone(gate.open_phase([]))
        enter = ev("phase", 1, phase="build", action="enter")
        self.assertEqual(gate.open_phase([enter, ev("check", 2, check_id="C1")]), "build")
        self.assertIsNone(gate.open_phase([enter, ev("phase", 3, phase="build", action="exit")]))
```

Append to `PhaseTest` in `tests/test_phase.py`:

```python
    def test_a_hand_edited_state_json_changes_nothing(self):  # gap #26, Review Focus 1
        wt, env, task_id = self.sb.through_triage("ph-tamper", {"C1": "true"})
        path = taskfiles.task_dir(wt, task_id) / "state.json"
        taskfiles.write_json(path, {**taskfiles.read_json(path), "phase": "verify", "phase_open": True,
                                    "controlling_session": "S1"})
        r = self.phase(wt, env, "verify", "exit")
        self.assertEqual(r.returncode, 1)
        self.assertIn("phase verify is not open (open: none)", r.stderr)
        self.assertEqual(self.phase(wt, env, "build", "enter").returncode, 0)
        self.assertEqual(self.phases(wt, task_id)[-1], ("build", "enter"))
```

In `test_triage_needs_this_sessions_passing_doctor` replace the two `state` lines (25–26) with:

```python
        evs = [e for e in self.sb.spool(wt) if e.get("task_id") == task_id]
        self.assertEqual(gate.open_phase(evs), "triage")
        self.assertEqual([e["controlling_session"] for e in evs if e["kind"] == "phase"], ["S1"])
```

and add `gate` to its import: `from harness import gate, gitio, spool, taskfiles`.

In `tests/test_start.py`, `StartNewTest.test_registers_the_task_and_starts_the_clock`, replace the
`state` assertion (lines 33–34) with:

```python
        self.assertEqual(state, {"task_id": task_id, "branch": "t-reg", "created_at": state["created_at"]})
```

Append to `BootstrapTest`:

```python
    def test_bootstrap_prints_the_tasks_phase(self):  # gap #26
        wt, env, task_id = self.sb.begin_task("st-phase")
        self.assertIn("phase: none yet", self.sb.harness("start", cwd=wt, env=env).stdout)
        self.sb.harness("phase", "triage", "enter", cwd=wt, env=env)
        self.assertIn("phase: triage (open)", self.sb.harness("start", cwd=wt, env=env).stdout)
```

In `tests/test_pr.py` add `from harness import gate` to the imports, add this helper to `PrTest`:

```python
    def task_events(self, wt, task_id):
        return [e for e in self.sb.spool(wt) if e.get("task_id") == task_id]
```

and replace both `state.json` `phase_open` assertions (lines 68 and 135) with
`self.assertIsNone(gate.open_phase(self.task_events(wt, task_id)))`.

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_gate.py tests/test_phase.py tests/test_start.py tests/test_pr.py`
Expected: failures for `open_phase` missing, the tamper test (exit 0 instead of 1), the state shape and
the bootstrap phase line.

- [ ] **Step 3: Implement**

Add to `harness/gate.py` after `needs_build_enter`:

```python
def open_phase(events: list[dict]) -> str | None:
    """The phase the task's last phase event left open, in log order. The event log, not state.json,
    is the record (gap #26)."""
    phases = _of(events, "phase")
    if not phases or phases[-1].get("action") != "enter":
        return None
    return phases[-1].get("phase")
```

In `harness/commands/phase.py` change the import to
`from harness import HarnessError, context, gate, taskfiles` and replace `enter`, `exit_phase` and
`_write` with:

```python
def enter(ctx, task_id: str, name: str) -> None:
    folder = _folder(ctx, task_id)
    if name == "triage" and not _doctor_passed(ctx, task_id):
        raise HarnessError("run `harness start` first: triage needs this session's passing doctor check")
    snapshot = name == "build" and not (folder / "plan.approved.md").exists()
    if snapshot and not (folder / "plan.md").exists():
        raise HarnessError("plan.md is missing; triage writes it")
    current = gate.open_phase(context.task_events(ctx, task_id))
    if current:
        if current == "triage":
            _finish_triage(ctx, task_id, folder)  # an implicit triage exit stamps and copies too (R-3, §6.6)
        _write(ctx, task_id, current, "exit", False)  # phases are contiguous (§5.1)
    if snapshot:
        shutil.copyfile(folder / "plan.md", folder / "plan.approved.md")  # first build entry only (§5.2)
    _write(ctx, task_id, name, "enter", False)
    print(f"{name}: entered")


def exit_phase(ctx, task_id: str, name: str, handoff: bool = False) -> None:
    folder = _folder(ctx, task_id)
    current = gate.open_phase(context.task_events(ctx, task_id))
    if current != name:
        raise HarnessError(f"phase {name} is not open (open: {current or 'none'})")
    if name == "triage":
        _finish_triage(ctx, task_id, folder)
    _write(ctx, task_id, name, "exit", handoff)
    print(f"{name}: exited")


def _write(ctx, task_id, name, action, handoff) -> None:
    context.record(ctx, context.event(ctx, "phase", task_id, phase=name, action=action, handoff=handoff,
                                      controlling_session=ctx.identity.session_id))  # null for your manual commands (§6.9)
```

In `harness/commands/pr.py` (`gate` is already imported) replace lines 53–55 with:

```python
    current = gate.open_phase(evs)
    if current:
        phase.exit_phase(ctx, task_id, current)  # a ready writes the missing exit first
```

and in `refresh`'s `except HarnessError:` block replace the two `state` lines with:

```python
        if gate.open_phase(context.task_events(ctx, task_id)):
            phase.exit_phase(ctx, task_id, "build", handoff=True)
```

In `harness/commands/start.py`, `new_task`: write `state.json` as

```python
        taskfiles.write_json(folder / "state.json", {
            "task_id": task_id, "branch": ctx.git.branch, "created_at": events.now_ts()})
```

and in `bootstrap` replace the final `print` with:

```python
    print(f"task {task_id}\n{_where(context.task_events(ctx, task_id))}\n"
          f"harness checkout: {REPO}\nNow read {REPO / 'AGENTS.md'}.")
```

adding `gate` to the import line and this helper below `bootstrap`:

```python
def _where(evs: list[dict]) -> str:
    """Where a later session picks up: the open phase, the last one, or none (gap #26)."""
    if gate.needs_build_enter(evs):
        return "phase: after ready; any further change starts with `harness phase build enter`"
    current = gate.open_phase(evs)
    if current:
        return f"phase: {current} (open)"
    exits = [e for e in evs if e.get("kind") == "phase"]
    return f"phase: {exits[-1]['phase']} (exited)" if exits else "phase: none yet"
```

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add harness tests
git commit -m "fix(phase): take a task's phase from its event log, never state.json (#26)"
```

---

### Task 3: Phase commands refuse an unusable plan (#28)

**Files:**
- Modify: `harness/planfile.py` (add `problems`), `harness/commands/phase.py` (`enter`, `exit_phase`)
- Test: `tests/test_planfile.py`, `tests/test_phase.py`

**Interfaces:**
- Produces: `planfile.problems(text: str, tier: str | None = None) -> list[str]` (empty when usable).

- [ ] **Step 1: Write the failing tests**

Append to `PlanfileTest` in `tests/test_planfile.py`:

```python
    def test_problems(self):  # gap #28
        self.assertEqual(planfile.problems(PLAN, "M"), [])
        no_checks = PLAN[:PLAN.index("### C1")] + PLAN[PLAN.index("## Tier"):]
        self.assertEqual(planfile.problems(no_checks, "M"),
                         ["plan.md has no acceptance checks (`### C1 — …` under `## Acceptance checks`)"])
        unmarked = PLAN.replace("(observational)", "")
        self.assertIn("C2 has no fenced command and is not marked (observational)", planfile.problems(unmarked, "M"))
        self.assertIn("C2 is observational; every S check must be runnable", planfile.problems(PLAN, "S"))
        self.assertIn("plan.md has no `## Goal`", planfile.problems(PLAN.replace("Add a greeting.", ""), "M"))
```

Append to `PhaseTest` in `tests/test_phase.py`:

```python
    def test_phase_commands_refuse_a_plan_without_checks(self):  # gap #28
        wt, env, task_id = self.sb.through_triage("ph-noplan", {"C1": "true"})
        (taskfiles.task_dir(wt, task_id) / "plan.md").write_text("# rewritten\n\n## Goal\nAdd a greeting.\n")
        r = self.phase(wt, env, "build", "enter")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no acceptance checks", r.stderr)
        self.assertNotIn(("build", "enter"), self.phases(wt, task_id))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_planfile.py tests/test_phase.py`
Expected: `problems` missing; `build enter` succeeds (exit 0).

- [ ] **Step 3: Implement**

Add to `harness/planfile.py` after `checks`:

```python
def problems(text: str, tier: str | None = None) -> list[str]:
    """What makes plan.md unusable as the task's contract (gap #28); empty when it is usable."""
    out = [] if goal(text) else ["plan.md has no `## Goal`"]
    found = checks(text)
    if not found:
        out.append("plan.md has no acceptance checks (`### C1 — …` under `## Acceptance checks`)")
    for c in found.values():
        if not c.command and not c.observational:
            out.append(f"{c.id} has no fenced command and is not marked (observational)")
        if tier == "S" and c.observational:
            out.append(f"{c.id} is observational; every S check must be runnable")
    return out
```

In `harness/commands/phase.py` add `planfile` to the import and this helper:

```python
def _require_usable_plan(folder) -> None:
    path = folder / "plan.md"
    if not path.exists():
        raise HarnessError("plan.md is missing; triage writes it (see skills/phases/triage.md)")
    config = folder / "config.json"
    tier = taskfiles.read_json(config).get("record", {}).get("tier") if config.exists() else None
    found = planfile.problems(path.read_text(), tier)
    if found:
        raise HarnessError("fix plan.md first:\n" + "\n".join(f"- {p}" for p in found))
```

Call it before any write: in `enter`, right after computing `current`, add
`if name != "triage": _require_usable_plan(folder)` and delete the now-redundant two lines
`if snapshot and not (folder / "plan.md").exists(): raise …`; in `exit_phase`, right after the
`current != name` refusal, add `_require_usable_plan(folder)`.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass. If an existing test enters a later phase without a plan, it was relying on the
gap; give it a plan with `write_plan` rather than weakening the check.

- [ ] **Step 5: Commit**

```bash
git add harness tests
git commit -m "fix(phase): refuse a plan.md without a goal or usable checks (#28)"
```

---

### Task 4: Runnable checks gate the PR; observational checks gate `ready` (#41)

**Files:**
- Modify: `harness/gate.py` (`unmet_checks`, `failing_checks`), `harness/commands/pr.py`
  (`pr_body`, `publish`, `refresh`, `run`)
- Test: `tests/test_pr.py`

**Interfaces:**
- Produces: `gate.unmet_checks(plan_text, events, code_tree, before_ts=None) -> dict[str, str]`
  (check id → reason); `gate.failing_checks(...)` keeps its signature and output.
- `pr.publish(ctx, project, task_id) -> str` returns `"ready"` or `"pending"`.
- `pr.pr_body(task_id, plan, scope, pending=()) -> str`.

- [ ] **Step 1: Write the failing tests**

Add to `PrTest` in `tests/test_pr.py`:

```python
    def observed_task(self, slug):
        """Through verify with C1 runnable and passing, C2 observational and unrecorded."""
        wt, env, task_id = self.sb.through_triage(slug, {"C1": "true", "C2": None})
        self.h(wt, env, "phase", "build", "enter")
        (wt / "feature.txt").write_text("f\n")
        commit(wt, "build")
        self.h(wt, env, "phase", "verify", "enter")
        commit(wt, "verify enter")
        self.assertEqual(self.h(wt, env, "check", "--all").returncode, 0)
        return wt, env, task_id

    def test_observational_checks_wait_for_the_open_pr(self):  # gap #41
        wt, env, task_id = self.observed_task("pr-observe")
        creates = self.gh_log().count("pr create")
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("not ready", r.stdout)
        self.assertEqual(self.gh_log().count("pr create"), creates + 1)
        self.assertIn("Waiting for observation: C2", self.gh_log())
        kinds = [k for k, _, _ in self.kinds(wt, task_id)]
        self.assertIn("pr", kinds)
        self.assertNotIn("ready", kinds)
        self.assertEqual(gate.open_phase(self.task_events(wt, task_id)), "verify")
        (wt / "late.txt").write_text("late\n")          # Review Focus 3: an old observation goes stale
        commit(wt, "late change")
        self.h(wt, env, "check", "C1")
        self.h(wt, env, "check", "C2", "--observed", "pass")
        (wt / "later.txt").write_text("later\n")
        commit(wt, "later change")
        self.h(wt, env, "check", "C1")
        self.assertIn("not ready", self.h(wt, env, "pr", task_id).stdout)
        self.assertEqual(self.h(wt, env, "check", "C2", "--observed", "pass").returncode, 0)
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ready:", r.stdout)
        self.assertEqual(self.gh_log().count("pr create"), creates + 1)
        self.assertEqual([k for k, _, _ in self.kinds(wt, task_id)].count("pr"), 1)

    def test_refresh_hands_back_when_an_observation_is_stale(self):  # gap #41, Review Focus 5
        wt, env, task_id = self.observed_task("pr-obs-refresh")
        self.h(wt, env, "check", "C2", "--observed", "pass")
        self.assertEqual(self.h(wt, env, "pr", task_id).returncode, 0)
        (self.sb.main / "moved.txt").write_text("m\n")
        commit(self.sb.main, "main moves")
        git(self.sb.main, "push", "-q", "origin", "main", env=self.sb.env)
        r = self.h(wt, {}, "pr", "--refresh", task_id)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("not ready", r.stdout)
        evs = self.sb.task_file_events(wt, task_id)
        last = [e for e in evs if e["kind"] == "phase"][-1]
        self.assertEqual((last["phase"], last["action"], last["handoff"]), ("build", "exit", True))
        self.assertEqual(sum(e["kind"] == "ready" for e in evs), 1)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_pr.py`
Expected: both new tests fail (`pr` refuses with "C2: no recorded attempt").

- [ ] **Step 3: Implement `gate.unmet_checks`**

Replace `failing_checks` in `harness/gate.py` with:

```python
def unmet_checks(plan_text: str, events: list[dict], code_tree: str | None,
                 before_ts: str | None = None) -> dict[str, str]:
    """Final checks whose latest completed attempt (before before_ts) did not pass at code_tree with
    the check text in plan_text, each with its reason. A check with no attempt is unmet (§6.11)."""
    attempts = [e for e in _of(events, "check") if before_ts is None or e["ts"] < before_ts]
    out = {}
    for cid, check in planfile.checks(plan_text).items():
        mine = [e for e in attempts if e.get("check_id") == cid]
        if not mine:
            out[cid] = "no recorded attempt"
            continue
        last = max(mine, key=lambda e: e["ts"])
        if last.get("result") != "pass":
            out[cid] = f"latest attempt {last.get('result')}"
        elif last.get("code_tree") != code_tree:
            out[cid] = "latest pass ran on another code tree"
        elif last.get("check_text_hash") != planfile.check_hash(check):
            out[cid] = "check text changed since its latest pass"
    return out


def failing_checks(plan_text: str, events: list[dict], code_tree: str | None, before_ts: str | None = None) -> list[str]:
    """unmet_checks as `C<n>: <reason>` lines; a plan with no checks fails (§6.11)."""
    if not planfile.checks(plan_text):
        return ["plan.md has no acceptance checks"]
    return [f"{cid}: {why}" for cid, why in unmet_checks(plan_text, events, code_tree, before_ts).items()]
```

- [ ] **Step 4: Implement the pending path in `harness/commands/pr.py`**

Replace `pr_body`, `publish` and `refresh`, and make `run` return 0 for both publish outcomes:

```python
def pr_body(task_id: str, plan: str, scope: tuple[str, ...], pending: tuple[str, ...] = ()) -> str:
    lines = [f"Harness task `{task_id}`.", "", "## Goal", planfile.goal(plan), "", "## Acceptance checks"]
    lines += [f"- {c.text.splitlines()[0].removeprefix('### ')}" for c in planfile.checks(plan).values()]
    if pending:
        lines += ["", "## Not ready yet",
                  f"Waiting for observation: {', '.join(pending)}. Do not merge before the harness reports `ready`."]
    if scope:
        lines += ["", "## Potential scope reduction",
                  f"Changed since plan approval: {', '.join(scope)}.",
                  f"Merge only if the original outcome still holds, then run `harness close {task_id} --done`."]
    return "\n".join(lines) + "\n"


def publish(ctx, project: dict, task_id: str) -> str:
    """Open or update the PR. Runnable checks must pass first; observational checks still unrecorded
    at this code tree leave it open without `ready` (gap #41). Returns "ready" or "pending"."""
    folder = taskfiles.task_dir(ctx.root, task_id)
    evs = context.task_events(ctx, task_id)
    if not any(e.get("kind") == "phase" and e.get("phase") == "triage" and e.get("action") == "enter" for e in evs):
        raise HarnessError("no `harness phase triage enter` recorded for this task")
    if gate.needs_build_enter(evs):
        raise HarnessError("after `ready`, run `harness phase build enter` before `harness pr`")
    dirty = gitio.dirty_outside_harness(ctx.root)
    if dirty:
        raise HarnessError("commit your changes first:\n" + "\n".join(dirty))
    plan = (folder / "plan.md").read_text()
    tree = gitio.code_tree(ctx.root)
    checks = planfile.checks(plan)
    if not checks:
        raise HarnessError("checks are not passing at this code tree:\nplan.md has no acceptance checks")
    unmet = gate.unmet_checks(plan, evs, tree)
    blocking = [f"{cid}: {why}" for cid, why in unmet.items() if checks[cid].command]
    if blocking:
        raise HarnessError("checks are not passing at this code tree:\n" + "\n".join(blocking))
    if not (folder / "plan.approved.md").exists():  # R-49: the done gate needs it and a merge can't create it
        raise HarnessError("no plan.approved.md: run `harness phase build enter` first (its first entry snapshots the plan)")
    pending = tuple(unmet)  # only observational checks remain
    current = gate.open_phase(evs)
    if current and not pending:
        phase.exit_phase(ctx, task_id, current)  # a ready writes the missing exit first
    remote, base, branch = project["integration_remote"], project["default_branch"], ctx.git.branch
    gitio.commit_paths(ctx.root, ".harness", f"harness: record {task_id}")
    gitio.push(ctx.root, remote, branch)
    scope = planfile.diff((folder / "plan.approved.md").read_text(), plan).scope_reductions()
    body = pr_body(task_id, plan, scope, pending)
    prior = [e for e in evs if e.get("kind") == "pr"]
    if prior:
        number, url = prior[-1]["number"], prior[-1]["url"]
        ghio.pr_edit_body(ctx.root, number, body)  # re-emit: no second PR (R-15)
    else:
        number, url = ghio.pr_create(ctx.root, base, branch, title(plan, task_id), body)
        context.record(ctx, context.event(ctx, "pr", task_id, number=number, url=url))
    if pending:
        gitio.commit_paths(ctx.root, ".harness", f"harness: pr {task_id}")
        gitio.push(ctx.root, remote, branch)
        names = " ".join(pending)
        print(f"pr open: {url}\nnot ready: observe {names} on the open PR, record each with "
              f"`harness check <C-id> --observed pass|fail`, then run `harness pr {task_id}` again.")
        return "pending"
    tip = gitio.out(["rev-parse", "HEAD"], ctx.root)
    context.record(ctx, context.event(ctx, "ready", task_id, tip_commit=tip, code_tree=tree))
    gitio.commit_paths(ctx.root, ".harness", f"harness: ready {task_id}")
    try:
        gitio.push(ctx.root, remote, branch)
    except HarnessError as e:
        raise HarnessError(f"{e}\n`ready` is recorded; finish with `git push {remote} HEAD`") from e
    print(f"ready: {url}")
    return "ready"


def refresh(ctx, project: dict, task_id: str) -> int:
    phase.enter(ctx, task_id, "build")
    try:
        if rebase.rebase(ctx, project) == "conflict":
            rebase.abort(ctx)
            phase.exit_phase(ctx, task_id, "build", handoff=True)  # control returns to you (R-1)
            print("rebase conflict: aborted. A session in this worktree resolves it with `harness rebase`, "
                  "then runs `harness pr`.")
            return 1
        plan = (taskfiles.task_dir(ctx.root, task_id) / "plan.md").read_text()
        results = [check.run_one(ctx, task_id, c) for c in planfile.checks(plan).values() if c.command]
        if "fail" in results:
            phase.exit_phase(ctx, task_id, "build", handoff=True)
            print("checks fail at the rebased code: a session in this worktree fixes them, then runs `harness pr`.")
            return 1
        if publish(ctx, project, task_id) == "pending":
            phase.exit_phase(ctx, task_id, "build", handoff=True)  # observations are owed at the new code
            return 1
        return 0
    except HarnessError:
        # R-44: any other non-ready ending still closes build with handoff; skip if publish already closed it
        if gate.open_phase(context.task_events(ctx, task_id)):
            phase.exit_phase(ctx, task_id, "build", handoff=True)
        raise
```

In `run`, replace the last line with:

```python
    if args.refresh:
        return refresh(ctx, project, args.task_id)
    publish(ctx, project, args.task_id)
    return 0
```

Note the `pr` event is now recorded right after `pr_create` (before `ready`); update
`test_publish_pushes_opens_one_pr_and_records_ready` to expect the last three kinds as
`[("phase", "verify", "exit"), ("pr", None, None), ("ready", None, None)]`.

- [ ] **Step 5: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add harness tests
git commit -m "feat(pr): open the PR before observational checks; ready waits for them (#41)"
```

---

### Task 5: PR title, optional task id, merge rule, one hooked push (P2, #37, Q1, #2)

**Files:**
- Modify: `harness/commands/pr.py` (`add_args`, `run`, `title`, `publish`), `harness/ghio.py`
  (`pr_edit_body` → `pr_edit`), `harness/gitio.py` (`push`), `harness/taskfiles.py` (`load_project`),
  `harness/commands/install.py` (`PROJECT_DEFAULTS`)
- Test: `tests/test_pr.py`, `tests/test_taskfiles.py`

**Interfaces:**
- CLI: `harness pr [<task-id>] [--title TITLE] [--refresh]`.
- `pr.title(plan: str, task_id: str, given: str | None = None) -> str`.
- `pr.merge_rule(project: dict, task_id: str, number: int) -> str`.
- `ghio.pr_edit(cwd, number: int, body: str, title: str | None = None) -> None`.
- `gitio.push(cwd, remote: str, branch: str, verify: bool = True) -> None`.
- `project.json` key `merge`: `"user"` (default when absent) or `"agent"`.

- [ ] **Step 1: Write the failing tests**

Add `from pathlib import Path` and `from harness.commands import pr` to the imports at the top of
`tests/test_pr.py`, and append:

```python
class PrUnitTest(unittest.TestCase):
    def test_title_given_wins_and_default_cuts_at_a_word(self):  # clash P2/W3, gap #6
        plan = "## Goal\n" + "word " * 30 + "\n"
        self.assertEqual(pr.title(plan, "t", "fix(x): greet"), "fix(x): greet")
        default = pr.title(plan, "t")
        self.assertLessEqual(len(default), 72)
        self.assertTrue(default.endswith("word…"), default)

    def test_merge_rule_follows_project_json(self):  # Q1, clash P1
        self.assertIn("the user merges", pr.merge_rule({}, "t1", 7))
        rule = pr.merge_rule({"merge": "agent"}, "t1", 7)
        self.assertIn("harness pr --refresh t1", rule)
        self.assertIn("gh pr merge 7 --match-head-commit", rule)
        self.assertIn("Never enable auto-merge", rule)
```

Add to `PrTest`:

```python
    def test_title_flag_task_id_from_branch_and_one_hooked_push(self):  # P2, #37, #2
        wt, env, task_id = self.built("pr-title")
        hook = Path(gitio.info(wt).common_dir) / "hooks" / "pre-push"
        log = self.sb.tmp / "pre-push.log"
        hook.write_text(f"#!/bin/sh\necho push >> {log}\n")
        hook.chmod(0o755)
        self.addCleanup(hook.unlink)
        r = self.h(wt, env, "pr", "--title", "feat: add a greeting")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--title feat: add a greeting", self.gh_log())
        self.assertIn("the user merges", r.stdout)
        self.assertEqual(log.read_text().count("push"), 1)
```

Append to `TaskfilesTest` in `tests/test_taskfiles.py`:

```python
    def test_load_project_refuses_an_unknown_merge_rule(self):  # Review Focus 4
        self.write_project(merge="sometimes")
        with self.assertRaisesRegex(HarnessError, "merge must be"):
            taskfiles.load_project(self.repo)
        self.write_project(merge="agent")
        self.assertEqual(taskfiles.load_project(self.repo)["merge"], "agent")
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_pr.py tests/test_taskfiles.py`
Expected: failures (`title()` takes 2 arguments; `merge_rule` missing; `--title` unknown; two pushes ran
the hook; `merge` not validated).

- [ ] **Step 3: Implement**

`harness/gitio.py` — replace `push`:

```python
def push(cwd, remote: str, branch: str, verify: bool = True) -> None:
    """Push HEAD to the same-named remote branch. The project's pre-push hook runs (R-14, §4.6) unless
    verify is False, which `harness pr` uses only for a push that adds harness bookkeeping in
    `.harness/` on top of a push whose hook already ran on the same code tree (gap #2)."""
    run(["push", "--force-with-lease", "--set-upstream", *([] if verify else ["--no-verify"]),
         remote, f"HEAD:refs/heads/{branch}"], cwd, capture=False)
```

`harness/ghio.py` — replace `pr_edit_body`:

```python
def pr_edit(cwd, number: int, body: str, title: str | None = None) -> None:
    _ok(["pr", "edit", str(number), "--body", body, *(["--title", title] if title else [])], cwd)
```

`harness/taskfiles.py`, `load_project` — before `return project` add:

```python
    if project.get("merge", "user") not in ("user", "agent"):
        raise HarnessError("fix .harness/project.json: merge must be \"user\" or \"agent\"")
```

`harness/commands/install.py` — add `"merge": "user",` to `PROJECT_DEFAULTS` after `"cloud_env_vars"`.

`harness/commands/pr.py`:

```python
import textwrap

MERGE_RULES = {
    "user": "Merge: the user merges this PR after `harness pr --refresh {task_id}`; do not merge it "
            "or enable auto-merge.",
    "agent": "Merge: run `harness pr --refresh {task_id}`; when it prints ready, merge with "
             "`gh pr merge {number} --match-head-commit <the head it prints>` and the project's merge "
             "method. Never enable auto-merge.",
}


def add_args(p) -> None:
    p.add_argument("task_id", nargs="?", help="default: the task on this branch")
    p.add_argument("--title", help="the PR title, in the project's commit-message style")
    p.add_argument("--refresh", action="store_true", help="before merging: rebase, recheck, re-emit ready")


def run(args, ctx) -> int:
    project = ctx.require_project()
    task_id = args.task_id or taskfiles.resolve(ctx.root, ctx.cwd, ctx.env, ctx.git)
    folder = taskfiles.task_dir(ctx.root, task_id)
    if not (folder / "state.json").exists():
        raise HarnessError(f"task {task_id} has no folder here; run this in the task's worktree")
    if taskfiles.read_json(folder / "state.json")["branch"] != ctx.git.branch:
        raise HarnessError("run `harness pr` on the task's branch")
    if args.refresh:
        return refresh(ctx, project, task_id)
    publish(ctx, project, task_id, args.title)
    return 0


def title(plan: str, task_id: str, given: str | None = None) -> str:
    if given:
        return given
    goal = planfile.goal(plan)
    return textwrap.shorten(goal.splitlines()[0], 72, placeholder="…") if goal else task_id


def merge_rule(project: dict, task_id: str, number: int) -> str:
    return MERGE_RULES[project.get("merge", "user")].format(task_id=task_id, number=number)
```

In `publish`: add a `given_title: str | None = None` parameter; replace the PR create/edit block with

```python
    if prior:
        number, url = prior[-1]["number"], prior[-1]["url"]
        ghio.pr_edit(ctx.root, number, body, given_title)  # re-emit: no second PR (R-15)
    else:
        number, url = ghio.pr_create(ctx.root, base, branch, title(plan, task_id, given_title), body)
        context.record(ctx, context.event(ctx, "pr", task_id, number=number, url=url))
```

pass `verify=False` to the two bookkeeping pushes (the `harness: pr` push in the pending branch and the
`harness: ready` push), keep the first `gitio.push` hooked, and replace the final `print` with:

```python
    head = gitio.out(["rev-parse", "HEAD"], ctx.root)
    print(f"ready: {url} (head {head})\n{merge_rule(project, task_id, number)}")
```

`refresh` calls `publish(ctx, project, task_id)` (no title: a refresh keeps the existing one).

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass (the stub `gh` accepts `pr edit … --title`).

- [ ] **Step 5: Commit**

```bash
git add harness tests
git commit -m "feat(pr): --title, task id from the branch, printed merge rule, one hooked push"
```

---

### Task 6: Wall time pauses when the controller ends; mid-turn prompts keep agent time (#40, #43)

**Files:**
- Modify: `harness/timing.py` (`charged_intervals`, `agent_time`)
- Test: `tests/test_timing.py`

**Interfaces:** unchanged signatures (`timing.wall`, `timing.agent_time`).

- [ ] **Step 1: Write the failing tests**

Append to `WallTest` in `tests/test_timing.py`:

```python
    def test_controller_session_end_pauses_until_the_next_harness_command(self):  # gap #40, Review Focus 2
        w = self.wall([ev("start", 0), ph(1, "verify", "enter"),
                       hook("session_end", 10),                       # S1 ends inside verify, no handoff
                       hook("session_start", 50, session="S2"),
                       ev("resume", 52, session_id="S2"),             # S2's `harness start`
                       ph(59, "verify", "exit", session="S2"), ev("ready", 60)])
        self.assertEqual(w.total_ms, (10 + 8) * MIN)
        self.assertEqual(w.by_phase, {"between_phases": 2 * MIN, "verify": 16 * MIN})
        self.assertTrue(w.complete)

    def test_another_sessions_end_does_not_pause(self):  # gap #40 (review sessions, delegates)
        w = self.wall([ev("start", 0), ph(1, "build", "enter"), hook("session_end", 5, session="REVIEW"),
                       ph(29, "build", "exit"), ev("ready", 30)])
        self.assertEqual(w.total_ms, 30 * MIN)
```

In `AgentTimeTest.test_prompt_to_last_stop_per_session_plus_helpers` change the comment on S2's line
to `# first span: closed by the second prompt` and the assertions to:

```python
        self.assertEqual(a.total_ms, (8 + 2 + 4 + 2) * MIN)  # S2's first turn ran until its second prompt
        self.assertEqual(a.unknown_spans, 2)  # S2's second prompt without a stop, helper a2
        self.assertEqual(a.by_phase, {"build": 16 * MIN})
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_timing.py`
Expected: 3 failures (wall 59 min instead of 18; agent time 14 instead of 16).

- [ ] **Step 3: Implement**

Replace `charged_intervals` in `harness/timing.py`:

```python
def charged_intervals(events: list[dict], until_ms: int) -> tuple[list[tuple[int, int]], list[str]]:
    """Spans the wall clock runs. `ready`, a handoff exit and an abandon pause it; a later revision
    restarts at its resume or build enter (R-2). The controlling session's end also pauses it (no
    agent is left working), and the task's next `harness` command restarts it (gap #40)."""
    intervals, missing = [], []
    started, running, since, resumes = False, False, 0, {}
    controller, ended = None, False
    for e in events:
        kind, t = e.get("kind"), ts_ms(e["ts"])
        if kind == "phase" and e.get("action") == "enter":
            controller = e.get("controlling_session")
        if kind == "start":
            started, running, since = True, True, t
            continue
        if not started:
            continue
        if ended and e.get("source") != "hook":
            running, since, ended = True, t, False
        if _pauses(e):
            if running:
                intervals.append((since, t))
                running, resumes = False, {}
            elif kind == "ready":
                missing.append(f"ready at {e['ts']} has no revision start (no `phase build enter` after the last pause)")
        elif kind == "session_end" and running and controller and e.get("session_id") == controller:
            intervals.append((since, t))
            running, resumes, ended = False, {}, True
        elif kind == "resume" and not running:
            resumes[e.get("session_id")] = t  # the latest resume per session
        elif kind == "phase" and e.get("action") == "enter" and not running:
            since = resumes.get(controller, t) if controller else t  # R-2
            running = True
    if not started:
        missing.append("no start event")
    elif running:
        intervals.append((since, max(since, until_ms)))
    return intervals, missing
```

In `agent_time`, replace the `if kind in ("prompt", "session_end"):` branch with:

```python
            if kind == "prompt" and prompt_t is not None and stop_t is None:
                spans.append((prompt_t, ts_ms(e["ts"])))  # a prompt delivered mid-turn: that turn ran until now (gap #43)
                prompt_t = ts_ms(e["ts"])
            elif kind in ("prompt", "session_end"):
                close(prompt_t, stop_t)
                prompt_t, stop_t = (ts_ms(e["ts"]), None) if kind == "prompt" else (None, None)
```

and update its docstring to: `"""Per session: prompt → last stop before the next prompt or session
end (a prompt that arrives before any stop closes the open span at that prompt); plus helper start →
stop."""`

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass. (`test_e2e` and `test_score` cards that end their sessions after `ready` are
unaffected; if one changes, check its controller ended before `ready` and update the expectation with
a comment naming gap #40.)

- [ ] **Step 5: Commit**

```bash
git add harness/timing.py tests/test_timing.py
git commit -m "fix(timing): pause on the controller's end; keep agent time across mid-turn prompts (#40, #43)"
```

---

### Task 7: Instruction files (#27, #24, #32, #7/#31, G1, P1, P7, #42, #26, #41, P2)

**Files:**
- Modify: `hooks/bootstrap.md`, `AGENTS.md`, `skills/phases/triage.md`, `skills/phases/build.md`,
  `skills/phases/verify.md`
- Test: `tests/test_instructions.py`

- [ ] **Step 1: Write the failing test**

Append to `InstructionsTest`:

```python
    def test_pr_lines_give_a_title(self):  # clash P2
        for path in (REPO / "AGENTS.md", PHASE_DIR / "build.md", PHASE_DIR / "verify.md"):
            for line in re.findall(r"`harness pr <task-id>[^`]*`", path.read_text()):
                self.assertIn("--title", line, f"{path.name}: {line}")
```

Run: `python3 -m pytest -q tests/test_instructions.py` — expected: FAIL.

- [ ] **Step 2: Rewrite `hooks/bootstrap.md`** (one line, kept as one paragraph):

```
If another agent launched you, ignore this file and follow your prompt. Otherwise run `harness start`, then read `AGENTS.md` from the checkout it prints. If `harness start` fails or is refused in a repository that has `.harness/project.json`, stop and tell the user: never work on a harness task without it.
```

- [ ] **Step 3: Edit `AGENTS.md`**

- First paragraph: "`harness start` sent you here and printed the task id and its phase."
- "Order" paragraph: replace "If `.harness/runs/<task-id>/state.json` already names a `phase`" with
  "If `harness start` printed a phase other than `none yet`".
- Replace item 3 with:

```
3. The last phase file ends with `harness pr <task-id> --title "<title>"`; write the title in the
   project's commit-message style. If it prints `not ready`, observe the checks it names on the open
   PR, record each with `harness check <C-id> --observed pass|fail`, and run `harness pr` again. Stop
   when it prints `ready`, then follow the merge rule it prints. Never enable auto-merge.
```

- In "Rules for every phase":
  - After "Commit it together with your code." add: "Never edit its `state.json`, `events.jsonl` or
    `plan.approved.md`: harness commands write them."
  - Notes template: replace `<date time>` with `<date>` and drop ", never reconstructed"; replace the
    `Check:` sentence with: "Decisions need `Why:`; a Decision that changes checks or the goal names each
    (`Check: C3`, `Check: C6, C7`, `Check: goal`)."
  - Replace the project-rules bullet with:

```
- The project's own rules decide how to build, test, push and clean up; acceptance checks call the
  project's commands. The harness alone plans the task, opens its PR, sets who merges it and rebases
  its branch: skills or project rules that do those another way do not apply inside a task.
- Write to GitHub only through `harness pr` and the merge rule it prints: no PR comments or edits.
```

- [ ] **Step 4: Edit the phase files**

`skills/phases/triage.md`:
- Step 2, after the sentence listing the M/L sections, add: "S plans add `## Decisions` when there is
  one to log, for example a check that departs from the request's wording."
- Step 3, after the observational paragraph, add: "A check that compares with the integration branch
  diffs against `$(git merge-base HEAD <remote>/<branch>)`: the branch moves while the task runs, so
  never use a fixed commit or the branch tip."

`skills/phases/build.md`: in the **Commands** line and step 7, write
`harness pr <task-id> --title "<title>"`.

`skills/phases/verify.md`: in the **Commands** line and step 5 write
`harness pr <task-id> --title "<title>"`; append to step 3: "One that needs the open PR (for example
its CI) is recorded after `harness pr` opens it (see `AGENTS.md` item 3)."

- [ ] **Step 5: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md hooks/bootstrap.md skills tests/test_instructions.py
git commit -m "docs(instructions): stop without the harness, date-only notes, PR titles, task ownership"
```

---

### Task 8: Project setup guide (the generic half of the clash record)

**Files:**
- Create: `docs/project-setup.md`

- [ ] **Step 1: Write `docs/project-setup.md`**

```markdown
# Setting up a project for the harness

The harness is generic. A project's own agent rules should complement it, not repeat or contradict it.

| The harness owns | The project owns |
|---|---|
| Phases, `plan.md`, acceptance checks, notes | How to build, test, lint and format |
| Opening the PR (`harness pr`), `ready`, who merges | Pre-push and pre-commit hooks, CI |
| Rebasing a task branch (`harness rebase`, `pr --refresh`) | Domain rules (data, security, catalogs) |
| Task records and timing | Cleanup after merge |

## Checklist

- **Merge rule:** `.harness/project.json` `merge` is `"user"` (default) or `"agent"`. `harness pr`
  prints the rule at `ready`. With `agent`, the agent runs `harness pr --refresh` and merges with
  `gh pr merge --match-head-commit`, never auto-merge. Prefer squash or merge commits: the done gate
  cannot see a commit added to a rebase merge after the last `ready`.
- **Project instructions** that prescribe planning, opening or merging PRs, rebasing or worktrees: add
  "In a harness task, follow the harness for these; everything else here still applies."
- **Permissions:** match the merge rule. With `user`, deny task agents `gh pr merge` and `gh api`;
  check allow-lists inherited from the main checkout's `.claude/settings.local.json`.
- **Commit conventions:** agents pass `harness pr --title` in the project's style; the squash commit on
  the default branch takes that title.
- **Pre-push hooks** run once per `harness pr` (on the push that carries code).
- **Machine-wide plugins with hooks** (stop gates, extra review sessions) run inside task sessions:
  check they cannot hold a session open or start work outside the task.
- **Checks are commands the agent writes.** `harness check` runs them with the agent's own access, so
  permission rules do not limit what a check can run; review checks in the plan.
```

- [ ] **Step 2: Commit**

```bash
git add docs/project-setup.md
git commit -m "docs: how a project's agent rules complement the harness"
```

---

### Task 9: Real-data regression, rollout notes, PR

**Files:** none in the repo (verification); PR description.

- [ ] **Step 1: Re-score real tasks in a copy of the state directory**

```bash
SCRATCH=$(mktemp -d)
cp -R ~/.local/state/harness "$SCRATCH/harness"
for p in echo-wiki mvp; do
  (cd ~/Desktop/src/echo-official/$p && XDG_STATE_HOME="$SCRATCH" python3 ~/Desktop/src/echo-official/lean-harness/harness/cli.py score)
done
```

Run from the `v0-hardening` checkout (adjust the `cli.py` path if implementing in a worktree). Compare
each new card with its copy under `~/.local/state/harness/<hash>/scorecards/`. Expected changes, and
only these:

| Task | Field | Before | Expected after | Rule |
|---|---|---|---|---|
| prereqs-table | `done`, gate reasons | false, "C7 changed … without a Decision" | true, none | #35 |
| journey-fixture-prettier (M1) | `wall.total_ms` | 8125823 | ≈ 998000 (14:32:22.5→14:39:58, then 16:38:45→16:47:48) | #40 |
| ech-171-parity (M3) | `agent_time.by_phase.triage`, `unknown_spans` | absent, 1 | present, 0 | #43 |
| echo-wiki-ci (E2) | `wall.total_ms` | 1409482 | ≈ 1363000 (s1 ended 17:15:14 inside verify; s2 resumed 17:16:00) | #40 |
| any card | `agent_time` | — | may rise where a session had back-to-back prompts | #43 |

Other cards may change only where one of these rules applies: a controlling session ended before
`ready` (#40) or a session had a prompt before any stop (#43). Explain each such change in the PR body
with its event times; a change no rule explains is a bug, so stop and investigate before opening the PR.

- [ ] **Step 2: Push and open the PR**

```bash
git push -u origin v0-hardening
gh pr create --base main --title "fix: v0 hardening from the first real tasks" --body-file <file>
```

The body lists each gap fixed (table above), the Deferred table, the re-score diff from Step 1, and the
rollout steps below. It ends with the attribution line.

- [ ] **Step 3: Rollout steps (in the PR body; run after merge)**

1. `cd ~/Desktop/src/echo-official/lean-harness && git switch main && git pull --ff-only`.
2. `harness install --user` — required: the bootstrap text changed, and `harness doctor` fails every
   task start until the installed copy matches.
3. `harness doctor` in mvp, echo-wiki and echo-theory-plugins.
4. `harness score` in echo-wiki and mvp (real state dir) once the diff above is accepted.
5. Projects keep working without edits (`merge` absent = `user`). Project-side follow-ups are in
   `~/Desktop/src/echo-official/harness-tasks/project-clashes.md`.

---

### Task 10: Spec deltas (this repo, same branch as this plan)

**Files:**
- Modify: `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md`

- [ ] **Step 1: Apply each delta exactly**

| § | Replace | With |
|---|---|---|
| Header | `Status: approved 2026-10-08 (Fable review: APPROVE) · owner: the user (sole developer).` | `Status: approved 2026-10-08 (Fable review: APPROVE); amended 2026-10-09 by the v0 hardening plan (H1–H10 in §2.2) · owner: the user (sole developer).` |
| 2.2 | (table end) | Add rows H1–H10, Type **A** or **O**, one per change below, Why = the gap number and the task that showed it |
| 4.6 | "`harness pr`'s push still triggers the project's pre-push hook (mvp runs `npm run preflight`), and that time is charged to the task because it is real;" | "`harness pr`'s first push triggers the project's pre-push hook (mvp runs `npm run preflight`), and that time is charged to the task because it is real; its follow-up push adds only harness bookkeeping in `.harness/` on the same code tree and skips the hook (H7); the agent writes the PR title in the project's commit style (`--title`, H6);" |
| 5.2 PR row | "Passing checks → an open PR and `ready`" / "`harness pr <task-id>`" / "`ready` emitted" | "Runnable checks pass → an open PR; every check passes, observational ones included → `ready`" / "`harness pr [<task-id>] [--title T]`" / "`ready` emitted (until then the PR body says it is not ready)" (H5) |
| 5.5 | Template `<date time> · …` and "one stamped line per entry" | Template `<date> · …`; "one dated line per entry; the event log holds exact times" (H8). `Check:` may list several ids (`Check: C6, C7`) (H1) |
| 5.7 | "A re-plan may change a check only with a Decision naming it (`Check: C3`, or `Check: goal`)." | "A re-plan may change a check only with a Decision naming it (`Check: C3`, `Check: C6, C7`, or `Check: goal`)." (H1) |
| 6.1 | `state.json` row: "`start --new`; `harness phase`" / "Start; every phase enter/exit" | "`start --new`" / "Start" (H2) |
| 6.2 | (table) | Add row: `merge` · `"user"` · "Who merges after `ready`: `user`, or `agent` (after `pr --refresh`, with `gh pr merge --match-head-commit`); printed by `harness pr`; never auto-merge" (H4) |
| 6.4 | "`task_id`, `branch`, `phase`, `phase_open` (bool), `controlling_session` (nullable), `created_at`." | "`task_id`, `branch`, `created_at`. The open phase and its controlling session come from the task's phase events; `harness start` prints them; nothing reads them from `state.json` (H2)." |
| 6.10 | After "…from a `--handoff` phase exit to the successor's `resume`." | Add: "The controlling session's end (the session of the latest phase enter) also pauses the clock, and the task's next `harness` command restarts it: no agent is working in between. A session that waits for your reply stays alive and stays charged (H3)." And in the agent-time sentence after "before the next prompt or session end": "(a prompt that arrives before any stop, such as a queued message delivered mid-turn, closes the open span at that prompt) (H9)" |
| 7 | `pr <task-id>` row | Command `pr [<task-id>] [--title T]`; Does: "Runnable checks must pass; commit `.harness/`, push (hooked), open or update the PR; if observational checks are unrecorded at this code tree: `pr`, PR body 'not ready', exit 0 without `ready`; else `ready` + `pr`, commit, push (no hook), print the merge rule" (H5–H7) |
| 7 | `pr --refresh` row | Add to Does: "observational checks owed at the rebased code: PR body 'not ready', `build exit --handoff`, exit 1" (H5) |
| 7 | `phase` row, Refuses when | Add: "`plan.md` without a goal or usable checks (every command but `triage enter`) (H10)" — and add H10 to §2.2 |

(H1 Decision lists · H2 phase from events · H3 controller-end pause · H4 merge rule · H5 observational
checks after the PR · H6 PR title · H7 one hooked push · H8 date-only notes · H9 mid-turn prompts ·
H10 plan validation.)

- [ ] **Step 2: Re-read the whole spec for sentences that now contradict a delta** (§5.2 "After
  `ready`" paragraph, §6.11, §9, §17 daily use) and fix each in the same commit.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md
git commit -m "docs(lean-harness): spec deltas H1–H10 from the v0 hardening plan"
```

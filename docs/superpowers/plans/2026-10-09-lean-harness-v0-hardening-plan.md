# Lean Harness v0 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every harness defect that real tasks proved would give a wrong record, block a task, or
clash with project rules, before the harness is used for production work and before Codex (Slice 2).

**Architecture:** Small, generic changes to the existing CLI and instruction files. The event log
becomes the only source of a task's phase; `harness pr` separates "PR open" from `ready`; timing gains
one pause rule, one span rule and a cutoff; instruction files gain a few lines. No new commands, no new
event kinds, no project-specific code.

**Tech Stack:** Python 3.12 standard library only; `unittest` (run with `python3 -m pytest -q`); git;
`gh`.

**Spec:** `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md` (this repo). Evidence:
`~/Desktop/src/echo-official/harness-tasks/testing-notes.md` (gap rows #1–#44) and
`~/Desktop/src/echo-official/harness-tasks/project-clashes.md` (G1–G5, P1–P10, W1–W3, E1–E2).

**Code:** `~/Desktop/src/echo-official/lean-harness` (GitHub `echotheorylabsai/lean-harness`), branch
`v0-hardening` from `main` (`235cf61`). File paths below are relative to that repo unless they start
with `docs/superpowers/` (this repo).

**Execution:** Native (one implementer in one session: the tasks share `pr.py`, `phase.py`, `gate.py`
and are small), then the user's review protocol on the PR: independent adversarial reviews by Fable
(`fable-reviewer`) and GPT Astra (`codex:codex-rescue`, `--model gpt-6-astra --effort xhigh --fresh`).

**Revision:** r4 (2026-10-09). Round 1: Fable and GPT Astra both REVISE. Round 2: Fable APPROVE, GPT
Astra REVISE. Round 3: Fable APPROVE, GPT Astra REVISE (one instruction line). The review log at the end lists every finding and how each revision handles it.

## Global Constraints

- Python 3.12 stdlib only; tests are `unittest` classes; the suite stays green after every task.
- No new `harness` commands and no new event kinds (spec §6.7 schema v1 unchanged).
- Nothing project-specific in code or instruction files (no `mvp`, `echo-wiki`, `npm`, `preflight`).
- Scoring stays idempotent over raw events (§6.12) and needs no forge API (§9.8): re-scoring old tasks
  may change their cards only where this plan changes a rule; Task 9 lists each expected change.
- Instruction files stay terse: one line per rule; `AGENTS.md` is read by every task session.
- Agent-agnostic: every rule reads only fields any adapter can emit (`session_end`, `prompt`, `stop`,
  CLI events). An adapter without a session-end event keeps today's timing (no pause), so Slice 2
  (Codex) stays additive.
- Default behavior of installed projects is unchanged unless a gap requires it (`project.json`
  without `merge` means `user`).

## What this plan fixes, and why each is in

| Gap | Evidence (testing-notes / clashes) | Fix | Task |
|---|---|---|---|
| #35 gate reads only the first id after `Check:` | prereqs-table card stays not-done after `close --done`; `planfile.DECISION_CHECK_RE` | Parse a comma list, each id bounded | 1 |
| #26 `state.json` trusted for the phase | M1 s2 hand-edited `phase` to `verify`; `phase.py`, `pr.py` read it | Phase comes from the event log; `state.json` keeps only `task_id`, `branch`, `created_at` | 2 |
| #28 plan rewritten without checks; #17 headings inside fences | M1 s2 dropped `## Acceptance checks`; a `## ` comment inside a check command splits the plan | Fence-aware parsing; every `phase` command (except `triage enter`) refuses an unusable `plan.md` | 3 |
| #41 observed check that needs the PR | E2 C8 ("CI passes on this PR") could not be recorded before `harness pr`; agent had to drop and restore it | Runnable checks gate opening the PR; observational checks gate `ready`; after a handoff, work starts with a phase enter; `ready` is revalidated under the spool lock; CLI events take their timestamp under that lock and the gate counts attempts before the last `ready` in log order | 4 |
| P2/W3, #6 PR titles | mvp `main`: `Fix ECH-200: … must emit the (#553)` breaks conventional commits | `harness pr --title`; default cut at a word | 5 |
| #37 `pr` needs the task id | E4 s2's first `harness pr --refresh` failed on usage | Task id optional, resolved like `phase`/`check` | 5 |
| Q1, #29/P1 merge rule | User wants agents able to merge when mandated (cloud); mvp's skill says `--auto` | `project.json` `merge: user\|agent`, printed by `harness pr` at `ready` | 5 |
| #2/P4 pre-push hook runs twice | M3 `ready` push took ~2 min more (preflight again) | The bookkeeping-only second push skips hooks | 5 |
| #40 clock runs with no harness-driven agent | M1 wall 2.26 h, about 17 min of it harness-driven work | The controlling session's end pauses the clock until the task's next `harness` command | 6 |
| #43 agent time drops a span | M3 lost 207 s and its whole triage: a queued message fired a second prompt with no stop | A prompt that arrives before a stop closes the open span at that prompt | 6 |
| #15 agent time not cut at the clock stop | `timing.agent_time` ignores `until_ms` | Clip spans at the cutoff | 6 |
| #27 agent works without the harness | M1 s2 carried on after `harness start` was denied | Bootstrap: stop if `harness start` fails in a harness project | 7 |
| #24 note times made up | 6 of 6 tasks wrote clock times that disagree with events | Notes carry the date only (deletion; no metric reads the time) | 7 |
| #32 checks pinned to a fixed SHA | prereqs-table C6/C7 broke after `harness pr` rebased | `triage.md`: diff against `git merge-base HEAD <remote>/<branch>` | 7 |
| #7/#31 S plans have no Decisions | E3 silently turned the requested observed check into a runnable one | S plans may add `## Decisions` | 7 |
| G1, P1, P7, #42 clashes | superpowers "must use skills" (potential); mvp `--auto`; M3 posted a PR comment | `AGENTS.md`: the harness alone plans, opens PRs, sets who merges, rebases; GitHub writes only through `harness pr`; never auto-merge | 7 |
| Clash record (generic half) | User asked that project rules complement the harness | `docs/project-setup.md` in the harness repo | 8 |

## Deferred (not in this plan), with the reason

| Gap | Why it waits |
|---|---|
| #4 rebase-merge with a commit after the last `ready` passes the gate | Detecting it needs the forge's merge commit, and §9.8 keeps scoring forge-free. Squash and merge commits are caught today. The boundary is stated in `docs/project-setup.md` and spec §14 (rebase merges unsupported by the gate) |
| #36 conflict/revision counts | Diagnostic only, with no consumer before Slice 3. Approximate inputs already exist (`ready` events, handoff exits after a `ready`); Slice 3 defines exact counts |
| #8 extra review sessions counted | Topology is observe-only (§5.4); count-or-exclude is a Slice 3 scoring decision, not a defect |
| #38 `harness check` runs any plan command | Inherent: the agent writes its checks and could run the same command through any allowed tool. Stated in `docs/project-setup.md` |
| #3 `/clear` identity, #20 Codex fixtures, #21 desktop hooks, cloud spool | Slice 2 / later, per the roadmap (§11) |
| #11/#25 triage depth and tier under-calls | Product decisions about the workflow, not defects |
| Merge queues with `merge: agent` | `gh pr merge` may enable auto-merge on merge-queue repositories; the agent rule excludes them (stated in the printed rule and spec §14) until a project needs it |
| #1, #5, #9, #10, #12–#14, #16, #18, #19, #22, #23, #30, #33, #34, #39, #44 | Low severity, by design, or covered by a fix above (#33 is the gate working; #34/#39 by the `AGENTS.md` lines) |

## Review Focus

1. **A task folder created before this change** (its `state.json` still has `phase`, `phase_open`,
   `controlling_session`): every command ignores those keys and uses the event log. Pinned by Task 2's
   hand-edited `state.json` test, which writes exactly those keys.
2. **Successive sessions that each continue an open phase and end without a handoff** (E2 s1 → s2
   pattern, twice): each end pauses the clock and each session's first `harness` command restarts it.
   Pinned by Task 6's two-endings test.
3. **New commits after a PR opened "not ready"**: an observation recorded on an older code tree is
   stale, so `harness pr` stays not ready. Pinned by Task 4's stale-observation assertions.
4. **An invalid `merge` value in `project.json`** fails loudly at load, not with a wrong printed rule.
   Pinned by Task 5's `load_project` test.
5. **`harness pr --refresh` by the user with observational checks**: hands control back (exit 1,
   `build exit --handoff`), prints a next step that keeps the record complete, and a later `check`
   without a phase enter is refused. Pinned by Task 4's refresh test.

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
- Produces: `planfile.decision_refs(text: str) -> set[str]` (same signature; reads lists).

- [ ] **Step 1: Write the failing tests**

Append to `PlanfileTest` in `tests/test_planfile.py`:

```python
    def test_decision_refs_read_every_id_in_a_list(self):  # gap #35
        extra = ("- 2026-10-09 · claude · build — Rebased C6/C7. Why: main moved. [Check: C6, C7]\n"
                 "- 2026-10-09 · claude · build — Allow versions. Why: #15 merged. Check: C5, goal\n")
        self.assertEqual(planfile.decision_refs(PLAN + extra), {"C3", "C5", "C6", "C7", "goal"})

    def test_decision_refs_need_whole_ids(self):  # gap #35: no partial matches
        typos = ("- 2026-10-09 · claude · build — Typo. Why: z. Check: goalpost\n"
                 "- 2026-10-09 · claude · build — Typo. Why: z. Check: C1suffix\n"
                 "- 2026-10-09 · claude · build — Half. Why: z. Check: C6, C7x\n")
        self.assertEqual(planfile.decision_refs(PLAN + typos), {"C3", "C6"})
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
Expected: the list test and the gate test fail (`C7` missing; C1 still listed). The whole-ids test may
already pass; it guards the new regex.

- [ ] **Step 3: Implement**

In `harness/planfile.py` replace line 9 with:

```python
_REF = r"(?:C\d+|goal)\b"
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
- Produces: `gate.open_phase(events: list[dict]) -> str | None`: the phase the task's last phase event
  left open, in log order; `None` when that event is an exit or there is none.
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

and change the file's import to `from harness import gate, gitio, spool, taskfiles`.

In `tests/test_start.py`, `StartNewTest.test_registers_the_task_and_starts_the_clock`, replace the
`state` assertion (lines 33–34) with:

```python
        self.assertEqual(state, {"task_id": task_id, "branch": "t-reg", "created_at": state["created_at"]})
```

Append to `BootstrapTest` in `tests/test_start.py`:

```python
    def test_bootstrap_prints_the_tasks_phase(self):  # gap #26
        wt, env, task_id = self.sb.begin_task("st-phase")
        self.assertIn("phase: none yet", self.sb.harness("start", cwd=wt, env=env).stdout)
        self.sb.harness("phase", "triage", "enter", cwd=wt, env=env)
        self.assertIn("phase: triage (open)", self.sb.harness("start", cwd=wt, env=env).stdout)
```

In `tests/test_pr.py` add `gate` to the `harness` import, add this helper to `PrTest`:

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
    sid = ctx.identity.session_id  # null for your own manual commands (§6.9)
    context.record(ctx, context.event(ctx, "phase", task_id, phase=name, action=action, handoff=handoff,
                                      controlling_session=sid))
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

In `harness/commands/start.py`, add `gate` to the `harness` import; in `new_task` write `state.json` as

```python
        taskfiles.write_json(folder / "state.json", {
            "task_id": task_id, "branch": ctx.git.branch, "created_at": events.now_ts()})
```

and in `bootstrap` replace the final `print` with:

```python
    print(f"task {task_id}\n{_where(context.task_events(ctx, task_id))}\n"
          f"harness checkout: {REPO}\nNow read {REPO / 'AGENTS.md'}.")
```

adding this helper below `bootstrap`:

```python
def _where(evs: list[dict]) -> str:
    """Where a later session picks up: the open phase, the last one, or none (gap #26)."""
    if gate.needs_build_enter(evs):
        return "phase: after ready; any further change starts with `harness phase build enter`"
    current = gate.open_phase(evs)
    if current:
        return f"phase: {current} (open)"
    phases = [e for e in evs if e.get("kind") == "phase"]
    return f"phase: {phases[-1]['phase']} (exited)" if phases else "phase: none yet"
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

### Task 3: Fence-aware plan parsing; phase commands refuse an unusable plan (#17, #28)

**Files:**
- Modify: `harness/planfile.py` (`_split`, add `_fenced_spans`, add `problems`),
  `harness/commands/phase.py` (`enter`, `exit_phase`, add `_require_usable_plan`)
- Test: `tests/test_planfile.py`, `tests/test_phase.py`

**Interfaces:**
- Produces: `planfile.problems(text: str, tier: str | None = None) -> list[str]` (empty when usable).
- `planfile.sections` and `planfile.checks` ignore heading-shaped lines inside triple-backtick fences.

- [ ] **Step 1: Write the failing tests**

Append to `PlanfileTest` in `tests/test_planfile.py`:

```python
    def test_headings_inside_a_fence_are_command_text(self):  # gap #17
        plan = PLAN.replace("grep -q hi greeting.txt\n", "## look for hi\ngrep -q hi greeting.txt\n")
        self.assertEqual(planfile.checks(plan)["C1"].command, "## look for hi\ngrep -q hi greeting.txt\n")
        self.assertEqual(list(planfile.checks(plan)), ["C1", "C2"])
        self.assertEqual(planfile.problems(plan, "M"), [])

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
Expected: the fence test fails (C1's command is cut at the `## ` line), `problems` is missing, and
`build enter` succeeds (exit 0).

- [ ] **Step 3: Implement**

In `harness/planfile.py` add above `_split`:

```python
FENCE_LINE_RE = re.compile(r"^```", re.M)


def _fenced_spans(text: str) -> list[tuple[int, int]]:
    """Character spans of triple-backtick fenced blocks; an unclosed fence runs to the end (gap #17)."""
    spans, opened = [], None
    for m in FENCE_LINE_RE.finditer(text):
        if opened is None:
            opened = m.start()
        else:
            spans.append((opened, m.end()))
            opened = None
    if opened is not None:
        spans.append((opened, len(text)))
    return spans
```

and replace `_split` with:

```python
def _split(text: str, pattern: re.Pattern) -> list[tuple[re.Match, str]]:
    fenced = _fenced_spans(text)
    matches = [m for m in pattern.finditer(text) if not any(a <= m.start() < b for a, b in fenced)]
    return [(m, text[m.start(): matches[i + 1].start() if i + 1 < len(matches) else len(text)])
            for i, m in enumerate(matches)]
```

Add after `checks`:

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

Call it before any write. In `enter`: delete the two lines
`if snapshot and not (folder / "plan.md").exists(): raise …` and, right after computing `current`, add
`if name != "triage": _require_usable_plan(folder)`. In `exit_phase`: right after the
`current != name` refusal, add `_require_usable_plan(folder)`.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass. If an existing test enters a later phase without a usable plan, it relied on the
gap; give it a plan with `write_plan` rather than weakening the check.

- [ ] **Step 5: Commit**

```bash
git add harness tests
git commit -m "fix(plan): fence-aware parsing; phase commands refuse an unusable plan.md (#17, #28)"
```

---

### Task 4: Runnable checks gate the PR; observational checks gate `ready` (#41)

**Files:**
- Modify: `harness/gate.py` (`unmet_checks`, `failing_checks`, `needs_phase_enter`, `evaluate`),
  `harness/spool.py` (`append`), `harness/context.py` (`record`), `harness/commands/check.py:25-26`,
  `harness/commands/phase.py` (`exit_phase`, `_write`), `harness/commands/start.py` (`_where`),
  `harness/commands/pr.py` (`pr_body`, `publish`, `refresh`, `run`)
- Test: `tests/test_pr.py`, `tests/test_gate.py`, `tests/test_spool.py`

**Interfaces:**
- Produces: `gate.unmet_checks(plan_text, events, code_tree) -> dict[str, str]` (check id → reason);
  `gate.failing_checks(plan_text, events, code_tree) -> list[str]` (the `before_ts` parameter is
  removed: `evaluate` passes only the events before the last `ready`, in log order).
- Produces: `gate.needs_phase_enter(events) -> str | None`: why the next `check` or `pr` must wait for
  a phase enter (after `ready`: `build enter`, R-5; after a handoff exit: the next phase's enter), else
  None.
- `spool.append(state_dir, event, task_events=None, *, held=False, stamp=False)`: with `stamp`, the
  event's `ts` is set under the lock; `context.record` always stamps, so CLI events' log order is their
  time order.
- `phase.exit_phase(ctx, task_id, name, handoff=False, held=False)`: `held` records under a lock the
  caller already holds.
- `pr.publish(ctx, project, task_id) -> tuple[str, ...]`: the observational check ids still owed;
  `()` means `ready` was emitted.
- `pr.pr_body(task_id, plan, scope, pending=()) -> str`.

- [ ] **Step 1: Write the failing tests**

Append to `GateTest` in `tests/test_gate.py`:

```python
    def test_needs_phase_enter_after_ready_or_a_handoff_exit(self):  # R-5, gap #41
        self.assertIsNone(gate.needs_phase_enter([]))
        self.assertIn("build enter", gate.needs_phase_enter([ev("ready", 1)]))
        handoff = ev("phase", 2, phase="research", action="exit", handoff=True)
        self.assertIn("a handoff closed research", gate.needs_phase_enter([handoff]))
        self.assertIsNone(gate.needs_phase_enter([handoff, ev("phase", 3, phase="plan", action="enter")]))

    def test_attempts_count_before_the_last_ready_in_log_order(self):  # same-millisecond ties
        tie = [check(1, "C1", "fail"), check(2, "C2"), check(3, "C1"), ev("ready", 3, code_tree="T1")]
        self.assertTrue(gate.evaluate(PLAN, PLAN, tie, "T1").passed)
        logged_after = PASSING + [check(3, "C1", "fail")]
        self.assertTrue(gate.evaluate(PLAN, PLAN, logged_after, "T1").passed)
```

In `GateTest.test_failing_checks` replace the `before_ts=` assertion (line 35) with
`self.assertEqual(gate.failing_checks(PLAN, later_fail[:2], "T1"), [])`.

Append to `SpoolTest` in `tests/test_spool.py`:

```python
    def test_stamped_appends_take_their_time_under_the_lock(self):  # CLI log order = time order
        spool.append(self.tmp, events.make("check", "cli", "2000-01-01T00:00:00.000Z"), stamp=True)
        spool.append(self.tmp, events.make("check", "cli", "2000-01-01T00:00:00.000Z"))
        stamped, kept = spool.read(self.tmp)
        self.assertGreater(stamped["ts"], "2026-01-01")
        self.assertEqual(kept["ts"], "2000-01-01T00:00:00.000Z")
```

Add `import sys` and `from pathlib import Path` to the imports of `tests/test_pr.py`, add `REPO` and
`spool` to the `harness` import, and add to `PrTest`:

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

    def test_observational_checks_wait_for_the_open_pr(self):  # gap #41, Review Focus 3
        wt, env, task_id = self.observed_task("pr-observe")
        creates = self.gh_log().count("pr create")
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("not ready", r.stdout)
        self.assertIn("run `harness pr` again", r.stdout)
        self.assertEqual(self.gh_log().count("pr create"), creates + 1)
        self.assertIn("Waiting for observation: C2", self.gh_log())
        kinds = [k for k, _, _ in self.kinds(wt, task_id)]
        self.assertIn("pr", kinds)
        self.assertNotIn("ready", kinds)
        self.assertEqual(gate.open_phase(self.task_events(wt, task_id)), "verify")
        (wt / "late.txt").write_text("late\n")          # an observation on an older tree goes stale
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
        self.assertIn("harness phase build enter", r.stdout)
        evs = self.sb.task_file_events(wt, task_id)
        last = [e for e in evs if e["kind"] == "phase"][-1]
        self.assertEqual((last["phase"], last["action"], last["handoff"]), ("build", "exit", True))
        self.assertEqual(sum(e["kind"] == "ready" for e in evs), 1)
        self.assertIn("handoff", self.h(wt, env, "check", "C2", "--observed", "pass").stderr)
        self.h(wt, env, "phase", "build", "enter")
        self.assertEqual(self.h(wt, env, "check", "C2", "--observed", "pass").returncode, 0)
        self.assertIn("ready:", self.h(wt, env, "pr", task_id).stdout)

    def late_fail_hook(self, wt, task_id):
        """A pre-push hook that logs a failing C1 attempt, as a delegate could while `harness pr` pushes."""
        spool_file = spool.project_dir(self.sb.env, gitio.info(wt).common_dir) / "spool.jsonl"
        script = self.sb.tmp / f"late_fail_{task_id}.py"
        script.write_text(
            "import sys\n"
            f"sys.path.insert(0, {str(REPO)!r})\n"
            "from harness import events\n"
            f"with open({str(spool_file)!r}, 'a') as f:\n"
            f"    f.write(events.dumps(events.make('check', 'cli', events.now_ts(), task_id={task_id!r}, "
            "check_id='C1', result='fail')))\n")
        hook = Path(gitio.info(wt).common_dir) / "hooks" / "pre-push"
        hook.write_text(f"#!/bin/sh\n{sys.executable} {script}\n")
        hook.chmod(0o755)
        self.addCleanup(hook.unlink)

    def test_a_check_that_fails_while_the_pr_opens_blocks_ready(self):  # ready revalidated under the lock
        wt, env, task_id = self.built("pr-race")
        self.late_fail_hook(wt, task_id)
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("changed while the PR was opening", r.stderr)
        self.assertNotIn("ready", [k for k, _, _ in self.kinds(wt, task_id)])
        self.assertEqual(gate.open_phase(self.task_events(wt, task_id)), "verify")  # still open: retry works

    def test_a_late_failure_during_refresh_still_hands_back(self):  # the phase closes only with `ready`
        wt, env, task_id = self.built("pr-race-refresh")
        self.assertEqual(self.h(wt, env, "pr", task_id).returncode, 0)
        self.late_fail_hook(wt, task_id)
        r = self.h(wt, {}, "pr", "--refresh", task_id)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        last = [e for e in self.sb.task_file_events(wt, task_id) if e["kind"] == "phase"][-1]
        self.assertEqual((last["phase"], last["action"], last["handoff"]), ("build", "exit", True))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_gate.py tests/test_pr.py`
Expected: the new tests fail (`needs_phase_enter` and `stamp` missing; the same-millisecond tie fails
the gate; `pr` refuses with "C2: no recorded attempt"; `ready` is emitted despite the late failure).

- [ ] **Step 3: Implement in `harness/gate.py`**

Add after `needs_build_enter`:

```python
def needs_phase_enter(events: list[dict]) -> str | None:
    """Why the next check or PR must wait for a phase enter, or None. After `ready`, any further change
    starts with `build enter` (R-5); after a handoff exit, the successor first enters a phase, so its
    time is charged (gap #41)."""
    if needs_build_enter(events):
        return "after `ready`, run `harness phase build enter` first"
    phases = _of(events, "phase")
    if phases and phases[-1].get("action") == "exit" and phases[-1].get("handoff"):
        return (f"a handoff closed {phases[-1].get('phase')}: enter the phase you continue in "
                "(`harness phase <name> enter`) first")
    return None
```

Replace `failing_checks` with:

```python
def unmet_checks(plan_text: str, events: list[dict], code_tree: str | None) -> dict[str, str]:
    """Final checks whose latest attempt in events did not pass at code_tree with the check text in
    plan_text, each with its reason. A check with no attempt is unmet (§6.11)."""
    attempts = _of(events, "check")
    out = {}
    for cid, check in planfile.checks(plan_text).items():
        mine = [e for e in attempts if e.get("check_id") == cid]
        if not mine:
            out[cid] = "no recorded attempt"
            continue
        last = mine[-1]  # log order (CLI events are stamped under the spool lock)
        if last.get("result") != "pass":
            out[cid] = f"latest attempt {last.get('result')}"
        elif last.get("code_tree") != code_tree:
            out[cid] = "latest pass ran on another code tree"
        elif last.get("check_text_hash") != planfile.check_hash(check):
            out[cid] = "check text changed since its latest pass"
    return out


def failing_checks(plan_text: str, events: list[dict], code_tree: str | None) -> list[str]:
    """unmet_checks as `C<n>: <reason>` lines; a plan with no checks fails (§6.11)."""
    if not planfile.checks(plan_text):
        return ["plan.md has no acceptance checks"]
    return [f"{cid}: {why}" for cid, why in unmet_checks(plan_text, events, code_tree).items()]
```

In `evaluate`, replace the `else:` branch under `if not readies:` with:

```python
    else:
        i = max(n for n, e in enumerate(events) if e.get("kind") == "ready")  # events are time-ordered
        last = events[i]
        if merge_code_tree is not None and last.get("code_tree") != merge_code_tree:
            reasons.append("merged code differs from the last ready tip (run `harness pr --refresh` before merging)")
        reasons += failing_checks(final_plan, events[:i], last.get("code_tree"))  # attempts logged before it
```

In `harness/spool.py`, replace `append` with:

```python
def append(state_dir: Path, event: dict, task_events: Path | None = None, *, held: bool = False,
           stamp: bool = False) -> None:
    """Append one complete line to the spool, and to the task's events.jsonl when given. With stamp,
    the event takes its timestamp under the lock, so stamped events' log order is their time order."""
    with nullcontext() if held else locked(state_dir):
        line = events.dumps({**event, "ts": events.now_ts()} if stamp else event).encode()
        for path in [state_dir / "spool.jsonl", *([task_events] if task_events else [])]:
            try:
                fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
                try:
                    os.write(fd, line)
                finally:
                    os.close(fd)
            except OSError as e:
                raise HarnessError(f"cannot append to {path}: {e}. {FIX}") from e
```

and in `harness/context.py`, `record`, change the last line to
`spool.append(ctx.state_dir, ev, task_file, held=held, stamp=True)`.

In `harness/commands/phase.py`, give `exit_phase` and `_write` a `held: bool = False` parameter and pass
it through to `context.record(..., held=held)`, so `publish` can close the phase under its lock.

- [ ] **Step 4: Use it in `harness/commands/check.py`**

Replace lines 25–26 with:

```python
    blocked = gate.needs_phase_enter(context.task_events(ctx, task_id))
    if blocked:
        raise HarnessError(blocked)
```

In `harness/commands/start.py`, `_where`, replace its first two lines (the `needs_build_enter` test)
with:

```python
    blocked = gate.needs_phase_enter(evs)
    if blocked:
        return f"phase: none open; {blocked}"
```

and in `BootstrapTest.test_bootstrap_prints_the_tasks_phase` nothing changes (it never reaches `ready`).

- [ ] **Step 5: Implement the pending path in `harness/commands/pr.py`**

Add `spool` to the `harness` import. Replace `pr_body`, `publish`, `refresh` and the end of `run`:

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


def publish(ctx, project: dict, task_id: str) -> tuple[str, ...]:
    """Open or update the PR. Runnable checks must pass first; observational checks not yet passed at
    this code tree leave it open without `ready` (gap #41). Returns those check ids; () = ready."""
    folder = taskfiles.task_dir(ctx.root, task_id)
    evs = context.task_events(ctx, task_id)
    if not any(e.get("kind") == "phase" and e.get("phase") == "triage" and e.get("action") == "enter" for e in evs):
        raise HarnessError("no `harness phase triage enter` recorded for this task")
    blocked = gate.needs_phase_enter(evs)
    if blocked:
        raise HarnessError(blocked)
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
        print(f"pr open: {url}\nnot ready: waiting for observation of {', '.join(pending)}.")
        return pending
    tip = gitio.out(["rev-parse", "HEAD"], ctx.root)
    with spool.locked(ctx.state_dir):  # no check lands between this read and `ready`; not reentrant: pass held=True inside
        now = context.task_events(ctx, task_id)
        late = gate.failing_checks(plan, now, tree)
        if late:  # the phase stays open, so a retry or refresh's hand-back still works
            raise HarnessError("a check changed while the PR was opening; run `harness pr` again:\n"
                               + "\n".join(late))
        current = gate.open_phase(now)
        if current:
            phase.exit_phase(ctx, task_id, current, held=True)  # a ready writes the missing exit first
        context.record(ctx, context.event(ctx, "ready", task_id, tip_commit=tip, code_tree=tree), held=True)
    gitio.commit_paths(ctx.root, ".harness", f"harness: ready {task_id}")
    try:
        gitio.push(ctx.root, remote, branch)
    except HarnessError as e:
        raise HarnessError(f"{e}\n`ready` is recorded; finish with `git push {remote} HEAD`") from e
    print(f"ready: {url}")
    return ()


HAND_BACK = "Next, a session in this worktree runs `harness phase build enter`, {fix}, then `harness pr`."


def refresh(ctx, project: dict, task_id: str) -> int:
    phase.enter(ctx, task_id, "build")
    try:
        if rebase.rebase(ctx, project) == "conflict":
            rebase.abort(ctx)
            phase.exit_phase(ctx, task_id, "build", handoff=True)  # control returns to you (R-1)
            print("rebase conflict: aborted. " + HAND_BACK.format(
                fix="resolves it with `harness rebase`, runs `harness check --all`"))
            return 1
        plan = (taskfiles.task_dir(ctx.root, task_id) / "plan.md").read_text()
        results = [check.run_one(ctx, task_id, c) for c in planfile.checks(plan).values() if c.command]
        if "fail" in results:
            phase.exit_phase(ctx, task_id, "build", handoff=True)
            print("checks fail at the rebased code. " + HAND_BACK.format(fix="fixes and rechecks them"))
            return 1
        pending = publish(ctx, project, task_id)
        if pending:
            phase.exit_phase(ctx, task_id, "build", handoff=True)  # observations are owed at the new code
            print(HAND_BACK.format(fix="records each with `harness check <C-id> --observed pass|fail`"))
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
    if publish(ctx, project, args.task_id):
        print("Next: observe them on the open PR, record each with "
              "`harness check <C-id> --observed pass|fail`, then run `harness pr` again.")
    return 0
```

The `pr` event is now recorded right after `pr_create`, and the phase exit right before `ready`; update
`test_publish_pushes_opens_one_pr_and_records_ready` to expect the last three kinds as
`[("pr", None, None), ("phase", "verify", "exit"), ("ready", None, None)]`. `test_check.py`'s
`test_after_ready_checks_need_a_build_enter` keeps passing ("build enter" is in the new message).

- [ ] **Step 6: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add harness tests
git commit -m "feat(pr): open the PR before observational checks; ready waits for them (#41)"
```

---

### Task 5: PR title, optional task id, merge rule, one hooked push (P2, #37, Q1, #2)

**Files:**
- Modify: `harness/commands/pr.py` (`add_args`, `run`, `title`, `publish`, add `merge_rule`),
  `harness/ghio.py` (`pr_edit_body` → `pr_edit`), `harness/gitio.py` (`push`), `harness/taskfiles.py`
  (`load_project`), `harness/commands/install.py` (`PROJECT_DEFAULTS`)
- Test: `tests/test_pr.py`, `tests/test_taskfiles.py`

**Interfaces:**
- CLI: `harness pr [<task-id>] [--title TITLE] [--refresh]`.
- `pr.title(plan: str, task_id: str, given: str | None = None) -> str`.
- `pr.merge_rule(project: dict, task_id: str, number: int) -> str`.
- `ghio.pr_edit(cwd, number: int, body: str, title: str | None = None) -> None`.
- `gitio.push(cwd, remote: str, branch: str, verify: bool = True) -> None`.
- `project.json` key `merge`: `"user"` (default when absent) or `"agent"`.

- [ ] **Step 1: Write the failing tests**

Add `from harness.commands import pr` to the imports of `tests/test_pr.py` and append:

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
        self.assertIn("merge queue", rule)
        self.assertIn("Never enable auto-merge", rule)
```

Add to `PrTest`:

```python
    def test_title_flag_task_id_from_the_branch_and_one_hooked_push(self):  # P2, #37, #2
        wt, env, task_id = self.built("pr-title")
        hook = Path(gitio.info(wt).common_dir) / "hooks" / "pre-push"
        log = self.sb.tmp / "pre-push.log"
        hook.write_text(f"#!/bin/sh\necho push >> {log}\n")
        hook.chmod(0o755)
        self.addCleanup(hook.unlink)
        no_task_var = {k: v for k, v in env.items() if k != "HARNESS_TASK_ID"}
        r = self.h(wt, no_task_var, "pr", "--title", "feat: add a greeting")
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

`harness/commands/pr.py` — add `import textwrap` at the top, and:

```python
MERGE_RULES = {
    "user": "Merge: the user merges this PR after `harness pr --refresh {task_id}`; do not merge it "
            "or enable auto-merge.",
    "agent": "Merge: run `harness pr --refresh {task_id}`; when it prints ready, merge with "
             "`gh pr merge {number} --match-head-commit <the head it prints>` and the project's merge "
             "method (not in a repository that uses a merge queue). Never enable auto-merge.",
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
    if publish(ctx, project, task_id, args.title):
        print("Next: observe them on the open PR, record each with "
              "`harness check <C-id> --observed pass|fail`, then run `harness pr` again.")
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

`refresh` keeps calling `publish(ctx, project, task_id)` (no title: a refresh keeps the existing one).

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass (the stub `gh` accepts `pr edit … --title`).

- [ ] **Step 5: Commit**

```bash
git add harness tests
git commit -m "feat(pr): --title, task id from the branch, printed merge rule, one hooked push"
```

---

### Task 6: Wall time pauses when the controller ends; agent time keeps mid-turn prompts and stops at the cutoff (#40, #43, #15)

**Files:**
- Modify: `harness/timing.py` (`charged_intervals`, `agent_time`)
- Test: `tests/test_timing.py`

**Interfaces:** unchanged signatures (`timing.wall`, `timing.agent_time`). For timing, the controlling
session is the session of the latest phase enter (none for your manual commands) or `resume` (a
`harness start`).

- [ ] **Step 1: Write the failing tests**

Append to `WallTest` in `tests/test_timing.py`:

```python
    def test_controller_session_end_pauses_until_the_next_harness_command(self):  # gap #40
        w = self.wall([ev("start", 0), ph(1, "verify", "enter"),
                       hook("session_end", 10),                       # S1 ends inside verify, no handoff
                       hook("session_start", 50, session="S2"),       # hooks alone do not restart it
                       ev("resume", 52, session_id="S2"),             # S2's `harness start`
                       ph(59, "verify", "exit", session="S2"), ev("ready", 60)])
        self.assertEqual(w.total_ms, (10 + 8) * MIN)
        self.assertEqual(w.by_phase, {"between_phases": 2 * MIN, "verify": 16 * MIN})
        self.assertTrue(w.complete)

    def test_each_successor_that_ends_without_handoff_pauses_too(self):  # gap #40, Review Focus 2
        w = self.wall([ev("start", 0), ph(1, "verify", "enter"), hook("session_end", 10),
                       ev("resume", 50, session_id="S2"), hook("session_end", 60, session="S2"),
                       ev("resume", 200, session_id="S3"), ph(209, "verify", "exit", session="S3"),
                       ev("ready", 210)])
        self.assertEqual(w.total_ms, (10 + 10 + 10) * MIN)

    def test_another_sessions_end_does_not_pause(self):  # gap #40 (review sessions, delegates)
        w = self.wall([ev("start", 0), ph(1, "build", "enter"), hook("session_end", 5, session="REVIEW"),
                       ph(29, "build", "exit"), ev("ready", 30)])
        self.assertEqual(w.total_ms, 30 * MIN)

    def test_your_manual_refresh_is_not_paused_by_the_old_agent(self):  # gap #40
        first = [ev("start", 0), ph(1, "build", "enter"), ph(29, "build", "exit"), ev("ready", 30)]
        w = self.wall(first + [ph(100, "build", "enter", session=None), hook("session_end", 105),
                               ph(109, "build", "exit", session=None), ev("ready", 110)])
        self.assertEqual(w.total_ms, 40 * MIN)
```

In `AgentTimeTest.test_prompt_to_last_stop_per_session_plus_helpers` change the comment on S2's line to
`# first span: closed by the second prompt` and the assertions to:

```python
        self.assertEqual(a.total_ms, (8 + 2 + 4 + 2) * MIN)  # S2's first turn ran until its second prompt
        self.assertEqual(a.unknown_spans, 2)  # S2's second prompt without a stop, helper a2
        self.assertEqual(a.by_phase, {"build": 16 * MIN})
```

and append to `AgentTimeTest`:

```python
    def test_spans_stop_at_the_cutoff(self):  # gap #15
        evs = [hook("prompt", 0), hook("stop", 10), hook("prompt", 20), hook("stop", 30), hook("prompt", 40),
               hook("stop", 50)]
        self.assertEqual(timing.agent_time(evs, BASE + 25 * MIN).total_ms, (10 + 5) * MIN)
        late = timing.agent_time(evs + [hook("prompt", 60), hook("subagent_start", 61, agent_id="a9")], BASE + 25 * MIN)
        self.assertEqual(late.unknown_spans, 0)  # nothing that starts after the cutoff counts
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 -m pytest -q tests/test_timing.py`
Expected: failures in the two pause tests (idle time charged) and the agent-time tests (14 and 30
minutes); the other-session and manual-refresh tests may already pass and guard the rule's scope.

- [ ] **Step 3: Implement**

Replace `charged_intervals` in `harness/timing.py`:

```python
def charged_intervals(events: list[dict], until_ms: int) -> tuple[list[tuple[int, int]], list[str]]:
    """Spans the wall clock runs. `ready`, a handoff exit and an abandon pause it; a later revision
    restarts at its resume or build enter (R-2). The controlling session's end also pauses it, and the
    task's next `harness` command restarts it (gap #40). The controlling session is the one of the
    latest phase enter (none for your manual commands) or `resume`."""
    intervals, missing = [], []
    started, running, since, resumes = False, False, 0, {}
    controller, ended = None, False
    for e in events:
        kind, t = e.get("kind"), ts_ms(e["ts"])
        enter = kind == "phase" and e.get("action") == "enter"
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
        elif enter and not running:
            sid = e.get("controlling_session")
            since = resumes.get(sid, t) if sid else t  # R-2
            running = True
        if enter:
            controller = e.get("controlling_session")  # your manual enters clear it
        elif kind == "resume":
            controller = e.get("session_id")
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

cut everything at the cutoff (gap #15): in `close`, change the first test to
`if prompt_t is None or prompt_t >= until_ms: return`; for a `subagent_stop` without a start, count it
unknown only when its own time is before `until_ms`; replace `unknown += len(helpers)` with
`unknown += sum(1 for started in helpers.values() if started < until_ms)`; and just before
`by_phase = split_by_phase(...)` add:

```python
    spans = [(a, min(b, until_ms)) for a, b in spans if a < until_ms]  # nothing after the clock stops (gap #15)
```

and update its docstring to: `"""Per session: prompt → last stop before the next prompt or session end
(a prompt that arrives before any stop closes the open span at that prompt); plus helper start → stop;
all cut at until_ms."""`

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass. (`test_e2e`/`test_score`/`test_scorecard` end their sessions after `ready`; if a
card changes, confirm its controller ended before `ready` and update the expectation with a comment
naming gap #40.)

- [ ] **Step 5: Commit**

```bash
git add harness/timing.py tests/test_timing.py
git commit -m "fix(timing): pause on the controller's end; keep mid-turn prompts; cut at the stop (#40, #43, #15)"
```

---

### Task 7: Instruction files (#27, #24, #32, #7/#31, G1, P1, P7, #42, #26, #41, P2)

**Files:**
- Modify: `hooks/bootstrap.md`, `AGENTS.md`, `skills/phases/triage.md`, `skills/phases/build.md`,
  `skills/phases/verify.md`

No new test: `tests/test_instructions.py` already checks every named command exists; Task 5 tests the
title behavior.

- [ ] **Step 1: Rewrite `hooks/bootstrap.md`** (one paragraph):

```
If another agent launched you, ignore this file and follow your prompt. Otherwise run `harness start`, then read `AGENTS.md` from the checkout it prints. If `harness start` fails or is refused in a repository that has `.harness/project.json`, stop and tell the user: never work on a harness task without it.
```

- [ ] **Step 2: Edit `AGENTS.md`**

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

- [ ] **Step 3: Edit the phase files**

`skills/phases/triage.md`:
- Step 2, after the sentence listing the M/L sections, add: "S plans add `## Decisions` when there is
  one to log, for example a check that departs from the request's wording."
- Step 3, after the observational paragraph, add: "A check that compares with the integration branch
  diffs against `$(git merge-base HEAD <remote>/<branch>)`: the branch moves while the task runs, so
  never use a fixed commit or the branch tip."

`skills/phases/build.md`:
- **Commands** line and step 7: write `harness pr <task-id> --title "<title>"`.
- Step 4, first clause: "When a milestone's checks pass (all but any that need the open PR), add one
  implementation-note line…" (rest unchanged).
- Step 6, first sentence: "When every milestone's checks that can pass before the PR have passed, run
  `harness rebase`." (rest unchanged).
- Step 7, first line: "7. Build ends when every check passes after the rebase, except checks that need
  the open PR (verify records those after `harness pr` opens it)." 
- Last paragraph: "After `ready`, any edit, rebase or check starts with `harness phase build enter`;
  after a handoff, with the enter of the phase you continue in. Running `harness pr` again re-emits
  `ready` without opening a second PR."

`skills/phases/verify.md`:
- **Commands** line: replace `harness phase verify exit`, `harness pr <task-id>` with
  `harness pr <task-id> --title "<title>"` (it exits verify when it emits `ready`).
- Append to step 3: "One that needs the open PR (for example its CI) is recorded after `harness pr`
  opens it."
- Replace step 5 with: "5. Verify ends when every check that can pass before the PR has passed. Run
  `harness pr <task-id> --title "<title>"`; it closes verify when it prints `ready`. If it prints
  `not ready`, follow `AGENTS.md` item 3."

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md hooks/bootstrap.md skills
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
  `gh pr merge --match-head-commit`, never auto-merge; not for repositories with a merge queue.
- **Merge method:** squash or merge commits. The done gate cannot see a commit added to a rebase merge
  after the last `ready`.
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

Run with the `v0-hardening` code (adjust the `cli.py` path if implementing in a worktree). Compare each
new card with its copy under `~/.local/state/harness/<hash>/scorecards/`. Expected changes (wall values
from round-1 review runs of this plan's timing code over both spools):

| Task | Field | Before | Expected after | Rule |
|---|---|---|---|---|
| prereqs-table | `done`, gate reasons | false, "C7 changed … without a Decision" | true, none | #35 |
| journey-fixture-prettier (M1) | `wall.total_ms` | 8125823 | 998167 | #40 |
| echo-wiki-ci (E2) | `wall.total_ms` | 1409482 | 1363985 | #40 |
| validate-json (E1) | `wall.total_ms` | 2097662 | 2076214 | #40 |
| ech-171-parity (M3) | `agent_time.by_phase.triage`, `unknown_spans` | absent, 1 | present, 0 (total +207 s) | #43 |
| any card | `agent_time` | — | may change where a session had a prompt before any stop (#43) or activity after the cutoff (#15) | #43, #15 |

Any other change must be explained by one of these rules, with event times, in the PR body; a change
no rule explains is a bug, so stop and investigate before opening the PR.

- [ ] **Step 2: Push and open the PR**

```bash
git push -u origin v0-hardening
gh pr create --base main --title "fix: v0 hardening from the first real tasks" --body-file <file>
```

The body lists each gap fixed (table above), the Deferred table, the re-score diff from Step 1, and the
rollout steps below. It ends with the attribution line.

- [ ] **Step 3: Rollout steps (in the PR body; run after merge)**

1. `cd ~/Desktop/src/echo-official/lean-harness && git switch main && git pull --ff-only`.
2. `harness install --user` — required: the bootstrap text changed, and every `harness start` fails
   its install probe until the installed copy matches.
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
| Header | `Status: approved 2026-10-08 (Fable review: APPROVE) · owner: the user (sole developer).` | `Status: approved 2026-10-08 (Fable review: APPROVE); amended 2026-10-09 by the v0 hardening plan (H1–H12 in §2.2) · owner: the user (sole developer).` |
| 2.2 | (table end) | Add rows H1–H12 (list below), Type **A** (added) or **O** (override), Why = the gap number and the task that showed it |
| 3 | Controlling session: "…for the task (recorded in `state.json`)" | "…for the task (the session of the latest phase enter, or of the latest `harness start` in the task, from the event log)" (H2) |
| 4.6 | "`harness pr`'s push still triggers the project's pre-push hook (mvp runs `npm run preflight`), and that time is charged to the task because it is real;" | "`harness pr`'s first push triggers the project's pre-push hook (mvp runs `npm run preflight`), and that time is charged to the task because it is real; its follow-up push adds only harness bookkeeping in `.harness/` on the same code tree and skips the hook (H7); the agent writes the PR title in the project's commit style (`--title`, H6);" |
| 5.2 Build row | Ends when: "All milestones' checks pass after the rebase" | "All milestones' checks pass after the rebase, except checks that need the open PR (H5)" |
| 5.2 Verify row | Ends when: "Every final check passes; a failure returns to build" | "Every check that can pass before the PR passes; a failure returns to build; checks that need the open PR are recorded after `harness pr` opens it (H5)" |
| 5.2 PR row | "Passing checks → an open PR and `ready`" / "`harness pr <task-id>`" / "`ready` emitted" | "Runnable checks pass → an open PR; every check passes, observational ones included → `ready`" / "`harness pr [<task-id>] [--title T]`" / "`ready` emitted (until then the PR body says it is not ready)" (H5) |
| 5.2 after the table | "After `ready`: any edit, rebase or check starts with `harness phase build enter`;" | "After `ready`: any edit, rebase or check starts with `harness phase build enter`; after a handoff exit, with the enter of the phase the successor continues in (`check` and `pr` refuse until then, H5);" |
| 5.5 | Template `<date time> · …`; "one stamped line per entry" | Template `<date> · …`; "one dated line per entry; the event log holds exact times" (H8); `Check:` may list ids (`Check: C6, C7`) (H1) |
| 5.7 | "A re-plan may change a check only with a Decision naming it (`Check: C3`, or `Check: goal`)." | "A re-plan may change a check only with a Decision naming it (`Check: C3`, `Check: C6, C7`, or `Check: goal`)." (H1) |
| 6.1 | `state.json` row: "`start --new`; `harness phase`" / "Start; every phase enter/exit" | "`start --new`" / "Start" (H2) |
| 6.2 | (table) | Add row: `merge` · `"user"` · "Who merges after `ready`: `user`, or `agent` (after `pr --refresh`, with `gh pr merge --match-head-commit`; not with a merge queue); printed by `harness pr`; never auto-merge" (H4) |
| 6.4 | "`task_id`, `branch`, `phase`, `phase_open` (bool), `controlling_session` (nullable), `created_at`." | "`task_id`, `branch`, `created_at`. The open phase comes from the task's phase events, and `harness start` prints it; nothing reads a phase from `state.json` (H2)." |
| 6.5 | "S plans hold only the first five." | "S plans hold the first five, plus `## Decisions` when one is logged (H11)." |
| 6.10 | After "…from a `--handoff` phase exit to the successor's `resume`." | Add: "The controlling session's end (§3) also pauses the clock, and the task's next `harness` command restarts it: no harness-driven agent works in between. Work by a session that never runs a `harness` command is not charged. A session waiting for your reply stays alive and stays charged; an adapter without a session-end event keeps the clock running; a second session that runs `harness start` while the controller still works takes over as controller (H3)." In the agent-time sentence, after "before the next prompt or session end", add: "(a prompt that arrives before any stop, such as a queued message delivered mid-turn, closes the open span at that prompt), cut at the clock's stop; nothing that starts after the stop counts, not even as unknown (H9)" |
| 6.11 | "the latest completed attempt before the last `ready` passed" | "the latest attempt logged before the last `ready` passed (CLI events take their timestamp under the spool lock, so log order is time order, H12)" |
| 7 | `phase` row, Does: "`state.json` + phase event; first `build enter` snapshots `plan.approved.md`" | "Phase event; first `build enter` snapshots `plan.approved.md`"; Refuses when: add "`plan.md` without a goal or usable checks (every command but `triage enter`) (H10)" |
| 7 | `check` row, Refuses when | Add: "after `ready` or a handoff exit, until a phase enter (H5)" |
| 7 | `pr <task-id>` row | Command `pr [<task-id>] [--title T]`; Does: "Runnable checks must pass; commit `.harness/`, push (hooked), open or update the PR; observational checks not yet passed at this code tree: `pr`, PR body 'not ready', no `ready`; else `ready` (revalidated under the spool lock) + `pr`, commit, push (no hook), print the merge rule"; Refuses when: "Failing or stale runnable checks; a check that failed while the PR opened; no `triage enter`; delegate; after `ready` or a handoff exit until a phase enter" (H5–H7) |
| 7 | `pr --refresh` row | Run by: "You (the agent when `merge` is `agent`)"; Does: add "observational checks owed at the rebased code: PR body 'not ready', `build exit --handoff`" (H4, H5) |
| 9 item 3 | "…takes the spool's exclusive file lock and writes one complete line…" | Add: "CLI events take their timestamp under that lock (H12)." |
| 9 item 5 | "Only the controlling session (or you, for `pr --refresh` and manual `build enter`)" | "Only the controlling session (or you, for `pr --refresh` and manual `build enter`; the agent may run `pr --refresh` when `merge` is `agent`)" (H4) |
| 14 | (table) | Add rows: "Rebase merges: a commit added after the last `ready` is not seen by the gate · Use squash or merge commits (`docs/project-setup.md`); the gate stays forge-free (§9.8)" and "`merge: agent` in a repository with a merge queue: `gh pr merge` may enable auto-merge · Not supported; the printed rule excludes it" |

H1 Decision lists · H2 phase from events · H3 controller-end pause · H4 merge rule · H5 observational
checks after the PR and phase enter after a handoff · H6 PR title · H7 one hooked push · H8 date-only
notes · H9 mid-turn prompts and cutoff · H10 plan validation with fence-aware parsing · H11 S-plan
Decisions · H12 CLI timestamps under the spool lock; the gate counts attempts before the last `ready` in
log order.

- [ ] **Step 2: Re-read the whole spec for sentences that now contradict a delta** (§4.4, §5.2, §6.11,
  §7, §9, §17) and fix each in the same commit.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md
git commit -m "docs(lean-harness): spec deltas H1–H12 from the v0 hardening plan"
```

---

## Review log

### Round 1 (r1 → r2): Fable REVISE, GPT Astra REVISE

| # | Reviewer | Finding | r2 |
|---|---|---|---|
| 1 | Astra (blocker), Fable (major) | Controller only from phase enters: a successor that continues an open phase and ends never pauses | Fixed: controller also from `resume`; two-endings test (Task 6) |
| 2 | Astra, Fable (blocker) | Refresh hand-back printed "run `harness pr`" → `ready` with the clock paused, incomplete timing | Fixed: hand-back messages say `harness phase build enter` first; `check`/`pr` refuse after a handoff exit until a phase enter (`gate.needs_phase_enter`); tests assert both (Task 4) |
| 3 | Astra (blocker) | `publish` emits `ready` from a stale event snapshot; a check failing during the push was missed | Fixed: revalidate under the spool lock before `ready`; pre-push-hook race test (Task 4) |
| 4 | Astra, Fable (blocker) | Instructions still said verify ends when every check passes; `build.md` last line failed the new title test | Fixed: `verify.md` step 5 and Commands, `build.md` last paragraph reworded; the title-text test dropped (Task 5 covers behavior) (Task 7) |
| 5 | Astra (blocker) | New regex lost the word boundary: `Check: goalpost` counted as `goal` | Fixed: each id bounded; negative tests (Task 1) |
| 6 | Astra (blocker) | Validation would refuse valid plans whose check commands contain `## ` lines (#17) | Fixed: fence-aware `_split` (Task 3) |
| 7 | Astra (major) | #4 and #15 still give wrong scores | #15 fixed (cutoff, Task 6). #4 kept deferred: needs the forge (§9.8); boundary stated in docs and spec §14 |
| 8 | Astra (major) | `gh pr merge` may enable auto-merge with a merge queue | Printed rule and docs exclude merge-queue repositories; spec §14 row |
| 9 | Astra (major), Fable (minor) | Spec deltas missed §3, §6.5, §7 `phase`/`pr` rows; §6.4 promised a printed controller | Added §3, §5.2 Verify and after-table, §6.5, §7 rows, §9, §14; §6.4 no longer mentions a printed controller |
| 10 | Fable (major) | Task 9 listed changes as "only these"; E1 also changes | E1 row added with Fable's computed value; the rule-explanation clause kept |
| 11 | Fable (minor) | "No agent is working" is not literal (M1 s2 worked without `harness start`) | §6.10 delta says "no harness-driven agent" and states the uncharged case |
| 12 | Fable (minor) | H3 depends on a session-end event Codex may not emit | Stated in Global Constraints and §6.10 delta |
| 13 | Fable (minor) | Title test claimed "task id from the branch" but the env carried it | Test now removes `HARNESS_TASK_ID` |
| 14 | Astra (YAGNI) | #36 "derivable" overstated | Deferred row reworded |
| 15 | Fable (YAGNI, optional) | Cut the `merge` knob | Kept: the user asked that agents can merge when mandated (cloud); one key and one string, default unchanged |

### Round 2 (r2 → r3): Fable APPROVE, GPT Astra REVISE

| # | Reviewer | Finding | r3 |
|---|---|---|---|
| 1 | Astra (blocker) | `build.md` still says build ends when every check passes, so a PR-dependent check blocks reaching verify | Fixed: `build.md` step 7 and spec §5.2 Build row except checks that need the open PR (Task 7, Task 10) |
| 2 | Astra (blocker) | Check events take their timestamp before the lock, so one can be logged after `ready` with an earlier time | Fixed: CLI events are stamped under the spool lock (`spool.append(stamp=True)` from `context.record`); the gate counts attempts before the last `ready` by log position; tie and spool tests (Task 4, spec H12) |
| 3 | Astra (blocker) | Your manual refresh (no session) kept the old agent as controller, so its end paused the refresh | Fixed: every phase enter sets the controller, clearing it for manual enters; manual-refresh test (Task 6) |
| 4 | Astra (blocker) | `publish` closed the phase before pushing; a late revalidation failure left nothing open, so refresh recorded no handoff | Fixed: the phase closes under the lock right before `ready` (`exit_phase(held=True)`); late-failure tests for `pr` and `--refresh` (Task 4) |
| 5 | Astra (major), Fable (minor) | §5.2 delta and the guard's message said "build enter" after any handoff | Fixed: after a handoff, the enter of the phase you continue in (message, `build.md`, spec §5.2) |
| 6 | Astra (major) | Prompts or helpers that start after the cutoff still counted as unknown | Fixed: unknown spans count only what starts before the cutoff (Task 6) |
| 7 | Fable (minor) | `harness start` printed "build (exited)" after a handoff instead of the reason | Fixed: `_where` uses `needs_phase_enter` (Task 4) |
| 8 | Fable (minor) | Controller-from-`resume` trade-off unstated | Stated in the §6.10 delta |
| 9 | Astra | Rebase merges (#4) | Accepted as non-blocking under the stated boundary |

### Round 3 (r3 → r4): Fable APPROVE, GPT Astra REVISE

| # | Reviewer | Finding | r4 |
|---|---|---|---|
| 1 | Astra (blocker) | `build.md` step 6 ("when every milestone passes, run `harness rebase`") still blocks a milestone that names a PR-dependent check | Fixed: steps 4 and 6 except checks that need the open PR (Task 7) |
| 2 | Fable (minor) | `flock` is not reentrant: a future call inside `publish`'s locked block must pass `held=True` | Comment added at the `with` (Task 4) |

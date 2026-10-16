# Lean Harness Slice 2a (Codex agents) Implementation Plan

> **For agentic workers:** implement task by task, test first. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Make Codex a first-class harness agent additively, and give task worktrees one predictable home
per project and agent, as specified in the Slice 2a spec.

**Spec:** `docs/superpowers/specs/2026-10-16-lean-harness-slice-2a-codex-spec.md` (this repo; the approved
revision). Section numbers below (§n) are the spec's.

**Code:** `echotheorylabsai/lean-harness`, branch `claude/harness-codex-agents-4t0dap` from `main`
(`88c0e8c`). Paths are relative to that repo unless they start with `docs/superpowers/` (this repo).

**Tech stack:** Python 3.12 standard library only (`tomllib` reads TOML; nothing writes it); `unittest`
(run with `python3 -m unittest discover -s tests -t .`); git; the Logbook's existing browser tests.

**Evidence:** Phase 0b (§10): fixtures and facts from Codex 0.163.0 (Linux container) and 0.160.0 (the
user's Mac). Copies of the container probe files live in the session scratchpad; the fixtures are
regenerated in Task 3 with `tests/smoke/codex_facts.py`.

**Execution:** one implementer in one session (tasks share `adapters/`, `doctor.py`, `start.py`), then the
user's review protocol on the PR: an independent adversarial review (Fable, max effort) until APPROVE.

**Revision:** r3 (2026-10-16): plan review round 1 applied (review log at the end).

## Global constraints

- Python 3.12 stdlib only; tests are `unittest` classes; the suite stays green after every task (the two
  "unwritable state dir" tests fail only when run as root, as on `main`).
- Additive (§1): no test of the Claude adapter, recording or scoring is edited. The only edits to existing
  tests are the three declared ones: `CLEARED` in `tests/helpers.py` (Task 1), the main-checkout hint in
  `tests/test_doctor.py` (Task 8), and the no-reader agent in `tests/test_logbook.py`
  `test_readers_are_chosen_by_the_recorded_agent` (Task 9).
- Shared Codex test setup lives in one new file, `tests/codex_helpers.py` (Task 5), never in `helpers.py`.
- No new harness commands; no new event kinds or fields (schema v1). One new optional flag:
  `start --new --agent`.
- Nothing project-specific in code or instruction files.
- `AGENTS.md` and the phase files do not change. `hooks/bootstrap.md` gets exactly §15's two edits.
- Every write to a user file under `$CODEX_HOME` is append-only or a marked block, never reorders, never
  writes a file it cannot parse, and backs up before uninstall (and before the `config.toml` edit).

## What this plan builds

| Spec | Task |
|---|---|
| Test isolation (§12) | 1 |
| Found agents, own-agent probes (§4) | 2 |
| Codex events and fixtures (§6) | 3 |
| Codex install and uninstall (§5) | 4 |
| Codex doctor probes (§8) | 5 |
| Registering Codex; cross-agent rows (§3, §7 table) | 6 |
| Helper lookup from the event log; delegate notice (§7) | 7 |
| Task worktrees, `--agent`, doctor hint, bootstrap sentence (§15) | 8 |
| Logbook: `read_codex_log`, token-only cost (§9) | 9 |
| `codex_facts.py`, Codex smoke (§10, §12) | 10 |
| Docs (§2.1) | 11 |
| Regression and the Mac checks before the PR (§11 Regression) | 12 |
| v0 spec deltas (§14) | 13 |

## Deferred (not in this plan)

Everything in §2.2 (Slice 2b) and §2.3. The proof tasks P1–P6 (§11) are real tasks the user runs after the
PR merges; Task 12 lists the rollout that precedes them.

## Review focus

1. **Claude unchanged:** with no Codex home and no `--agent`, every command's output and every record is
   byte-identical to `main` (Task 2's and Task 6's regression tests; Task 12's re-score diff).
2. **User files under `$CODEX_HOME`:** append-only hooks, marked bootstrap block, verified `config.toml`
   edit with restore, uninstall listing shifted hooks (Task 4).
3. **Identity:** the event-log lookup never fires for a Claude session in a task worktree (its markers set
   `HARNESS_PARENT_SESSION`) and never makes a main Codex session a delegate (Task 7).
4. **Worktrees:** nothing left behind on any failure; the main checkout never changes (Task 8).
5. **Logbook:** a Codex-only project builds; Claude-only cost fields unchanged (Task 9).

---

### Task 0: Branch and baseline

- [ ] Attach `echotheorylabsai/lean-harness` with push access; `git fetch origin main && git switch -c
  claude/harness-codex-agents-4t0dap origin/main`.
- [ ] `python3 -m unittest discover -s tests -t .` → 340 tests; only the two root-only failures (container).

---

### Task 1: Tests never see the real Codex home or the running agent (§12)

**Files:** `tests/helpers.py` (declared edit).

- [ ] **Failing test** `tests/test_isolation.py::test_clean_env_clears_agent_variables`: with
  `CODEX_HOME=/real/codex` and `CLAUDECODE=1` in `os.environ` (patched), `clean_env()` contains neither.
- [ ] Add `"CODEX_HOME", "CLAUDECODE"` to `CLEARED`.
- [ ] Suite green.

---

### Task 2: Found agents; an agent session probes its own agent (§4)

**Files:** `harness/adapters/__init__.py`, `harness/adapters/claude.py`, `harness/doctor.py`,
`harness/commands/{install,uninstall,doctor,start}.py`, tests `tests/test_found.py` (new).

**Interfaces:**
- Each adapter: `found(home: Path, env: Mapping) -> bool` (its home exists) and `RUNNING_VAR: str`.
  Claude: `(home / ".claude").exists()`, `RUNNING_VAR = "CLAUDECODE"`.
- `adapters.DEFAULT = "claude"`; `adapters.found_agents(home, env) -> list[str]`: the adapters whose
  `found` is true, in registry order; if none, `[DEFAULT]` (§4: Claude when no agent home exists).
- `doctor.agent_install(ctx, agents: list[str] | None = None) -> list[Callable]`: probes of `agents`
  (default: `found_agents`).

**Behavior:**
- `install --user`: dispatcher as today; then for each found agent, run its `install_user` and print that
  adapter's change lines before the next adapter runs; "already installed; nothing changed" when no line at
  all (today's text); finally one extra line `agents: <names>` (additive line, F15).
- `uninstall --user`: every registered adapter (each is a no-op without its files), as today.
- `harness doctor`: install group = `agent_install(ctx)`.
- `start --new`: `agent_install(ctx)`.
- `start` (bootstrap): `agent_install(ctx, [ctx.identity.agent])` when the identity has an agent, else
  `agent_install(ctx)`.

**Tests first (`tests/test_found.py`):**
- [ ] `found_agents` for: empty home → `["claude"]`; `.claude` only → `["claude"]` (the `.codex` cases are
  asserted once, in Task 6, with the live registry).
- [ ] Claude-only home: `install --user` prints today's lines in today's order, then `agents: claude` as the
  only extra line (the expected lines are the ones `tests/test_install.py` already pins).
- [ ] An agent session's `start` runs only its agent's install probes (doctor event `checks` keys).
- [ ] Suite green (no Claude test edited).

---

### Task 3: Codex events (§6) and fixtures

**Files:** `harness/adapters/codex.py` (new: events part), `tests/fixtures/codex/*.json` (new, 7 files),
`tests/test_adapter_codex.py` (new).

**Fixtures:** copy the scrubbed payloads from a `codex_facts.py` run (the container's
`facts-run2/fixtures/*.json`, or a fresh run if the session has Codex) to `tests/fixtures/codex/`, and
record their sha256 in the commit message; Task 12 compares their field lists with the Mac's. Files: `SessionStart`, `UserPromptSubmit`,
`UserPromptSubmit-subagent`, `Stop`, `SubagentStart`, `SubagentStop`, `SessionEnd`.

**Interfaces (mirroring `claude.py`):** `NAME = "codex"`, `IDENTITY_VAR = "CODEX_THREAD_ID"`,
`RUNNING_VAR = "CODEX_THREAD_ID"`, `HOOK_EVENTS` (same six names → kinds), `SNAKE` (event → trust-key
name: `session_start`, `user_prompt_submit`, `stop`, `subagent_start`, `subagent_stop`, `session_end`),
`REQUIRED` per §6, `parent_session(payload_session_id, env, foreign_vars)`, `to_event(...)`,
`on_event(...)` (no-op).

```python
REQUIRED = {
    "SessionStart": ("session_id", "source"),
    "UserPromptSubmit": ("session_id", "turn_id"),
    "Stop": ("session_id", "turn_id"),
    "SubagentStart": ("session_id", "agent_id", "agent_type"),
    "SubagentStop": ("session_id", "agent_id", "agent_type"),
    "SessionEnd": ("session_id", "reason"),
}


def parent_session(payload_session_id, env, foreign_vars):
    """HARNESS_PARENT_SESSION; else an inherited CODEX_THREAD_ID that differs from this session (a codex
    exec child's hooks inherit the parent's CODEX_THREAD_ID, §10 0b.3); else this session (§7)."""
    if env.get(PARENT_VAR):
        return env[PARENT_VAR]
    if env.get(IDENTITY_VAR) and env[IDENTITY_VAR] != payload_session_id:
        return env[IDENTITY_VAR]
    return payload_session_id


def to_event(hook_event, payload, env, foreign_vars):
    kind = HOOK_EVENTS.get(hook_event)
    if kind is None:
        return {}, [f"unknown hook event {hook_event}"]
    if payload.get("agent_id") and kind not in ("subagent_start", "subagent_stop"):
        return {}, []  # a built-in subagent's own prompt (or a future helper event): its span is start→stop
    missing = [n for n in REQUIRED[hook_event] if payload.get(n) in (None, "")]
    transcript, helper_transcript = payload.get("transcript_path"), payload.get("agent_transcript_path")
    if kind == "subagent_start":  # Codex puts the helper's own log here (§10 0b.4)
        transcript, helper_transcript = None, payload.get("transcript_path")
    fields = {"kind": kind, "agent": NAME, "session_id": payload.get("session_id"),
              "parent_session": parent_session(payload.get("session_id"), env, foreign_vars),
              "task_id": env.get(TASK_VAR), "model": payload.get("model"), "effort": None,
              "transcript_path": transcript, "agent_transcript_path": helper_transcript}
    if kind in ("subagent_start", "subagent_stop"):
        fields.update(agent_id=payload.get("agent_id"), agent_type=payload.get("agent_type"))
    if kind == "session_start":
        fields["trigger"] = payload.get("source")
    if kind == "session_end":
        fields["reason"] = payload.get("reason")
    if kind in ("prompt", "stop"):
        fields["turn_id"] = payload.get("turn_id")
    return fields, missing
```

**Tests first:**
- [ ] Every fixture maps with no `missing`, `agent == "codex"`, the right kind; `UserPromptSubmit-subagent`
  maps to `({}, [])`.
- [ ] `SubagentStart`: `transcript_path` None and `agent_transcript_path` = the payload's `transcript_path`;
  `SubagentStop`: both kept.
- [ ] Null `transcript_path` on any event: no `missing` entry.
- [ ] A payload without `session_id` (or `turn_id` on `Stop`): reported missing, no crash; unknown event
  name reported.
- [ ] `parent_session`: plain → self; inherited `CODEX_THREAD_ID` = P ≠ S → P; equal to S → S;
  `HARNESS_PARENT_SESSION` wins.
- [ ] Through `harness hook codex <Event>` (subprocess, Sandbox): a fixture lands in the spool with the
  common git fields (works before registration because `hook.py` looks the adapter up by name — so this
  test lands in Task 6, after registering).

---

### Task 4: Codex install and uninstall (§5)

**Files:** `harness/adapters/codex.py` (install part, including the `config.toml` editor: one adapter
module, D7), `harness/adapters/claude.py` (an ignored `env=None` parameter on `install_user` /
`uninstall_user`; Task 13 records it in the spec's §3 row), `tests/test_install_codex.py` (new).

Tests in this task call `codex.install_user(home, dispatcher, env)` / `codex.uninstall_user(...)` directly
(unit level, temp home): the CLI reaches Codex only after Task 6 registers it.

**Interfaces:** `codex_home(home, env) -> Path` (`env["CODEX_HOME"]` or `home/.codex`);
`found(home, env)`; `install_user(home, dispatcher, env) -> list[str]`;
`uninstall_user(home, dispatcher, env) -> list[str]`. The registry calls every adapter's install and
uninstall with `env` (Claude's accept and ignore it: one signature, keyword default `env=None`).

**hooks.json:** load (absent → `{"hooks": {}}`; invalid JSON → `HarnessError`, never written). For each
event append, if no handler in that event already has the exact command, a group
`{"hooks": [{"type": "command", "command": "<quoted dispatcher> hook codex <Event>"}]}`, with
`"timeout": 3` on `SessionEnd`. Write with `indent=2`. Never reorder or rewrite other groups.

**AGENTS.md:** block = `<!-- lean-harness bootstrap: begin -->\n<bootstrap.md text>\n<!-- lean-harness
bootstrap: end -->\n`. Absent file → created with the block; block present and current → no change; block
present and stale → replaced in place; no block → appended after a blank line.

**config.toml (`add_root(path, root) / remove_root(path, root)` in `codex.py`):**

```python
BLOCK = "\n[sandbox_workspace_write]\nwritable_roots = [{root}]\n"

def add_root(path: Path, root: str) -> str | None:
    """Add root to [sandbox_workspace_write].writable_roots. Returns a change line, or None if present.
    Raises HarnessError with the manual line when the edit cannot be verified (file restored)."""
    text = path.read_text() if path.exists() else ""
    before = _parse(text, path)                      # HarnessError when not valid TOML
    roots = before.get("sandbox_workspace_write", {}).get("writable_roots", [])
    if root in roots:
        return None
    lit = json.dumps(root)                           # a TOML basic string for any path
    new = _insert(text, lit)                         # append BLOCK, insert the key under the header, or
                                                     # insert `lit, ` right after the array's `[`
    after = _parse(new, path, quiet=True)
    want = copy.deepcopy(before)
    want.setdefault("sandbox_workspace_write", {}).setdefault("writable_roots", []).insert(0, root)
    if after != want:                                # anything else changed, or the edit missed
        raise HarnessError(f"could not add the harness state folder to {path} safely; add it by hand: "
                           f"[sandbox_workspace_write] writable_roots = [{lit}, …]")
    backup = _backup(path) if path.exists() else None  # same permission bits as the original
    path.write_text(new)
    return f"{path}: added {root} to writable_roots" + (f" (backup {backup})" if backup else "")
```

`_insert` handles three shapes: no `[sandbox_workspace_write]` header and no dotted
`sandbox_workspace_write.` key → append `BLOCK`; header present without a `writable_roots` line in its
section → insert `writable_roots = [lit]` right after the header; `writable_roots = [` in that section →
insert `lit, ` after the `[` (TOML allows a trailing comma). Every other shape fails verification and gets
the manual line. `remove_root` reverses: removes `BLOCK` verbatim if present, else the `lit, `/`lit` text
inside the array, verified the same way (`want` = before minus the root); when the remaining text is
empty (install created the file), the file is removed. It never raises: a failed verification restores the
file and returns the line "`config.toml`: remove <lit> from writable_roots by hand", so the uninstall's
other change lines still print.

**Override:** `AGENTS.override.md` in the Codex home → `HarnessError` before any Codex write (after Claude's
lines were printed, Task 2).

**Manual step (§5):** when any hook group was added, `install_user` also returns the line "open Codex, run
`/hooks`, and trust the harness hooks" (the same string as `codex_hooks_trusted`'s fix text).

**Uninstall:** backup `hooks.json`; drop each harness handler (and a group it leaves empty); list, per
event, the user's groups that sat after a removed harness group: "`<event>` group <i> moved: Codex skips it
until you trust it again in `/hooks`"; remove the marked block (and `AGENTS.md` if the block was all it held); `remove_root`.

**Tests first (temp HOME with `.codex`, `CODEX_HOME` set explicitly):**
- [ ] Fresh install writes six groups, the block and the root; second install: no change lines.
- [ ] Existing user groups keep their index; harness groups come after them.
- [ ] Stale block replaced in place; text before and after untouched.
- [ ] Invalid `hooks.json` / `config.toml`: `HarnessError`, files byte-identical.
- [ ] `config.toml` shapes: absent file; no table; table without key; single-line array; multi-line array;
  empty array; a `[profiles.x.sandbox_workspace_write]` decoy (must not be edited; verification passes
  only for the right table); an inline-table form → manual line, file restored.
- [ ] Override file: `install_user` raises before writing anything under the Codex home.
- [ ] Uninstall after a clean install restores all three files byte-for-byte (`AGENTS.md`/`config.toml`
  absent before → absent after); a user group added after install is listed as moved; a `config.toml` the
  remover cannot verify is restored and named in a manual line, and the other lines still return.
- [ ] The manual trust line is returned on the first install only.
- [ ] Symlinked `CODEX_HOME` works (writes through to the target directory, which is where Codex reads).

---

### Task 5: Codex doctor probes (§8)

**Files:** `harness/adapters/codex.py` (probes), `tests/codex_helpers.py` (new), `tests/test_doctor_codex.py`
(new).

**`tests/codex_helpers.py`:** `trust_all(codex_home: Path)` appends to `config.toml` one
`[hooks.state."<resolved hooks.json>:<snake>:<gi>:<hi>"]` table per harness hook position
(`trusted_hash = "sha256:test"`, `enabled = true`); `codex_ready(home: Path, env: dict) -> dict` creates
`home/.codex`, returns `env` with `CODEX_HOME` set (used with the CLI once Task 6 registers Codex: it then
runs `install --user` and `trust_all`). Tasks 5, 6, 7, 9 and 10 use it. Codex ignores these entries under
`--dangerously-bypass-hook-trust` (0b.6), so the smoke can use them too.

**Probes** (`doctor_probes()` returns them in this order): `codex_hooks`, `codex_hooks_trusted`,
`codex_writable_root`, `codex_bootstrap`, `codex_no_override`, `codex_full_access`.

Trust match (§8):

```python
def _trusted(ctx) -> list[str]:
    """Harness hooks with no matching trust entry: key suffix :<snake>:<group>:<handler>, path part resolved
    equal to $CODEX_HOME/hooks.json resolved, a trusted_hash, enabled not false."""
    hooks_json = (codex_home(ctx.home, ctx.env) / "hooks.json").resolve()
    state = _config(ctx).get("hooks", {}).get("state", {})
    missing = []
    for event, gi, hi in _harness_positions(ctx):
        suffix = f":{SNAKE[event]}:{gi}:{hi}"
        ok = any(k.endswith(suffix) and Path(k[: -len(suffix)]).resolve() == hooks_json
                 and v.get("trusted_hash") and v.get("enabled") is not False for k, v in state.items())
        if not ok:
            missing.append(event)
    return missing
```

`codex_full_access`: fails only when `ctx.identity.agent == "codex"` and
`any(ctx.env.get(v) for v in ("CODEX_SANDBOX", "CODEX_SANDBOX_NETWORK_DISABLED"))` (macOS sets both;
Linux only the second).

**Tests first** (unit level: probes called with a small context object; `codex.install_user` then
`trust_all`): each probe passes on that fresh install and fails with its fix text when: a group is missing;
`[features] hooks = false`; no trust entry; a bare `hooks.json:…` key; `enabled = false`; root missing;
stale block; override present; Codex identity with `CODEX_SANDBOX=seatbelt`, and with only
`CODEX_SANDBOX_NETWORK_DISABLED=1`. A symlinked `CODEX_HOME` with entries keyed by the resolved path passes.

---

### Task 6: Register Codex; cross-agent rows go live (§3, §7)

**Files:** `harness/adapters/__init__.py` (`REGISTRY = {claude.NAME: claude, codex.NAME: codex}`),
`tests/test_cross_agent.py` (new), `tests/helpers.py` is **not** edited (new helpers live in the new test
module).

**Tests first (live registry, no patching of `identity_vars`):**
- [ ] Claude P in a task worktree (Sandbox `claude_session`), then a "codex exec child" environment =
  P's markers + `CODEX_THREAD_ID=C`: `harness check C1` is recorded with `agent=codex`, `session_id=C`,
  `parent_session=P`, `delegate=true`; `harness phase build enter` refuses.
- [ ] Codex P (env `CODEX_THREAD_ID=P`, Codex hooks fired through `harness hook codex SessionStart`) → a
  Claude child (Claude SessionStart with `CODEX_THREAD_ID=P` in the hook env): the child's markers carry
  `HARNESS_PARENT_SESSION=P`; its `check` has `agent=claude`, `parent_session=P`, `delegate=true`.
- [ ] `harness hook codex <Event>` with each fixture lands in the spool (Task 3's deferred test).
- [ ] CLI (moved from Task 4): with a `.codex` home, `install --user` prints Claude's lines, then raises on
  an `AGENTS.override.md` with Claude's files in place; `uninstall --user` lists a user group that sat after
  a harness group.
- [ ] Codex-only home (`.codex` only): `found_agents` → `["codex"]`; `install --user` writes no `.claude/*`
  and prints `agents: codex`; `doctor`'s install group has no `claude_*` probe. Both homes → both, in
  registry order.
- [ ] With no Codex home: `doctor` output, `install --user` lines (except the `agents:` line) and the
  spool records of a full Claude task (`Sandbox.through_triage`) are identical to `main`'s (assert the
  probe-name list and the absence of any `codex` field value).

---

### Task 7: Helpers found in the event log; delegate notice (§7)

**Files:** `harness/context.py`, `harness/commands/start.py` (notice), `tests/test_helper_lookup.py` (new).

```python
def _from_log(ident, env, state_dir) -> identity.Identity:
    """§7: a session with an identity, not a delegate by its environment, and no HARNESS_PARENT_SESSION
    is a delegate when the spool says so: its latest session_start names another parent (rule 1), or a
    subagent_start names it as a helper (rule 2)."""
    if ident.session_id is None or ident.delegate or env.get(identity.PARENT_VAR):
        return ident
    sid = ident.session_id
    hooks = [e for e in spool.read(state_dir) if e.get("source") == "hook"]
    starts = [e for e in hooks if e.get("kind") == "session_start" and e.get("session_id") == sid]
    r1 = starts[-1].get("parent_session") if starts else None          # rule 1: the latest session_start
    r1 = None if r1 == sid else r1
    r2 = next((e.get("session_id") for e in hooks                    # rule 2: named as a built-in helper
               if e.get("kind") == "subagent_start" and e.get("agent_id") == sid), None)
    parent = r1 or r2
    return identity.Identity(sid, ident.agent, parent, True) if parent else ident
```

`context.load` applies it only inside a harness project (a git checkout with `.harness/project.json`: it
reads that project's spool); elsewhere (`install`, `uninstall`, `doctor` outside a repository) the identity
is as today. Rule 1 takes the latest `session_start` (a resume keeps the recorded parent of that
start). Notice: `start` prints `delegate of task <id>: follow your prompt (parent session <P>)`.

**Tests first:**
- [ ] Rule 1: spool has `session_start` S with `parent_session` P (≠ S) → `phase` refuses, `check` records
  `delegate=true`, `parent_session=P`; `start` prints the notice with P.
- [ ] Rule 1 negative: `parent_session` = S → not a delegate.
- [ ] Rule 2: `subagent_start` with `agent_id` = S under session P → delegate of P.
- [ ] A Claude session in a task worktree (markers set) is never looked up (spy on `spool.read` count, or
  a spool that would make it a delegate if read → still the controller).
- [ ] No hook events for S → not a delegate; no identity → unchanged.

---

### Task 8: Task worktrees (§15)

**Files:** `harness/commands/start.py`, `harness/gitio.py` (`is_main_checkout`, `worktree_add`,
`worktree_remove`, `branch_delete`), `harness/commands/doctor.py` (hint), `hooks/bootstrap.md` (one
sentence), `tests/test_doctor.py` (declared edit of the hint assertion), `tests/test_worktrees.py` (new).

**Flow** (`new_task`):

```python
def new_task(args, ctx) -> int:
    ...validate slug, tier, request as today...
    ctx.require_project()                                # first, as today ("no .harness/project.json here")
    if gitio.is_main_checkout(ctx.root):
        return _new_worktree_task(args, ctx, request)
    results = doctor.run(doctor.agent_install(ctx) + doctor.PRE_START, ctx, task_id)   # today's in-place flow
    if not doctor.passed(results):
        print(doctor.format(results)); return 1
    if _register(args, ctx, request) != 0:
        return 1
    print(f"task {task_id} registered; the clock is running.\nharness checkout: {REPO}")   # today's line
    return 0

def _new_worktree_task(args, ctx, request) -> int:
    agent = _task_agent(args.agent, ctx)                # --agent; one RUNNING_VAR; the one found agent
    task_id = f"{date.today().isoformat()}-{args.new}"
    results = doctor.run(doctor.agent_install(ctx) + [doctor.probe_not_cloud], ctx, task_id)
    if _task_id_used(ctx, task_id):
        results.append(("unused", False, "use a new slug"))
    if not doctor.passed(results):
        print(doctor.format(results)); return 1
    p = ctx.require_project()
    path = ctx.root.parent / "worktrees" / ctx.root.name / agent / task_id
    gitio.fetch(ctx.root, p["integration_remote"], p["default_branch"])
    try:
        gitio.worktree_add(ctx.root, path, task_id, f"{p['integration_remote']}/{p['default_branch']}")
    except HarnessError as e:
        raise HarnessError(f"{e}\nIf no task {task_id} is registered: git worktree remove --force {path}; "
                           f"git branch -D {task_id}") from e
    registered = False
    try:
        wctx = dataclasses.replace(context.load(path, ctx.env), identity=Identity(None, agent, None, False))
        results = doctor.run(doctor.PRE_START, wctx, task_id)   # pre-start probes inside the new worktree
        if not doctor.passed(results):
            print(doctor.format(results))
        else:
            registered = _register(args, wctx, request) == 0
    finally:
        if not registered:                              # a failed probe, a used id, an exception, Ctrl-C
            gitio.worktree_remove(ctx.root, path)       # --force
            gitio.branch_delete(ctx.root, task_id)      # -D
    if not registered:
        return 1
    print(f"task {task_id} registered in {path}; the clock is running: open {agent} there now. "
          f"This session does not work on the task.\nharness checkout: {REPO}")
    return 0
```

`_register(args, ctx, request)` is today's body after the probes, minus its final print (each flow prints
its own line): the locked `probe_unused`, the task folder, the `start` event (`context.event(ctx, ...)`, so
the worktree flow's identity override gives it the task's agent and no session); returns 0 or 1. The
worktree flow's last line adds `harness checkout: <path>` after §15 step 6's text, as today's line does
(additive). `_task_agent`: `--agent` must be in `REGISTRY`; else the
adapters whose `RUNNING_VAR` is set — exactly one wins; else `found_agents` — exactly one wins; else
`HarnessError("pass --agent " + "|".join(REGISTRY))`. `_task_id_used`: §15 step 2's uniqueness check run
for branch `<task-id>`: a `start` event with that task id or branch in the spool, a remote branch
`<task-id>`, or `.harness/runs/<task-id>` on the integration ref (not `probe_unused`, which tests the main
checkout's own branch).

`gitio.is_main_checkout(cwd)`: `git rev-parse --path-format=absolute --git-dir --git-common-dir` equal.

**Doctor** (main checkout = git dir equals common dir, any branch): hint "`harness start --new` here
creates the task's worktree; these checks apply there"; only the Install group sets the exit code (today's
default-branch rule, now keyed on the main checkout). `probe_task_branch`'s fix text becomes "run `harness
start --new` in the main checkout".

**Bootstrap** (`hooks/bootstrap.md`): the first sentence's "ignore this file" becomes "ignore these
instructions"; appended sentence: "To start a new harness task for the user, run
`harness start --new` in the project's main checkout with the user's tier (ask if they gave none) and the
user's request text verbatim, saved outside any checkout; it creates the task's worktree and says where to
open the next session."

**Tests first (`tests/test_worktrees.py`, Sandbox):**
- [ ] Main checkout on `main`: creates `<tmp>/worktrees/main/claude/<task-id>` (Sandbox's main checkout
  folder is named `main`) on branch `<task-id>`, registered inside it; main checkout's branch, HEAD and
  `git status --porcelain` unchanged; the `start` event: `agent=claude`, `session_id`/`parent_session`
  null, `branch=<task-id>`, `cwd` = the worktree.
- [ ] Main checkout on another branch (`harness-install`): same result.
- [ ] Agent resolution: `--agent codex` → `codex/` folder; `CLAUDECODE=1` → claude; `CODEX_THREAD_ID` →
  codex; both set → refuses (`pass --agent`); neither, Claude-only home → claude; `--agent nope` → refuses.
- [ ] A used task id refuses before `git worktree add` (no folder, no branch).
- [ ] An existing branch `<task-id>` (an interrupted run): refuses with the two recovery commands; nothing
  else created.
- [ ] A pre-start probe failing inside the new worktree: a `.git/hooks/post-checkout` in the Sandbox's main
  repo that writes `stray.txt` (git runs it on `worktree add`), so `probe_clean` fails → worktree and branch
  removed, nothing in the spool. And the locked check failing: push `.harness/runs/<task-id>/state.json`
  to the remote without fetching in the main checkout → same cleanup.
- [ ] In a linked worktree: behaves exactly as today (existing `test_start.py` untouched).
- [ ] Doctor hint text in the main checkout; `tests/test_doctor.py`'s hint assertion edited to it.
- [ ] `test_instructions` still passes (the sentence names only `harness start`).

---

### Task 9: Logbook — Codex logs and token-only cost (§9)

**Files:** `logbook/build.py`, `logbook/viewer.html`, `logbook/README.md` (documents `cost.tokens_only`, a
null `usd`, the "tokens only" captions and `summary.usd_runs`), `logbook/tests/shapes.py` (a token-only
task shape for the browser test),
`tests/test_logbook.py` (new tests, plus the declared edit: `test_readers_are_chosen_by_the_recorded_agent`
uses `gemini` as the agent with no reader), recorded Codex log fixtures `tests/fixtures/codex/logs/{e-0,c-0,c-1}.jsonl`
captured on the Mac by `codex_facts.py` (Task 10): run E's log (`logs/e-0.jsonl`: a `harness check C1`
line, a `gh pr merge 1 --squash` line, an `apply_patch` through `exec_command`, `effort` set,
`token_count` events) and run C's parent and subagent logs (`logs/c-0.jsonl`, `logs/c-1.jsonl`) for the
helper-tokens test. `apply_patch` parsing is
tested with lines in the format a Codex `apply_patch` call records (`*** Update File: <path>`), checked
against a real capture if the Mac's Codex offers the tool to the mock model, else marked as format-assumed
in the test.

**`read_codex_log(path, until, with_prompts=False, since=None)`** returns the same keys as
`read_claude_log` plus `"token_only": True`:
- `session_meta` → known; `origin = {"entrypoint": originator}` (no first prompt: exec logs carry it only
  as a user message after `<environment_context>`).
- `turn_context` → remember `model`, `effort`; at the end `models[last model] = 1` and `effort` = the last
  effort (a key Claude's reader lacks; `session_out` uses it when the records carry no effort).
- `response_item` `function_call` `exec_command` (`arguments.cmd`) or `shell` (`arguments.command`, a list
  → `shlex.join`) → the same `inspect()` path as Claude's `_SHELL_TOOLS` branch (harness commands,
  uninspected, GitHub writes, harness-file writes, rebases); its `function_call_output` → outcome from
  `Process exited with code N` or, for an intercepted `apply_patch`, `Exit code: N` (0 → done, else
  failed); a refusal text → refused, matched by a Codex-specific pattern from the 0.163 binary's strings
  (`sandbox denied exec error`, `exec command rejected by user`, `rejected by user`, `requires approval`;
  tested from a synthetic output and marked format-assumed); none → no result.
- `apply_patch` → an edit of a harness-owned file when a `*** (Add|Update|Delete) File:` path matches
  `HARNESS_FILE`, in all three recorded forms: an `exec_command` whose `cmd` starts with `apply_patch`
  (observed on 0.163: Codex intercepts it, records an `item_completed` `FileChange` with absolute paths, and
  answers `Exit code: 0`), a `shell` argv whose first word is `apply_patch`, and a `custom_tool_call`
  `apply_patch` (real models; format-assumed in the test). Such a call is not also fed to `inspect()`.
- `function_call` `spawn_agent` → `agent_calls` (`type` = `codex:subagent`).
- Every other call → `tools["other"]`, uninspected when it carries command-like keys (Claude's rule).
- `event_msg` `token_count` with `info` present → `usage` = that `info.total_token_usage` (the last one),
  mapped `input_tokens`→`input`, `output_tokens`→`output`, `reasoning_output_tokens`→`thinking`,
  `cached_input_tokens`→`cache_read`, `cache_write_input_tokens`→`cache_write`.
- Lines outside `[since, until)` are not counted (Claude's rule); unparsable lines → `skipped`.

`READERS["codex"] = read_codex_log`; `TOKEN_ONLY = {"codex"}` (agents whose logs carry no dollars), so
`cost_summary` classifies `(agent, None)` pairs (missing logs) without a log to read.

**Cost:** `cost_summary(pairs)` takes `(agent, log)` pairs per §9 (the call site passes main, side and
delegate sessions as today, plus Codex helper logs read from `agent_transcript_path`); a log with
`token_only` is token-only; `sessions`/`logs_total` count sessions whose agent has no token-only reader
(Claude's; never helpers), missing logs by their session's agent. Record when any Claude log has a cost record or any token-only log was read; Claude-only results
are unchanged plus `tokens_only: 0`; `usd`/`usd_exact` null when no cost record; token-only models listed
with their output tokens and `usd: null`. `batch_summary`: `exact` skips null; `usd_runs` counts non-null.

**Viewer:** every print of a null `usd` on a task with `tokens_only > 0` says "tokens only" (the task's
dollar tile, the project table's cost cell; the sort puts such tasks with the unpriced ones); the tile says
"excludes N token-only sessions" when `usd` is set and `tokens_only > 0`, and the partial caption wins when
both apply; the tokens caption ("N output · tokens only" for token-only tasks) prints whenever `cost` is
present, outside the `if (md.length)` model-bar block; no bar for token-only models; the project tile says
"N tasks with dollar totals"; `partialCost` unchanged (it reads `sessions`/`logs_total`). The page names no
agent (`test_no_adapter_names_or_prefixes`).

**Tests first** (synthetic Codex records use a new `ck(sid, kind, t, log=None, parent=None, **f)` helper
in the new tests, since `by()`/`hk()` hard-code Claude; calls are windowed from `T0`, so the fixture tests
pass `now ≥ 7 * 86_400_000`):
- [ ] `read_codex_log` on `e-0.jsonl`: `harness_cmds == 1`, one `gh pr merge` write, `harness_edits == 0`
  (the patch touches `.harness/runs/x/note.md`, not a harness-owned file), `effort == "high"`,
  `usage["output"] == 20`, the model, `token_only`; on `c-0.jsonl`: one agent call.
- [ ] A synthetic `exec_command` `apply_patch` with `*** Update File: .harness/runs/x/state.json` and
  `Exit code: 0` → one harness edit; the `shell` argv and `custom_tool_call` forms likewise (format-assumed).
- [ ] A synthetic refused output (each pattern) → refused.
- [ ] Window: calls after `until` not counted.
- [ ] `cost_summary`: Claude-only inputs give today's dict plus `tokens_only: 0` (pin with an existing
  test's expected dict); an open Claude session without a cost record → `None`, as today; Codex-only →
  `usd` null, tokens set, `tokens_only: 1`, not partial; mixed with all Claude logs read → not partial.
- [ ] `batch_summary` with one Codex-only task builds; `usd_runs` excludes it.
- [ ] A Codex helper's log adds its tokens to `tokens_only` and the sums.
- [ ] A Claude S1 with a `subagent_stop` whose `agent_transcript_path` points to a Claude log with a cost
  record: `cost` is today's dict plus `tokens_only: 0` (the helper log is not an input).
- [ ] The declared edit: `read_log("gemini", …)` is `no_reader`; `read_log("codex", good Claude log, …)` is
  `unsupported`.
- [ ] The Logbook build's parity check passes on a Sandbox project with a Codex task (Codex hooks fired
  through `harness hook codex`).
- [ ] Browser acceptance (`logbook/tests/accept.py`, which renders `shapes()`) with a token-only task in
  `logbook/tests/shapes.py`: the tile text and the tokens caption render; every number prints through
  `num(…, tp(t, "cost/tokens_only"))` or `vp(key, "summary/usd_runs")` (accept.py fails on a digit outside
  a `[data-src]` element); the table sort uses `t.cost && t.cost.usd != null ? t.cost.usd : -1`.

---

### Task 10: `codex_facts.py` and the Codex smoke (§10, §12)

**Files:** `tests/smoke/codex_facts.py` (the Phase 0b script, unchanged), `tests/smoke/run_smoke.py`
(an opt-in `--agent codex` run), `tests/smoke/README` lines in `README.md`.

- [ ] Add the script as run on the Mac (sha256 `d1d5a7fb…`): run E has the shell run
  `harness check C1 || true`, `gh pr merge 1 --squash || true` and an `apply_patch` adding
  `.harness/runs/x/note.md`, with `model_reasoning_effort="high"`; every run's session logs are copied,
  scrubbed (paths; `session_meta.base_instructions` dropped), to `<out>/logs/`.
- [ ] A unit test runs its mock server class standalone (no Codex needed) to keep it importable.
- [ ] `run_smoke.py --agent codex`: throwaway `CODEX_HOME` (with the user's `auth.json` copied in when
  present, deleted in a `finally`; else skip with a message), `install --user` into the temp home, then
  `trust_all` (so the agent's `harness start` passes `codex_hooks_trusted`), a scripted task driven by
  `codex exec -s danger-full-access --dangerously-bypass-hook-trust "<prompt>" < /dev/null`, then
  `harness score` and the expected card fields; never touches the real `~/.codex`.

---

### Task 11: Docs (§2.1)

**Files:** `README.md`, `docs/project-setup.md`, the Logbook Guide (where the viewer's Guide text lives),
and their fact tests.

- [ ] Keep every string the Logbook tests pin (`git worktree add <path> -b <branch> origin/<default-branch>`
  in the README; the Guide's by-hand example and cleanup snippet): the by-hand flow stays as the
  alternative, after the main-checkout flow.
- [ ] README: supported agents (Claude Code, Codex CLI and desktop app); install (`install --user` sets up
  found agents; Codex: open `/hooks` and trust the six harness hooks; launch Codex with full access);
  "Run a task" becomes: write the request outside any checkout → `harness start --new <slug>
  --benchmark-tier S|M|L --request <file> [--agent claude|codex]` in the main checkout → open the agent in
  the printed folder; the layout tree; cleanup with the new path; uninstall covers Codex; the "registering
  session does not work on the task" rule; time from registration is charged.
- [ ] project-setup: `AGENTS.override.md` in `$CODEX_HOME` blocks install; Codex projects trusting; the
  layout's `worktrees/` folder sits outside every repository.
- [ ] Guide: Codex tokens ("tokens only", "excludes N token-only sessions"); path examples keep `<agent>`
  as a placeholder (the Guide and page name no agent: `test_logbook.py` lines 214 and 239).
- [ ] `test_instructions` and the Guide tests pass (every named command exists; facts match the code).

---

### Task 12: Regression, the Mac checks and the PR

- [ ] Full suite green (only the two root-only failures in the container).
- [ ] On the Mac (through the user's Remote Control session, read-only for the user's real state): run
  `logbook/tests/parity.py <projects…> --now-ms <fixed> --installed <checkout> --keep <dir>` twice, once
  with a `main` (`88c0e8c`) checkout and once with this branch (it scores a frozen copy of the state dir
  with `SCORER`); the two kept card sets must be identical (`as_of` included); any difference is a bug.
- [ ] On the Mac: `python3 tests/smoke/codex_facts.py --out <tmp>` with the Mac's Codex; fixture field
  lists equal the committed fixtures'.
- [ ] Push; open the PR: summary, the spec link, the declared test edits, the re-score result, the rollout:
  1. merge; `git pull` in the harness checkout;
  2. `harness install --user` (sets up Codex; reruns Claude's bootstrap copy);
  3. open Codex → `/hooks` → trust the six harness hooks;
  4. `harness doctor` in each project's main checkout;
  5. run P1–P6 (§11).

---

### Task 13: v0 spec deltas (this repo)

**Files:** `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md`.

- [ ] In the 2a spec's §3 table, the `claude.py` row adds "and an ignored `env=None` parameter on
  `install_user`/`uninstall_user`" (plan review round 1).
- [ ] Apply every §14 row of the 2a spec exactly; re-read §4.3–4.4, §6.9, §7, §8, §11, §13–14, §16–17 for
  sentences that now contradict them and fix each in the same commit.


---

## Review log

### Plan round 1 (r2 → r3): Fable (max effort) REVISE

| Finding | Resolution |
|---|---|
| R1 Task 4/5 CLI tests before Codex is registered | Tasks 4–5 test the adapter directly; the CLI tests move to Task 6 |
| R2 no Codex test or smoke can pass `codex_hooks_trusted` | `tests/codex_helpers.py` (`trust_all`, `codex_ready`), used by Tasks 5, 6, 7, 9, 10 |
| R3 `codex_full_access` missed the Linux variable | Both variables (Task 5) |
| R4 fixture has no harness-owned edit | Exact counts on `e-0`; the positive case from a synthetic line |
| R5 Codex refusal texts | Named patterns, format-assumed test |
| R6 rule order in `_from_log` | Two scans: latest `session_start`, else the first `subagent_start` |
| R7 double print | `_register` returns without printing; each flow prints its line |
| R8 failure-path test | `post-checkout` hook and a pushed task folder |
| R9 `require_project` first | Kept first in `new_task` |
| R10 `remove_root` must not abort uninstall | Returns a manual line; empty file removed |
| R11 token-only agents without a log; key map | `TOKEN_ONLY`; the spec's map |
| R12 synthetic Codex records; the `T0` window | `ck()` helper; `now` noted |
| R13 the manual trust line | Returned by `install_user` |
| R14 two vs three declared edits | Three |
| R15 Codex-only home behavior | Task 6 |
| R16 Claude helper log not an input | Task 9 test |
| R17 Logbook README | Listed |
| R18 fixture provenance | Copy from the container run; sha256 in the commit |
| R19 `CODEX_SANDBOX_NETWORK_DISABLED` in `CLEARED` | Not taken: matters only inside a sandboxed Codex shell; stays within the spec's declared edit |
| R20 viewer tag paths and sort | Task 9 browser test |
| Spec–plan: Claude `env=None`; one module; extra print line | Task 13 amends §3; `codexconf.py` folded into `codex.py`; the extra line declared additive |
| Cuts: stub registry; `codexconf.py`; Codex first prompt; new re-score procedure | All taken |

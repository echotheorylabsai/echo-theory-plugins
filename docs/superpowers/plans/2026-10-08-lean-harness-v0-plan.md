# Lean Harness v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `harness` CLI, the Claude Code hook adapter and the phase instruction files so one real `mvp` task, and two in parallel, run through the harness and get a complete scorecard (Phase 0 and Slice 1 of spec §11); Slices 2 and 3 are outlined as ordered task lists.

**Architecture:** A pure core (event schema, identity rules, plan parsing, done gate, timing, task resolution, scorecards) over thin edge modules (git, gh, spool, task files). One file per CLI command, registered in one dispatch table in `harness/cli.py`. One module per agent in `harness/adapters/`, listed in one registry dict; each adapter owns its identity variable, payload → event mapping, user-install entries and doctor probes.

**Tech Stack:** Python 3.12 standard library only (`unittest`, `fcntl`, `subprocess`, `json`, `hashlib`), git 2.54, GitHub CLI `gh`, Claude Code 2.1.295 hooks.

**Spec:** `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md` (source of truth). Parent design: `docs/lean-coding-harness-v0-design.md` (governs what the spec does not mention; the spec wins on conflicts). Both live in `echotheorylabsai/echo-theory-plugins`.

## Global Constraints

- Python 3.12, standard library only; tests use `unittest` (§4.2, §12). Run every Python command with `python3.12`.
- Harness repo: `~/Desktop/src/echo-official/lean-harness`, private, GitHub `echotheorylabsai/lean-harness`; holds code only (§4.1).
- State dir: `${XDG_STATE_HOME:-~/.local/state}/harness/<project-hash>/`; `<project-hash>` = first 16 hex chars of SHA-256 of `git rev-parse --path-format=absolute --git-common-dir` (§4.1).
- Event schema version `v: 1`; `ts` is UTC with milliseconds (§6.7).
- `project.json` defaults: `schema_version` 1; `cloud_env_vars` `[]` (mvp: `["ECHO_CODEX_CLOUD","ECHO_CLAUDE_CLOUD"]`); `deadline_hours` `{"S": 4, "M": 16, "L": 48}`; `expiry_days` 21; `defect_window_days` 14; `target_benchmark_tier` `"M"`, `n` 10, `alpha` 0.05, `min_gain` 0.20; `baseline_commit` = harness repo HEAD at install; `challenger_commit`, `shared_commit`, `memory_snapshot_commit` `null` (§6.2).
- Every task is assigned arm `"baseline"` and `assigned_commit` = harness repo HEAD (§2.2 C13).
- Hook handlers never block or fail the agent; CLI commands fail loudly and never drop events (§9.6).
- Local only: refuse when `CLAUDE_CODE_REMOTE=true` or any `cloud_env_vars` variable is `1` (§4.7).
- Native agent memory is never disabled, checked or recorded (C1). No harness-defined subagents (C2). No `worktree.baseRef` (C11).
- `.gitattributes` line: `.harness/memory/*.md merge=union` (§4.1).
- Allow rule: `Bash(harness:*)` (§4.1).
- Claude Code and Codex run on your subscriptions, not API keys: nothing in the harness reads, sets or needs an API key, and smoke and real runs use your logged-in sessions.

## Conventions

- **[YOU]** marks a step only the user performs: creating the GitHub repo; any change to user-scope files in `~/.claude`, `~/.codex` or `~/.local/bin` (`install --user`, Phase 0's temporary hooks, removing `codex exec` trust entries); desktop-app checks; approving Codex hooks; opening or merging any PR (including the `harness install` PRs in mvp and echo-wiki); running real tasks. The executor prepares everything else and waits at each **[YOU]** step.
- `H=~/Desktop/src/echo-official/lean-harness`. Unless a step says otherwise, commands run in `$H`.
- Test command for the whole suite: `python3.12 -m unittest discover -s tests -t . -v`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (omitted below for brevity; add it to every commit).

## Spec readings

Gaps the spec leaves open, and the reading this plan takes. Each stays inside the spec and the parent; none adds a feature.

| # | Gap | Reading taken |
|---|---|---|
| R-1 | §6.10 ends a revision at "a `--refresh` `build exit` without `ready`", but the `phase` event has no field marking it | `pr --refresh` writes that exit with `handoff: true`: control returns to the user, which is what `--handoff` means. Timing then treats it like any handoff exit (clock pauses until the next revision start) |
| R-2 | §6.10 "the `resume` of the session that re-enters build" | After a pause, a revision starts at the latest `resume` whose `session_id` equals the next `phase enter`'s `controlling_session`; with no such resume, at that `enter` |
| R-3 | §6.3 `record` fields the agent cannot know (`benchmark_tier`, `arm`, `assigned_commit`, `predicted_knobs`) | Triage writes `knobs`, `record.tier`, `record.triage_signals`; `harness phase triage exit` fills the rest from the task's `start` event, sets `origin_tier` once, and refuses if `config.json` or a valid `record.tier` is missing |
| R-4 | §9.8 says `score` is deterministic, but in-flight deadlines need "now" | The scoring core takes `now` as an input; each card records it as `as_of` |
| R-5 | Parent: `check` and `pr` "refuse after a `ready` unless build is the open phase" | Refuse while the last `ready` is later than the last `phase build enter`; a revision may then move on to verify |
| R-6 | Where a `check` event is written | Parent rule, generalized: a CLI event goes to the task's `events.jsonl` (plus the spool) only when its kind is not spool-only and the current branch equals `state.json`'s branch; otherwise to the spool only |
| R-7 | CLI task resolution order | `--task` / explicit id, else `HARNESS_TASK_ID`, else the current branch (during a stopped rebase, the rebase's head name and pre-rebase tip, per parent); zero or several matches fail loudly |
| R-8 | `harness install` "on a branch" | On the default branch it creates `harness-install`, writes both files and commits them; you set mvp's `cloud_env_vars` by hand in that PR (no flag exists) |
| R-9 | Slice 1 phase files vs Slice 2 commands | Slice 1 phase files name no Slice 2 command (`tier`, `review`, `memory`, `retro-bundle`) and no retro phase; Slice 1 M tasks run triage → research → plan → build → verify → `pr`. Slice 2 revises the files |
| R-10 | "orphans" on a per-task card vs the summary | Summary: every unresolved event, counted by branch. Card: unresolved events from sessions that also have events resolved to that task |
| R-11 | Standalone `harness doctor` mid-task | Agent-install probes always; the pre-start task probes only on a branch with no task (no task id to check); the session probe only when an agent identity is present. It writes no harness records (`git fetch` still updates the remote-tracking ref) |
| R-12 | §4.7 says plain `start` refuses in cloud sessions; §8 lists the cloud check under D | Bootstrap `start` runs the agent-install probes, the not-cloud probe and the session probe |
| R-13 | A check command that edits files or moves HEAD | The result is not recorded and the command fails loudly (a result produced while code changed cannot satisfy readiness) |
| R-14 | Pushes "with `--set-upstream`; `--force-with-lease` after a rebase" | Every harness push uses both flags: the lease is a no-op for a first push or a fast-forward and protects after a rebase |
| R-15 | Where the scope-reduction flag appears "in the PR" | In the PR body; a re-emitted `ready` refreshes the body with `gh pr edit` |
| R-16 | `doctor` event's "per-check pass or fail" | Field `checks`: `{probe name: bool}`; it passed when every value is true |
| R-17 | `harness_version` "installed CLI commit" | `git rev-parse HEAD` of the harness checkout the CLI runs from |
| R-18 | Wall time for a merged task whose clock is still running | The clock stops at the merge commit's committer time |
| R-19 | Charged time outside any phase (startup, gaps between an exit and the next enter) | Reported per phase as `between_phases` |
| R-20 | Hook entry command and GUI apps' `PATH` | Hook entries call the dispatcher by absolute path; Phase 0 checks `PATH` in desktop-app Bash |
| R-21 | Phase 0's `install --user` dry run (§11) | Replaced, per your instruction, by a temporary hand-added logging hook; Task 0.7 writes this into the spec |
| R-22 | §8's check list (your direction, 2026-10-08: keep doctor minimal) | Doctor keeps only checks that catch silent failures or record discrepancies: Claude hook entries present and enabled, bootstrap import, not cloud, task branch, clean checkout, started from the fetched integration branch, branch and id unused, this session's hooks reaching the spool. Hard dependencies (Python version, git, gh, `gh auth`, repository permission, push access, state-dir writability, dispatcher on PATH, `project.json` validity, `.gitattributes`, allow rule) are left to fail loudly when used. Task 0.7 writes this into spec §8 |

## §9 invariants: where each is enforced

| # | Invariant (§9) | Enforced in exactly one place | Test |
|---|---|---|---|
| 1 | One task = one branch = one worktree; names and ids never reused | `doctor.probe_unused` (run by `start --new` under the spool lock) | `test_start.StartNewTest.test_same_slug_in_two_worktrees_registers_once` |
| 2 | Parallel tasks write disjoint folders; `project.json` read-only during tasks | `taskfiles.task_dir` is the only task-folder path constructor; only `commands/install.py` writes `project.json` | `test_e2e.E2ETest.test_two_parallel_tasks_score_independently` |
| 3 | Every append takes the spool lock and writes one complete line; `start --new` holds it across check, assignment, append; readers ignore an incomplete last line | `spool.append` / `spool.locked` / `events.parse_lines` | `test_spool.SpoolTest.test_parallel_appends_never_interleave`, `test_events.EventsTest.test_parse_lines_skips_incomplete_last_line_and_keeps_unknown_fields` |
| 4 | `git fetch` retries with backoff on ref-lock errors | `gitio.fetch` | `test_gitio.GitioTest.test_fetch_retries_on_ref_lock_errors`, `test_concurrent_fetches_from_worktrees_all_succeed` |
| 5 | Only the controller (or you) issues `phase`, `review`, `pr`; delegates only `check` | `cli.guard` (`controller_only` flag in the dispatch table) | `test_cli.CliGuardTest.test_delegate_cannot_run_controller_commands` |
| 6 | Hooks never block or fail; CLI fails loudly, never drops events | `commands/hook.run` (catch-all, exit 0); `spool.append` raises `HarnessError` with the fix | `test_hook.HookTest.test_garbage_payload_warns_and_exits_zero`, `test_spool.SpoolTest.test_unwritable_state_dir_fails_loudly_with_fix` |
| 7 | While a rebase is stopped, only conflict resolution, plain `start` and the `rebase` rerun touch the worktree | `cli.guard` (`during_rebase` predicate in the dispatch table) | `test_rebase.RebaseTest.test_conflict_stops_guards_and_reruns` |
| 8 | `score` is deterministic and idempotent, makes no commits, needs no forge API | `scorecard.task_card` (pure, `now` passed in); `commands/score.collect` reads git only | `test_score.ScoreTest.test_score_is_deterministic_and_commits_nothing` |

## Review Focus

Input classes the spec implies but a happy-path test would miss; each has a test in the named task.

1. **A hook payload that is not JSON, or lacks fields** (an agent upgrade changes its format): the agent must not notice; one stderr line and a `format_warning` event. Test: Task 1.8 `test_garbage_payload_warns_and_exits_zero`.
2. **A Claude session launched from inside another Claude task session** (`claude -p` in a Bash tool): it must be a delegate of the parent, may run `check`, may not run `phase`. Test: Task 1.12 `test_delegate_is_refused`, Task 1.14 `test_delegate_check_is_flagged`.
3. **The same slug registered the same day from two worktrees at once**: exactly one task exists afterwards. Test: Task 1.11 `test_same_slug_in_two_worktrees_registers_once`.
4. **A check command that writes files** (build output, a formatter): its result must not count. Test: Task 1.14 `test_check_that_changes_the_checkout_is_not_recorded`.
5. **Merging after `main` moved without `pr --refresh`**: the task must score not-done with the reason named. Test: Task 1.21 `test_merge_without_refresh_fails_gate`.

---

## Phase 0: confirm the open platform facts

Exit criteria (spec §11, with R-21): hook-payload fixtures captured from both agents; desktop-app sessions of both agents run user-level hooks; `git hash-object -t tree` runs in a sandboxed `codex exec`; each item confirmed, or its fallback chosen and written into the spec.

Paths used in Phase 0:
- Throwaway repo: `~/Desktop/src/echo-official/harness-phase0` (`$P0`)
- Tools (outside the repo so captures are never committed): `~/Desktop/src/echo-official/harness-phase0-tools` (`$T`)

### Task 0.1: Create the harness repo

**Files:**
- Create: `$H/.gitignore`, `$H/tests/fixtures/claude/.gitkeep`, `$H/tests/fixtures/codex/.gitkeep`

Spec: §4.1 (harness repo location and org).

- [ ] **Step 1: Create the local repo**

```bash
mkdir -p ~/Desktop/src/echo-official/lean-harness && cd ~/Desktop/src/echo-official/lean-harness
git init -b main
printf '__pycache__/\n*.pyc\n' > .gitignore
mkdir -p tests/fixtures/claude tests/fixtures/codex
touch tests/fixtures/claude/.gitkeep tests/fixtures/codex/.gitkeep
git add . && git commit -m "chore: start lean-harness"
```

Expected: one commit on `main`.

- [ ] **Step 2: [YOU] Create the private GitHub repo and push**

```bash
cd ~/Desktop/src/echo-official/lean-harness && gh repo create echotheorylabsai/lean-harness --private --source . --remote origin --push
```

Expected: `git -C ~/Desktop/src/echo-official/lean-harness remote -v` lists `origin` on `echotheorylabsai/lean-harness`.

### Task 0.2: Throwaway repo and the temporary logging hook

**Files:**
- Create: `$P0/README.md`, `$P0/src/a.txt` (a subfolder, so tree hashes include a `040000` entry)
- Create: `$T/log_hook.py`, `$T/add_phase0_hooks.py`, `$T/remove_phase0_hooks.py`

Spec: §11 Phase 0 (fixtures, desktop hooks), §12 (adapter contract fixtures), R-20, R-21.

- [ ] **Step 1: Create the throwaway repo**

```bash
mkdir -p ~/Desktop/src/echo-official/harness-phase0/src ~/Desktop/src/echo-official/harness-phase0-tools
cd ~/Desktop/src/echo-official/harness-phase0
git init -b main
echo "phase 0 throwaway" > README.md && echo a > src/a.txt
git add . && git commit -m init
```

- [ ] **Step 2: Write the logging hook**

`$T/log_hook.py`:

```python
#!/usr/bin/env python3
"""Phase 0 temporary hook: save each payload from the throwaway repo, plus a few env vars."""
import json
import os
import sys
import time
from pathlib import Path

AGENT, EVENT = sys.argv[1], sys.argv[2]
THROWAWAY = os.path.realpath(os.path.expanduser("~/Desktop/src/echo-official/harness-phase0"))
OUT = Path(__file__).resolve().parent / "captures"
KEEP = ("PATH", "CLAUDE_ENV_FILE", "CLAUDE_CODE_SESSION_ID", "CODEX_THREAD_ID", "CODEX_SANDBOX",
        "HARNESS_SESSION_ID", "HARNESS_PARENT_SESSION", "HARNESS_TASK_ID")

raw = sys.stdin.read()
try:
    payload = json.loads(raw)
except json.JSONDecodeError:
    payload = {"_raw": raw}
cwd = os.path.realpath(payload.get("cwd") or os.getcwd())
# User-level hooks fire in every session; keep only the throwaway repo (prompts carry text).
if cwd == THROWAWAY or cwd.startswith(THROWAWAY + os.sep):
    OUT.mkdir(exist_ok=True)
    record = {"agent": AGENT, "event": EVENT, "payload": payload,
              "env": {k: os.environ.get(k) for k in KEEP}}
    (OUT / f"{AGENT}-{EVENT}-{time.time_ns()}.json").write_text(json.dumps(record, indent=2))
```

- [ ] **Step 3: Check the hook filters by folder**

```bash
cd ~/Desktop/src/echo-official/harness-phase0-tools
echo '{"cwd":"/tmp","session_id":"x"}' | python3.12 log_hook.py claude SessionStart
ls captures 2>/dev/null | wc -l
echo "{\"cwd\":\"$HOME/Desktop/src/echo-official/harness-phase0\",\"session_id\":\"x\"}" | python3.12 log_hook.py claude SessionStart
ls captures | wc -l && rm -rf captures
```

Expected: `0`, then `1`.

- [ ] **Step 4: Write the add and remove scripts (you run them)**

`$T/add_phase0_hooks.py`:

```python
"""Append the Phase 0 logging hook to the Claude and Codex user hook files (run by you)."""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
EVENTS = ["SessionStart", "UserPromptSubmit", "Stop", "SubagentStart", "SubagentStop", "SessionEnd"]


def add(path: Path, agent: str) -> None:
    data = json.loads(path.read_text()) if path.exists() else {}
    hooks = data.setdefault("hooks", {})
    for event in EVENTS:
        command = f"{sys.executable} {TOOLS / 'log_hook.py'} {agent} {event}"
        entries = hooks.setdefault(event, [])
        if not any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
            entries.append({"hooks": [{"type": "command", "command": command}]})  # append: never reorder
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"updated {path}")


add(Path.home() / ".claude" / "settings.json", "claude")
add(Path.home() / ".codex" / "hooks.json", "codex")
```

`$T/remove_phase0_hooks.py`:

```python
"""Remove the Phase 0 logging hook entries and list the Codex approval tables to delete (run by you)."""
import json
from pathlib import Path

SNAKE = {"SessionStart": "session_start", "UserPromptSubmit": "user_prompt_submit", "Stop": "stop",
         "SubagentStart": "subagent_start", "SubagentStop": "subagent_stop", "SessionEnd": "session_end"}


def is_phase0(entry: dict) -> bool:
    return any("log_hook.py" in h.get("command", "") for h in entry.get("hooks", []))


def remove(path: Path) -> None:
    data = json.loads(path.read_text())
    kept = {}
    for event, entries in data.get("hooks", {}).items():
        for i, entry in enumerate(entries):
            if is_phase0(entry):
                print(f'  approval table to delete if present: [hooks.state."{path}:{SNAKE.get(event, event)}:{i}:0"]')
        rest = [e for e in entries if not is_phase0(e)]
        if rest:
            kept[event] = rest
    data["hooks"] = kept
    if not kept:
        del data["hooks"]
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"cleaned {path}")


remove(Path.home() / ".claude" / "settings.json")
remove(Path.home() / ".codex" / "hooks.json")
```

- [ ] **Step 5: [YOU] Back up the user files, add the hooks, approve them in Codex**

```bash
cp ~/.claude/settings.json ~/.claude/settings.json.phase0-backup
cp ~/.codex/hooks.json ~/.codex/hooks.json.phase0-backup
cp ~/.codex/config.toml ~/.codex/config.toml.phase0-backup
python3.12 ~/Desktop/src/echo-official/harness-phase0-tools/add_phase0_hooks.py
```

Then open `codex` once in `~/Desktop/src/echo-official/harness-phase0` and approve the six Phase 0 hooks when Codex asks. Your existing Codex `Stop` hook keeps position `0:0`, so its approval is untouched.

Expected: `grep -c log_hook.py ~/.claude/settings.json ~/.codex/hooks.json` prints `6` for each file.

### Task 0.3: Capture CLI payload fixtures from both agents

**Files:**
- Create: `$T/pick_fixtures.py`
- Create: `$H/tests/fixtures/claude/{SessionStart,UserPromptSubmit,Stop,SubagentStart,SubagentStop,SessionEnd}.json`
- Create: `$H/tests/fixtures/codex/` (the same six names)

Spec: §12 adapter contract ("captured in Phase 0 from throwaway sessions"), §16 field list.

- [ ] **Step 1: [YOU] Run one Claude and one Codex session that each spawn a helper** (each `codex exec` also writes a trust entry to `~/.codex/config.toml`; Task 0.6 removes it)

```bash
cd ~/Desktop/src/echo-official/harness-phase0
claude -p "Use the Task tool to start one general-purpose subagent that runs 'echo hi' and reports back. Then reply DONE." --allowedTools "Task" "Bash(echo:*)" < /dev/null
codex exec -s danger-full-access "Spawn one helper agent that runs 'echo hi' and reports back. Wait for it, then reply DONE." < /dev/null
ls ~/Desktop/src/echo-official/harness-phase0-tools/captures | sed 's/-[0-9]*\.json$//' | sort | uniq -c
```

Expected: at least one capture for each of the 12 (agent, event) pairs. If a pair is missing, rerun that agent once; if it is still missing, record it in Task 0.7 as an open item and stop to ask the user before Slice 1.

- [ ] **Step 2: Write the fixture picker**

`$T/pick_fixtures.py`:

```python
"""Copy one payload per (agent, event) from the captures into the harness repo's fixtures."""
import json
import sys
from pathlib import Path

EVENTS = ["SessionStart", "UserPromptSubmit", "Stop", "SubagentStart", "SubagentStop", "SessionEnd"]
captures, dest = Path(sys.argv[1]), Path(sys.argv[2])
seen = set()
for f in sorted(captures.glob("*.json")):
    record = json.loads(f.read_text())
    key = (record["agent"], record["event"])
    if key in seen:
        continue
    seen.add(key)
    out = dest / record["agent"] / f"{record['event']}.json"
    out.write_text(json.dumps(record["payload"], indent=2, sort_keys=True) + "\n")
    print(out, sorted(record["payload"]))
print("missing:", [(a, e) for a in ("claude", "codex") for e in EVENTS if (a, e) not in seen])
```

- [ ] **Step 3: Copy the fixtures and check their fields against spec §16**

```bash
python3.12 ~/Desktop/src/echo-official/harness-phase0-tools/pick_fixtures.py \
  ~/Desktop/src/echo-official/harness-phase0-tools/captures ~/Desktop/src/echo-official/lean-harness/tests/fixtures
```

Expected: `missing: []`, and these keys present (§16):

| Fixture | Must contain |
|---|---|
| every Claude and Codex fixture | `session_id`, `transcript_path`, `cwd` |
| Claude `SessionStart` | `source` |
| Claude `Stop`, `SubagentStop` | `effort` with `level` (record it if absent; the adapter treats effort as optional) |
| Claude and Codex `SubagentStart`, `SubagentStop` | `agent_id`, `agent_type`; `SubagentStop` also `agent_transcript_path` |
| Claude `SessionEnd` | `reason` |
| Codex, all but `SessionEnd` | `model`, `turn_id` (`turn_id` may be absent on `SessionStart`; record what you see) |

Write any difference into Task 0.7's notes; the Claude adapter's `REQUIRED` table (Task 1.7) must match what the fixtures carry.

- [ ] **Step 4: Commit the fixtures**

```bash
cd ~/Desktop/src/echo-official/lean-harness
git rm -q tests/fixtures/claude/.gitkeep tests/fixtures/codex/.gitkeep
git add tests/fixtures && git commit -m "test: Phase 0 hook payload fixtures (Claude Code 2.1.295, Codex 0.160.0)"
git push
```

### Task 0.4: [YOU] Desktop-app sessions run the user-level hooks

Spec: §11 Phase 0, §13 first remaining unknown, R-20.

- [ ] **Step 1: [YOU] Claude desktop app (Code tab)**: open `~/Desktop/src/echo-official/harness-phase0` and send: `Run echo $PATH and command -v python3.12, show me the output, then reply OK.`
- [ ] **Step 2: [YOU] Codex app**: open the same folder with full access and send the same prompt.
- [ ] **Step 3: Check the captures**

```bash
cd ~/Desktop/src/echo-official/harness-phase0-tools/captures
ls -t | head -20
python3.12 -c "import json,glob; [print(f, json.load(open(f))['env']['PATH']) for f in sorted(glob.glob('*SessionStart*'))[-2:]]"
```

Expected: new `claude-*` and `codex-*` captures timestamped after Steps 1–2. Record for each app: hooks ran (yes/no), the hook process `PATH`, and the Bash `PATH` the agent printed, including whether it contains `~/.local/bin`.

Fallbacks: if an app runs no user-level hooks, the fallback is "launch harness tasks from that agent's CLI only" (check E would fail there anyway). If an app's Bash `PATH` lacks `~/.local/bin`, stop and ask the user before Slice 1 (it changes how the bootstrap calls `harness`).

### Task 0.5: `git hash-object -t tree` inside a sandboxed `codex exec`

**Files:**
- Create: `$T/tree_probe.py`

Spec: §6.11 (code trees computed without writing objects), §13 second remaining unknown.

- [ ] **Step 1: Write the probe**

`$T/tree_probe.py`:

```python
"""Phase 0 probe: hash HEAD's tree with `git hash-object -t tree --stdin` (no -w) and compare."""
import os
import subprocess

raw = subprocess.run(["git", "ls-tree", "-z", "HEAD"], capture_output=True, check=True).stdout
body = b""
for entry in filter(None, raw.split(b"\0")):
    meta, name = entry.split(b"\t", 1)
    mode, _kind, sha = meta.split(b" ")
    body += (b"40000" if mode == b"040000" else mode) + b" " + name + b"\0" + bytes.fromhex(sha.decode())
r = subprocess.run(["git", "hash-object", "-t", "tree", "--stdin"], input=body, capture_output=True)
expected = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True, text=True).stdout.strip()
print("sandbox:", os.environ.get("CODEX_SANDBOX"), "rc:", r.returncode, "stderr:", r.stderr.decode().strip())
print("MATCH" if r.stdout.decode().strip() == expected else "MISMATCH")
```

- [ ] **Step 2: [YOU] Run it natively, then inside a sandboxed `codex exec`** (writes a trust entry to `~/.codex/config.toml`; Task 0.6 removes it)

```bash
cd ~/Desktop/src/echo-official/harness-phase0
python3.12 ../harness-phase0-tools/tree_probe.py
codex exec -s workspace-write "Run exactly this command and print its output verbatim: python3.12 $HOME/Desktop/src/echo-official/harness-phase0-tools/tree_probe.py" < /dev/null
```

Expected: native `sandbox: None rc: 0 ...` then `MATCH`; sandboxed `sandbox: seatbelt rc: 0 ...` then `MATCH`.

Fallback if the sandboxed run fails: compute the tree hash in Python (`hashlib.sha1(b"tree %d\0" % len(body) + body).hexdigest()`); Task 1.4 Step 3 then uses that line instead of the subprocess. Record the outcome in Task 0.7.

### Task 0.6: [YOU] Remove the temporary hooks and the `codex exec` trust entries

Spec: §12 ("Remove the trust entries `codex exec` adds for throwaway folders afterwards"), R-21.

- [ ] **Step 1: [YOU] Remove the hook entries**

```bash
python3.12 ~/Desktop/src/echo-official/harness-phase0-tools/remove_phase0_hooks.py
```

Expected: `cleaned` for both files, and a list of Codex approval table names.

- [ ] **Step 2: [YOU] Edit `~/.codex/config.toml`**: delete each `[hooks.state."…"]` table the script listed (two lines each: header and `trusted_hash`), and each `[projects."…harness-phase0…"]` table `codex exec` added.

- [ ] **Step 3: Verify, then [YOU] delete the backups when satisfied**

```bash
grep -c log_hook.py ~/.claude/settings.json ~/.codex/hooks.json
grep -n "harness-phase0" ~/.codex/config.toml
diff <(python3.12 -m json.tool ~/.codex/hooks.json) <(python3.12 -m json.tool ~/.codex/hooks.json.phase0-backup) && echo "codex hooks restored"
```

Expected: `0` for both files; no `harness-phase0` lines; `codex hooks restored`.

### Task 0.7: Write the Phase 0 results into the spec

**Files:**
- Modify: `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md` in `echotheorylabsai/echo-theory-plugins` (§11 Phase 0 row, §13 "Remaining" table, §16)

Spec: §11 Phase 0 exit criteria ("written into this spec").

- [ ] **Step 1: Branch from fresh `origin/main` in the plugins repo**

```bash
cd ~/Desktop/src/echo-official/echo-theory-plugins && git fetch origin
git worktree add ../echo-theory-plugins-phase0 -b claude/lean-harness-phase0-results origin/main
```

- [ ] **Step 2: Edit the spec**
  - §11 Phase 0 "Adds" cell: replace "`install --user` dry run there" with "a temporary hand-added logging hook for the user-level hook checks (removed afterwards; `install --user` is first exercised in Slice 1)".
  - §13 "Remaining" table: for the desktop-app row and the `hash-object` row, state the Phase 0 result (confirmed, or the fallback chosen) with the date.
  - §8: replace the group table with R-22's list of checks, and note the dropped ones fail loudly at use (your direction).
  - §16: add a "Phase 0 (date)" paragraph: fixture fields that differ from §16 (if any), desktop-app hook results, hook and Bash `PATH` per app, the `hash-object` result.

- [ ] **Step 3: Commit and push**

```bash
cd ~/Desktop/src/echo-official/echo-theory-plugins-phase0
git add docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md
git commit -m "docs(lean-harness): record Phase 0 results in the v0 spec"
git push -u origin claude/lean-harness-phase0-results
```

- [ ] **Step 4: [YOU] Open and merge the PR**: `gh pr create --base main --fill`, review, merge.

### Phase 0 checkpoint (spec §11)

- [ ] 12 fixtures committed in `$H/tests/fixtures/` (or the gap recorded and the user asked).
- [ ] Desktop-app hook result recorded for both apps, with the fallback where needed.
- [ ] `hash-object` result recorded; Task 1.4 uses `git hash-object` or the Python fallback accordingly.
- [ ] Temporary hooks and trust entries removed; spec PR merged.
- [ ] Do not start Slice 1 until every box is ticked.

---
## Slice 1: one measured task (Claude)

Exit criteria (spec §11): one real mvp M task merged with a complete scorecard (all boundaries present, gate evaluated, no unexplained orphans); two tasks in parallel in mvp scored correctly.

Records (§11, §6.12): every raw input in §6.12 except `tier`, `defect` and harness memory events.

### File structure (harness repo)

| Path | Kind | Responsibility | Spec |
|---|---|---|---|
| `harness/__init__.py` | core | `REPO`, `HarnessError`, `dispatcher_path` | §4.1 |
| `harness/events.py` | pure | Event schema v1: build, serialize, tolerant parse, timestamps | §6.7, §9.3 |
| `harness/identity.py` | pure | Session identity and delegate rules | §6.9 |
| `harness/planfile.py` | pure | `plan.md` sections, acceptance checks, check hash, Decisions, check diff | §5.5, §5.7, §6.5 |
| `harness/gate.py` | pure | Readiness pre-check, post-`ready` rule, done gate | §6.11 |
| `harness/resolve.py` | pure | Events → tasks (id, branch, last known branch), orphans | §6.8 |
| `harness/timing.py` | pure | Wall time (revisions, excluded gaps), agent time, per phase | §6.10 |
| `harness/scorecard.py` | pure | Per-task card and summary | §10 |
| `harness/spool.py` | edge | State dir paths, lock, one-line appends, reads | §6.6, §9.3 |
| `harness/gitio.py` | edge | Every git subprocess: info, code tree, fetch retry, push, rebase state | §6.11, §9.4 |
| `harness/ghio.py` | edge | Every `gh` subprocess | §7 `pr`, §8 D |
| `harness/taskfiles.py` | edge | Task folder paths, `state.json`/`config.json`, task lookup by branch, state-dir copies | §6.1–6.4, §6.6 |
| `harness/context.py` | edge | Per-invocation context; builds and records CLI events | §6.7, §6.9 |
| `harness/doctor.py` | edge | Silent-failure probes and runner; agent probes come from adapters | §8, R-22 |
| `harness/cli.py` | edge | Dispatch table and its two guards | §7, §9.5, §9.7 |
| `harness/commands/{hook,install,doctor,start,phase,check,rebase,pr,close,score}.py` | edge | One file per CLI command | §7 |
| `harness/adapters/__init__.py` | — | Adapter registry dict | §15 |
| `harness/adapters/claude.py` | edge | Claude identity var, payload → event, §6.9 markers, user install, doctor probes | §4.3, §6.9, §8 B |
| `bin/harness` | — | Dispatcher template (`@PYTHON@`, `@HARNESS_REPO@`) | §4.1 |
| `hooks/bootstrap.md` | — | The fixed bootstrap text | §4.4 |
| `AGENTS.md`, `skills/phases/{triage,research,resolve,plan,build,verify}.md` | — | Map and Slice 1 phase files | §4.2, §5.2 |
| `tests/helpers.py` | test | Temp repos, CLI runner, `Sandbox` (fake HOME, bare remote, stub `gh`) | §12 |
| `tests/test_*.py` | test | Unit, integration, adapter contract | §12 |

Import rule: pure modules import only other pure modules and the standard library. Edge modules may import pure ones, never the reverse.

### Task 1.1: Package skeleton and event schema

**Files:**
- Create: `harness/__init__.py`, `harness/events.py`, `tests/__init__.py` (empty), `tests/test_events.py`

**Interfaces:**
- Produces: `harness.REPO: Path`; `harness.HarnessError(Exception)`; `harness.dispatcher_path(home: Path) -> Path`; `events.COMMON: tuple[str, ...]`; `events.KINDS: dict[str, tuple[str, ...]]`; `events.SPOOL_ONLY: frozenset[str]`; `events.make(kind: str, source: str, ts: str, **fields) -> dict`; `events.dumps(event: dict) -> str`; `events.parse_lines(text: str) -> list[dict]`; `events.now_ts() -> str`; `events.ts_ms(ts: str) -> int`; `events.ts_from_ms(ms: int) -> str`

Spec: §6.7 (schema), §9.3 (readers ignore an incomplete last line), design rule "readers tolerate unknown and missing optional fields".

- [ ] **Step 1: Write the failing tests**

`tests/test_events.py`:

```python
import unittest

from harness import events

TS = "2026-10-08T12:00:00.000Z"


class EventsTest(unittest.TestCase):
    def test_make_fills_every_common_and_kind_field(self):
        e = events.make("check", "cli", TS, check_id="C1", result="pass")
        for name in events.COMMON + events.KINDS["check"]:
            self.assertIn(name, e)
        self.assertEqual((e["v"], e["kind"], e["source"], e["check_id"], e["model"]),
                         (1, "check", "cli", "C1", None))

    def test_make_rejects_unknown_kind_unknown_field_and_writer_fields(self):
        with self.assertRaises(ValueError):
            events.make("nope", "cli", TS)
        with self.assertRaises(ValueError):
            events.make("resume", "cli", TS, check_id="C1")
        with self.assertRaises(ValueError):
            events.make("resume", "cli", TS, kind="phase")

    def test_parse_lines_skips_incomplete_last_line_and_keeps_unknown_fields(self):
        good = events.dumps({**events.make("resume", "cli", TS), "future_field": 1})
        parsed = events.parse_lines(good + good[: len(good) // 2])
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["future_field"], 1)

    def test_parse_lines_tolerates_missing_optional_fields(self):
        parsed = events.parse_lines('{"kind":"stop","ts":"2026-10-08T12:00:00.000Z"}\n')
        self.assertIsNone(parsed[0].get("session_id"))

    def test_timestamps_round_trip_at_millisecond_precision(self):
        self.assertEqual(events.ts_ms(events.ts_from_ms(1791460800123)), 1791460800123)
        self.assertRegex(events.now_ts(), r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")

    def test_spool_only_kinds_match_the_spec(self):
        self.assertEqual(events.SPOOL_ONLY,
                         {"start", "resume", "tier", "close", "defect", "memory", "doctor"})
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_events -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'harness'`.

- [ ] **Step 3: Write the implementation**

`harness/__init__.py`:

```python
"""Lean Harness v0: a measured, tiered workflow for coding agents."""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class HarnessError(Exception):
    """A refusal or failure; the CLI prints it as `harness: <message>` and exits 1."""


def dispatcher_path(home: Path) -> Path:
    """Where `harness install --user` puts the `harness` command (spec §4.1)."""
    return home / ".local" / "bin" / "harness"
```

`harness/events.py`:

```python
"""Event schema v1: build, serialize and tolerantly read events (spec §6.7). Pure."""
import json
import time
from datetime import datetime, timezone

SCHEMA_VERSION = 1

COMMON = (
    "v", "ts", "kind", "source", "agent", "session_id", "agent_id", "agent_type",
    "parent_session", "task_id", "branch", "head", "cwd", "git_common_dir",
    "model", "effort", "transcript_path", "agent_transcript_path", "harness_version",
)
WRITER_FIELDS = ("v", "ts", "kind", "source")

KINDS = {
    "session_start": ("trigger",),
    "prompt": ("prompt_id", "turn_id"),
    "stop": ("turn_id",),
    "subagent_start": (),
    "subagent_stop": (),
    "session_end": ("reason",),
    "start": ("benchmark_tier", "request_sha256", "arm", "assigned_commit"),
    "resume": (),
    "phase": ("phase", "action", "handoff", "controlling_session"),
    "check": ("check_id", "result", "mode", "code_tree", "check_text_hash",
              "exit_code", "duration_ms", "delegate"),
    "review": ("action",),
    "ready": ("tip_commit", "code_tree"),
    "pr": ("number", "url"),
    "tier": ("tier", "origin_tier"),
    "close": ("disposition",),
    "defect": ("defect_id", "text", "resolved"),
    "memory": ("area", "lesson_id", "action"),
    "doctor": ("checks",),
    "format_warning": ("adapter", "event", "missing"),
}

# CLI kinds that go to the spool only; every other CLI kind also goes to the task's events.jsonl.
# Hook events always go to the spool only.
SPOOL_ONLY = frozenset({"start", "resume", "tier", "close", "defect", "memory", "doctor"})


def ts_from_ms(ms: int) -> str:
    dt = datetime.fromtimestamp(ms // 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ms % 1000:03d}Z"


def now_ts() -> str:
    return ts_from_ms(time.time_ns() // 1_000_000)


def ts_ms(ts: str) -> int:
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    return int(dt.timestamp()) * 1000 + dt.microsecond // 1000


def make(kind: str, source: str, ts: str, **fields) -> dict:
    """A complete event: every common and kind field present, null when not observable."""
    if kind not in KINDS:
        raise ValueError(f"unknown event kind: {kind}")
    allowed = (set(COMMON) - set(WRITER_FIELDS)) | set(KINDS[kind])
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"unknown fields for {kind}: {sorted(unknown)}")
    event = {name: None for name in (*COMMON, *KINDS[kind])}
    event.update(fields)
    event.update(v=SCHEMA_VERSION, ts=ts, kind=kind, source=source)
    return event


def dumps(event: dict) -> str:
    return json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"


def parse_lines(text: str) -> list[dict]:
    """Parse JSONL, skipping malformed lines (an incomplete last line included) (spec §9.3)."""
    out = []
    for line in text.split("\n"):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "kind" in obj and "ts" in obj:
            out.append(obj)
    return out
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_events -v`
Expected: 6 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/__init__.py harness/events.py tests/__init__.py tests/test_events.py
git commit -m "feat: event schema v1"
```

### Task 1.2: Spool

**Files:**
- Create: `harness/spool.py`, `tests/test_spool.py`

**Interfaces:**
- Consumes: `events.dumps`, `events.parse_lines`, `HarnessError`
- Produces: `spool.FIX: str`; `spool.state_root(env: Mapping[str, str]) -> Path`; `spool.project_hash(git_common_dir: str) -> str`; `spool.project_dir(env, git_common_dir: str) -> Path`; `spool.locked(state_dir: Path)` (context manager); `spool.append(state_dir: Path, event: dict, task_events: Path | None = None, *, held: bool = False) -> None`; `spool.read(state_dir: Path) -> list[dict]`; `spool.read_file(path: Path) -> list[dict]`

Spec: §4.1 (state dir, project hash), §6.6, §7 last paragraph (fail loudly with the fix), §9.3.

- [ ] **Step 1: Write the failing tests**

`tests/test_spool.py`:

```python
import hashlib
import multiprocessing
import tempfile
import unittest
from pathlib import Path

from harness import HarnessError, events, spool


def _writer(state_dir: str, n: int, tag: int) -> None:
    for i in range(n):
        spool.append(Path(state_dir), events.make("resume", "cli", events.now_ts(), task_id=f"{tag}-{i}"))


class SpoolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_project_hash_is_first_16_hex_of_sha256(self):
        self.assertEqual(spool.project_hash("/x/.git"), hashlib.sha256(b"/x/.git").hexdigest()[:16])

    def test_state_root_honors_xdg_state_home(self):
        self.assertEqual(spool.state_root({"XDG_STATE_HOME": "/s", "HOME": "/h"}), Path("/s/harness"))
        self.assertEqual(spool.state_root({"HOME": "/h"}), Path("/h/.local/state/harness"))

    def test_parallel_appends_never_interleave(self):  # spec §9.3
        procs = [multiprocessing.Process(target=_writer, args=(str(self.tmp), 200, t)) for t in range(8)]
        for p in procs:
            p.start()
        for p in procs:
            p.join()
        self.assertEqual(len((self.tmp / "spool.jsonl").read_text().splitlines()), 1600)
        self.assertEqual(len(spool.read(self.tmp)), 1600)

    def test_append_writes_task_file_and_spool_under_one_lock(self):
        task_file = self.tmp / "task" / "events.jsonl"
        task_file.parent.mkdir()
        spool.append(self.tmp, events.make("check", "cli", events.now_ts()), task_file)
        self.assertEqual(len(spool.read_file(task_file)), 1)
        self.assertEqual(len(spool.read(self.tmp)), 1)

    def test_unwritable_state_dir_fails_loudly_with_fix(self):  # spec §7, §9.6
        ro = self.tmp / "ro"
        ro.mkdir()
        ro.chmod(0o500)
        self.addCleanup(ro.chmod, 0o700)
        with self.assertRaisesRegex(HarnessError, "install --user"):
            spool.append(ro / "project", events.make("resume", "cli", events.now_ts()))
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_spool -v`
Expected: FAIL with `ImportError: cannot import name 'spool'`.

- [ ] **Step 3: Write the implementation**

`harness/spool.py`:

```python
"""Per-machine spool: state dir, exclusive lock, one-line appends (spec §6.6, §9.3). Edge."""
import fcntl
import hashlib
import os
from collections.abc import Mapping
from contextlib import contextmanager, nullcontext
from pathlib import Path

from harness import HarnessError, events

FIX = "Fix: run `harness install --user`, or relaunch Codex with full access."


def state_root(env: Mapping[str, str]) -> Path:
    base = env.get("XDG_STATE_HOME") or str(Path(env.get("HOME") or Path.home()) / ".local" / "state")
    return Path(base) / "harness"


def project_hash(git_common_dir: str) -> str:
    return hashlib.sha256(git_common_dir.encode()).hexdigest()[:16]


def project_dir(env: Mapping[str, str], git_common_dir: str) -> Path:
    return state_root(env) / project_hash(git_common_dir)


@contextmanager
def locked(state_dir: Path):
    """Hold the spool's exclusive lock (spec §9.3)."""
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
        fd = os.open(state_dir / "spool.lock", os.O_RDWR | os.O_CREAT, 0o644)
    except OSError as e:
        raise HarnessError(f"cannot open the spool lock in {state_dir}: {e}. {FIX}") from e
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)  # closing the descriptor releases the lock


def append(state_dir: Path, event: dict, task_events: Path | None = None, *, held: bool = False) -> None:
    """Append one complete line to the spool, and to the task's events.jsonl when given."""
    line = events.dumps(event).encode()
    with nullcontext() if held else locked(state_dir):
        for path in [state_dir / "spool.jsonl", *([task_events] if task_events else [])]:
            try:
                fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
                try:
                    os.write(fd, line)
                finally:
                    os.close(fd)
            except OSError as e:
                raise HarnessError(f"cannot append to {path}: {e}. {FIX}") from e


def read_file(path: Path) -> list[dict]:
    return events.parse_lines(path.read_text()) if path.exists() else []


def read(state_dir: Path) -> list[dict]:
    return read_file(state_dir / "spool.jsonl")
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_spool -v`
Expected: 5 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/spool.py tests/test_spool.py
git commit -m "feat: spool with exclusive lock and one-line appends"
```

### Task 1.3: Identity and delegates

**Files:**
- Create: `harness/identity.py`, `tests/test_identity.py`

**Interfaces:**
- Produces: `identity.PARENT_VAR = "HARNESS_PARENT_SESSION"`; `identity.TASK_VAR = "HARNESS_TASK_ID"`; `identity.Identity(session_id: str | None, agent: str | None, parent_session: str | None, delegate: bool)` (frozen dataclass); `identity.AmbiguousIdentity(Exception)`; `identity.resolve(env: Mapping[str, str], identity_vars: Mapping[str, str]) -> Identity` (`identity_vars` maps agent name → its identity variable)

Spec: §6.9 (identity in commands, delegates), C5, C10.

- [ ] **Step 1: Write the failing tests**

`tests/test_identity.py`:

```python
import unittest

from harness.identity import AmbiguousIdentity, Identity, resolve

# Two adapters, so the cross-agent rules are tested even before the Codex adapter exists (Slice 2).
VARS = {"claude": "HARNESS_SESSION_ID", "codex": "CODEX_THREAD_ID"}


class IdentityTest(unittest.TestCase):
    def check(self, env, expected):
        self.assertEqual(resolve(env, VARS), expected)

    def test_no_identity_is_a_manual_command(self):
        self.check({}, Identity(None, None, None, False))

    def test_top_claude_session(self):
        self.check({"HARNESS_SESSION_ID": "S", "HARNESS_PARENT_SESSION": "S"}, Identity("S", "claude", "S", False))

    def test_top_codex_session(self):
        self.check({"CODEX_THREAD_ID": "T"}, Identity("T", "codex", None, False))

    def test_codex_launched_by_claude_is_a_delegate(self):
        self.check({"HARNESS_SESSION_ID": "P", "HARNESS_PARENT_SESSION": "P", "CODEX_THREAD_ID": "T"},
                   Identity("T", "codex", "P", True))

    def test_claude_launched_by_codex_is_a_delegate(self):
        self.check({"CODEX_THREAD_ID": "P", "HARNESS_PARENT_SESSION": "P", "HARNESS_SESSION_ID": "C"},
                   Identity("C", "claude", "P", True))

    def test_claude_launched_by_claude_is_a_delegate(self):
        self.check({"HARNESS_SESSION_ID": "C", "HARNESS_PARENT_SESSION": "P"}, Identity("C", "claude", "P", True))

    def test_disagreeing_ids_without_parent_are_ambiguous(self):
        with self.assertRaises(AmbiguousIdentity):
            resolve({"HARNESS_SESSION_ID": "A", "CODEX_THREAD_ID": "B"}, VARS)

    def test_two_ids_differing_from_parent_are_ambiguous(self):
        with self.assertRaises(AmbiguousIdentity):
            resolve({"HARNESS_SESSION_ID": "A", "CODEX_THREAD_ID": "B", "HARNESS_PARENT_SESSION": "P"}, VARS)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_identity -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'harness.identity'`.

- [ ] **Step 3: Write the implementation**

`harness/identity.py`:

```python
"""Session identity and delegate detection from environment variables (spec §6.9). Pure."""
from collections.abc import Mapping
from dataclasses import dataclass

PARENT_VAR = "HARNESS_PARENT_SESSION"
TASK_VAR = "HARNESS_TASK_ID"


@dataclass(frozen=True)
class Identity:
    session_id: str | None
    agent: str | None
    parent_session: str | None
    delegate: bool


class AmbiguousIdentity(Exception):
    pass


def resolve(env: Mapping[str, str], identity_vars: Mapping[str, str]) -> Identity:
    """identity_vars maps each adapter's agent name to its identity variable."""
    found = {agent: env[var] for agent, var in identity_vars.items() if env.get(var)}
    parent = env.get(PARENT_VAR) or None
    if parent:
        differing = {agent: sid for agent, sid in found.items() if sid != parent}
        if len(differing) > 1:
            raise AmbiguousIdentity(f"several identity variables differ from {PARENT_VAR}: {differing}")
        if differing:
            (agent, sid), = differing.items()
            return Identity(sid, agent, parent, True)
        if found:
            return Identity(parent, next(iter(found)), parent, False)
        return Identity(None, None, parent, False)
    if len(set(found.values())) > 1:
        raise AmbiguousIdentity(f"identity variables disagree and {PARENT_VAR} is unset: {found}")
    if not found:
        return Identity(None, None, None, False)
    agent, sid = next(iter(found.items()))
    return Identity(sid, agent, None, False)
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_identity -v`
Expected: 8 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/identity.py tests/test_identity.py
git commit -m "feat: identity and delegate rules"
```

### Task 1.4: Git edge

**Files:**
- Create: `harness/gitio.py`, `tests/helpers.py`, `tests/test_gitio.py`

**Interfaces:**
- Consumes: `REPO`, `HarnessError`
- Produces (all in `gitio`): `run(args: list[str], cwd, *, input=None, env=None, check=True, binary=False, capture=True) -> CompletedProcess`; `out(args, cwd, **kw) -> str`; `GitInfo(toplevel: Path, common_dir: str, branch: str | None, head: str | None)`; `info(cwd) -> GitInfo | None`; `git_path(cwd, name) -> Path`; `rebase_in_progress(cwd) -> bool`; `effective_branch(cwd, git: GitInfo) -> tuple[str | None, str | None]` (branch, revision to read task files from, or None for the working tree); `code_tree(cwd, rev="HEAD") -> str`; `status_clean(cwd) -> bool`; `dirty_outside_harness(cwd) -> list[str]`; `fetch(cwd, remote, branch, attempts=6, sleep=time.sleep) -> None`; `show(cwd, rev, path) -> str | None`; `exists_at(cwd, rev, path) -> bool`; `ls_dir(cwd, rev, path) -> list[str]`; `last_change(cwd, ref, path) -> str | None`; `commit_ms(cwd, sha) -> int`; `commit_paths(cwd, path, message) -> bool`; `push(cwd, remote, branch) -> None`; `remote_default_branch(cwd, remote) -> str`; `remote_branch_exists(cwd, remote, branch) -> bool`; `harness_version() -> str | None`
- Produces (in `tests/helpers.py`): `sh(*args, cwd, env=None, check=True, input=None) -> CompletedProcess`; `git(cwd, *args, env=None) -> str`; `init_repo(path: Path) -> Path`; `GIT_ENV: dict[str, str]`

Spec: §6.11 (code tree: the commit's tree with `.harness/` removed, computed without writing objects; merge commit = last first-parent commit on the integration branch that changed the task folder), §9.4 (fetch retry), §7 `pr` (push flags, R-14), R-7 (branch during a stopped rebase), R-17.

- [ ] **Step 1: Write the test helpers**

`tests/helpers.py`:

```python
"""Shared test helpers: temp git repos and subprocess runners."""
import os
import subprocess
from pathlib import Path

GIT_ENV = {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@example.com",
           "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@example.com"}


def sh(*args, cwd, env=None, check=True, input=None) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), cwd=cwd, env=env or {**os.environ, **GIT_ENV}, check=check,
                          capture_output=True, text=True, input=input)


def git(cwd, *args, env=None) -> str:
    return sh("git", *args, cwd=cwd, env=env).stdout.strip()


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main")
    (path / "README.md").write_text("hello\n")
    (path / "src").mkdir()
    (path / "src" / "a.txt").write_text("a\n")
    git(path, "add", ".")
    git(path, "commit", "-qm", "init")
    return path
```

- [ ] **Step 2: Write the failing tests**

`tests/test_gitio.py`:

```python
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from harness import HarnessError, gitio
from tests.helpers import git, init_repo, sh


def _done(rc, stderr=""):
    return subprocess.CompletedProcess([], rc, "", stderr)


class GitioTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = init_repo(self.tmp / "r")

    def test_info_reports_branch_head_and_common_dir(self):
        g = gitio.info(self.repo)
        self.assertEqual(g.branch, "main")
        self.assertEqual(g.head, git(self.repo, "rev-parse", "HEAD"))
        self.assertEqual(Path(g.common_dir).resolve(), (self.repo / ".git").resolve())
        self.assertIsNone(gitio.info(self.tmp))

    def test_code_tree_equals_head_tree_without_harness_folder(self):
        self.assertEqual(gitio.code_tree(self.repo), git(self.repo, "rev-parse", "HEAD^{tree}"))

    def test_code_tree_drops_harness_and_writes_no_object(self):  # spec §6.11
        (self.repo / ".harness" / "runs" / "t").mkdir(parents=True)
        (self.repo / ".harness" / "runs" / "t" / "state.json").write_text("{}\n")
        (self.repo / "src" / "a.txt").write_text("changed\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "code and harness")
        tree = gitio.code_tree(self.repo)
        self.assertNotEqual(sh("git", "cat-file", "-e", tree, cwd=self.repo, check=False).returncode, 0)
        git(self.repo, "rm", "-rq", ".harness")
        git(self.repo, "commit", "-qm", "drop harness")
        self.assertEqual(tree, git(self.repo, "rev-parse", "HEAD^{tree}"))

    def test_dirty_outside_harness_ignores_the_harness_folder(self):
        (self.repo / ".harness").mkdir()
        (self.repo / ".harness" / "x").write_text("x")
        self.assertEqual(gitio.dirty_outside_harness(self.repo), [])
        self.assertFalse(gitio.status_clean(self.repo))
        (self.repo / "src" / "b.txt").write_text("b")
        self.assertEqual(gitio.dirty_outside_harness(self.repo), ["?? src/b.txt"])

    def test_fetch_retries_on_ref_lock_errors(self):  # spec §9.4
        lock = _done(1, "error: cannot lock ref 'refs/remotes/origin/main': is at x but expected y")
        with mock.patch.object(gitio, "run", side_effect=[lock, lock, _done(0)]) as run:
            gitio.fetch(self.repo, "origin", "main", sleep=lambda s: None)
        self.assertEqual(run.call_count, 3)
        with mock.patch.object(gitio, "run", return_value=_done(128, "fatal: no such remote")):
            with self.assertRaises(HarnessError):
                gitio.fetch(self.repo, "origin", "main", sleep=lambda s: None)

    def test_concurrent_fetches_from_worktrees_all_succeed(self):  # spec §9.4, §12
        remote = self.tmp / "remote.git"
        sh("git", "clone", "-q", "--bare", str(self.repo), str(remote), cwd=self.tmp)
        clone = self.tmp / "clone"
        sh("git", "clone", "-q", str(remote), str(clone), cwd=self.tmp)
        trees = []
        for i in range(6):
            wt = self.tmp / f"wt{i}"
            git(clone, "worktree", "add", "-q", str(wt), "-b", f"b{i}", "origin/main")
            trees.append(wt)
        for i in range(5):  # give every fetch something to update
            (self.repo / f"f{i}").write_text(str(i))
            git(self.repo, "add", ".")
            git(self.repo, "commit", "-qm", f"c{i}")
        git(self.repo, "push", "-q", str(remote), "main")
        errors = []

        def worker(path):
            try:
                gitio.fetch(path, "origin", "main")
            except HarnessError as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(wt,)) for wt in trees]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])

    def test_effective_branch_during_a_stopped_rebase(self):  # parent design, R-7
        git(self.repo, "switch", "-qc", "feature")
        (self.repo / "README.md").write_text("feature\n")
        git(self.repo, "commit", "-qam", "feature")
        tip = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "switch", "-q", "main")
        (self.repo / "README.md").write_text("main\n")
        git(self.repo, "commit", "-qam", "main")
        git(self.repo, "switch", "-q", "feature")
        sh("git", "rebase", "--merge", "main", cwd=self.repo, check=False)
        self.assertTrue(gitio.rebase_in_progress(self.repo))
        g = gitio.info(self.repo)
        self.assertIsNone(g.branch)
        self.assertEqual(gitio.effective_branch(self.repo, g), ("feature", tip))

    def test_harness_version_is_the_checkout_head(self):
        self.assertRegex(gitio.harness_version() or "", r"^[0-9a-f]{40}$")
```

- [ ] **Step 3: Write the implementation**

`harness/gitio.py`:

```python
"""Git edge: every git subprocess the harness runs (spec §6.11, §9.4). Edge."""
import functools
import random
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from harness import REPO, HarnessError

LOCK_ERRORS = ("cannot lock ref", "Unable to create", "unable to update local ref")


def run(args, cwd, *, input=None, env=None, check=True, binary=False, capture=True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, input=input, env=env, text=not binary,
                       stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE)
    if check and r.returncode != 0:
        err = r.stderr.decode(errors="replace") if binary else r.stderr
        raise HarnessError(f"git {' '.join(args)} failed: {err.strip()}")
    return r


def out(args, cwd, **kw) -> str:
    return run(args, cwd, **kw).stdout.strip()


@dataclass(frozen=True)
class GitInfo:
    toplevel: Path
    common_dir: str
    branch: str | None  # None on a detached HEAD
    head: str | None


def info(cwd) -> GitInfo | None:
    r = run(["rev-parse", "--path-format=absolute", "--show-toplevel", "--git-common-dir"], cwd, check=False)
    if r.returncode != 0:
        return None
    top, common = r.stdout.splitlines()[:2]
    sym = run(["symbolic-ref", "-q", "HEAD"], cwd, check=False).stdout.strip()
    head = run(["rev-parse", "-q", "--verify", "HEAD"], cwd, check=False).stdout.strip() or None
    branch = sym.removeprefix("refs/heads/") if sym.startswith("refs/heads/") else None
    return GitInfo(Path(top), common, branch, head)


def git_path(cwd, name: str) -> Path:
    return Path(out(["rev-parse", "--path-format=absolute", "--git-path", name], cwd))


def rebase_in_progress(cwd) -> bool:
    return git_path(cwd, "rebase-merge").is_dir() or git_path(cwd, "rebase-apply").is_dir()


def effective_branch(cwd, git: GitInfo) -> tuple[str | None, str | None]:
    """The branch, and the revision to read task files from (None: the working tree).
    During a stopped rebase: the rebase's head name and pre-rebase tip (parent design)."""
    rebase_dir = git_path(cwd, "rebase-merge")
    if git.branch is None and rebase_dir.is_dir():
        head_name = (rebase_dir / "head-name").read_text().strip()
        return head_name.removeprefix("refs/heads/"), (rebase_dir / "orig-head").read_text().strip()
    return git.branch, None


def code_tree(cwd, rev: str = "HEAD") -> str:
    """Hash of rev's tree with the top-level `.harness` entry removed; writes no objects (§6.11)."""
    raw = run(["ls-tree", "-z", rev], cwd, binary=True).stdout
    body = b""
    for entry in filter(None, raw.split(b"\0")):
        meta, name = entry.split(b"\t", 1)
        if name == b".harness":
            continue
        mode, _kind, sha = meta.split(b" ")
        body += (b"40000" if mode == b"040000" else mode) + b" " + name + b"\0" + bytes.fromhex(sha.decode())
    return run(["hash-object", "-t", "tree", "--stdin"], cwd, input=body, binary=True).stdout.decode().strip()


def status_clean(cwd) -> bool:
    return out(["status", "--porcelain", "--untracked-files=all"], cwd) == ""


def dirty_outside_harness(cwd) -> list[str]:
    """Porcelain lines for changes outside `.harness/`; cwd must be the worktree root."""
    text = run(["status", "--porcelain", "--untracked-files=all", "--", ".", ":(exclude).harness"], cwd).stdout
    return [line for line in text.splitlines() if line.strip()]


def fetch(cwd, remote: str, branch: str, attempts: int = 6, sleep=time.sleep) -> None:
    """`git fetch`, retried with backoff on ref-lock errors (spec §9.4)."""
    for i in range(attempts):
        r = run(["fetch", "-q", remote, branch], cwd, check=False)
        if r.returncode == 0:
            return
        if i == attempts - 1 or not any(m in r.stderr for m in LOCK_ERRORS):
            raise HarnessError(f"git fetch {remote} {branch} failed: {r.stderr.strip()}")
        sleep(0.25 * 2 ** i + random.uniform(0, 0.25))


def show(cwd, rev: str, path: str) -> str | None:
    r = run(["show", f"{rev}:{path}"], cwd, check=False)
    return r.stdout if r.returncode == 0 else None


def exists_at(cwd, rev: str, path: str) -> bool:
    return run(["cat-file", "-e", f"{rev}:{path}"], cwd, check=False).returncode == 0


def ls_dir(cwd, rev: str, path: str) -> list[str]:
    r = run(["ls-tree", "--name-only", f"{rev}:{path}"], cwd, check=False)
    return r.stdout.split() if r.returncode == 0 else []


def last_change(cwd, ref: str, path: str) -> str | None:
    """Last first-parent commit on ref that changed path: the task's merge commit (§6.11)."""
    return out(["log", "--first-parent", "-1", "--format=%H", ref, "--", path], cwd) or None


def commit_ms(cwd, sha: str) -> int:
    return int(out(["show", "-s", "--format=%ct", sha], cwd)) * 1000


def commit_paths(cwd, path: str, message: str) -> bool:
    """Commit everything under path (relative to the root cwd); False when nothing changed."""
    if not (Path(cwd) / path).exists():
        return False
    run(["add", "-A", "--", path], cwd)
    if run(["diff", "--cached", "--quiet", "--", path], cwd, check=False).returncode == 0:
        return False
    run(["commit", "-q", "-m", message, "--", path], cwd)
    return True


def push(cwd, remote: str, branch: str) -> None:
    """Push HEAD to the same-named remote branch; the project's pre-push hook runs (R-14, §4.6)."""
    run(["push", "--force-with-lease", "--set-upstream", remote, f"HEAD:refs/heads/{branch}"], cwd, capture=False)


def remote_default_branch(cwd, remote: str) -> str:
    for line in out(["ls-remote", "--symref", remote, "HEAD"], cwd).splitlines():
        if line.startswith("ref: refs/heads/"):
            return line.split()[1].removeprefix("refs/heads/")
    raise HarnessError(f"cannot resolve the default branch of {remote}")


def remote_branch_exists(cwd, remote: str, branch: str) -> bool:
    return out(["ls-remote", "--heads", remote, f"refs/heads/{branch}"], cwd) != ""


@functools.cache
def harness_version() -> str | None:
    """The harness checkout's HEAD: the installed CLI commit (R-17)."""
    return run(["rev-parse", "HEAD"], REPO, check=False).stdout.strip() or None
```

If Phase 0 chose the Python fallback for tree hashing (Task 0.5), replace the last line of `code_tree` with `return hashlib.sha1(b"tree %d\0" % len(body) + body).hexdigest()` and add `import hashlib`.

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_gitio -v`
Expected: 8 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/gitio.py tests/helpers.py tests/test_gitio.py
git commit -m "feat: git edge with code-tree hashing and fetch retry"
```

### Task 1.5: `plan.md` parsing

**Files:**
- Create: `harness/planfile.py`, `tests/test_planfile.py`

**Interfaces:**
- Produces: `planfile.sections(text) -> dict[str, str]`; `planfile.Check(id: str, text: str, command: str | None, observational: bool)` (frozen); `planfile.checks(text) -> dict[str, Check]` (in file order); `planfile.check_hash(check: Check) -> str`; `planfile.goal(text) -> str`; `planfile.decision_refs(text) -> set[str]`; `planfile.CheckDiff(added, dropped, rewritten: tuple[str, ...], goal_changed: bool)` with `.changed() -> set[str]` and `.scope_reductions() -> tuple[str, ...]`; `planfile.diff(approved: str, final: str) -> CheckDiff`

Spec: §5.5 (note template, `Check:` on Decisions), §5.7 (numbered checks, one fenced command, hash covers the whole entry, observational checks say so), §6.5 (section order), §6.11 (checks added, dropped or rewritten since approval need a Decision), parent (scope reduction = deleted or rewritten approved check, or changed goal).

- [ ] **Step 1: Write the failing tests**

`tests/test_planfile.py`:

````python
import unittest

from harness import planfile

PLAN = """# 2026-10-08-demo

## Goal
Add a greeting.

## Outcome
`greeting.txt` says hi.

## Acceptance checks

### C1 — greeting file says hi
Expected: exit 0.
```sh
grep -q hi greeting.txt
```

### C2 — page shows the greeting (observational)
Expected: the page shows hi.

## Tier
M

## Source
prompt

## Decisions
- 2026-10-08 12:00 · Claude/Opus 5.5 · plan — Dropped C3. Why: duplicate of C1. [Check: C3]
"""


class PlanfileTest(unittest.TestCase):
    def test_sections_in_order(self):
        self.assertEqual(list(planfile.sections(PLAN)),
                         ["Goal", "Outcome", "Acceptance checks", "Tier", "Source", "Decisions"])
        self.assertEqual(planfile.goal(PLAN), "Add a greeting.")

    def test_checks_parse_command_and_observational(self):
        checks = planfile.checks(PLAN)
        self.assertEqual(list(checks), ["C1", "C2"])
        self.assertEqual(checks["C1"].command, "grep -q hi greeting.txt\n")
        self.assertFalse(checks["C1"].observational)
        self.assertIsNone(checks["C2"].command)
        self.assertTrue(checks["C2"].observational)

    def test_hash_covers_the_whole_entry_but_not_trailing_spaces(self):
        h = planfile.check_hash(planfile.checks(PLAN)["C1"])
        self.assertEqual(h, planfile.check_hash(planfile.checks(PLAN.replace("exit 0.", "exit 0.   "))["C1"]))
        self.assertNotEqual(h, planfile.check_hash(planfile.checks(PLAN.replace("exit 0.", "exit zero."))["C1"]))

    def test_decision_refs(self):
        self.assertEqual(planfile.decision_refs(PLAN), {"C3"})
        self.assertEqual(planfile.decision_refs(PLAN + "- x · y · plan — New goal. Why: z. [Check: goal]\n"),
                         {"C3", "goal"})

    def test_diff_finds_added_dropped_rewritten_and_goal(self):
        approved = PLAN.replace("### C2", "### C3 — old check\nExpected: x.\n```sh\ntrue\n```\n\n### C2")
        final = PLAN.replace("exit 0.", "exit zero.").replace("Add a greeting.", "Add a louder greeting.")
        final = final.replace("## Tier", "### C4 — new\nExpected: y.\n```sh\ntrue\n```\n\n## Tier")
        d = planfile.diff(approved, final)
        self.assertEqual((d.added, d.dropped, d.rewritten, d.goal_changed), (("C4",), ("C3",), ("C1",), True))
        self.assertEqual(d.changed(), {"C1", "C3", "C4", "goal"})
        self.assertEqual(d.scope_reductions(), ("C1", "C3", "goal"))
````

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_planfile -v`
Expected: FAIL with `ImportError: cannot import name 'planfile'`.

- [ ] **Step 3: Write the implementation**

`harness/planfile.py`:

```python
"""plan.md parsing: sections, acceptance checks, Decisions (spec §5.5, §5.7, §6.5). Pure."""
import hashlib
import re
from dataclasses import dataclass

SECTION_RE = re.compile(r"^## +(.+?)\s*$", re.M)
CHECK_RE = re.compile(r"^### +(C\d+)\b.*$", re.M)
FENCE_RE = re.compile(r"^```[^\n]*\n(.*?)^```[ \t]*$", re.M | re.S)
DECISION_CHECK_RE = re.compile(r"\bCheck:\s*(C\d+|goal)\b")


def _split(text: str, pattern: re.Pattern) -> list[tuple[re.Match, str]]:
    matches = list(pattern.finditer(text))
    return [(m, text[m.start(): matches[i + 1].start() if i + 1 < len(matches) else len(text)])
            for i, m in enumerate(matches)]


def sections(text: str) -> dict[str, str]:
    return {m.group(1): chunk[m.end() - m.start():].strip("\n") for m, chunk in _split(text, SECTION_RE)}


@dataclass(frozen=True)
class Check:
    id: str
    text: str  # the whole entry, trailing whitespace removed
    command: str | None
    observational: bool


def _normalize(entry: str) -> str:
    return "\n".join(line.rstrip() for line in entry.strip().splitlines())


def checks(text: str) -> dict[str, Check]:
    out = {}
    for m, chunk in _split(sections(text).get("Acceptance checks", ""), CHECK_RE):
        entry = _normalize(chunk)
        fence = FENCE_RE.search(entry)
        out[m.group(1)] = Check(m.group(1), entry, fence.group(1) if fence else None,
                                "(observational)" in m.group(0).lower())
    return out


def check_hash(check: Check) -> str:
    return hashlib.sha256(check.text.encode()).hexdigest()


def goal(text: str) -> str:
    return sections(text).get("Goal", "").strip()


def decision_refs(text: str) -> set[str]:
    return set(DECISION_CHECK_RE.findall(sections(text).get("Decisions", "")))


@dataclass(frozen=True)
class CheckDiff:
    added: tuple[str, ...]
    dropped: tuple[str, ...]
    rewritten: tuple[str, ...]
    goal_changed: bool

    def changed(self) -> set[str]:
        return {*self.added, *self.dropped, *self.rewritten, *(("goal",) if self.goal_changed else ())}

    def scope_reductions(self) -> tuple[str, ...]:
        """Dropped or rewritten approved checks and a changed goal (parent design)."""
        return tuple(sorted({*self.dropped, *self.rewritten})) + (("goal",) if self.goal_changed else ())


def diff(approved: str, final: str) -> CheckDiff:
    a, f = checks(approved), checks(final)
    return CheckDiff(
        added=tuple(sorted(set(f) - set(a))),
        dropped=tuple(sorted(set(a) - set(f))),
        rewritten=tuple(sorted(i for i in set(a) & set(f) if check_hash(a[i]) != check_hash(f[i]))),
        goal_changed=goal(approved) != goal(final),
    )
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_planfile -v`
Expected: 5 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/planfile.py tests/test_planfile.py
git commit -m "feat: plan.md parsing and check diff"
```

### Task 1.6: Task files

**Files:**
- Create: `harness/taskfiles.py`, `tests/test_taskfiles.py`

**Interfaces:**
- Consumes: `gitio.effective_branch`, `gitio.ls_dir`, `gitio.show`, `identity.TASK_VAR`
- Produces: `taskfiles.RUNS = ".harness/runs"`; `taskfiles.GITATTRIBUTES_LINE`; `task_dir(root: Path, task_id: str) -> Path`; `load_project(root: Path) -> dict | None`; `read_json(path) -> dict`; `write_json(path, data) -> None`; `find_by_branch(root, branch, rev=None) -> list[str]`; `resolve(root, cwd, env, git: GitInfo, explicit: str | None = None) -> str`; `copy_to_state(folder: Path, dest: Path) -> list[str]`

Spec: §6.1, §6.4, §6.6 (`tasks/<task-id>/` copies), §9.2 (`task_dir` is the only task-folder path constructor), R-7.

- [ ] **Step 1: Write the failing tests**

`tests/test_taskfiles.py`:

```python
import tempfile
import unittest
from pathlib import Path

from harness import HarnessError, gitio, taskfiles
from tests.helpers import git, init_repo


class TaskfilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = init_repo(self.tmp / "r")
        git(self.repo, "switch", "-qc", "feat")
        self.folder = taskfiles.task_dir(self.repo, "2026-10-08-x")
        self.folder.mkdir(parents=True)
        taskfiles.write_json(self.folder / "state.json", {"task_id": "2026-10-08-x", "branch": "feat"})

    def test_task_dir_layout(self):
        self.assertEqual(self.folder, self.repo / ".harness" / "runs" / "2026-10-08-x")

    def test_find_by_branch_in_working_tree_and_at_a_revision(self):
        self.assertEqual(taskfiles.find_by_branch(self.repo, "feat"), ["2026-10-08-x"])
        self.assertEqual(taskfiles.find_by_branch(self.repo, "other"), [])
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "task")
        rev = git(self.repo, "rev-parse", "HEAD")
        (self.folder / "state.json").unlink()
        self.assertEqual(taskfiles.find_by_branch(self.repo, "feat", rev), ["2026-10-08-x"])

    def test_resolve_order_explicit_env_branch(self):
        g = gitio.info(self.repo)
        self.assertEqual(taskfiles.resolve(self.repo, self.repo, {}, g, explicit="E"), "E")
        self.assertEqual(taskfiles.resolve(self.repo, self.repo, {"HARNESS_TASK_ID": "V"}, g), "V")
        self.assertEqual(taskfiles.resolve(self.repo, self.repo, {}, g), "2026-10-08-x")
        git(self.repo, "switch", "-qc", "none")
        with self.assertRaisesRegex(HarnessError, "found 0"):
            taskfiles.resolve(self.repo, self.repo, {}, gitio.info(self.repo))

    def test_copy_to_state_copies_what_exists(self):
        (self.folder / "request.md").write_text("do it\n")
        dest = self.tmp / "state" / "tasks" / "2026-10-08-x"
        self.assertEqual(taskfiles.copy_to_state(self.folder, dest), ["request.md"])
        self.assertEqual((dest / "request.md").read_text(), "do it\n")
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_taskfiles -v`
Expected: FAIL with `ImportError: cannot import name 'taskfiles'`.

- [ ] **Step 3: Write the implementation**

`harness/taskfiles.py`:

```python
"""Task folder files in the project checkout (spec §6.1–6.4, §6.6). Edge."""
import json
import shutil
from collections.abc import Mapping
from pathlib import Path

from harness import HarnessError, gitio
from harness.identity import TASK_VAR

RUNS = ".harness/runs"
GITATTRIBUTES_LINE = ".harness/memory/*.md merge=union"


def task_dir(root: Path, task_id: str) -> Path:
    """The only constructor of task folder paths, so parallel tasks write disjoint folders (§9.2)."""
    return Path(root) / RUNS / task_id


def load_project(root: Path) -> dict | None:
    path = Path(root) / ".harness" / "project.json"
    return json.loads(path.read_text()) if path.exists() else None


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def write_json(path: Path, data: dict) -> None:
    Path(path).write_text(json.dumps(data, indent=2) + "\n")


def find_by_branch(root: Path, branch: str, rev: str | None = None) -> list[str]:
    """Task ids whose state.json names branch: in the working tree, or at rev (during a rebase)."""
    ids = []
    if rev is None:
        for path in sorted((Path(root) / RUNS).glob("*/state.json")):
            if read_json(path).get("branch") == branch:
                ids.append(path.parent.name)
        return ids
    for name in gitio.ls_dir(root, rev, RUNS):
        text = gitio.show(root, rev, f"{RUNS}/{name}/state.json")
        if text and json.loads(text).get("branch") == branch:
            ids.append(name)
    return ids


def resolve(root: Path, cwd: Path, env: Mapping[str, str], git: gitio.GitInfo, explicit: str | None = None) -> str:
    """Task id from an explicit id, else HARNESS_TASK_ID, else the branch (R-7)."""
    if explicit:
        return explicit
    if env.get(TASK_VAR):
        return env[TASK_VAR]
    branch, rev = gitio.effective_branch(cwd, git)
    ids = find_by_branch(root, branch, rev) if branch else []
    if len(ids) != 1:
        raise HarnessError(f"expected one task for branch {branch!r}, found {len(ids)}; pass the task id")
    return ids[0]


def copy_to_state(folder: Path, dest: Path) -> list[str]:
    """Copy request.md and config.json to the state dir (spec §6.6); returns the names copied."""
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in ("request.md", "config.json"):
        if (folder / name).exists():
            shutil.copy2(folder / name, dest / name)
            copied.append(name)
    return copied
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_taskfiles -v`
Expected: 4 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/taskfiles.py tests/test_taskfiles.py
git commit -m "feat: task folder files and task lookup"
```

### Task 1.7: Claude adapter, registry and bootstrap text

**Files:**
- Create: `harness/adapters/__init__.py`, `harness/adapters/claude.py`, `hooks/bootstrap.md`, `tests/test_adapter_claude.py`

**Interfaces:**
- Consumes: `REPO`, `identity.PARENT_VAR`, `identity.TASK_VAR`; fixtures from Task 0.3
- Produces: `adapters.REGISTRY: dict[str, module]`; `adapters.identity_vars() -> dict[str, str]`; `adapters.foreign_vars(name: str) -> list[str]`. Every adapter module defines: `NAME: str`; `IDENTITY_VAR: str`; `HOOK_EVENTS: dict[str, str]` (hook event → event kind); `to_event(hook_event: str, payload: dict, env: Mapping, foreign_vars: list[str]) -> tuple[dict, list[str]]` (fields including `kind`, without git fields; and the missing-field list); `on_event(hook_event, payload, env, lookup_task: Callable[[], str | None], foreign_vars) -> None`; `install_user(home: Path, dispatcher: Path) -> list[str]` (changes made); `doctor_probes() -> list[Callable]` (checks that catch silent failures only, R-22). A probe is `probe(ctx, task_id) -> tuple[str, bool, str]` (name, ok, fix) and may raise `HarnessError`.
- Claude extras: `claude.markers(payload_session_id: str, env, task_id: str | None, foreign_vars) -> dict[str, str]`; `claude.parent_session(payload_session_id, env, foreign_vars) -> str | None`; `claude.IMPORT_LINE`; `claude.ALLOW_RULE`; `claude.BOOTSTRAP_COPY`

Spec: §4.1 and §4.3 (user-scope files, append-only install, allow rule), §4.4 (bootstrap text), §6.7 (`model` null in Claude hooks; `effort` from Stop/SubagentStop `effort.level`; transcript paths, C15), §6.9 (markers, parent derivation), §8 B (Claude probes), §12 (adapter contract: a changed payload gives `format_warning`, never a crash), R-20.

- [ ] **Step 1: Write the bootstrap text (fixed, §4.4)**

`hooks/bootstrap.md`:

```markdown
If another agent launched you, ignore this file and follow your prompt. Otherwise run `harness start`, then read `AGENTS.md` from the checkout it prints.
```

- [ ] **Step 2: Write the failing tests**

`tests/test_adapter_claude.py`:

```python
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from harness import REPO
from harness.adapters import REGISTRY, claude, foreign_vars, identity_vars

FIXTURES = REPO / "tests" / "fixtures" / "claude"


class ClaudeAdapterTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        self.dispatcher = self.home / ".local" / "bin" / "harness"

    def test_registry(self):
        self.assertIs(REGISTRY["claude"], claude)
        self.assertEqual(identity_vars(), {"claude": "HARNESS_SESSION_ID"})
        self.assertEqual(foreign_vars("claude"), [])

    def test_every_captured_payload_maps_without_warnings(self):  # spec §12 adapter contract
        self.assertEqual(sorted(p.stem for p in FIXTURES.glob("*.json")), sorted(claude.HOOK_EVENTS))
        for path in FIXTURES.glob("*.json"):
            fields, missing = claude.to_event(path.stem, json.loads(path.read_text()), {}, [])
            self.assertEqual(missing, [], path.name)
            self.assertEqual(fields["kind"], claude.HOOK_EVENTS[path.stem])
            self.assertEqual(fields["agent"], "claude")
            self.assertTrue(fields["transcript_path"])

    def test_changed_payload_reports_missing_fields_without_crashing(self):
        payload = json.loads((FIXTURES / "SubagentStop.json").read_text())
        del payload["agent_id"]
        fields, missing = claude.to_event("SubagentStop", payload, {}, [])
        self.assertEqual(missing, ["agent_id"])
        self.assertIsNone(fields["agent_id"])
        self.assertEqual(claude.to_event("Renamed", {}, {}, [])[1], ["unknown hook event Renamed"])

    def test_effort_and_trigger(self):
        fields, _ = claude.to_event("Stop", {"session_id": "S", "transcript_path": "/t", "effort": {"level": "high"}}, {}, [])
        self.assertEqual(fields["effort"], "high")
        fields, _ = claude.to_event("SessionStart", {"session_id": "S", "transcript_path": "/t", "source": "resume"}, {}, [])
        self.assertEqual(fields["trigger"], "resume")

    def test_parent_session_derivation(self):  # spec §6.9
        self.assertEqual(claude.parent_session("S", {}, ["CODEX_THREAD_ID"]), "S")
        self.assertEqual(claude.parent_session("S", {"CODEX_THREAD_ID": "P"}, ["CODEX_THREAD_ID"]), "P")
        self.assertEqual(claude.parent_session("S", {"HARNESS_PARENT_SESSION": "Q", "CODEX_THREAD_ID": "P"},
                                               ["CODEX_THREAD_ID"]), "Q")

    def test_markers(self):  # spec §6.9
        self.assertEqual(claude.markers("S", {}, "T", []),
                         {"HARNESS_SESSION_ID": "S", "HARNESS_TASK_ID": "T", "HARNESS_PARENT_SESSION": "S"})
        self.assertEqual(claude.markers("C", {"HARNESS_TASK_ID": "T0", "HARNESS_PARENT_SESSION": "P"}, "T", []),
                         {"HARNESS_SESSION_ID": "C"})
        self.assertEqual(claude.markers("C", {"CODEX_THREAD_ID": "P"}, "T", ["CODEX_THREAD_ID"])["HARNESS_PARENT_SESSION"], "P")

    def test_on_event_exports_markers_through_claude_env_file(self):
        env_file = self.home / "env"
        env_file.write_text("")
        claude.on_event("SessionStart", {"session_id": "S 1"}, {"CLAUDE_ENV_FILE": str(env_file)}, lambda: "T", [])
        out = subprocess.run(["sh", "-c", f'. "{env_file}"; echo "$HARNESS_SESSION_ID|$HARNESS_TASK_ID"'],
                             capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "S 1|T")
        claude.on_event("SessionStart", {"session_id": "S"}, {"CLAUDE_ENV_FILE": str(env_file)}, lambda: None, [])
        claude.on_event("Stop", {"session_id": "S"}, {"CLAUDE_ENV_FILE": str(env_file)}, lambda: "T", [])
        self.assertEqual(env_file.read_text().count("export HARNESS_SESSION_ID"), 1)

    def test_install_user_appends_once_and_keeps_existing_entries_first(self):  # spec §4.3
        settings = self.home / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        mine = {"hooks": [{"type": "command", "command": "my-stop-hook"}]}
        settings.write_text(json.dumps({"model": "opus", "hooks": {"Stop": [mine]}}))
        (self.home / ".claude" / "CLAUDE.md").write_text("# mine\n")
        changes = claude.install_user(self.home, self.dispatcher)
        self.assertTrue(changes)
        data = json.loads(settings.read_text())
        self.assertEqual(data["model"], "opus")
        self.assertEqual(data["hooks"]["Stop"][0], mine)
        self.assertEqual(sorted(data["hooks"]), sorted(claude.HOOK_EVENTS))
        self.assertIn(f"{self.dispatcher} hook claude Stop", json.dumps(data))
        self.assertIn("Bash(harness:*)", data["permissions"]["allow"])
        self.assertEqual((self.home / ".claude" / "CLAUDE.md").read_text(), "# mine\n@~/.claude/harness-bootstrap.md\n")
        self.assertEqual((self.home / ".claude" / "harness-bootstrap.md").read_text(),
                         (REPO / "hooks" / "bootstrap.md").read_text())
        self.assertEqual(claude.install_user(self.home, self.dispatcher), [])

    def test_doctor_probes_fail_before_install_and_pass_after(self):  # spec §8 B, R-22
        ctx = SimpleNamespace(home=self.home)
        before = [fn(ctx, None) for fn in claude.doctor_probes()]
        self.assertEqual([(name, ok) for name, ok, _ in before], [("claude_hooks", False), ("claude_bootstrap", False)])
        self.assertTrue(all("install --user" in fix for _, _, fix in before))
        claude.install_user(self.home, self.dispatcher)
        self.assertTrue(all(ok for _, ok, _ in (fn(ctx, None) for fn in claude.doctor_probes())))
        settings = self.home / ".claude" / "settings.json"
        settings.write_text(json.dumps({**json.loads(settings.read_text()), "disableAllHooks": True}))
        self.assertFalse(claude.probe_claude_hooks(ctx, None)[1])
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_adapter_claude -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'harness.adapters'`.

- [ ] **Step 4: Write the implementation**

`harness/adapters/__init__.py`:

```python
"""Adapter registry: one module per agent; a new agent is one module plus one line (spec §15)."""
from harness.adapters import claude

REGISTRY = {claude.NAME: claude}


def identity_vars() -> dict[str, str]:
    return {name: module.IDENTITY_VAR for name, module in REGISTRY.items()}


def foreign_vars(name: str) -> list[str]:
    """Identity variables of every other agent (spec §6.9)."""
    return [module.IDENTITY_VAR for other, module in REGISTRY.items() if other != name]
```

`harness/adapters/claude.py`:

```python
"""Claude Code adapter: payload → event, §6.9 markers, user install, doctor probes. Edge."""
import json
import shlex
import shutil
from collections.abc import Callable, Mapping
from pathlib import Path

from harness import REPO
from harness.identity import PARENT_VAR, TASK_VAR

NAME = "claude"
IDENTITY_VAR = "HARNESS_SESSION_ID"  # not CLAUDE_CODE_SESSION_ID (C5)
HOOK_EVENTS = {
    "SessionStart": "session_start",
    "UserPromptSubmit": "prompt",
    "Stop": "stop",
    "SubagentStart": "subagent_start",
    "SubagentStop": "subagent_stop",
    "SessionEnd": "session_end",
}
# Fields the payload must carry (spec §16, confirmed by the Phase 0 fixtures).
REQUIRED = {
    "SessionStart": ("session_id", "transcript_path", "source"),
    "UserPromptSubmit": ("session_id", "transcript_path"),
    "Stop": ("session_id", "transcript_path"),
    "SubagentStart": ("session_id", "transcript_path", "agent_id", "agent_type"),
    "SubagentStop": ("session_id", "transcript_path", "agent_id", "agent_type", "agent_transcript_path"),
    "SessionEnd": ("session_id", "transcript_path", "reason"),
}
ALLOW_RULE = "Bash(harness:*)"
BOOTSTRAP_COPY = Path(".claude") / "harness-bootstrap.md"
IMPORT_LINE = "@~/.claude/harness-bootstrap.md"
FIX = "run `harness install --user`"


def parent_session(payload_session_id: str | None, env: Mapping[str, str], foreign_vars: list[str]) -> str | None:
    """HARNESS_PARENT_SESSION, else an inherited foreign identity, else this session (spec §6.9)."""
    if env.get(PARENT_VAR):
        return env[PARENT_VAR]
    for var in foreign_vars:
        if env.get(var):
            return env[var]
    return payload_session_id


def to_event(hook_event: str, payload: dict, env: Mapping[str, str], foreign_vars: list[str]) -> tuple[dict, list[str]]:
    kind = HOOK_EVENTS.get(hook_event)
    if kind is None:
        return {}, [f"unknown hook event {hook_event}"]
    missing = [name for name in REQUIRED[hook_event] if payload.get(name) in (None, "")]
    effort = payload.get("effort")
    fields = {
        "kind": kind,
        "agent": NAME,
        "session_id": payload.get("session_id"),
        "parent_session": parent_session(payload.get("session_id"), env, foreign_vars),
        "task_id": env.get(TASK_VAR),
        "model": payload.get("model"),  # Claude hooks carry none today; scoring fills it from transcripts
        "effort": effort.get("level") if isinstance(effort, dict) else None,
        "transcript_path": payload.get("transcript_path"),
        "agent_transcript_path": payload.get("agent_transcript_path"),
    }
    if kind in ("subagent_start", "subagent_stop"):
        fields.update(agent_id=payload.get("agent_id"), agent_type=payload.get("agent_type"))
    if kind == "session_start":
        fields["trigger"] = payload.get("source")
    if kind == "session_end":
        fields["reason"] = payload.get("reason")
    if kind == "prompt":
        fields["prompt_id"] = payload.get("prompt_id")
    return fields, missing


def markers(payload_session_id: str, env: Mapping[str, str], task_id: str | None, foreign_vars: list[str]) -> dict[str, str]:
    """The §6.9 markers this SessionStart exports."""
    out = {IDENTITY_VAR: payload_session_id}
    if not env.get(TASK_VAR) and task_id:
        out[TASK_VAR] = task_id
    if not env.get(PARENT_VAR):
        out[PARENT_VAR] = parent_session(payload_session_id, env, foreign_vars)
    return out


def on_event(hook_event: str, payload: dict, env: Mapping[str, str],
             lookup_task: Callable[[], str | None], foreign_vars: list[str]) -> None:
    """On every SessionStart in a worktree whose branch has a task, export the markers."""
    env_file, session_id = env.get("CLAUDE_ENV_FILE"), payload.get("session_id")
    if hook_event != "SessionStart" or not env_file or not session_id:
        return
    task_id = lookup_task()
    if not task_id:
        return
    exports = markers(session_id, env, task_id, foreign_vars)
    with open(env_file, "a") as f:
        f.write("".join(f"export {k}={shlex.quote(v)}\n" for k, v in exports.items()))


def _settings_path(home: Path) -> Path:
    return home / ".claude" / "settings.json"


def _settings(home: Path) -> dict:
    path = _settings_path(home)
    return json.loads(path.read_text()) if path.exists() else {}


def hook_command(dispatcher: Path, hook_event: str) -> str:
    return f"{shlex.quote(str(dispatcher))} hook {NAME} {hook_event}"


def install_user(home: Path, dispatcher: Path) -> list[str]:
    """Append hook entries and the allow rule, copy the bootstrap, import it (spec §4.3)."""
    changes = []
    path, settings = _settings_path(home), _settings(home)
    hooks = settings.setdefault("hooks", {})
    for event in HOOK_EVENTS:
        command = hook_command(dispatcher, event)
        entries = hooks.setdefault(event, [])
        if not any(h.get("command") == command for e in entries for h in e.get("hooks", [])):
            entries.append({"hooks": [{"type": "command", "command": command}]})  # append, never reorder
            changes.append(f"{path}: added {event} hook")
    allow = settings.setdefault("permissions", {}).setdefault("allow", [])
    if ALLOW_RULE not in allow:
        allow.append(ALLOW_RULE)
        changes.append(f"{path}: added allow rule {ALLOW_RULE}")
    if changes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(settings, indent=2) + "\n")
    src, dst = REPO / "hooks" / "bootstrap.md", home / BOOTSTRAP_COPY
    if not dst.exists() or dst.read_text() != src.read_text():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        changes.append(f"wrote {dst}")
    claude_md = home / ".claude" / "CLAUDE.md"
    text = claude_md.read_text() if claude_md.exists() else ""
    if IMPORT_LINE not in text.splitlines():
        claude_md.write_text(text + ("" if text.endswith("\n") or not text else "\n") + IMPORT_LINE + "\n")
        changes.append(f"{claude_md}: imports the bootstrap")
    return changes


def probe_claude_hooks(ctx, task_id):
    """Every hook entry present and hooks not disabled; otherwise events go missing silently."""
    settings = _settings(ctx.home)
    hooks = settings.get("hooks", {})
    missing = [e for e in HOOK_EVENTS if not any(
        f" hook {NAME} {e}" in h.get("command", "") for entry in hooks.get(e, []) for h in entry.get("hooks", []))]
    disabled = settings.get("disableAllHooks") is True
    return ("claude_hooks", not missing and not disabled,
            f"missing Claude hooks {missing} or `disableAllHooks: true` in ~/.claude/settings.json: {FIX}")


def probe_claude_bootstrap(ctx, task_id):
    claude_md, copy = ctx.home / ".claude" / "CLAUDE.md", ctx.home / BOOTSTRAP_COPY
    ok = (claude_md.exists() and IMPORT_LINE in claude_md.read_text().splitlines()
          and copy.exists() and copy.read_text() == (REPO / "hooks" / "bootstrap.md").read_text())
    return "claude_bootstrap", ok, f"bootstrap import missing or stale: {FIX}"


def doctor_probes() -> list[Callable]:
    return [probe_claude_hooks, probe_claude_bootstrap]
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_adapter_claude -v`
Expected: 9 tests, OK. If `test_every_captured_payload_maps_without_warnings` fails, compare the fixture's keys with `REQUIRED`: the fixtures are the truth; change `REQUIRED` to match and note the difference in the spec PR of Task 0.7 (or a follow-up commit there).

- [ ] **Step 6: Commit**

```bash
git add harness/adapters hooks/bootstrap.md tests/test_adapter_claude.py
git commit -m "feat: Claude adapter, adapter registry and bootstrap text"
```

### Task 1.8: Context, CLI dispatch and the `hook` command

**Files:**
- Create: `harness/context.py`, `harness/cli.py`, `harness/commands/__init__.py` (empty), `harness/commands/hook.py`, `bin/harness`, `tests/test_cli.py`, `tests/test_hook.py`
- Modify: `tests/helpers.py` (add `cli`, `clean_env`, `spool_events`)

**Interfaces:**
- Consumes: Tasks 1.1–1.7
- Produces: `context.Ctx(cwd: Path, env: dict, home: Path, git: GitInfo | None, project: dict | None, identity: Identity)` with properties `root -> Path`, `state_dir -> Path` and method `require_project() -> dict`; `context.load(cwd=None, env=None) -> Ctx`; `context.event(ctx, kind, task_id, **extra) -> dict`; `context.record(ctx, event, *, held=False) -> None`; `context.task_events(ctx, task_id) -> list[dict]`; `cli.Command(module, during_rebase: Callable[[Namespace], bool], controller_only: bool)`; `cli.COMMANDS: dict[str, Command]`; `cli.guard(cmd, args, ctx) -> None`; `cli.main(argv=None) -> int`. Every command module defines `add_args(parser)` and `run(args, ctx) -> int`.
- Test helpers: `clean_env(**extra) -> dict` (environment without harness/agent identity variables); `cli(*args, cwd, env, input=None) -> CompletedProcess`; `spool_events(repo, env) -> list[dict]`

Spec: §4.4 (silence outside harness work; handlers never exit non-zero), §6.7 (CLI events: common fields; spool-only kinds), §6.9 (identity; ambiguous identity refuses), §7 (dispatcher), §9.5, §9.6, §9.7, R-6.

- [ ] **Step 1: Add the test helpers**

Append to `tests/helpers.py`:

```python
import sys

from harness import REPO, gitio, spool

CLEARED = ("HARNESS_SESSION_ID", "HARNESS_PARENT_SESSION", "HARNESS_TASK_ID", "CODEX_THREAD_ID",
           "CODEX_SANDBOX", "CLAUDE_CODE_REMOTE", "CLAUDE_ENV_FILE", "XDG_STATE_HOME", "GIT_DIR", "GIT_WORK_TREE")


def clean_env(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in CLEARED}
    return {**env, **GIT_ENV, **extra}


def cli(*args, cwd, env, input=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(REPO / "harness" / "cli.py"), *args], cwd=cwd, env=env,
                          capture_output=True, text=True, input=input)


def spool_events(repo, env) -> list[dict]:
    return spool.read(spool.project_dir(env, gitio.info(repo).common_dir))
```

- [ ] **Step 2: Write the failing tests**

`tests/test_hook.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from harness import taskfiles
from tests.helpers import cli, clean_env, git, init_repo, spool_events


class HookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.env = clean_env(HOME=str(self.tmp / "home"), XDG_STATE_HOME=str(self.tmp / "state"))
        self.repo = init_repo(self.tmp / "p")
        (self.repo / ".harness").mkdir()
        (self.repo / ".harness" / "project.json").write_text('{"schema_version": 1}\n')

    def fire(self, event, payload, cwd=None, env=None):
        return cli("hook", "claude", event, cwd=cwd or self.repo, env={**self.env, **(env or {})},
                   input=payload if isinstance(payload, str) else json.dumps(payload))

    def test_silent_outside_a_harness_project(self):  # spec §4.4
        plain = init_repo(self.tmp / "plain")
        r = self.fire("Stop", {"session_id": "S", "transcript_path": "/t", "cwd": str(plain)}, cwd=plain)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        self.assertFalse((self.tmp / "state").exists())

    def test_appends_event_with_git_fields(self):
        r = self.fire("SessionStart", {"session_id": "S", "transcript_path": "/t/S.jsonl",
                                       "cwd": str(self.repo), "source": "startup"})
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        [e] = spool_events(self.repo, self.env)
        self.assertEqual((e["kind"], e["source"], e["session_id"], e["branch"], e["trigger"], e["transcript_path"]),
                         ("session_start", "hook", "S", "main", "startup", "/t/S.jsonl"))
        self.assertEqual(e["head"], git(self.repo, "rev-parse", "HEAD"))
        self.assertTrue(e["harness_version"])

    def test_garbage_payload_warns_and_exits_zero(self):  # spec §4.4, §9.6, Review Focus 1
        r = self.fire("Stop", "this is not json")
        self.assertEqual(r.returncode, 0)
        self.assertIn("missing", r.stderr)
        kinds = [e["kind"] for e in spool_events(self.repo, self.env)]
        self.assertIn("format_warning", kinds)

    def test_unknown_agent_warns_and_exits_zero(self):
        r = cli("hook", "grok", "Stop", cwd=self.repo, env=self.env, input="{}")
        self.assertEqual(r.returncode, 0)
        self.assertEqual([e["kind"] for e in spool_events(self.repo, self.env)], ["format_warning"])

    def test_unwritable_state_dir_never_fails_the_agent(self):  # spec §9.6
        state = self.tmp / "state"
        state.mkdir()
        state.chmod(0o500)
        self.addCleanup(state.chmod, 0o700)
        r = self.fire("Stop", {"session_id": "S", "transcript_path": "/t", "cwd": str(self.repo)})
        self.assertEqual(r.returncode, 0)
        self.assertIn("harness hook:", r.stderr)

    def test_session_start_in_a_task_worktree_exports_markers(self):  # spec §6.9
        git(self.repo, "switch", "-qc", "feat")
        folder = taskfiles.task_dir(self.repo, "2026-10-08-x")
        folder.mkdir(parents=True)
        taskfiles.write_json(folder / "state.json", {"task_id": "2026-10-08-x", "branch": "feat"})
        env_file = self.tmp / "envfile"
        env_file.write_text("")
        self.fire("SessionStart", {"session_id": "S", "transcript_path": "/t", "cwd": str(self.repo), "source": "startup"},
                  env={"CLAUDE_ENV_FILE": str(env_file)})
        text = env_file.read_text()
        for line in ("export HARNESS_SESSION_ID=S", "export HARNESS_TASK_ID=2026-10-08-x", "export HARNESS_PARENT_SESSION=S"):
            self.assertIn(line, text)
```

`tests/test_cli.py`:

```python
import argparse
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from harness import HarnessError, cli, context, gitio
from harness.identity import Identity
from tests.helpers import init_repo


def fake_ctx(delegate=False):
    return types.SimpleNamespace(git=object(), cwd=Path("."), identity=Identity("C", "claude", "P", delegate))


class CliGuardTest(unittest.TestCase):
    def test_stopped_rebase_refuses_unless_allowed(self):  # spec §9.7
        cmd = cli.Command(types.SimpleNamespace())
        with mock.patch.object(gitio, "rebase_in_progress", return_value=True):
            with self.assertRaisesRegex(HarnessError, "rebase is stopped"):
                cli.guard(cmd, argparse.Namespace(), fake_ctx())
            cli.guard(cli.Command(types.SimpleNamespace(), during_rebase=lambda a: True), argparse.Namespace(), fake_ctx())

    def test_delegate_cannot_run_controller_commands(self):  # spec §9.5
        cmd = cli.Command(types.SimpleNamespace(), controller_only=True)
        with mock.patch.object(gitio, "rebase_in_progress", return_value=False):
            with self.assertRaisesRegex(HarnessError, "delegates"):
                cli.guard(cmd, argparse.Namespace(), fake_ctx(delegate=True))
            cli.guard(cmd, argparse.Namespace(), fake_ctx(delegate=False))

    def test_harness_errors_print_and_exit_one(self):
        module = types.SimpleNamespace(__doc__="Fails.", add_args=lambda p: None,
                                       run=mock.Mock(side_effect=HarnessError("nope")))
        with mock.patch.dict(cli.COMMANDS, {"fails": cli.Command(module, during_rebase=lambda a: True)}):
            with mock.patch("sys.stderr") as err:
                self.assertEqual(cli.main(["fails"]), 1)
        self.assertIn("harness: nope", "".join(c.args[0] for c in err.write.call_args_list))


class ContextTest(unittest.TestCase):
    def test_ambiguous_identity_refuses(self):  # spec §6.9
        repo = init_repo(Path(tempfile.mkdtemp()) / "r")
        with mock.patch("harness.context.identity_vars",
                        return_value={"claude": "HARNESS_SESSION_ID", "codex": "CODEX_THREAD_ID"}):
            with self.assertRaisesRegex(HarnessError, "disagree"):
                context.load(repo, {"HARNESS_SESSION_ID": "A", "CODEX_THREAD_ID": "B", "HOME": "/tmp"})

    def test_cli_event_carries_identity_and_git_fields(self):
        repo = init_repo(Path(tempfile.mkdtemp()) / "r")
        ctx = context.load(repo, {"HARNESS_SESSION_ID": "S", "HARNESS_PARENT_SESSION": "S", "HOME": "/tmp"})
        e = context.event(ctx, "resume", "T")
        self.assertEqual((e["source"], e["agent"], e["session_id"], e["parent_session"], e["task_id"], e["branch"]),
                         ("cli", "claude", "S", "S", "T", "main"))
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_cli tests.test_hook -v`
Expected: FAIL with `ImportError: cannot import name 'cli'` (and `context`).

- [ ] **Step 4: Write the implementation**

`harness/context.py`:

```python
"""Per-invocation context for CLI commands; builds and records CLI events (spec §6.7, §6.9). Edge."""
import json
import os
from dataclasses import dataclass
from pathlib import Path

from harness import HarnessError, events, gitio, identity, spool, taskfiles
from harness.adapters import identity_vars


@dataclass
class Ctx:
    cwd: Path
    env: dict
    home: Path
    git: gitio.GitInfo | None
    project: dict | None
    identity: identity.Identity

    @property
    def root(self) -> Path:
        if self.git is None:
            raise HarnessError("not inside a git repository")
        return self.git.toplevel

    @property
    def state_dir(self) -> Path:
        if self.git is None:
            raise HarnessError("not inside a git repository")
        return spool.project_dir(self.env, self.git.common_dir)

    def require_project(self) -> dict:
        if self.project is None:
            raise HarnessError("no .harness/project.json here: run `harness install` and merge its PR")
        return self.project


def load(cwd=None, env=None) -> Ctx:
    cwd = Path(cwd or os.getcwd())
    env = dict(os.environ if env is None else env)
    git = gitio.info(cwd)
    project = taskfiles.load_project(git.toplevel) if git else None
    try:
        ident = identity.resolve(env, identity_vars())
    except identity.AmbiguousIdentity as e:
        raise HarnessError(f"ambiguous agent identity: {e}") from e
    return Ctx(cwd, env, Path(env.get("HOME") or Path.home()), git, project, ident)


def event(ctx: Ctx, kind: str, task_id: str | None, **extra) -> dict:
    """A CLI event with identity and fresh git fields (spec §6.7)."""
    g = gitio.info(ctx.cwd)
    return events.make(
        kind, "cli", events.now_ts(),
        agent=ctx.identity.agent, session_id=ctx.identity.session_id, parent_session=ctx.identity.parent_session,
        task_id=task_id, branch=g.branch if g else None, head=g.head if g else None, cwd=str(ctx.cwd),
        git_common_dir=g.common_dir if g else None, harness_version=gitio.harness_version(), **extra)


def record(ctx: Ctx, ev: dict, *, held: bool = False) -> None:
    """Spool always; the task's events.jsonl too unless the kind is spool-only or this checkout
    is not on the task's branch (spec §6.7, R-6)."""
    task_file = None
    if ev["kind"] not in events.SPOOL_ONLY and ev["task_id"]:
        state = taskfiles.task_dir(ctx.root, ev["task_id"]) / "state.json"
        if state.exists() and json.loads(state.read_text()).get("branch") == ev["branch"]:
            task_file = state.parent / "events.jsonl"
    spool.append(ctx.state_dir, ev, task_file, held=held)


def task_events(ctx: Ctx, task_id: str) -> list[dict]:
    return [e for e in spool.read(ctx.state_dir) if e.get("task_id") == task_id]
```

`harness/commands/hook.py`:

```python
"""Record an agent hook event in the spool; never blocks or fails the agent (spec §4.4, §9.6)."""
import json
import os
import sys

from harness import events, gitio, spool, taskfiles
from harness.adapters import REGISTRY, foreign_vars


def add_args(p) -> None:
    p.add_argument("agent")  # plain strings: argparse errors would exit non-zero
    p.add_argument("event")


def run(args, ctx=None) -> int:
    try:
        handle(args.agent, args.event, sys.stdin.read(), dict(os.environ))
    except Exception as e:  # noqa: BLE001 — a hook must never fail the agent (spec §9.6)
        print(f"harness hook: {type(e).__name__}: {e}", file=sys.stderr)
    return 0


def handle(agent: str, hook_event: str, raw: str, env: dict) -> None:
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    cwd = payload.get("cwd") or os.getcwd()
    git = gitio.info(cwd)
    if git is None or not (git.toplevel / ".harness" / "project.json").exists():
        return  # not a harness project: silent (spec §4.4)
    state_dir = spool.project_dir(env, git.common_dir)
    common = dict(branch=git.branch, head=git.head, cwd=str(cwd), git_common_dir=git.common_dir,
                  harness_version=gitio.harness_version())
    adapter = REGISTRY.get(agent)
    if adapter is None:
        fields, missing = {}, [f"unknown agent {agent}"]
    else:
        fields, missing = adapter.to_event(hook_event, payload, env, foreign_vars(agent))
    if fields:
        kind = fields.pop("kind")
        spool.append(state_dir, events.make(kind, "hook", events.now_ts(), **fields, **common))
    if missing:
        print(f"harness hook: {agent} {hook_event}: payload missing {missing}", file=sys.stderr)
        spool.append(state_dir, events.make("format_warning", "hook", events.now_ts(), agent=agent,
                                            session_id=payload.get("session_id"), adapter=agent,
                                            event=hook_event, missing=missing, **common))
    if adapter is not None:
        def lookup_task():
            branch, rev = gitio.effective_branch(cwd, git)
            ids = taskfiles.find_by_branch(git.toplevel, branch, rev) if branch else []
            return ids[0] if len(ids) == 1 else None
        adapter.on_event(hook_event, payload, env, lookup_task, foreign_vars(agent))
```

`harness/cli.py`:

```python
"""`harness` entry point: one dispatch table and its two guards (spec §7, §9.5, §9.7)."""
import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

if __package__ in (None, ""):  # run as a script by the dispatcher
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from harness import HarnessError, context, gitio  # noqa: E402
from harness.commands import hook  # noqa: E402


def _never(args) -> bool:
    return False


def _always(args) -> bool:
    return True


@dataclass(frozen=True)
class Command:
    module: object
    during_rebase: Callable[[argparse.Namespace], bool] = _never  # allowed while a rebase is stopped?
    controller_only: bool = False  # refused to delegates (spec §9.5)


COMMANDS = {
    "hook": Command(hook, during_rebase=_always),
}


def guard(cmd: Command, args, ctx) -> None:
    if ctx.git is not None and not cmd.during_rebase(args) and gitio.rebase_in_progress(ctx.cwd):
        raise HarnessError("a rebase is stopped in this worktree: resolve the conflicts, `git add` them, "
                           "then run `harness rebase`")
    if cmd.controller_only and ctx.identity.delegate:
        raise HarnessError("delegates may run `harness check` only; follow your prompt")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="harness")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, cmd in COMMANDS.items():
        cmd.module.add_args(sub.add_parser(name, help=(cmd.module.__doc__ or "").split("\n")[0]))
    args = parser.parse_args(argv)
    if args.command == "hook":  # builds its own context from the payload; never fails
        return hook.run(args)
    cmd = COMMANDS[args.command]
    try:
        ctx = context.load()
        guard(cmd, args, ctx)
        return cmd.module.run(args, ctx)
    except HarnessError as e:
        print(f"harness: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

`bin/harness` (template; `install --user` fills in the placeholders):

```sh
#!/bin/sh
# Lean Harness dispatcher, installed by `harness install --user`.
exec "@PYTHON@" "@HARNESS_REPO@/harness/cli.py" "$@"
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_cli tests.test_hook -v`
Expected: 11 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/context.py harness/cli.py harness/commands bin/harness tests/helpers.py tests/test_cli.py tests/test_hook.py
git commit -m "feat: CLI dispatch with rebase and delegate guards; hook command"
```

### Task 1.9: `install` (user and project) and the test sandbox

**Files:**
- Create: `harness/commands/install.py`, `tests/test_install.py`
- Modify: `harness/cli.py` (register `install`), `tests/helpers.py` (add `GH_STUB`, `Sandbox`)

**Interfaces:**
- Consumes: `dispatcher_path`, `adapters.REGISTRY` (`install_user`), `gitio`, `taskfiles.GITATTRIBUTES_LINE`
- Produces: `install.render_dispatcher(python: str = sys.executable, repo: Path = REPO) -> str`; `install.PROJECT_DEFAULTS: dict`; `Sandbox` in `tests/helpers.py` with `tmp`, `home`, `env`, `remote`, `main`, `harness(*args, cwd, env=None, input=None)`, `worktree(branch) -> Path`, `hook(wt, event, session_id, env=None, **payload)`, `claude_session(wt, session_id, env=None) -> dict[str, str]`, `spool(wt) -> list[dict]`

Spec: §4.1, §4.3 (both install commands; idempotent; prints each change), §6.2 (defaults), C7, R-8.

- [ ] **Step 1: Register the command**

In `harness/cli.py`, change the import line to `from harness.commands import hook, install  # noqa: E402` and add to `COMMANDS`:

```python
    "install": Command(install, during_rebase=lambda a: a.user),
```

- [ ] **Step 2: Add the sandbox to the test helpers**

Append to `tests/helpers.py`:

```python
import json
import shlex
import tempfile

GH_STUB = """#!/bin/sh
echo "$*" >> "$GH_LOG"
case "$1 $2" in
  "auth status") exit 0 ;;
  "repo view") echo ADMIN ;;
  "pr create") echo "https://github.com/o/r/pull/$(grep -c '^pr create' "$GH_LOG")" ;;
  "pr edit") exit 0 ;;
  *) echo "unexpected gh $*" >&2; exit 1 ;;
esac
"""


class Sandbox:
    """Fake HOME and state dir, a bare remote, a clone with the harness installed and merged, a stub gh."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        self.home.mkdir()
        bindir = self.tmp / "bin"
        bindir.mkdir()
        (bindir / "gh").write_text(GH_STUB)
        (bindir / "gh").chmod(0o755)
        self.env = clean_env(HOME=str(self.home), XDG_STATE_HOME=str(self.tmp / "state"),
                             GH_LOG=str(self.tmp / "gh.log"),
                             PATH=f"{self.home}/.local/bin:{bindir}:{os.environ['PATH']}")
        seed = init_repo(self.tmp / "seed")
        self.remote = self.tmp / "remote.git"
        sh("git", "clone", "-q", "--bare", str(seed), str(self.remote), cwd=self.tmp, env=self.env)
        self.main = self.tmp / "main"
        sh("git", "clone", "-q", str(self.remote), str(self.main), cwd=self.tmp, env=self.env)
        for args in (("install", "--user"), ("install",)):
            r = self.harness(*args, cwd=self.main)
            assert r.returncode == 0, r.stderr
        git(self.main, "push", "-q", "origin", "harness-install:main", env=self.env)
        git(self.main, "switch", "-q", "main", env=self.env)
        git(self.main, "pull", "-q", "--ff-only", env=self.env)

    def harness(self, *args, cwd, env=None, input=None) -> subprocess.CompletedProcess:
        return cli(*args, cwd=cwd, env={**self.env, **(env or {})}, input=input)

    def worktree(self, branch: str) -> Path:
        path = self.tmp / branch
        git(self.main, "fetch", "-q", "origin", env=self.env)
        git(self.main, "worktree", "add", "-q", str(path), "-b", branch, "origin/main", env=self.env)
        return path

    def hook(self, wt: Path, event: str, session_id: str, env=None, **payload) -> subprocess.CompletedProcess:
        body = {"session_id": session_id, "transcript_path": f"/t/{session_id}.jsonl", "cwd": str(wt), **payload}
        return self.harness("hook", "claude", event, cwd=wt, env=env, input=json.dumps(body))

    def claude_session(self, wt: Path, session_id: str, env=None) -> dict:
        """Fire SessionStart as Claude would; return the markers its Bash commands would see."""
        env_file = self.tmp / f"env-{session_id}"
        env_file.write_text("")
        self.hook(wt, "SessionStart", session_id, env={**(env or {}), "CLAUDE_ENV_FILE": str(env_file)},
                  source="startup")
        markers = {}
        for line in env_file.read_text().splitlines():
            key, _, value = line.removeprefix("export ").partition("=")
            markers[key] = shlex.split(value)[0]
        return {**(env or {}), **markers}

    def spool(self, wt: Path) -> list[dict]:
        return spool_events(wt, self.env)
```

- [ ] **Step 3: Write the failing tests**

`tests/test_install.py`:

```python
import json
import os
import tempfile
import unittest
from pathlib import Path

from harness import gitio
from harness.commands.install import render_dispatcher
from tests.helpers import Sandbox, cli, clean_env, git, init_repo, sh


class InstallTest(unittest.TestCase):
    def test_user_install_writes_a_working_dispatcher_and_is_idempotent(self):
        tmp = Path(tempfile.mkdtemp())
        env = clean_env(HOME=str(tmp))
        first = cli("install", "--user", cwd=tmp, env=env)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("wrote", first.stdout)
        dispatcher = tmp / ".local" / "bin" / "harness"
        self.assertTrue(os.access(dispatcher, os.X_OK))
        self.assertEqual(dispatcher.read_text(), render_dispatcher())
        self.assertEqual(sh(str(dispatcher), "--help", cwd=tmp, env=env).returncode, 0)
        self.assertIn("nothing changed", cli("install", "--user", cwd=tmp, env=env).stdout)

    def test_project_install_commits_two_files_on_a_new_branch(self):  # spec §4.3, C7, R-8
        tmp = Path(tempfile.mkdtemp())
        remote = tmp / "remote.git"
        sh("git", "clone", "-q", "--bare", str(init_repo(tmp / "seed")), str(remote), cwd=tmp)
        clone = tmp / "clone"
        sh("git", "clone", "-q", str(remote), str(clone), cwd=tmp)
        r = cli("install", cwd=clone, env=clean_env(HOME=str(tmp)))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(gitio.info(clone).branch, "harness-install")
        self.assertEqual(git(clone, "show", "--name-only", "--format=", "HEAD").split(),
                         [".gitattributes", ".harness/project.json"])
        project = json.loads((clone / ".harness" / "project.json").read_text())
        self.assertEqual((project["integration_remote"], project["default_branch"], project["deadline_hours"],
                          project["expiry_days"], project["challenger_commit"]),
                         ("origin", "main", {"S": 4, "M": 16, "L": 48}, 21, None))
        self.assertEqual(project["baseline_commit"], gitio.harness_version())
        self.assertIn(".harness/memory/*.md merge=union", (clone / ".gitattributes").read_text())

    def test_project_install_refuses_outside_git(self):
        tmp = Path(tempfile.mkdtemp())
        r = cli("install", cwd=tmp, env=clean_env(HOME=str(tmp)))
        self.assertEqual(r.returncode, 1)
        self.assertIn("not inside a git repository", r.stderr)

    def test_sandbox_builds(self):
        sb = Sandbox()
        self.assertTrue((sb.main / ".harness" / "project.json").exists())
        self.assertEqual(gitio.info(sb.main).branch, "main")
```

- [ ] **Step 4: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_install -v`
Expected: FAIL with `ImportError: cannot import name 'install'`.

- [ ] **Step 5: Write the implementation**

`harness/commands/install.py`:

```python
"""Install the user-scope files (`--user`) or this project's harness files on a branch (spec §4.3)."""
import json
import sys
from pathlib import Path

from harness import REPO, HarnessError, dispatcher_path, gitio, taskfiles
from harness.adapters import REGISTRY

PROJECT_DEFAULTS = {
    "schema_version": 1,
    "cloud_env_vars": [],
    "deadline_hours": {"S": 4, "M": 16, "L": 48},
    "expiry_days": 21,
    "defect_window_days": 14,
    "target_benchmark_tier": "M",
    "n": 10,
    "alpha": 0.05,
    "min_gain": 0.20,
    "challenger_commit": None,
    "shared_commit": None,
    "memory_snapshot_commit": None,
}


def render_dispatcher(python: str = sys.executable, repo: Path = REPO) -> str:
    return (REPO / "bin" / "harness").read_text().replace("@PYTHON@", python).replace("@HARNESS_REPO@", str(repo))


def add_args(p) -> None:
    p.add_argument("--user", action="store_true", help="install the user-scope files")


def run(args, ctx) -> int:
    return install_user(ctx) if args.user else install_project(ctx)


def install_user(ctx) -> int:
    changes = []
    dispatcher = dispatcher_path(ctx.home)
    text = render_dispatcher()
    if not dispatcher.exists() or dispatcher.read_text() != text:
        dispatcher.parent.mkdir(parents=True, exist_ok=True)
        dispatcher.write_text(text)
        dispatcher.chmod(0o755)
        changes.append(f"wrote {dispatcher}")
    for adapter in REGISTRY.values():
        changes += adapter.install_user(ctx.home, dispatcher)
    print("\n".join(changes) if changes else "already installed; nothing changed")
    return 0


def install_project(ctx) -> int:
    root = ctx.root
    if ctx.project is not None:
        print(f"{root / '.harness' / 'project.json'} already exists; nothing changed")
        return 0
    remote = "origin"
    if remote not in gitio.out(["remote"], root).split():
        raise HarnessError("no `origin` remote in this repository")
    default = gitio.remote_default_branch(root, remote)
    if ctx.git.branch in (None, default):
        gitio.run(["switch", "-q", "-c", "harness-install"], root)
    project = {"schema_version": 1, "integration_remote": remote, "default_branch": default,
               **{k: v for k, v in PROJECT_DEFAULTS.items() if k != "schema_version"},
               "baseline_commit": gitio.harness_version()}
    path = root / ".harness" / "project.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project, indent=2) + "\n")
    attributes = root / ".gitattributes"
    text = attributes.read_text() if attributes.exists() else ""
    if taskfiles.GITATTRIBUTES_LINE not in text.splitlines():
        attributes.write_text(text + ("" if text.endswith("\n") or not text else "\n") + taskfiles.GITATTRIBUTES_LINE + "\n")
    gitio.run(["add", "--", ".harness/project.json", ".gitattributes"], root)
    gitio.run(["commit", "-q", "-m", "chore: install lean harness", "--", ".harness/project.json", ".gitattributes"], root)
    branch = gitio.info(root).branch
    print(f"committed .harness/project.json and .gitattributes on {branch}.\n"
          f"Set cloud_env_vars if this project has any (amend), push {branch}, open a PR, "
          f"and merge it before the first task.")
    return 0
```

- [ ] **Step 6: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_install -v`
Expected: 4 tests, OK.

- [ ] **Step 7: Commit**

```bash
git add harness/commands/install.py harness/cli.py tests/helpers.py tests/test_install.py
git commit -m "feat: install --user and project install; test sandbox"
```

### Task 1.10: `doctor`

**Files:**
- Create: `harness/ghio.py`, `harness/doctor.py`, `harness/commands/doctor.py`, `tests/test_doctor.py`
- Modify: `harness/cli.py` (register `doctor`)

**Interfaces:**
- Consumes: `context.Ctx`, `adapters.REGISTRY` (`doctor_probes`), `gitio`, `spool`, `taskfiles`
- Produces: `ghio.pr_create(cwd, base, head, title, body) -> tuple[int, str]`; `ghio.pr_edit_body(cwd, number, body) -> None`; `doctor.LIVE_WINDOW_MS`; every `doctor.probe_*(ctx, task_id) -> tuple[str, bool, str]`; `doctor.PRE_START: list`; `doctor.agent_install() -> list`; `doctor.run(probes, ctx, task_id=None) -> list[tuple[str, bool, str]]`; `doctor.passed(results) -> bool`; `doctor.format(results) -> str`

Spec: §8 as narrowed by R-22 (only checks that catch silent failures or record discrepancies; three entry points; read-only), §4.7, §9.1, C9, R-11, R-12, R-16.

| Probe | Catches (silently wrong otherwise) |
|---|---|
| `claude_hooks` (adapter) | A missing or disabled hook entry: that event is never recorded, with no error |
| `claude_bootstrap` (adapter) | No bootstrap: the agent works outside the harness while the task's clock runs |
| `not_cloud` | A cloud session recorded as a local task (§4.7) |
| `task_branch` | A task registered on the default branch, breaking one task = one branch |
| `clean` | Uncommitted work from before the clock started counted in the task |
| `up_to_date` | A worktree not started from the fetched integration branch: foreign commits counted in the task |
| `unused` | A reused branch or task id: two tasks' events merge (§9.1) |
| `session_live` | This session's hooks never reach the spool: its events are lost |

Dropped from §8 (R-22): Python version, git, gh, `gh auth`, repository permission, push dry run, state-dir writability, dispatcher on PATH, `project.json` validity, `.gitattributes`, allow rule. Each fails loudly at the moment it is needed.

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `doctor` from `harness.commands` and add `"doctor": Command(doctor, during_rebase=_always),`.

- [ ] **Step 2: Write the failing tests**

`tests/test_doctor.py`:

```python
import json
import unittest

from tests.helpers import Sandbox, commit


class DoctorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def doctor(self, cwd, env=None):
        return self.sb.harness("doctor", cwd=cwd, env=env)

    def test_pre_start_doctor_passes_in_a_fresh_worktree_and_writes_nothing(self):
        wt = self.sb.worktree("doc-ok")
        before = self.sb.spool(wt)
        r = self.doctor(wt)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for name in ("claude_hooks", "claude_bootstrap", "not_cloud", "task_branch", "clean", "up_to_date", "unused"):
            self.assertIn(f"ok    {name}", r.stdout)
        self.assertEqual(self.sb.spool(wt), before)

    def test_default_branch_fails_with_a_fix(self):
        r = self.doctor(self.sb.main)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  task_branch", r.stdout)

    def test_dirty_worktree_fails(self):
        wt = self.sb.worktree("doc-dirty")
        (wt / "scratch.txt").write_text("x")
        self.assertIn("FAIL  clean", self.doctor(wt).stdout)

    def test_foreign_commit_fails(self):
        wt = self.sb.worktree("doc-foreign")
        (wt / "old-work.txt").write_text("x")
        commit(wt, "work from before the task")
        self.assertIn("FAIL  up_to_date", self.doctor(wt).stdout)

    def test_cloud_session_fails(self):  # spec §4.7
        wt = self.sb.worktree("doc-cloud")
        self.assertIn("FAIL  not_cloud", self.doctor(wt, {"CLAUDE_CODE_REMOTE": "true"}).stdout)

    def test_missing_or_disabled_claude_hooks_fail(self):
        settings = self.sb.home / ".claude" / "settings.json"
        saved = settings.read_text()
        self.addCleanup(settings.write_text, saved)
        wt = self.sb.worktree("doc-hooks")
        settings.write_text(json.dumps({k: v for k, v in json.loads(saved).items() if k != "hooks"}))
        r = self.doctor(wt)
        self.assertIn("FAIL  claude_hooks", r.stdout)
        self.assertIn("install --user", r.stdout)
        settings.write_text(json.dumps({**json.loads(saved), "disableAllHooks": True}))
        self.assertIn("FAIL  claude_hooks", self.doctor(wt).stdout)

    def test_session_probe_needs_this_sessions_hooks(self):  # spec §8 E
        wt = self.sb.worktree("doc-live")
        env = {"HARNESS_SESSION_ID": "S9"}
        self.assertIn("FAIL  session_live", self.doctor(wt, env).stdout)
        self.sb.hook(wt, "UserPromptSubmit", "S9")
        self.assertIn("ok    session_live", self.doctor(wt, env).stdout)
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_doctor -v`
Expected: FAIL with `ImportError: cannot import name 'doctor'`.

- [ ] **Step 4: Write the implementation**

`harness/ghio.py`:

```python
"""GitHub CLI edge: every `gh` subprocess (spec §7 `pr`). Edge."""
import subprocess

from harness import HarnessError


def _ok(args: list[str], cwd) -> str:
    r = subprocess.run(["gh", *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise HarnessError(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def pr_create(cwd, base: str, head: str, title: str, body: str) -> tuple[int, str]:
    url = _ok(["pr", "create", "--base", base, "--head", head, "--title", title, "--body", body], cwd).splitlines()[-1]
    return int(url.rstrip("/").rsplit("/", 1)[1]), url


def pr_edit_body(cwd, number: int, body: str) -> None:
    _ok(["pr", "edit", str(number), "--body", body], cwd)
```

`harness/doctor.py`:

```python
"""Pre-start validation: only checks that catch silent failures or record discrepancies (spec §8, R-22). Edge."""
from harness import HarnessError, events, gitio, spool, taskfiles
from harness.adapters import REGISTRY

LIVE_WINDOW_MS = 10 * 60 * 1000  # "in the last few minutes" (§8 E)


def _project(ctx) -> dict:
    if ctx.project is None:
        raise HarnessError("no .harness/project.json: run `harness install` here and merge its PR")
    return ctx.project


def _integration_ref(ctx) -> str:
    p = _project(ctx)
    return f"{p['integration_remote']}/{p['default_branch']}"


def probe_not_cloud(ctx, task_id):
    names = (ctx.project or {}).get("cloud_env_vars", [])
    cloud = ctx.env.get("CLAUDE_CODE_REMOTE") == "true" or any(ctx.env.get(n) == "1" for n in names)
    return "not_cloud", not cloud, "harness tasks run locally only (spec §4.7)"


def probe_task_branch(ctx, task_id):
    branch = ctx.git.branch if ctx.git else None
    ok = branch is not None and branch != _project(ctx)["default_branch"]
    return "task_branch", ok, "git worktree add <path> -b <branch> origin/<default branch>, then cd there"


def probe_clean(ctx, task_id):
    return "clean", gitio.status_clean(ctx.root), "commit or remove changes so `git status --porcelain` is empty"


def probe_up_to_date(ctx, task_id):
    p = _project(ctx)
    gitio.fetch(ctx.root, p["integration_remote"], p["default_branch"])
    extra = gitio.out(["rev-list", "HEAD", "--not", _integration_ref(ctx)], ctx.root)
    return "up_to_date", extra == "", "create the worktree from fresh origin/<default branch>"


def probe_unused(ctx, task_id):
    """Branch and task id never used: integration branch, this branch, spool (spec §8 D, §9.1)."""
    p, branch = _project(ctx), ctx.git.branch
    starts = [e for e in spool.read(ctx.state_dir) if e.get("kind") == "start"]
    used = (any(e.get("branch") == branch for e in starts)
            or gitio.remote_branch_exists(ctx.root, p["integration_remote"], branch))
    if task_id is not None:
        used = used or (any(e.get("task_id") == task_id for e in starts)
                        or gitio.exists_at(ctx.root, _integration_ref(ctx), f"{taskfiles.RUNS}/{task_id}")
                        or taskfiles.task_dir(ctx.root, task_id).exists())
    return "unused", not used, "use a new branch name and a new slug"


def probe_session_live(ctx, task_id):
    sid = ctx.identity.session_id
    if sid is None:
        return "session_live", False, "no agent identity: launch the agent in this worktree after `harness install --user`"
    cutoff = events.ts_ms(events.now_ts()) - LIVE_WINDOW_MS
    ok = any(e.get("source") == "hook" and e.get("session_id") == sid and events.ts_ms(e["ts"]) >= cutoff
             for e in spool.read(ctx.state_dir))
    return "session_live", ok, "this session's hooks never reached the spool: run `harness install --user`, then relaunch"


PRE_START = [probe_not_cloud, probe_task_branch, probe_clean, probe_up_to_date]  # probe_unused runs under the lock


def agent_install() -> list:
    return [probe for adapter in REGISTRY.values() for probe in adapter.doctor_probes()]


def run(probes, ctx, task_id=None) -> list[tuple[str, bool, str]]:
    results = []
    for fn in probes:
        try:
            results.append(fn(ctx, task_id))
        except HarnessError as e:
            results.append((fn.__name__.removeprefix("probe_"), False, str(e)))
    return results


def passed(results) -> bool:
    return all(ok for _, ok, _ in results)


def format(results) -> str:
    return "\n".join(f"ok    {name}" if ok else f"FAIL  {name}: {fix}" for name, ok, fix in results)
```

`harness/commands/doctor.py`:

```python
"""Check for problems that would make the harness record wrong or nothing; writes no records (spec §8)."""
from harness import doctor, taskfiles


def add_args(p) -> None:
    pass


def run(args, ctx) -> int:
    probes = doctor.agent_install()
    on_task = bool(ctx.git and ctx.git.branch and ctx.project
                   and taskfiles.find_by_branch(ctx.root, ctx.git.branch))
    if ctx.git and not on_task:
        probes += doctor.PRE_START + [doctor.probe_unused]  # pre-start checks (R-11)
    if ctx.identity.session_id:
        probes.append(doctor.probe_session_live)
    results = doctor.run(probes, ctx)
    print(doctor.format(results))
    return 0 if doctor.passed(results) else 1
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_doctor -v`
Expected: 7 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/ghio.py harness/doctor.py harness/commands/doctor.py harness/cli.py tests/test_doctor.py
git commit -m "feat: doctor with silent-failure probes; gh edge"
```

### Task 1.11: `start --new` and bootstrap `start`

**Files:**
- Create: `harness/commands/start.py`, `tests/test_start.py`
- Modify: `harness/cli.py` (register `start`), `tests/helpers.py` (add `Sandbox.begin_task`)

**Interfaces:**
- Consumes: `doctor.PRE_START/agent_install/run/passed/format/probe_unused/probe_not_cloud/probe_session_live`, `spool.locked`, `context.event/record`, `taskfiles`, `gitio.harness_version`
- Produces: `start.SLUG_RE`; `Sandbox.begin_task(slug, tier="M", session="S1") -> tuple[Path, dict, str]` (worktree, the session's env, task id)

Spec: §4.4 (start flow; bootstrap; silence), §4.7, §7 `start` rows, §8 as narrowed by R-22 (install and pre-start probes in `start --new`; install, not-cloud and session probes at bootstrap, one `doctor` event), §6.6 (`start` holds the lock across uniqueness check, assignment, append), C13 (arm `baseline`), R-12, R-16.

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `start` and add `"start": Command(start, during_rebase=lambda a: not a.new),`.

- [ ] **Step 2: Add the sandbox task helper**

Add to `class Sandbox` in `tests/helpers.py`:

```python
    def begin_task(self, slug: str, tier: str = "M", session: str = "S1"):
        """Worktree, `start --new`, a Claude SessionStart, then the bootstrap `start`."""
        wt = self.worktree(f"task-{slug}")
        request = self.tmp / f"{slug}.md"
        request.write_text(f"Please do {slug}.\n")
        r = self.harness("start", "--new", slug, "--benchmark-tier", tier, "--request", str(request), cwd=wt)
        assert r.returncode == 0, r.stdout + r.stderr
        env = self.claude_session(wt, session)
        r = self.harness("start", cwd=wt, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        return wt, env, env["HARNESS_TASK_ID"]
```

- [ ] **Step 3: Write the failing tests**

`tests/test_start.py`:

```python
import hashlib
import subprocess
import sys
import unittest
from datetime import date

from harness import REPO, gitio, taskfiles
from tests.helpers import Sandbox, init_repo


class StartNewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def new(self, wt, slug, request=None, env=None):
        request = request or self.sb.tmp / f"{slug}.md"
        if not request.exists():
            request.write_text("Make it so.\n")
        return self.sb.harness("start", "--new", slug, "--benchmark-tier", "M", "--request", str(request),
                               cwd=wt, env=env)

    def test_registers_the_task_and_starts_the_clock(self):
        wt = self.sb.worktree("t-reg")
        request = self.sb.tmp / "reg.md"
        request.write_bytes(b"Exact bytes\r\n")
        r = self.new(wt, "reg", request)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        task_id = f"{date.today().isoformat()}-reg"
        folder = taskfiles.task_dir(wt, task_id)
        self.assertEqual((folder / "request.md").read_bytes(), b"Exact bytes\r\n")
        state = taskfiles.read_json(folder / "state.json")
        self.assertEqual((state["task_id"], state["branch"], state["phase"], state["phase_open"]),
                         (task_id, "t-reg", None, False))
        [start] = [e for e in self.sb.spool(wt) if e["kind"] == "start"]
        self.assertEqual((start["task_id"], start["benchmark_tier"], start["arm"], start["assigned_commit"],
                          start["request_sha256"]),
                         (task_id, "M", "baseline", gitio.harness_version(), hashlib.sha256(b"Exact bytes\r\n").hexdigest()))
        self.assertIn(str(REPO), r.stdout)
        self.assertFalse((folder / "events.jsonl").exists())  # start is spool-only

    def test_failed_doctor_registers_nothing(self):  # spec §8
        wt = self.sb.worktree("t-dirty")
        (wt / "scratch.txt").write_text("x")
        r = self.new(wt, "dirty")
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  clean", r.stdout)
        self.assertFalse((wt / ".harness" / "runs").exists())
        self.assertFalse(any(e["kind"] == "start" and e["branch"] == "t-dirty" for e in self.sb.spool(wt)))

    def test_cloud_session_refuses(self):  # spec §4.7
        r = self.new(self.sb.worktree("t-cloud"), "cloud", env={"CLAUDE_CODE_REMOTE": "true"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  not_cloud", r.stdout)

    def test_same_slug_in_two_worktrees_registers_once(self):  # spec §9.1, §9.3, Review Focus 3
        wts = [self.sb.worktree("t-race-a"), self.sb.worktree("t-race-b")]
        request = self.sb.tmp / "race.md"
        request.write_text("race\n")
        procs = [subprocess.Popen([sys.executable, str(REPO / "harness" / "cli.py"), "start", "--new", "race",
                                   "--benchmark-tier", "S", "--request", str(request)],
                                  cwd=wt, env=self.sb.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                 for wt in wts]
        codes = sorted(p.wait() for p in procs)
        self.assertEqual(codes, [0, 1])
        starts = [e for e in self.sb.spool(wts[0]) if e["kind"] == "start" and e["task_id"].endswith("-race")]
        self.assertEqual(len(starts), 1)


class BootstrapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def test_silent_outside_harness_work(self):  # spec §4.4
        r = self.sb.harness("start", cwd=self.sb.main)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        plain = init_repo(self.sb.tmp / "plain")
        r = self.sb.harness("start", cwd=plain)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_bootstrap_records_doctor_and_resume_and_prints_the_map(self):
        wt, env, task_id = self.sb.begin_task("boot")
        kinds = [(e["kind"], e["session_id"]) for e in self.sb.spool(wt) if e.get("task_id") == task_id]
        self.assertIn(("doctor", "S1"), kinds)
        self.assertIn(("resume", "S1"), kinds)
        [doc] = [e for e in self.sb.spool(wt) if e["kind"] == "doctor" and e["task_id"] == task_id]
        self.assertTrue(all(doc["checks"].values()))
        out = self.sb.harness("start", cwd=wt, env=env).stdout
        self.assertIn("AGENTS.md", out)
        self.assertIn(task_id, out)

    def test_delegate_gets_a_notice_and_appends_nothing(self):  # spec §6.9
        wt, env, task_id = self.sb.begin_task("deleg")
        before = len(self.sb.spool(wt))
        r = self.sb.harness("start", cwd=wt, env={**env, "HARNESS_SESSION_ID": "CHILD"})
        self.assertEqual(r.returncode, 0)
        self.assertIn(f"delegate of task {task_id}: follow your prompt", r.stdout)
        self.assertEqual(len(self.sb.spool(wt)), before)

    def test_session_without_hooks_fails_check_e(self):  # spec §8 E
        wt = self.sb.worktree("task-nohooks")
        request = self.sb.tmp / "nohooks.md"
        request.write_text("x\n")
        self.sb.harness("start", "--new", "nohooks", "--benchmark-tier", "S", "--request", str(request), cwd=wt)
        r = self.sb.harness("start", cwd=wt, env={"HARNESS_SESSION_ID": "GHOST", "HARNESS_PARENT_SESSION": "GHOST"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL  session_live", r.stdout)
        [doc] = [e for e in self.sb.spool(wt) if e["kind"] == "doctor" and e["session_id"] == "GHOST"]
        self.assertFalse(doc["checks"]["session_live"])
```

- [ ] **Step 4: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_start -v`
Expected: FAIL (`start` is not a registered command; argparse exits 2).

- [ ] **Step 5: Write the implementation**

`harness/commands/start.py`:

```python
"""`start --new`: register a task (you). `start`: bootstrap an agent session (spec §4.4)."""
import hashlib
import re
from datetime import date
from pathlib import Path

from harness import REPO, HarnessError, context, doctor, events, gitio, spool, taskfiles

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def add_args(p) -> None:
    p.add_argument("--new", metavar="SLUG", help="register a new task (run by you, before the agent)")
    p.add_argument("--benchmark-tier", choices=("S", "M", "L"))
    p.add_argument("--request", type=Path, help="the task text, in a file outside the worktree")


def run(args, ctx) -> int:
    return new_task(args, ctx) if args.new else bootstrap(ctx)


def new_task(args, ctx) -> int:
    if not args.benchmark_tier or not args.request:
        raise HarnessError("--new needs --benchmark-tier S|M|L and --request <file>")
    if not SLUG_RE.match(args.new):
        raise HarnessError("the slug must be lowercase letters, digits and dashes")
    try:
        request = args.request.expanduser().read_bytes()
    except OSError as e:
        raise HarnessError(f"cannot read {args.request}: {e}") from e
    ctx.require_project()
    task_id = f"{date.today().isoformat()}-{args.new}"
    results = doctor.run(doctor.agent_install() + doctor.PRE_START, ctx, task_id)
    if not doctor.passed(results):
        print(doctor.format(results))
        return 1
    with spool.locked(ctx.state_dir):  # uniqueness check, assignment and `start` under one lock (§9.3)
        results = doctor.run([doctor.probe_unused], ctx, task_id)
        if not doctor.passed(results):
            print(doctor.format(results))
            return 1
        folder = taskfiles.task_dir(ctx.root, task_id)
        folder.mkdir(parents=True)
        (folder / "request.md").write_bytes(request)
        taskfiles.write_json(folder / "state.json", {
            "task_id": task_id, "branch": ctx.git.branch, "phase": None, "phase_open": False,
            "controlling_session": None, "created_at": events.now_ts()})
        context.record(ctx, context.event(
            ctx, "start", task_id, benchmark_tier=args.benchmark_tier,
            request_sha256=hashlib.sha256(request).hexdigest(),
            arm="baseline", assigned_commit=gitio.harness_version()), held=True)
    print(f"task {task_id} registered; the clock is running.\nharness checkout: {REPO}")
    return 0


def bootstrap(ctx) -> int:
    if ctx.git is None or ctx.project is None:
        return 0  # not a harness project: silent (§4.4)
    branch, rev = gitio.effective_branch(ctx.cwd, ctx.git)
    ids = taskfiles.find_by_branch(ctx.root, branch, rev) if branch else []
    if not ids:
        return 0  # no task on this branch: silent (§4.4)
    if len(ids) > 1:
        raise HarnessError(f"several tasks name branch {branch}: {ids}")
    task_id = ids[0]
    if ctx.identity.delegate:
        print(f"delegate of task {task_id}: follow your prompt")
        return 0
    probes = doctor.agent_install() + [doctor.probe_not_cloud, doctor.probe_session_live]
    results = doctor.run(probes, ctx, task_id)
    context.record(ctx, context.event(ctx, "doctor", task_id, checks={n: ok for n, ok, _ in results}))
    context.record(ctx, context.event(ctx, "resume", task_id))
    if not doctor.passed(results):
        print(doctor.format(results))
        print("Fix the failures above, then relaunch the agent in this worktree. Do not start triage.")
        return 1
    print(f"task {task_id}\nharness checkout: {REPO}\nNow read {REPO / 'AGENTS.md'}.")
    return 0
```

- [ ] **Step 6: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_start -v`
Expected: 8 tests, OK.

- [ ] **Step 7: Commit**

```bash
git add harness/commands/start.py harness/cli.py tests/helpers.py tests/test_start.py
git commit -m "feat: start --new registration and bootstrap start"
```

### Task 1.12: `phase`

**Files:**
- Create: `harness/commands/phase.py`, `tests/test_phase.py`
- Modify: `harness/cli.py` (register `phase`), `tests/helpers.py` (add `write_plan`, `commit`, `Sandbox.through_triage`, `Sandbox.task_file_events`)

**Interfaces:**
- Consumes: `context`, `taskfiles`
- Produces: `phase.PHASES`; `phase.enter(ctx, task_id: str, name: str) -> None`; `phase.exit_phase(ctx, task_id: str, name: str, handoff: bool = False) -> None`. Test helpers: `write_plan(wt, task_id, checks: dict[str, str | None], tier="M", goal="Add a greeting.")`; `commit(wt, message)`; `Sandbox.through_triage(slug, checks, tier="M", session="S1") -> (wt, env, task_id)`; `Sandbox.task_file_events(wt, task_id) -> list[dict]`

Spec: §5.1 (contiguous phases: an `enter` on a still-open phase writes the missing exit first), §5.2 (triage enter gated on doctor; first build enter snapshots `plan.approved.md`), §6.3, §6.4, §6.6 (copies at triage exit), §6.9 (controlling session; manual commands record null), §7 `phase` row (refuses on the default branch, for delegates, and for triage without a passing check E), R-3.

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `phase` and add `"phase": Command(phase, controller_only=True),`.

- [ ] **Step 2: Add the test helpers**

Append to `tests/helpers.py` (module level):

```python
from harness import taskfiles


def write_plan(wt, task_id, checks, tier="M", goal="Add a greeting.") -> None:
    """plan.md with the given checks (id → command; None = observational) and a matching config.json."""
    entries = []
    for cid, command in checks.items():
        if command is None:
            entries.append(f"### {cid} — {cid} looks right (observational)\nExpected: it looks right.\n")
        else:
            entries.append(f"### {cid} — {cid} passes\nExpected: exit 0.\n```sh\n{command}\n```\n")
    folder = taskfiles.task_dir(wt, task_id)
    (folder / "plan.md").write_text(
        f"# {task_id}\n\n## Goal\n{goal}\n\n## Outcome\nIt works.\n\n## Acceptance checks\n\n"
        + "\n".join(entries) + f"\n## Tier\n{tier}\n\n## Source\nprompt\n\n## Decisions\n\n## Unknowns\n\n## Friction\n")
    taskfiles.write_json(folder / "config.json", {
        "knobs": {"phases": ["triage", "build"], "phase_agent": {}, "evaluator_cadence": "none", "plan_review": False},
        "record": {"tier": tier, "triage_signals": {}}})


def commit(wt, message) -> None:
    git(wt, "add", "-A")
    git(wt, "commit", "-qm", message)
```

Add to `class Sandbox`:

```python
    def through_triage(self, slug, checks, tier="M", session="S1"):
        wt, env, task_id = self.begin_task(slug, tier, session)
        for action in ("enter", "exit"):
            if action == "exit":
                write_plan(wt, task_id, checks, tier)
            r = self.harness("phase", "triage", action, cwd=wt, env=env)
            assert r.returncode == 0, r.stdout + r.stderr
        commit(wt, "triage")
        return wt, env, task_id

    def task_file_events(self, wt, task_id) -> list[dict]:
        return spool.read_file(taskfiles.task_dir(wt, task_id) / "events.jsonl")
```

- [ ] **Step 3: Write the failing tests**

`tests/test_phase.py`:

```python
import unittest

from harness import gitio, spool, taskfiles
from tests.helpers import Sandbox, write_plan


class PhaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def phase(self, wt, env, *args):
        return self.sb.harness("phase", *args, cwd=wt, env=env)

    def phases(self, wt, task_id):
        return [(e["phase"], e["action"]) for e in self.sb.task_file_events(wt, task_id) if e["kind"] == "phase"]

    def test_triage_needs_this_sessions_passing_doctor(self):  # spec §5.2, §8
        wt, env, task_id = self.sb.begin_task("ph-doc")
        other = {**env, "HARNESS_SESSION_ID": "OTHER", "HARNESS_PARENT_SESSION": "OTHER"}
        r = self.phase(wt, other, "triage", "enter")
        self.assertEqual(r.returncode, 1)
        self.assertIn("harness start", r.stderr)
        self.assertEqual(self.phase(wt, env, "triage", "enter").returncode, 0)
        state = taskfiles.read_json(taskfiles.task_dir(wt, task_id) / "state.json")
        self.assertEqual((state["phase"], state["phase_open"], state["controlling_session"]), ("triage", True, "S1"))
        self.assertEqual(self.phases(wt, task_id), [("triage", "enter")])

    def test_refuses_on_the_default_branch(self):
        r = self.phase(self.sb.main, {}, "build", "enter")
        self.assertEqual(r.returncode, 1)
        self.assertIn("default branch", r.stderr)

    def test_delegate_is_refused(self):  # spec §9.5, Review Focus 2
        wt, env, _ = self.sb.begin_task("ph-deleg")
        r = self.phase(wt, {**env, "HARNESS_SESSION_ID": "CHILD"}, "triage", "enter")
        self.assertEqual(r.returncode, 1)
        self.assertIn("delegates", r.stderr)

    def test_enter_closes_the_open_phase_and_build_snapshots_once(self):  # spec §5.1, §5.2
        wt, env, task_id = self.sb.through_triage("ph-flow", {"C1": "true"})
        folder = taskfiles.task_dir(wt, task_id)
        self.phase(wt, env, "research", "enter")
        self.phase(wt, env, "build", "enter")
        self.assertEqual(self.phases(wt, task_id)[-3:], [("research", "enter"), ("research", "exit"), ("build", "enter")])
        approved = (folder / "plan.approved.md").read_text()
        self.assertEqual(approved, (folder / "plan.md").read_text())
        (folder / "plan.md").write_text(approved + "- later note\n")
        self.phase(wt, env, "verify", "enter")
        self.phase(wt, env, "build", "enter")
        self.assertEqual((folder / "plan.approved.md").read_text(), approved)

    def test_triage_exit_stamps_config_and_copies_to_the_state_dir(self):  # spec §6.3, §6.6, R-3
        wt, env, task_id = self.sb.through_triage("ph-cfg", {"C1": "true"})
        record = taskfiles.read_json(taskfiles.task_dir(wt, task_id) / "config.json")["record"]
        self.assertEqual((record["benchmark_tier"], record["arm"], record["assigned_commit"], record["origin_tier"],
                          record["predicted_knobs"]), ("M", "baseline", gitio.harness_version(), "M", None))
        copies = spool.project_dir(self.sb.env, gitio.info(wt).common_dir) / "tasks" / task_id
        self.assertTrue((copies / "request.md").exists() and (copies / "config.json").exists())

    def test_implicit_triage_exit_also_stamps_config(self):  # spec §5.1, R-3
        wt, env, task_id = self.sb.begin_task("ph-implicit")
        self.phase(wt, env, "triage", "enter")
        write_plan(wt, task_id, {"C1": "true"})
        self.assertEqual(self.phase(wt, env, "research", "enter").returncode, 0)
        record = taskfiles.read_json(taskfiles.task_dir(wt, task_id) / "config.json")["record"]
        self.assertEqual((record["arm"], record["origin_tier"]), ("baseline", "M"))
        self.assertEqual(self.phases(wt, task_id), [("triage", "enter"), ("triage", "exit"), ("research", "enter")])

    def test_triage_exit_refuses_without_config(self):
        wt, env, task_id = self.sb.begin_task("ph-nocfg")
        self.phase(wt, env, "triage", "enter")
        r = self.phase(wt, env, "triage", "exit")
        self.assertEqual(r.returncode, 1)
        self.assertIn("config.json", r.stderr)
        self.assertTrue(taskfiles.read_json(taskfiles.task_dir(wt, task_id) / "state.json")["phase_open"])

    def test_exit_of_a_closed_phase_is_refused_and_handoff_is_recorded(self):
        wt, env, task_id = self.sb.through_triage("ph-exit", {"C1": "true"})
        self.assertEqual(self.phase(wt, env, "build", "exit").returncode, 1)
        self.phase(wt, env, "build", "enter")
        self.assertEqual(self.phase(wt, env, "build", "exit", "--handoff").returncode, 0)
        last = [e for e in self.sb.task_file_events(wt, task_id) if e["kind"] == "phase"][-1]
        self.assertEqual((last["phase"], last["action"], last["handoff"]), ("build", "exit", True))

    def test_manual_build_enter_records_a_null_controller(self):  # spec §6.9
        wt, env, task_id = self.sb.through_triage("ph-manual", {"C1": "true"})
        self.assertEqual(self.phase(wt, {}, "build", "enter").returncode, 0)
        state = taskfiles.read_json(taskfiles.task_dir(wt, task_id) / "state.json")
        self.assertIsNone(state["controlling_session"])
```

`test_manual_build_enter_records_a_null_controller` resolves the task by branch: the sandbox env carries no `HARNESS_TASK_ID`, as in your own terminal.

- [ ] **Step 4: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_phase -v`
Expected: FAIL (`phase` is not a registered command).

- [ ] **Step 5: Write the implementation**

`harness/commands/phase.py`:

```python
"""Enter or exit a workflow phase; records the controlling session (spec §5.1, §6.4, §6.9)."""
import shutil

from harness import HarnessError, context, taskfiles

PHASES = ("triage", "research", "resolve", "plan", "build", "verify", "retro")
TIERS = ("S", "M", "L")


def add_args(p) -> None:
    p.add_argument("name", choices=PHASES)
    p.add_argument("action", choices=("enter", "exit"))
    p.add_argument("--handoff", action="store_true", help="control returns to you after this exit")


def run(args, ctx) -> int:
    project = ctx.require_project()
    if ctx.git.branch is None or ctx.git.branch == project["default_branch"]:
        raise HarnessError("`harness phase` refuses on the default branch; run it on the task's branch")
    task_id = taskfiles.resolve(ctx.root, ctx.cwd, ctx.env, ctx.git)
    if args.action == "enter":
        enter(ctx, task_id, args.name)
    else:
        exit_phase(ctx, task_id, args.name, handoff=args.handoff)
    return 0


def _folder(ctx, task_id: str):
    folder = taskfiles.task_dir(ctx.root, task_id)
    if not (folder / "state.json").exists():
        raise HarnessError(f"task {task_id} has no folder in this checkout; run this in the task's worktree")
    return folder


def enter(ctx, task_id: str, name: str) -> None:
    folder = _folder(ctx, task_id)
    state = taskfiles.read_json(folder / "state.json")
    if name == "triage" and not _doctor_passed(ctx, task_id):
        raise HarnessError("run `harness start` first: triage needs this session's passing doctor check")
    snapshot = name == "build" and not (folder / "plan.approved.md").exists()
    if snapshot and not (folder / "plan.md").exists():
        raise HarnessError("plan.md is missing; triage writes it")
    if state["phase_open"]:
        if state["phase"] == "triage":
            _finish_triage(ctx, task_id, folder)  # an implicit triage exit stamps and copies too (R-3, §6.6)
        _write(ctx, task_id, folder, state, state["phase"], "exit", False)  # phases are contiguous (§5.1)
    if snapshot:
        shutil.copyfile(folder / "plan.md", folder / "plan.approved.md")  # first build entry only (§5.2)
    _write(ctx, task_id, folder, state, name, "enter", False)
    print(f"{name}: entered")


def exit_phase(ctx, task_id: str, name: str, handoff: bool = False) -> None:
    folder = _folder(ctx, task_id)
    state = taskfiles.read_json(folder / "state.json")
    if not state["phase_open"] or state["phase"] != name:
        raise HarnessError(f"phase {name} is not open (open: {state['phase'] if state['phase_open'] else 'none'})")
    if name == "triage":
        _finish_triage(ctx, task_id, folder)
    _write(ctx, task_id, folder, state, name, "exit", handoff)
    print(f"{name}: exited")


def _write(ctx, task_id, folder, state, name, action, handoff) -> None:
    sid = ctx.identity.session_id  # null for your own manual commands (§6.9)
    context.record(ctx, context.event(ctx, "phase", task_id, phase=name, action=action, handoff=handoff,
                                      controlling_session=sid))
    state.update(phase=name, phase_open=action == "enter")
    if action == "enter":
        state["controlling_session"] = sid
    taskfiles.write_json(folder / "state.json", state)


def _doctor_passed(ctx, task_id: str) -> bool:
    sid = ctx.identity.session_id
    docs = [e for e in context.task_events(ctx, task_id) if e.get("kind") == "doctor" and e.get("session_id") == sid]
    return sid is not None and bool(docs) and all(docs[-1].get("checks", {}).values())


def _finish_triage(ctx, task_id: str, folder) -> None:
    """Fill the harness-owned record fields and copy the triage files to the state dir (R-3, §6.6)."""
    path = folder / "config.json"
    if not path.exists():
        raise HarnessError("write config.json before `harness phase triage exit` (see skills/phases/triage.md)")
    config = taskfiles.read_json(path)
    record = config.setdefault("record", {})
    if record.get("tier") not in TIERS:
        raise HarnessError("config.json record.tier must be S, M or L")
    start = next((e for e in context.task_events(ctx, task_id) if e.get("kind") == "start"), None)
    if start is None:
        raise HarnessError(f"no start event for {task_id} in this machine's spool")
    record.update(benchmark_tier=start["benchmark_tier"], arm=start["arm"], assigned_commit=start["assigned_commit"])
    record.setdefault("origin_tier", record["tier"])
    record.setdefault("predicted_knobs", None)
    taskfiles.write_json(path, config)
    taskfiles.copy_to_state(folder, ctx.state_dir / "tasks" / task_id)
```

- [ ] **Step 6: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_phase -v`
Expected: 9 tests, OK.

- [ ] **Step 7: Commit**

```bash
git add harness/commands/phase.py harness/cli.py tests/helpers.py tests/test_phase.py
git commit -m "feat: phase enter/exit with triage gating and approval snapshot"
```

### Task 1.13: Readiness and done gate (pure)

**Files:**
- Create: `harness/gate.py`, `tests/test_gate.py`

**Interfaces:**
- Consumes: `planfile.checks`, `planfile.check_hash`, `planfile.diff`, `planfile.decision_refs`
- Produces: `gate.needs_build_enter(events: list[dict]) -> bool`; `gate.failing_checks(plan_text: str, events: list[dict], code_tree: str | None, before_ts: str | None = None) -> list[str]`; `gate.Gate(passed: bool, reasons: tuple[str, ...], scope_reductions: tuple[str, ...])`; `gate.evaluate(final_plan: str | None, approved_plan: str | None, events: list[dict], merge_code_tree: str | None) -> Gate`

Spec: §6.11 (done gate), §5.7 (a re-plan changes a check only with a Decision naming it), parent (post-`ready` refusal, R-5; scope reduction needs `close --done`), §7 `pr` (refuses on failing or stale checks).

- [ ] **Step 1: Write the failing tests**

`tests/test_gate.py`:

```python
import unittest

from harness import gate, planfile
from tests.test_planfile import PLAN

C1 = planfile.check_hash(planfile.checks(PLAN)["C1"])
C2 = planfile.check_hash(planfile.checks(PLAN)["C2"])


def ev(kind, second, **fields):
    return {"kind": kind, "ts": f"2026-10-08T12:00:{second:02d}.000Z", **fields}


def check(second, cid, result="pass", tree="T1", text_hash=None):
    return ev("check", second, check_id=cid, result=result, code_tree=tree,
              check_text_hash=text_hash or {"C1": C1, "C2": C2}[cid])


PASSING = [check(1, "C1"), check(2, "C2"), ev("ready", 3, code_tree="T1")]


class GateTest(unittest.TestCase):
    def test_needs_build_enter_after_ready(self):  # R-5
        self.assertFalse(gate.needs_build_enter([]))
        self.assertTrue(gate.needs_build_enter([ev("ready", 1)]))
        enter = ev("phase", 2, phase="build", action="enter")
        self.assertFalse(gate.needs_build_enter([ev("ready", 1), enter]))
        self.assertTrue(gate.needs_build_enter([ev("ready", 1), enter, ev("ready", 3)]))

    def test_failing_checks(self):
        self.assertEqual(gate.failing_checks(PLAN, PASSING, "T1"), [])
        self.assertEqual(gate.failing_checks(PLAN, [check(1, "C1")], "T1"), ["C2: no recorded attempt"])
        later_fail = [check(1, "C1"), check(2, "C2"), check(4, "C1", "fail")]
        self.assertEqual(gate.failing_checks(PLAN, later_fail, "T1"), ["C1: latest attempt fail"])
        self.assertEqual(gate.failing_checks(PLAN, later_fail, "T1", before_ts="2026-10-08T12:00:03.000Z"), [])
        self.assertIn("another code tree", gate.failing_checks(PLAN, PASSING, "T2")[0])
        stale = [check(1, "C1", text_hash="old"), check(2, "C2")]
        self.assertIn("text changed", gate.failing_checks(PLAN, stale, "T1")[0])

    def test_gate_passes_when_merged_tree_matches_and_checks_passed(self):
        self.assertEqual(gate.evaluate(PLAN, PLAN, PASSING, "T1"), gate.Gate(True, (), ()))

    def test_gate_fails_when_merged_code_differs_or_not_merged(self):  # spec §6.11
        self.assertIn("differs", gate.evaluate(PLAN, PLAN, PASSING, "T9").reasons[0])
        self.assertIn("not merged", gate.evaluate(PLAN, PLAN, PASSING, None).reasons)

    def test_changed_check_needs_a_decision_and_scope_reduction_needs_close_done(self):
        approved = PLAN.replace("## Tier", "### C3 — old\nExpected: x.\n```sh\ntrue\n```\n\n## Tier")
        result = gate.evaluate(PLAN, approved, PASSING, "T1")  # PLAN's Decisions name C3
        self.assertEqual(result.scope_reductions, ("C3",))
        self.assertEqual(result.reasons, ("scope reduction (C3) not confirmed with `harness close --done`",))
        confirmed = gate.evaluate(PLAN, approved, PASSING + [ev("close", 9, disposition="done")], "T1")
        self.assertTrue(confirmed.passed)
        no_decision = PLAN.replace("[Check: C3]", "")
        self.assertIn("C3 changed since approval without a Decision naming it",
                      gate.evaluate(no_decision, approved, PASSING, "T1").reasons)
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_gate -v`
Expected: FAIL with `ImportError: cannot import name 'gate'`.

- [ ] **Step 3: Write the implementation**

`harness/gate.py`:

```python
"""Readiness pre-check, the post-`ready` rule and the done gate (spec §6.11). Pure."""
from dataclasses import dataclass

from harness import planfile


def _of(events: list[dict], kind: str) -> list[dict]:
    return [e for e in events if e.get("kind") == kind]


def needs_build_enter(events: list[dict]) -> bool:
    """True while the last `ready` is later than the last `phase build enter` (R-5)."""
    readies = [e["ts"] for e in _of(events, "ready")]
    if not readies:
        return False
    enters = [e["ts"] for e in _of(events, "phase") if e.get("phase") == "build" and e.get("action") == "enter"]
    return not enters or max(enters) < max(readies)


def failing_checks(plan_text: str, events: list[dict], code_tree: str | None, before_ts: str | None = None) -> list[str]:
    """Final checks whose latest completed attempt (before before_ts) did not pass at code_tree
    with the check text in plan_text. A check with no attempt fails (§6.11)."""
    final = planfile.checks(plan_text)
    if not final:
        return ["plan.md has no acceptance checks"]
    attempts = [e for e in _of(events, "check") if before_ts is None or e["ts"] < before_ts]
    reasons = []
    for cid, check in final.items():
        mine = [e for e in attempts if e.get("check_id") == cid]
        if not mine:
            reasons.append(f"{cid}: no recorded attempt")
            continue
        last = max(mine, key=lambda e: e["ts"])
        if last.get("result") != "pass":
            reasons.append(f"{cid}: latest attempt {last.get('result')}")
        elif last.get("code_tree") != code_tree:
            reasons.append(f"{cid}: latest pass ran on another code tree")
        elif last.get("check_text_hash") != planfile.check_hash(check):
            reasons.append(f"{cid}: check text changed since its latest pass")
    return reasons


@dataclass(frozen=True)
class Gate:
    passed: bool
    reasons: tuple[str, ...]
    scope_reductions: tuple[str, ...]


def evaluate(final_plan: str | None, approved_plan: str | None, events: list[dict],
             merge_code_tree: str | None) -> Gate:
    if final_plan is None:
        return Gate(False, ("plan.md not found on the integration branch",), ())
    reasons = []
    if merge_code_tree is None:
        reasons.append("not merged")
    readies = _of(events, "ready")
    if not readies:
        reasons.append("no ready event")
    else:
        last = max(readies, key=lambda e: e["ts"])
        if merge_code_tree is not None and last.get("code_tree") != merge_code_tree:
            reasons.append("merged code differs from the last ready tip (run `harness pr --refresh` before merging)")
        reasons += failing_checks(final_plan, events, last.get("code_tree"), before_ts=last["ts"])
    scope: tuple[str, ...] = ()
    if approved_plan is None:
        reasons.append("plan.approved.md not found")
    else:
        d = planfile.diff(approved_plan, final_plan)
        named = planfile.decision_refs(final_plan)
        reasons += [f"{x} changed since approval without a Decision naming it" for x in sorted(d.changed() - named)]
        scope = d.scope_reductions()
        if scope and not any(e.get("disposition") == "done" for e in _of(events, "close")):
            reasons.append(f"scope reduction ({', '.join(scope)}) not confirmed with `harness close --done`")
    return Gate(not reasons, tuple(reasons), scope)
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_gate -v`
Expected: 5 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/gate.py tests/test_gate.py
git commit -m "feat: readiness pre-check and done gate"
```

### Task 1.14: `check`

**Files:**
- Create: `harness/commands/check.py`, `tests/test_check.py`
- Modify: `harness/cli.py` (register `check`)

**Interfaces:**
- Consumes: `context`, `taskfiles.resolve`, `planfile.checks/check_hash`, `gate.needs_build_enter`, `gitio.code_tree/dirty_outside_harness`
- Produces: `check.run_one(ctx, task_id: str, check: planfile.Check, observed: str | None = None) -> str` (`"pass"` or `"fail"`)

Spec: §5.3 (who ran each check: session id, delegate flag), §5.7, §6.7 `check` fields, §6.9 (delegates may run `check`, including `--observed`), §6.11 (code tree without writing objects), §7 `check` row (refuses when the checkout is not clean outside `.harness/` before or after), R-5, R-6, R-13.

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `check` and add `"check": Command(check),`.

- [ ] **Step 2: Write the failing tests**

`tests/test_check.py`:

```python
import unittest

from harness import events, gitio, planfile, spool, taskfiles
from tests.helpers import Sandbox, git


class CheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()
        cls.wt, cls.env, cls.task_id = cls.sb.through_triage(
            "chk", {"C1": "test -f README.md", "C2": "false", "C3": None, "C4": "touch made-by-check.txt"})

    def check(self, *args, env=None, cwd=None):
        return self.sb.harness("check", *args, cwd=cwd or self.wt, env=env or self.env)

    def checks_recorded(self, cid):
        return [e for e in self.sb.spool(self.wt) if e["kind"] == "check" and e["check_id"] == cid]

    def test_runnable_check_records_tree_hash_and_session(self):
        before = len(self.checks_recorded("C1"))
        r = self.check("C1")
        self.assertEqual(r.returncode, 0, r.stderr)
        e = self.checks_recorded("C1")[-1]
        plan = (taskfiles.task_dir(self.wt, self.task_id) / "plan.md").read_text()
        self.assertEqual((e["result"], e["mode"], e["exit_code"], e["delegate"], e["session_id"]),
                         ("pass", "run", 0, False, "S1"))
        self.assertEqual(e["code_tree"], gitio.code_tree(self.wt))
        self.assertEqual(e["check_text_hash"], planfile.check_hash(planfile.checks(plan)["C1"]))
        self.assertEqual(len(self.checks_recorded("C1")), before + 1)
        self.assertIn(e, self.sb.task_file_events(self.wt, self.task_id))

    def test_failing_check_records_fail(self):
        r = self.check("C2")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.checks_recorded("C2")[-1]["result"], "fail")

    def test_dirty_checkout_is_refused_and_nothing_recorded(self):  # spec §7
        before = len(self.checks_recorded("C1"))
        stray = self.wt / "stray.txt"
        stray.write_text("x")
        self.addCleanup(stray.unlink)
        r = self.check("C1")
        self.assertEqual(r.returncode, 1)
        self.assertIn("not clean", r.stderr)
        self.assertEqual(len(self.checks_recorded("C1")), before)

    def test_check_that_changes_the_checkout_is_not_recorded(self):  # R-13, Review Focus 4
        self.addCleanup(lambda: (self.wt / "made-by-check.txt").unlink(missing_ok=True))
        r = self.check("C4")
        self.assertEqual(r.returncode, 1)
        self.assertIn("changed the checkout", r.stderr)
        self.assertEqual(self.checks_recorded("C4"), [])

    def test_observational_check_needs_observed_and_runnable_refuses_it(self):  # spec §5.7
        self.assertIn("--observed", self.check("C3").stderr)
        self.assertEqual(self.check("C1", "--observed", "pass").returncode, 1)
        self.assertEqual(self.check("C3", "--observed", "pass").returncode, 0)
        e = self.checks_recorded("C3")[-1]
        self.assertEqual((e["mode"], e["result"], e["exit_code"]), ("observed", "pass", None))

    def test_all_runs_runnable_checks_and_skips_observational(self):
        wt, env, _ = self.sb.through_triage("chk-all", {"C1": "true", "C2": None})
        r = self.sb.harness("check", "--all", cwd=wt, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("skip C2", r.stdout)

    def test_delegate_check_is_flagged(self):  # spec §6.9, Review Focus 2
        self.assertEqual(self.check("C1", env={**self.env, "HARNESS_SESSION_ID": "CHILD"}).returncode, 0)
        e = self.checks_recorded("C1")[-1]
        self.assertEqual((e["session_id"], e["parent_session"], e["delegate"]), ("CHILD", "S1", True))

    def test_check_from_another_branch_goes_to_the_spool_only(self):  # R-6
        other = self.sb.tmp / "chk-other"
        git(self.wt, "worktree", "add", "-q", "-b", "chk-tmp", str(other), "HEAD", env=self.sb.env)
        before = len(self.sb.task_file_events(self.wt, self.task_id))
        r = self.check("--task", self.task_id, "C1", cwd=other, env={**self.env, "HARNESS_SESSION_ID": "SUB"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.checks_recorded("C1")[-1]["branch"], "chk-tmp")
        self.assertEqual(len(self.sb.task_file_events(self.wt, self.task_id)), before)
        self.assertFalse((taskfiles.task_dir(other, self.task_id) / "events.jsonl").exists())

    def test_after_ready_checks_need_a_build_enter(self):  # R-5
        wt, env, task_id = self.sb.through_triage("chk-ready", {"C1": "true"})
        state_dir = spool.project_dir(self.sb.env, gitio.info(wt).common_dir)
        spool.append(state_dir, events.make("ready", "cli", events.now_ts(), task_id=task_id))
        r = self.sb.harness("check", "C1", cwd=wt, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("build enter", r.stderr)
        self.sb.harness("phase", "build", "enter", cwd=wt, env=env)
        git(wt, "add", "-A")
        git(wt, "commit", "-qm", "build enter")
        self.assertEqual(self.sb.harness("check", "C1", cwd=wt, env=env).returncode, 0)
```

In `test_check_from_another_branch_goes_to_the_spool_only`, the plan files are committed by `through_triage`, so the second worktree has the task folder. The sandbox session env carries `HARNESS_TASK_ID`, and `--task` is passed explicitly as a delegate in a temporary worktree would.

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_check -v`
Expected: FAIL (`check` is not a registered command).

- [ ] **Step 4: Write the implementation**

`harness/commands/check.py`:

```python
"""Run an acceptance check, or record an observation, against a clean checkout (spec §5.7, §6.11)."""
import subprocess
import time

from harness import HarnessError, context, gate, gitio, planfile, taskfiles


def add_args(p) -> None:
    p.add_argument("check_id", nargs="?", help="C1, C2, …")
    p.add_argument("--all", action="store_true", help="every runnable check")
    p.add_argument("--task", help="task id (for delegates outside the task's branch)")
    p.add_argument("--observed", choices=("pass", "fail"), help="record an observational check")


def run(args, ctx) -> int:
    if bool(args.check_id) == args.all:
        raise HarnessError("give one check id or --all")
    if args.all and args.observed:
        raise HarnessError("--observed records one check at a time")
    ctx.require_project()
    task_id = taskfiles.resolve(ctx.root, ctx.cwd, ctx.env, ctx.git, explicit=args.task)
    plan_path = taskfiles.task_dir(ctx.root, task_id) / "plan.md"
    if not plan_path.exists():
        raise HarnessError(f"{plan_path} not found in this checkout")
    if gate.needs_build_enter(context.task_events(ctx, task_id)):
        raise HarnessError("after `ready`, run `harness phase build enter` before any check")
    checks = planfile.checks(plan_path.read_text())
    if args.all:
        targets = [c for c in checks.values() if c.command]
        for c in checks.values():
            if not c.command:
                print(f"skip {c.id}: observational; record it with `harness check {c.id} --observed pass|fail`")
    elif args.check_id in checks:
        targets = [checks[args.check_id]]
    else:
        raise HarnessError(f"{args.check_id} is not in {plan_path}")
    results = [run_one(ctx, task_id, c, args.observed) for c in targets]
    return 0 if all(r == "pass" for r in results) else 1


def _clean_head(root) -> str:
    dirty = gitio.dirty_outside_harness(root)
    if dirty:
        raise HarnessError("checkout not clean outside .harness/; commit first:\n" + "\n".join(dirty))
    return gitio.out(["rev-parse", "HEAD"], root)


def run_one(ctx, task_id: str, check: planfile.Check, observed: str | None = None) -> str:
    root = ctx.root
    head = _clean_head(root)
    tree = gitio.code_tree(root)
    if observed:
        if not check.observational:
            raise HarnessError(f"{check.id} is runnable; run it without --observed")
        result, mode, exit_code, duration_ms = observed, "observed", None, None
    else:
        if not check.command:
            raise HarnessError(f"{check.id} has no fenced command; record it with --observed pass|fail")
        started = time.monotonic()
        exit_code = subprocess.run(["bash", "-c", check.command], cwd=root).returncode
        duration_ms = int((time.monotonic() - started) * 1000)
        result, mode = ("pass" if exit_code == 0 else "fail"), "run"
        if gitio.dirty_outside_harness(root) or gitio.out(["rev-parse", "HEAD"], root) != head:
            raise HarnessError(f"{check.id} changed the checkout; its result was not recorded (R-13)")
    context.record(ctx, context.event(
        ctx, "check", task_id, check_id=check.id, result=result, mode=mode, code_tree=tree,
        check_text_hash=planfile.check_hash(check), exit_code=exit_code, duration_ms=duration_ms,
        delegate=ctx.identity.delegate))
    print(f"{check.id}: {result}")
    return result
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_check -v`
Expected: 9 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/commands/check.py harness/cli.py tests/test_check.py
git commit -m "feat: check command with clean-checkout and code-tree rules"
```

### Task 1.15: `rebase` (no memory cleanup)

**Files:**
- Create: `harness/commands/rebase.py`, `tests/test_rebase.py`
- Modify: `harness/cli.py` (register `rebase`)

**Interfaces:**
- Consumes: `gitio.commit_paths/fetch/run/git_path/rebase_in_progress/dirty_outside_harness`
- Produces: `rebase.MARKER = "harness-rebase"`; `rebase.rebase(ctx, project: dict) -> str` (`"done"` or `"conflict"`); `rebase.abort(ctx) -> None`

Spec: §5.6 and parent (commit `.harness/`, fetch with retry, `rebase --merge`, conflict rerun flow: `GIT_EDITOR=true git rebase --continue`, only while git reports a rebase it started), §7 `rebase` row (memory cleanup is Slice 2), §9.7.

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `rebase` and add `"rebase": Command(rebase, during_rebase=_always),`.

- [ ] **Step 2: Write the failing tests**

`tests/test_rebase.py`:

```python
import unittest

from harness import gitio, taskfiles
from tests.helpers import Sandbox, commit, git


class RebaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def advance_main(self, path, text):
        (self.sb.main / path).write_text(text)
        commit(self.sb.main, f"main changes {path}")
        git(self.sb.main, "push", "-q", "origin", "main", env=self.sb.env)

    def test_clean_rebase_commits_harness_first_and_lands_on_main(self):
        wt, env, task_id = self.sb.through_triage("rb-clean", {"C1": "true"})
        (wt / "feature.txt").write_text("f\n")
        commit(wt, "feature")
        plan = taskfiles.task_dir(wt, task_id) / "plan.md"
        plan.write_text(plan.read_text() + "- note before rebase\n")  # uncommitted .harness change
        self.advance_main("other.txt", "o\n")
        r = self.sb.harness("rebase", cwd=wt, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(gitio.status_clean(wt))
        self.assertEqual(git(wt, "rev-list", "HEAD..origin/main"), "")
        self.assertFalse(gitio.git_path(wt, "harness-rebase").exists())

    def test_dirty_code_is_refused(self):
        wt, env, _ = self.sb.through_triage("rb-dirty", {"C1": "true"})
        (wt / "loose.txt").write_text("x")
        r = self.sb.harness("rebase", cwd=wt, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not clean", r.stderr)

    def test_conflict_stops_guards_and_reruns(self):  # spec §9.7
        wt, env, task_id = self.sb.through_triage("rb-conflict", {"C1": "true"})
        (wt / "README.md").write_text("task version\n")
        commit(wt, "task edits README")
        self.advance_main("README.md", "main version\n")
        r = self.sb.harness("rebase", cwd=wt, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("rerun `harness rebase`", r.stdout)
        self.assertTrue(gitio.rebase_in_progress(wt))
        blocked = self.sb.harness("phase", "build", "enter", cwd=wt, env=env)
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("rebase is stopped", blocked.stderr)
        self.assertEqual(self.sb.harness("check", "C1", cwd=wt, env=env).returncode, 1)
        start = self.sb.harness("start", cwd=wt, env=env)
        self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
        self.assertIn(task_id, start.stdout)
        (wt / "README.md").write_text("resolved\n")
        git(wt, "add", "README.md")
        r = self.sb.harness("rebase", cwd=wt, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(gitio.rebase_in_progress(wt))
        self.assertEqual((wt / "README.md").read_text(), "resolved\n")
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_rebase -v`
Expected: FAIL (`rebase` is not a registered command).

- [ ] **Step 4: Write the implementation**

`harness/commands/rebase.py`:

```python
"""Commit .harness/, fetch, `rebase --merge` onto the integration branch; rerun after conflicts (§5.6, §7)."""
import os

from harness import HarnessError, gitio

MARKER = "harness-rebase"  # in the worktree's git dir: this rebase was started by harness


def add_args(p) -> None:
    pass


def run(args, ctx) -> int:
    if rebase(ctx, ctx.require_project()) == "conflict":
        print("rebase stopped on conflicts: resolve them, `git add` the files, then rerun `harness rebase`. "
              "Run no other harness command meanwhile (plain `harness start` is fine).")
        return 1
    print("rebased onto the integration branch")
    return 0


def rebase(ctx, project: dict) -> str:
    root = ctx.root
    marker = gitio.git_path(root, MARKER)
    env = {**os.environ, "GIT_EDITOR": "true"}
    if gitio.rebase_in_progress(root):
        if not marker.exists():
            raise HarnessError("a rebase not started by harness is in progress; finish or abort it with git")
        result = gitio.run(["rebase", "--continue"], root, env=env, check=False)
    else:
        dirty = gitio.dirty_outside_harness(root)
        if dirty:
            raise HarnessError("checkout not clean outside .harness/; commit first:\n" + "\n".join(dirty))
        gitio.commit_paths(root, ".harness", "harness: record before rebase")
        remote, branch = project["integration_remote"], project["default_branch"]
        gitio.fetch(root, remote, branch)
        marker.write_text("1\n")
        result = gitio.run(["rebase", "--merge", f"{remote}/{branch}"], root, env=env, check=False)
    if gitio.rebase_in_progress(root):
        return "conflict"
    marker.unlink(missing_ok=True)
    if result.returncode != 0:
        raise HarnessError(f"git rebase failed: {result.stderr.strip()}")
    return "done"


def abort(ctx) -> None:
    gitio.run(["rebase", "--abort"], ctx.root)
    gitio.git_path(ctx.root, MARKER).unlink(missing_ok=True)
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_rebase -v`
Expected: 3 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/commands/rebase.py harness/cli.py tests/test_rebase.py
git commit -m "feat: rebase with conflict rerun flow"
```

### Task 1.16: `pr` and `pr --refresh`

**Files:**
- Create: `harness/commands/pr.py`, `tests/test_pr.py`
- Modify: `harness/cli.py` (register `pr`)

**Interfaces:**
- Consumes: `phase.enter/exit_phase`, `check.run_one`, `rebase.rebase/abort`, `gate.needs_build_enter/failing_checks`, `planfile`, `ghio.pr_create/pr_edit_body`, `gitio.commit_paths/push/code_tree`
- Produces: `pr.publish(ctx, project, task_id) -> int`; `pr.refresh(ctx, project, task_id) -> int`; `pr.pr_body(task_id, plan, scope) -> str`; `pr.title(plan, task_id) -> str`

Spec: §5.2 (PR row; after `ready`: re-entry, re-emit without a second PR, `--refresh` before merging), §6.7 `ready` and `pr` fields, §7 `pr` and `pr --refresh` rows, parent (scope-reduction flag in the PR; a failed final push is finished with `git push <remote> HEAD`; a `ready` writes the missing exit first), R-1, R-14, R-15.

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `pr` and add `"pr": Command(pr, controller_only=True),`.

- [ ] **Step 2: Write the failing tests**

`tests/test_pr.py`:

```python
import unittest

from harness import gitio, taskfiles
from tests.helpers import Sandbox, commit, git, write_plan


class PrTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def h(self, wt, env, *args):
        return self.sb.harness(*args, cwd=wt, env=env)

    def gh_log(self):
        path = self.sb.tmp / "gh.log"
        return path.read_text() if path.exists() else ""

    def built(self, slug, checks=None, edit=("feature.txt", "f\n")):
        """A task through build and verify with passing checks, ready for `harness pr`."""
        wt, env, task_id = self.sb.through_triage(slug, checks or {"C1": "true"})
        self.h(wt, env, "phase", "build", "enter")
        (wt / edit[0]).write_text(edit[1])
        commit(wt, "build")
        self.h(wt, env, "phase", "verify", "enter")
        commit(wt, "verify enter")
        r = self.h(wt, env, "check", "--all")
        assert r.returncode == 0, r.stdout + r.stderr
        return wt, env, task_id

    def kinds(self, wt, task_id):
        return [(e["kind"], e.get("phase"), e.get("action")) for e in self.sb.task_file_events(wt, task_id)]

    def test_refuses_without_triage_enter(self):
        wt, env, task_id = self.sb.begin_task("pr-notriage")
        write_plan(wt, task_id, {"C1": "true"})
        commit(wt, "plan")
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 1)
        self.assertIn("triage enter", r.stderr)

    def test_refuses_failing_then_stale_checks(self):
        wt, env, task_id = self.sb.through_triage("pr-stale", {"C1": "test -f ok.txt"})
        self.h(wt, env, "check", "C1")
        self.assertIn("latest attempt fail", self.h(wt, env, "pr", task_id).stderr)
        (wt / "ok.txt").write_text("ok\n")
        commit(wt, "ok")
        self.h(wt, env, "check", "C1")
        (wt / "more.txt").write_text("more\n")
        commit(wt, "more code")
        self.assertIn("another code tree", self.h(wt, env, "pr", task_id).stderr)

    def test_publish_pushes_opens_one_pr_and_records_ready(self):
        wt, env, task_id = self.built("pr-pub")
        creates = self.gh_log().count("pr create")
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.gh_log().count("pr create"), creates + 1)
        kinds = self.kinds(wt, task_id)
        self.assertEqual(kinds[-3:], [("phase", "verify", "exit"), ("ready", None, None), ("pr", None, None)])
        ready = [e for e in self.sb.task_file_events(wt, task_id) if e["kind"] == "ready"][-1]
        self.assertEqual(ready["code_tree"], gitio.code_tree(wt))
        self.assertTrue(gitio.status_clean(wt))
        remote_tip = git(wt, "ls-remote", "origin", "refs/heads/task-pr-pub").split()[0]
        self.assertEqual(remote_tip, git(wt, "rev-parse", "HEAD"))
        self.assertFalse(taskfiles.read_json(taskfiles.task_dir(wt, task_id) / "state.json")["phase_open"])

    def test_reemit_needs_build_enter_and_opens_no_second_pr(self):  # spec §5.2
        wt, env, task_id = self.built("pr-again")
        creates = self.gh_log().count("pr create")
        self.h(wt, env, "pr", task_id)
        self.assertIn("build enter", self.h(wt, env, "pr", task_id).stderr)
        self.h(wt, env, "phase", "build", "enter")
        commit(wt, "revision")
        self.h(wt, env, "check", "--all")
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.gh_log().count("pr create"), creates + 1)
        self.assertIn("pr edit", self.gh_log())
        self.assertEqual(sum(k == "ready" for k, _, _ in self.kinds(wt, task_id)), 2)
        self.assertEqual(sum(k == "pr" for k, _, _ in self.kinds(wt, task_id)), 1)

    def test_scope_reduction_is_flagged_in_the_body(self):
        wt, env, task_id = self.sb.through_triage("pr-scope", {"C1": "true", "C2": "true"})
        self.h(wt, env, "phase", "build", "enter")
        plan = taskfiles.task_dir(wt, task_id) / "plan.md"
        text = plan.read_text()
        start = text.index("### C2")
        text = text[:start] + text[text.index("## Tier"):]
        text = text.replace("## Decisions\n", "## Decisions\n- 2026-10-08 12:00 · Claude/Opus 5.5 · build — Dropped C2. Why: moved to a follow-up. [Check: C2]\n")
        plan.write_text(text)
        commit(wt, "drop C2")
        self.h(wt, env, "check", "--all")
        r = self.h(wt, env, "pr", task_id)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Potential scope reduction", self.gh_log())
        self.assertIn(f"harness close {task_id} --done", self.gh_log())

    def test_refresh_rebases_rechecks_and_reemits(self):  # spec §7 pr --refresh
        wt, env, task_id = self.built("pr-refresh")
        self.h(wt, env, "pr", task_id)
        (self.sb.main / "unrelated.txt").write_text("u\n")
        commit(self.sb.main, "main moves")
        git(self.sb.main, "push", "-q", "origin", "main", env=self.sb.env)
        r = self.h(wt, {}, "pr", "--refresh", task_id)  # you, with no agent identity
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        evs = self.sb.task_file_events(wt, task_id)
        enters = [e for e in evs if e["kind"] == "phase" and e["action"] == "enter"]
        self.assertEqual((enters[-1]["phase"], enters[-1]["controlling_session"]), ("build", None))
        self.assertEqual(evs[-1]["kind"], "ready")
        self.assertTrue((wt / "unrelated.txt").exists())

    def test_refresh_conflict_aborts_and_hands_off(self):  # R-1
        wt, env, task_id = self.built("pr-conflict", edit=("README.md", "task version\n"))
        self.h(wt, env, "pr", task_id)
        (self.sb.main / "README.md").write_text("main version\n")
        commit(self.sb.main, "main edits README")
        git(self.sb.main, "push", "-q", "origin", "main", env=self.sb.env)
        r = self.h(wt, {}, "pr", "--refresh", task_id)
        self.assertEqual(r.returncode, 1)
        self.assertFalse(gitio.rebase_in_progress(wt))
        last = [e for e in self.sb.task_file_events(wt, task_id) if e["kind"] == "phase"][-1]
        self.assertEqual((last["phase"], last["action"], last["handoff"]), ("build", "exit", True))
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_pr -v`
Expected: FAIL (`pr` is not a registered command).

- [ ] **Step 4: Write the implementation**

`harness/commands/pr.py`:

```python
"""Open the task's PR and emit `ready`; `--refresh` rebases, rechecks and re-emits (spec §5.2, §7)."""
from harness import HarnessError, context, gate, ghio, gitio, planfile, taskfiles
from harness.commands import check, phase, rebase


def add_args(p) -> None:
    p.add_argument("task_id")
    p.add_argument("--refresh", action="store_true", help="before merging: rebase, recheck, re-emit ready")


def run(args, ctx) -> int:
    project = ctx.require_project()
    folder = taskfiles.task_dir(ctx.root, args.task_id)
    if not (folder / "state.json").exists():
        raise HarnessError(f"task {args.task_id} has no folder here; run this in the task's worktree")
    if taskfiles.read_json(folder / "state.json")["branch"] != ctx.git.branch:
        raise HarnessError("run `harness pr` on the task's branch")
    return refresh(ctx, project, args.task_id) if args.refresh else publish(ctx, project, args.task_id)


def title(plan: str, task_id: str) -> str:
    goal = planfile.goal(plan)
    return (goal.splitlines()[0] if goal else task_id)[:72]


def pr_body(task_id: str, plan: str, scope: tuple[str, ...]) -> str:
    lines = [f"Harness task `{task_id}`.", "", "## Goal", planfile.goal(plan), "", "## Acceptance checks"]
    lines += [f"- {c.text.splitlines()[0].removeprefix('### ')}" for c in planfile.checks(plan).values()]
    if scope:
        lines += ["", "## Potential scope reduction",
                  f"Changed since plan approval: {', '.join(scope)}.",
                  f"Merge only if the original outcome still holds, then run `harness close {task_id} --done`."]
    return "\n".join(lines) + "\n"


def publish(ctx, project: dict, task_id: str) -> int:
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
    failing = gate.failing_checks(plan, evs, tree)
    if failing:
        raise HarnessError("checks are not passing at this code tree:\n" + "\n".join(failing))
    state = taskfiles.read_json(folder / "state.json")
    if state["phase_open"]:
        phase.exit_phase(ctx, task_id, state["phase"])  # a ready writes the missing exit first
    remote, base, branch = project["integration_remote"], project["default_branch"], ctx.git.branch
    gitio.commit_paths(ctx.root, ".harness", f"harness: record {task_id}")
    gitio.push(ctx.root, remote, branch)
    approved = folder / "plan.approved.md"
    scope = planfile.diff(approved.read_text(), plan).scope_reductions() if approved.exists() else ()
    body = pr_body(task_id, plan, scope)
    prior = [e for e in evs if e.get("kind") == "pr"]
    if prior:
        number, url = prior[-1]["number"], prior[-1]["url"]
        ghio.pr_edit_body(ctx.root, number, body)  # re-emit: no second PR (R-15)
    else:
        number, url = ghio.pr_create(ctx.root, base, branch, title(plan, task_id), body)
    tip = gitio.out(["rev-parse", "HEAD"], ctx.root)
    context.record(ctx, context.event(ctx, "ready", task_id, tip_commit=tip, code_tree=tree))
    if not prior:
        context.record(ctx, context.event(ctx, "pr", task_id, number=number, url=url))
    gitio.commit_paths(ctx.root, ".harness", f"harness: ready {task_id}")
    try:
        gitio.push(ctx.root, remote, branch)
    except HarnessError as e:
        raise HarnessError(f"{e}\n`ready` is recorded; finish with `git push {remote} HEAD`") from e
    print(f"ready: {url}")
    return 0


def refresh(ctx, project: dict, task_id: str) -> int:
    phase.enter(ctx, task_id, "build")
    if rebase.rebase(ctx, project) == "conflict":
        rebase.abort(ctx)
        phase.exit_phase(ctx, task_id, "build", handoff=True)  # control returns to you (R-1)
        print("rebase conflict: aborted. Launch a revision session in this worktree to resolve it.")
        return 1
    plan = (taskfiles.task_dir(ctx.root, task_id) / "plan.md").read_text()
    results = [check.run_one(ctx, task_id, c) for c in planfile.checks(plan).values() if c.command]
    stale = gate.failing_checks(plan, context.task_events(ctx, task_id), gitio.code_tree(ctx.root))
    if "fail" in results or stale:
        phase.exit_phase(ctx, task_id, "build", handoff=True)
        print("checks do not all pass at the rebased code (observational checks need a revision session):\n"
              + "\n".join(stale))
        return 1
    return publish(ctx, project, task_id)
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_pr -v`
Expected: 7 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/commands/pr.py harness/cli.py tests/test_pr.py
git commit -m "feat: pr publish and refresh"
```

### Task 1.17: `close`

**Files:**
- Create: `harness/commands/close.py`, `tests/test_close.py`
- Modify: `harness/cli.py` (register `close`)

**Interfaces:**
- Consumes: `context.event/record/task_events`, `taskfiles.copy_to_state`
- Produces: nothing new for later tasks (`close` events are read by `gate.evaluate` and `scorecard.task_card`)

Spec: §5.2 (after merging: `close --done` for a flagged scope reduction; `close --abandon`), §6.6 (copies at `close --abandon`), §6.7 `close` (spool only).

- [ ] **Step 1: Register the command**

In `harness/cli.py`: import `close` and add `"close": Command(close, during_rebase=_always),`.

- [ ] **Step 2: Write the failing tests**

`tests/test_close.py`:

```python
import unittest

from harness import gitio, spool
from tests.helpers import Sandbox


class CloseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def test_done_and_abandon_go_to_the_spool_only(self):
        wt, env, task_id = self.sb.begin_task("cl")
        self.assertEqual(self.sb.harness("close", task_id, "--done", cwd=wt, env={}).returncode, 0)
        self.assertEqual(self.sb.harness("close", task_id, "--abandon", cwd=wt, env={}).returncode, 0)
        closes = [e["disposition"] for e in self.sb.spool(wt) if e["kind"] == "close"]
        self.assertEqual(closes, ["done", "abandon"])
        self.assertEqual([e for e in self.sb.task_file_events(wt, task_id) if e["kind"] == "close"], [])
        copies = spool.project_dir(self.sb.env, gitio.info(wt).common_dir) / "tasks" / task_id
        self.assertTrue((copies / "request.md").exists())

    def test_unknown_task_is_refused(self):
        r = self.sb.harness("close", "2026-01-01-nope", "--abandon", cwd=self.sb.main)
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown task", r.stderr)
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_close -v`
Expected: FAIL (`close` is not a registered command).

- [ ] **Step 4: Write the implementation**

`harness/commands/close.py`:

```python
"""Record a task's disposition: --done confirms a scope-reduced merge; --abandon ends it (spec §5.2)."""
from harness import HarnessError, context, taskfiles


def add_args(p) -> None:
    p.add_argument("task_id")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--done", action="store_true", help="the merged task still meets its original outcome")
    group.add_argument("--abandon", action="store_true", help="the task will not merge")


def run(args, ctx) -> int:
    ctx.require_project()
    if not any(e.get("kind") == "start" for e in context.task_events(ctx, args.task_id)):
        raise HarnessError(f"unknown task {args.task_id} (no start event in this machine's spool)")
    disposition = "done" if args.done else "abandon"
    context.record(ctx, context.event(ctx, "close", args.task_id, disposition=disposition))
    if args.abandon:
        folder = taskfiles.task_dir(ctx.root, args.task_id)
        if folder.exists():
            taskfiles.copy_to_state(folder, ctx.state_dir / "tasks" / args.task_id)
        else:
            print("note: the task folder is not in this checkout; copies made at triage exit (if any) remain")
    print(f"{args.task_id}: {disposition}")
    return 0
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_close -v`
Expected: 2 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/commands/close.py harness/cli.py tests/test_close.py
git commit -m "feat: close --done and --abandon"
```

### Task 1.18: Task resolution and timing (pure)

**Files:**
- Create: `harness/resolve.py`, `harness/timing.py`, `tests/test_resolve.py`, `tests/test_timing.py`

**Interfaces:**
- Consumes: `events.ts_ms`
- Produces: `resolve.resolve(events: list[dict], task_branches: dict[str, str]) -> tuple[dict[str, list[dict]], list[dict]]` (events per task, orphans); `timing.Wall(total_ms: int, by_phase: dict[str, int], complete: bool, missing: list[str])`; `timing.AgentTime(total_ms: int, by_phase: dict[str, int], unknown_spans: int)`; `timing.phase_intervals(events, until_ms) -> list[tuple[int, int, str]]`; `timing.wall(events, until_ms) -> Wall`; `timing.agent_time(events, until_ms) -> AgentTime`

Spec: §6.8 (resolution: task id, else branch, detached HEAD → session's last known branch; the rest are orphans), §6.10 (wall time with revisions and excluded human-wait gaps; startup charged; a missing boundary makes timing incomplete; agent time per session plus helpers; both per phase), R-1, R-2, R-18, R-19.

- [ ] **Step 1: Write the failing tests**

`tests/test_resolve.py`:

```python
import unittest

from harness.resolve import resolve


def ev(second, **fields):
    return {"kind": "stop", "ts": f"2026-10-08T12:00:{second:02d}.000Z", **fields}


class ResolveTest(unittest.TestCase):
    def test_task_id_then_branch_then_last_known_branch(self):  # spec §6.8
        tasks = {"T1": "b1", "T2": "b2"}
        evs = [ev(1, task_id="T1", branch="b2", session_id="A"),
               ev(2, branch="b2", session_id="B"),
               ev(3, branch=None, session_id="B"),          # detached HEAD during a rebase
               ev(4, branch="main", session_id="C"),
               ev(5, branch=None, session_id="D"),
               ev(6, task_id="GONE", branch="b1", session_id="E")]
        by_task, orphans = resolve(evs, tasks)
        self.assertEqual([e["session_id"] for e in by_task["T1"]], ["A", "E"])
        self.assertEqual([e["session_id"] for e in by_task["T2"]], ["B", "B"])
        self.assertEqual([e["session_id"] for e in orphans], ["C", "D"])
```

`tests/test_timing.py`:

```python
import unittest

from harness import events, timing

BASE = events.ts_ms("2026-10-08T12:00:00.000Z")
MIN = 60_000


def ev(kind, minute, **fields):
    return {"kind": kind, "ts": events.ts_from_ms(BASE + minute * MIN), **fields}


def ph(minute, phase, action, session="S1", handoff=False):
    return ev("phase", minute, phase=phase, action=action, controlling_session=session, handoff=handoff)


def hook(kind, minute, session="S1", **fields):
    return ev(kind, minute, source="hook", session_id=session, **fields)


class WallTest(unittest.TestCase):
    def wall(self, evs, until=10_000):
        return timing.wall(evs, BASE + until * MIN)

    def test_start_to_ready_split_by_phase(self):
        w = self.wall([ev("start", 0), ph(1, "triage", "enter"), ph(5, "triage", "exit"), ph(5, "build", "enter"),
                       ph(29, "build", "exit"), ev("ready", 30)])
        self.assertEqual((w.total_ms, w.complete), (30 * MIN, True))
        self.assertEqual(w.by_phase, {"between_phases": 2 * MIN, "triage": 4 * MIN, "build": 24 * MIN})

    def test_handoff_gap_is_excluded_until_the_successors_resume(self):  # spec §6.10
        w = self.wall([ev("start", 0), ph(1, "triage", "enter"), ph(5, "triage", "exit", handoff=True),
                       ev("resume", 50, session_id="S2"), ph(52, "research", "enter", session="S2"),
                       ph(59, "research", "exit", session="S2"), ev("ready", 60)])
        self.assertEqual(w.total_ms, 15 * MIN)

    def test_revision_starts_at_the_resume_of_the_session_that_reenters_build(self):  # R-2
        first = [ev("start", 0), ph(1, "build", "enter"), ph(29, "build", "exit"), ev("ready", 30)]
        w = self.wall(first + [ev("resume", 90, session_id="X"), ev("resume", 100, session_id="S3"),
                               ph(102, "build", "enter", session="S3"), ph(109, "build", "exit", session="S3"),
                               ev("ready", 110)])
        self.assertEqual(w.total_ms, 40 * MIN)

    def test_refresh_without_resume_starts_at_its_build_enter_and_conflict_exit_pauses(self):  # R-1
        first = [ev("start", 0), ph(1, "build", "enter"), ph(29, "build", "exit"), ev("ready", 30)]
        clean = self.wall(first + [ph(200, "build", "enter", session=None), ph(204, "build", "exit", session=None),
                                   ev("ready", 205)])
        self.assertEqual(clean.total_ms, 35 * MIN)
        conflict = self.wall(first + [ph(200, "build", "enter", session=None),
                                      ph(201, "build", "exit", session=None, handoff=True),
                                      ev("resume", 300, session_id="S4"), ph(301, "build", "enter", session="S4"),
                                      ph(309, "build", "exit", session="S4"), ev("ready", 310)])
        self.assertEqual(conflict.total_ms, 41 * MIN)

    def test_missing_boundaries_make_timing_incomplete(self):
        w = self.wall([ev("start", 0), ev("ready", 30), ev("ready", 40)])
        self.assertFalse(w.complete)
        self.assertIn("no revision start", w.missing[0])
        self.assertEqual(self.wall([ph(1, "triage", "enter")]).missing, ["no start event"])

    def test_abandon_stops_and_in_flight_runs_to_until(self):
        self.assertEqual(self.wall([ev("start", 0), ev("close", 10, disposition="abandon")]).total_ms, 10 * MIN)
        w = self.wall([ev("start", 0), ph(1, "triage", "enter")], until=50)
        self.assertEqual(w.total_ms, 50 * MIN)


class AgentTimeTest(unittest.TestCase):
    def test_prompt_to_last_stop_per_session_plus_helpers(self):  # spec §6.10
        evs = [ph(0, "build", "enter"),
               hook("prompt", 0), hook("stop", 5), hook("stop", 8), hook("prompt", 10), hook("stop", 12),
               hook("session_end", 20),
               hook("prompt", 1, session="S2"), hook("prompt", 3, session="S2"),          # first span: no stop
               hook("subagent_start", 2, agent_id="a1"), hook("subagent_stop", 6, agent_id="a1"),
               hook("subagent_start", 7, agent_id="a2")]                                 # never stopped
        a = timing.agent_time(evs, BASE + 30 * MIN)
        self.assertEqual(a.total_ms, (8 + 2 + 4) * MIN)
        self.assertEqual(a.unknown_spans, 3)  # S2's two prompts without a stop, helper a2
        self.assertEqual(a.by_phase, {"build": 14 * MIN})
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_resolve tests.test_timing -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'harness.resolve'`.

- [ ] **Step 3: Write the implementation**

`harness/resolve.py`:

```python
"""Resolve spool events to tasks at scoring time (spec §6.8). Pure."""


def resolve(events: list[dict], task_branches: dict[str, str]) -> tuple[dict[str, list[dict]], list[dict]]:
    """By task_id when it names a registered task; else by branch; on a detached HEAD, by the
    session's last known branch. Everything else is an orphan."""
    by_branch = {branch: task for task, branch in task_branches.items()}
    out: dict[str, list[dict]] = {task: [] for task in task_branches}
    orphans, last_branch = [], {}
    for e in sorted(events, key=lambda e: e.get("ts") or ""):
        session = e.get("session_id")
        if e.get("branch"):
            last_branch[session] = e["branch"]
        task = e.get("task_id") if e.get("task_id") in out else None
        if task is None:
            task = by_branch.get(e.get("branch") or last_branch.get(session))
        (out[task] if task else orphans).append(e)
    return out, orphans
```

`harness/timing.py`:

```python
"""Wall time and agent time over one task's events (spec §6.10). Pure."""
from dataclasses import dataclass

from harness.events import ts_ms


@dataclass(frozen=True)
class Wall:
    total_ms: int
    by_phase: dict[str, int]
    complete: bool
    missing: list[str]


@dataclass(frozen=True)
class AgentTime:
    total_ms: int
    by_phase: dict[str, int]
    unknown_spans: int


def _pauses(e: dict) -> bool:
    """`ready`, a handoff exit (incl. a `--refresh` exit without ready, R-1) and an abandon pause the clock."""
    kind = e.get("kind")
    return (kind == "ready"
            or (kind == "phase" and e.get("action") == "exit" and bool(e.get("handoff")))
            or (kind == "close" and e.get("disposition") == "abandon"))


def charged_intervals(events: list[dict], until_ms: int) -> tuple[list[tuple[int, int]], list[str]]:
    intervals, missing = [], []
    started, running, since, resumes = False, False, 0, {}
    for e in events:
        kind, t = e.get("kind"), ts_ms(e["ts"])
        if kind == "start":
            started, running, since = True, True, t
        elif not started:
            continue
        elif _pauses(e):
            if running:
                intervals.append((since, t))
                running, resumes = False, {}
            elif kind == "ready":
                missing.append(f"ready at {e['ts']} has no revision start (no `phase build enter` after the last pause)")
        elif kind == "resume" and not running:
            resumes[e.get("session_id")] = t  # the latest resume per session
        elif kind == "phase" and e.get("action") == "enter" and not running:
            controller = e.get("controlling_session")
            since = resumes.get(controller, t) if controller else t  # R-2
            running = True
    if not started:
        missing.append("no start event")
    elif running:
        intervals.append((since, max(since, until_ms)))
    return intervals, missing


def phase_intervals(events: list[dict], until_ms: int) -> list[tuple[int, int, str]]:
    out, open_phase = [], None
    for e in events:
        if e.get("kind") != "phase":
            continue
        t = ts_ms(e["ts"])
        if e.get("action") == "enter":
            if open_phase:
                out.append((open_phase[1], t, open_phase[0]))
            open_phase = (e.get("phase"), t)
        elif open_phase and e.get("phase") == open_phase[0]:
            out.append((open_phase[1], t, open_phase[0]))
            open_phase = None
    if open_phase:
        out.append((open_phase[1], max(open_phase[1], until_ms), open_phase[0]))
    return out


def split_by_phase(spans: list[tuple[int, int]], phases: list[tuple[int, int, str]]) -> dict[str, int]:
    """Charge each span to the phases it overlaps; the rest is `between_phases` (R-19)."""
    totals: dict[str, int] = {}
    for a, b in spans:
        covered = 0
        for pa, pb, name in phases:
            overlap = max(0, min(b, pb) - max(a, pa))
            if overlap:
                totals[name] = totals.get(name, 0) + overlap
                covered += overlap
        if b - a - covered:
            totals["between_phases"] = totals.get("between_phases", 0) + (b - a - covered)
    return totals


def wall(events: list[dict], until_ms: int) -> Wall:
    intervals, missing = charged_intervals(events, until_ms)
    return Wall(sum(b - a for a, b in intervals), split_by_phase(intervals, phase_intervals(events, until_ms)),
                not missing, missing)


def agent_time(events: list[dict], until_ms: int) -> AgentTime:
    """Per session: prompt → last stop before the next prompt or session end; plus helper start → stop."""
    hooks = [e for e in events if e.get("source") == "hook"]
    spans, unknown = [], 0
    sessions: dict[str | None, list[dict]] = {}
    for e in hooks:
        sessions.setdefault(e.get("session_id"), []).append(e)

    def close(prompt_t, stop_t):
        nonlocal unknown
        if prompt_t is None:
            return
        if stop_t is None:
            unknown += 1
        else:
            spans.append((prompt_t, stop_t))

    for evs in sessions.values():
        prompt_t = stop_t = None
        for e in evs:
            kind = e.get("kind")
            if kind in ("prompt", "session_end"):
                close(prompt_t, stop_t)
                prompt_t, stop_t = (ts_ms(e["ts"]), None) if kind == "prompt" else (None, None)
            elif kind == "stop" and prompt_t is not None:
                stop_t = ts_ms(e["ts"])
        close(prompt_t, stop_t)
    helpers: dict[tuple, int] = {}
    for e in hooks:
        key = (e.get("session_id"), e.get("agent_id"))
        if e.get("kind") == "subagent_start":
            helpers[key] = ts_ms(e["ts"])
        elif e.get("kind") == "subagent_stop":
            started = helpers.pop(key, None)
            if started is None:
                unknown += 1
            else:
                spans.append((started, ts_ms(e["ts"])))
    unknown += len(helpers)
    by_phase = split_by_phase(spans, phase_intervals(events, until_ms))
    return AgentTime(sum(b - a for a, b in spans), by_phase, unknown)
```

- [ ] **Step 4: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_resolve tests.test_timing -v`
Expected: 8 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add harness/resolve.py harness/timing.py tests/test_resolve.py tests/test_timing.py
git commit -m "feat: task resolution, wall time and agent time"
```

### Task 1.19: Scorecards and `score`

**Files:**
- Create: `harness/scorecard.py`, `harness/commands/score.py`, `tests/test_scorecard.py`, `tests/test_score.py`
- Modify: `harness/cli.py` (register `score`), `tests/helpers.py` (add `Sandbox.merge`, `Sandbox.card`)

**Interfaces:**
- Consumes: `gate.evaluate`, `timing.wall/agent_time`, `resolve.resolve`, `gitio.fetch/last_change/code_tree/commit_ms/show`, `spool.read`
- Produces: `scorecard.MergeFacts(code_tree: str, commit_ms: int)`; `scorecard.task_card(task_id, events, orphans, project, merge, final_plan, approved_plan, now_ms) -> dict`; `scorecard.summary(cards: list[dict], orphans: list[dict]) -> str`; `score.collect(ctx, project, ref, now_ms) -> tuple[list[dict], list[dict]]`; `Sandbox.merge(branch, method)` (`"merge"`, `"squash"` or `"rebase"`); `Sandbox.card(task_id) -> dict`

Spec: §10 (per-task card: disposition, gate, wall and agent time per phase, completeness, coverage, orphans; summary), §6.2 (`deadline_hours` per benchmark tier, `expiry_days`), §6.11 (merge commit), §6.12 (Slice 1 computes wall time, not done, agent time), §9.8, parent (completion after expiry stays not-done), R-4, R-10, R-18.

- [ ] **Step 1: Register the command and add the helpers**

In `harness/cli.py`: import `score` and add `"score": Command(score, during_rebase=_always),`.

Add to `class Sandbox` in `tests/helpers.py`:

```python
    def merge(self, branch: str, method: str) -> None:
        """Merge origin/<branch> into origin/main as GitHub would: merge commit, squash, or rebase."""
        m = self.tmp / "merger"
        if not m.exists():
            sh("git", "clone", "-q", str(self.remote), str(m), cwd=self.tmp, env=self.env)
        git(m, "fetch", "-q", "origin", env=self.env)
        git(m, "checkout", "-q", "-B", "main", "origin/main", env=self.env)
        if method == "merge":
            git(m, "merge", "-q", "--no-ff", "-m", f"Merge {branch}", f"origin/{branch}", env=self.env)
        elif method == "squash":
            git(m, "merge", "-q", "--squash", f"origin/{branch}", env=self.env)
            git(m, "commit", "-qm", f"{branch} (squashed)", env=self.env)
        else:
            git(m, "cherry-pick", f"origin/main..origin/{branch}", env=self.env)
        git(m, "push", "-q", "origin", "main", env=self.env)

    def card(self, task_id: str) -> dict:
        r = self.harness("score", cwd=self.main)
        assert r.returncode == 0, r.stdout + r.stderr
        path = spool.project_dir(self.env, gitio.info(self.main).common_dir) / "scorecards" / f"{task_id}.json"
        return json.loads(path.read_text())
```

- [ ] **Step 2: Write the failing tests**

`tests/test_scorecard.py`:

```python
import unittest

from harness import events, planfile, scorecard
from tests.test_planfile import PLAN

BASE = events.ts_ms("2026-10-08T12:00:00.000Z")
HOUR = 3_600_000
PROJECT = {"deadline_hours": {"S": 4, "M": 16, "L": 48}, "expiry_days": 21}
C1 = planfile.check_hash(planfile.checks(PLAN)["C1"])
C2 = planfile.check_hash(planfile.checks(PLAN)["C2"])


def ev(kind, hours, **fields):
    return {"kind": kind, "ts": events.ts_from_ms(BASE + int(hours * HOUR)), **fields}


def done_events(ready_at=2):
    return [ev("start", 0, task_id="T", benchmark_tier="M", branch="b"),
            ev("phase", 0.1, phase="build", action="enter", controlling_session="S"),
            ev("check", 1, check_id="C1", result="pass", code_tree="T1", check_text_hash=C1),
            ev("check", 1, check_id="C2", result="pass", code_tree="T1", check_text_hash=C2),
            ev("phase", ready_at - 0.1, phase="build", action="exit", controlling_session="S"),
            ev("ready", ready_at, code_tree="T1"),
            ev("stop", 1.5, source="hook", session_id="S")]


def card(evs, merge=None, now_hours=3, orphans=()):
    return scorecard.task_card("T", evs, list(orphans), PROJECT, merge, PLAN if merge else None,
                               PLAN if merge else None, BASE + now_hours * HOUR)


class ScorecardTest(unittest.TestCase):
    def test_merged_task_that_passes_the_gate_is_done(self):
        c = card(done_events(), scorecard.MergeFacts("T1", BASE + 3 * HOUR))
        self.assertEqual((c["disposition"], c["done"], c["gate"]["passed"], c["wall"]["total_ms"], c["wall"]["complete"]),
                         ("merged", True, True, 2 * HOUR, True))
        self.assertEqual(c["as_of"], events.ts_from_ms(BASE + 3 * HOUR))

    def test_merged_task_failing_the_gate_is_not_done_with_reasons(self):
        c = card(done_events(), scorecard.MergeFacts("T9", BASE + 3 * HOUR))
        self.assertFalse(c["done"])
        self.assertIn("differs", c["not_done_reasons"][0])

    def test_deadline_and_expiry(self):  # spec §6.2
        late = card(done_events(ready_at=17), scorecard.MergeFacts("T1", BASE + 18 * HOUR), now_hours=18)
        self.assertIn("deadline exceeded", late["not_done_reasons"])
        stale = card(done_events()[:2], now_hours=22 * 24)
        self.assertEqual(stale["disposition"], "not_done")
        self.assertIn("no terminal disposition within expiry_days", stale["not_done_reasons"])
        fresh = card(done_events()[:2], now_hours=3)
        self.assertEqual((fresh["disposition"], fresh["done"], fresh["gate"]), ("in_flight", False, None))

    def test_abandoned(self):
        c = card(done_events()[:2] + [ev("close", 1, disposition="abandon")])
        self.assertEqual((c["disposition"], c["done"], c["not_done_reasons"]), ("abandoned", False, ["abandoned"]))

    def test_task_orphans_are_from_its_own_sessions(self):  # R-10
        orphans = [ev("stop", 1, source="hook", session_id="S", branch=None),
                   ev("stop", 1, source="hook", session_id="Z", branch="main")]
        c = card(done_events(), now_hours=3, orphans=orphans)
        self.assertEqual([o["session_id"] for o in c["orphans"]], ["S"])

    def test_summary_lists_tasks_and_orphans_by_branch(self):
        c = card(done_events(), scorecard.MergeFacts("T1", BASE + 3 * HOUR))
        text = scorecard.summary([c], [ev("stop", 1, branch="main"), ev("stop", 2, branch="main")])
        self.assertIn("| T | M | merged | yes |", text)
        self.assertIn("| main | 2 |", text)
```

`tests/test_score.py`:

```python
import unittest

from harness import context, events, gitio
from harness.commands import score
from tests.helpers import Sandbox, commit, git


class ScoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()
        sb = cls.sb
        wt, env, cls.task_id = sb.through_triage("sc", {"C1": "test -f sc.txt"}, tier="S")
        sb.harness("phase", "build", "enter", cwd=wt, env=env)
        (wt / "sc.txt").write_text("sc\n")
        commit(wt, "build")
        sb.harness("check", "--all", cwd=wt, env=env)
        r = sb.harness("pr", cls.task_id, cwd=wt, env=env)
        assert r.returncode == 0, r.stdout + r.stderr
        sb.merge("task-sc", "squash")

    def test_merged_task_scores_done(self):
        card = self.sb.card(self.task_id)
        self.assertEqual((card["disposition"], card["done"], card["wall"]["complete"]), ("merged", True, True))
        self.assertGreater(card["wall"]["by_phase"]["build"], 0)

    def test_score_is_deterministic_and_commits_nothing(self):  # spec §9.8
        self.sb.card(self.task_id)
        refs = git(self.sb.main, "for-each-ref", "--format=%(refname) %(objectname)")
        ctx = context.load(self.sb.main, self.sb.env)
        project = ctx.require_project()
        now = events.ts_ms(events.now_ts())
        first = score.collect(ctx, project, "origin/main", now)
        second = score.collect(ctx, project, "origin/main", now)
        self.assertEqual(first, second)
        self.assertEqual(git(self.sb.main, "for-each-ref", "--format=%(refname) %(objectname)"), refs)
        self.assertTrue(gitio.status_clean(self.sb.main))
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `python3.12 -m unittest tests.test_scorecard tests.test_score -v`
Expected: FAIL with `ImportError: cannot import name 'scorecard'`.

- [ ] **Step 4: Write the implementation**

`harness/scorecard.py`:

```python
"""Per-task scorecard and summary (spec §10; Slice 1 fields). Pure."""
from dataclasses import asdict, dataclass

from harness import gate, timing
from harness.events import ts_from_ms, ts_ms

COVERAGE_FIELDS = ("session_id", "model", "effort", "transcript_path")
DAY_MS, HOUR_MS = 86_400_000, 3_600_000


@dataclass(frozen=True)
class MergeFacts:
    code_tree: str
    commit_ms: int


def task_card(task_id: str, events: list[dict], orphans: list[dict], project: dict, merge: MergeFacts | None,
              final_plan: str | None, approved_plan: str | None, now_ms: int) -> dict:
    events = sorted(events, key=lambda e: e.get("ts") or "")
    start = next((e for e in events if e.get("kind") == "start"), {})
    tier = start.get("benchmark_tier")
    abandon = next((e for e in events if e.get("kind") == "close" and e.get("disposition") == "abandon"), None)
    if merge:
        disposition, terminal_ms = "merged", merge.commit_ms
    elif abandon:
        disposition, terminal_ms = "abandoned", ts_ms(abandon["ts"])
    else:
        disposition, terminal_ms = "in_flight", None
    until = terminal_ms if terminal_ms is not None else now_ms  # R-18
    wall = timing.wall(events, until)
    agent = timing.agent_time(events, until)
    result = gate.evaluate(final_plan, approved_plan, events, merge.code_tree) if merge else None
    reasons = ["abandoned"] if abandon else []
    if result and not result.passed:
        reasons += list(result.reasons)
    deadline = project["deadline_hours"].get(tier)
    if deadline is not None and wall.total_ms > deadline * HOUR_MS:
        reasons.append("deadline exceeded")
    if start and (terminal_ms if terminal_ms is not None else now_ms) > ts_ms(start["ts"]) + project["expiry_days"] * DAY_MS:
        reasons.append("no terminal disposition within expiry_days")
    if disposition == "in_flight" and reasons:
        disposition = "not_done"
    hooks = [e for e in events if e.get("source") == "hook"]
    sessions = sorted({e["session_id"] for e in hooks if e.get("session_id")})
    return {
        "task_id": task_id,
        "as_of": ts_from_ms(now_ms),
        "benchmark_tier": tier,
        "arm": start.get("arm"),
        "assigned_commit": start.get("assigned_commit"),
        "branch": start.get("branch"),
        "disposition": disposition,
        "done": disposition == "merged" and not reasons,
        "gate": None if result is None else asdict(result),
        "not_done_reasons": reasons,
        "wall": {"total_ms": wall.total_ms, "by_phase": wall.by_phase, "complete": wall.complete,
                 "missing": wall.missing},
        "agent_time": asdict(agent),
        "coverage": {"events": len(events), "hook_events": len(hooks), "sessions": sessions,
                     "null": {f: sum(1 for e in hooks if e.get(f) is None) for f in COVERAGE_FIELDS}},
        "orphans": [{"ts": e.get("ts"), "kind": e.get("kind"), "session_id": e.get("session_id"),
                     "branch": e.get("branch")} for e in orphans if e.get("session_id") in set(sessions)],
    }


def summary(cards: list[dict], orphans: list[dict]) -> str:
    lines = ["# Harness scorecards", "",
             "| Task | Tier | Disposition | Done | Wall (h) | Agent (h) | Timing complete |",
             "|---|---|---|---|---|---|---|"]
    for c in cards:
        lines.append(f"| {c['task_id']} | {c['benchmark_tier']} | {c['disposition']} | {'yes' if c['done'] else 'no'} | "
                     f"{c['wall']['total_ms'] / HOUR_MS:.2f} | {c['agent_time']['total_ms'] / HOUR_MS:.2f} | "
                     f"{'yes' if c['wall']['complete'] else 'no'} |")
    counts: dict[str, int] = {}
    for e in orphans:
        branch = e.get("branch") or "(detached)"
        counts[branch] = counts.get(branch, 0) + 1
    lines += ["", "## Orphan events by branch", "", "| Branch | Events |", "|---|---|"]
    lines += [f"| {b} | {n} |" for b, n in sorted(counts.items())]
    return "\n".join(lines) + "\n"
```

`harness/commands/score.py`:

```python
"""Score every registered task of this project into the state dir (spec §10)."""
import json

from harness import events, gitio, resolve, scorecard, spool, taskfiles


def add_args(p) -> None:
    pass


def run(args, ctx) -> int:
    project = ctx.require_project()
    remote, base = project["integration_remote"], project["default_branch"]
    gitio.fetch(ctx.root, remote, base)
    cards, orphans = collect(ctx, project, f"{remote}/{base}", events.ts_ms(events.now_ts()))
    out = ctx.state_dir / "scorecards"
    out.mkdir(parents=True, exist_ok=True)
    for card in cards:
        (out / f"{card['task_id']}.json").write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    (out / "summary.md").write_text(scorecard.summary(cards, orphans))
    print(f"{len(cards)} scorecards in {out}")
    return 0


def collect(ctx, project: dict, ref: str, now_ms: int) -> tuple[list[dict], list[dict]]:
    """Read every input once, then score with pure functions; reads git, writes nothing (§9.8)."""
    all_events = spool.read(ctx.state_dir)
    starts = {e["task_id"]: e for e in all_events if e.get("kind") == "start"}
    by_task, orphans = resolve.resolve(all_events, {t: e.get("branch") for t, e in starts.items()})
    cards = []
    for task_id in sorted(starts):
        folder = f"{taskfiles.RUNS}/{task_id}"
        sha = gitio.last_change(ctx.root, ref, folder)
        merge = scorecard.MergeFacts(gitio.code_tree(ctx.root, sha), gitio.commit_ms(ctx.root, sha)) if sha else None
        final = gitio.show(ctx.root, ref, f"{folder}/plan.md") if sha else None
        approved = gitio.show(ctx.root, ref, f"{folder}/plan.approved.md") if sha else None
        cards.append(scorecard.task_card(task_id, by_task[task_id], orphans, project, merge, final, approved, now_ms))
    return cards, orphans
```

- [ ] **Step 5: Run the tests to see them pass**

Run: `python3.12 -m unittest tests.test_scorecard tests.test_score -v`
Expected: 8 tests, OK.

- [ ] **Step 6: Commit**

```bash
git add harness/scorecard.py harness/commands/score.py harness/cli.py tests/helpers.py tests/test_scorecard.py tests/test_score.py
git commit -m "feat: scorecards and score command"
```

### Task 1.20: Map, phase files and instruction checks

**Files:**
- Create: `AGENTS.md`, `skills/phases/triage.md`, `skills/phases/research.md`, `skills/phases/resolve.md`, `skills/phases/plan.md`, `skills/phases/build.md`, `skills/phases/verify.md`, `tests/test_instructions.py`

**Interfaces:**
- Consumes: `cli.COMMANDS`
- Produces: the files `harness start` points agents to

Spec: §4.2 (map and one file per phase: output and commands, never how to organize agents), §5.1–5.5, §5.7, §6.3, §6.5, §4.6, §10 last line (no phase file reads the state dir), C4, R-9. Retro, memory and `tier` arrive in Slice 2.

- [ ] **Step 1: Write the failing test**

`tests/test_instructions.py`:

```python
import re
import unittest

from harness import REPO, cli

PHASE_DIR = REPO / "skills" / "phases"
FILES = [REPO / "AGENTS.md", REPO / "hooks" / "bootstrap.md", *sorted(PHASE_DIR.glob("*.md"))]


class InstructionsTest(unittest.TestCase):
    def test_slice1_phase_files_exist(self):
        self.assertEqual({p.stem for p in PHASE_DIR.glob("*.md")},
                         {"triage", "research", "resolve", "plan", "build", "verify"})

    def test_every_harness_command_named_exists(self):
        for path in FILES:
            for name in re.findall(r"`harness ([a-z-]+)", path.read_text()):
                self.assertIn(name, cli.COMMANDS, f"{path.name} names `harness {name}`")

    def test_no_file_points_agents_at_the_state_dir_except_to_forbid_it(self):  # spec §10
        for path in FILES:
            for line in path.read_text().splitlines():
                if ".local/state" in line:
                    self.assertIn("Never read", line, path.name)
```

- [ ] **Step 2: Run the test to see it fail**

Run: `python3.12 -m unittest tests.test_instructions -v`
Expected: FAIL (`test_slice1_phase_files_exist`: empty set).

- [ ] **Step 3: Write the files**

`AGENTS.md`:

````markdown
# Lean Harness — map

`harness start` sent you here and printed the task id. Read files from this harness checkout; run
every `harness` command in the task's worktree (the project), never here.

## Order

If `.harness/runs/<task-id>/state.json` already names a `phase`, this is a later session of a task in
progress: read `plan.md`, re-read that phase's file and continue from there (after a `ready`, begin
with `harness phase build enter`, as `build.md` says). Otherwise:

1. Run `harness phase triage enter`, then follow `skills/phases/triage.md`. Triage sets the tier.
2. Run the phases your tier lists, in order. Read each phase file when you enter that phase.

| Tier | Phases |
|---|---|
| S | triage → build |
| M | triage → research → plan → build → verify |
| L | triage → research → resolve → plan → build → verify |

3. The last phase file ends with `harness pr <task-id>`. Stop when it prints `ready`.

## Rules for every phase

- The task folder is `.harness/runs/<task-id>/` in the worktree. Commit it together with your code.
- Notes: one line per entry, under 25 words, written as it happens, never reconstructed:
  `<date time> · <agent/model> · <phase> — <what>. [Why: <why>] [Check: C3] [Cites: path:line]`
  Decisions need `Why:`; a Decision that changes a check or the goal names it (`Check: C3`, `Check: goal`).
  Decisions, Unknowns and Friction go under those headings in `plan.md`.
- The project's own rules decide how to build, test, push and clean up; acceptance checks call the
  project's commands.
- Never read the harness state directory (`~/.local/state/harness`) or any scorecard.
- How you organize agents is your choice. Agents you launch may run `harness check`; only you run
  `harness phase` and `harness pr`.
- Stopping for a question, an approval or a blocker is fine; the task stays open, and a later
  session continues it after `harness start`.
````

`skills/phases/triage.md`:

````markdown
# Triage (S, M, L)

**Input:** `request.md`. **Output:** the first five sections of `plan.md`, and `config.json`.
**Commands:** `harness phase triage enter` (already run; it refuses until `harness start` passed),
`harness phase triage exit`.

1. Read `request.md`. Explore the code only as far as sizing the task needs.
2. Write `plan.md` with these sections, in order: `## Goal`, `## Outcome`, `## Acceptance checks`,
   `## Tier`, `## Source`. M and L plans later add `## Milestones`, `## Decisions`, `## Unknowns`,
   `## Friction`.
3. Acceptance checks are numbered C1, C2, …, one entry each:

   ~~~
   ### C1 — <what is checked>
   Expected: <expected result>
   ```sh
   <one command run from the project root; exit status 0 means pass>
   ```
   ~~~

   A check that can only be observed says so in its heading, `### C2 — <what> (observational)`, and
   has no command. In S every check must be runnable; an observational check makes the task M.
4. Tier: **S** if the diff fits in one sentence; **M** for a multi-file change in code that already
   exists; **L** for a new subsystem, a cross-cutting change, or unfamiliar code.
   Source: `prompt` or `ticket`.
5. Write `config.json`:

   ```json
   {"knobs": {"phases": ["triage", "build"],
              "phase_agent": {"build": "same"},
              "evaluator_cadence": "none",
              "plan_review": false},
    "record": {"tier": "S",
               "triage_signals": {"areas": ["src/api"], "file_count_estimate": 2, "familiarity": "high"}}}
   ```

   `phases` lists your tier's phases; `phase_agent` is `same` unless the user asked for another
   agent on a phase; `evaluator_cadence` is `none` for S, `end` for M, `per_milestone` for L.
   `harness phase triage exit` fills in the rest of `record`.
6. Triage ends when goal, outcome and at least one check are written without guessing:
   - a missing fact: explore or spike;
   - a missing preference: pick a default and log it as an Unknown;
   - a missing goal: stop and ask the user. Never default the goal.
7. Run `harness phase triage exit`. Next: S enters build; M and L enter research.
````

`skills/phases/research.md`:

```markdown
# Research (M, L)

**Input:** the code the task touches. **Output:** `research.md` in the task folder.
**Commands:** `harness phase research enter`, `harness phase research exit`.

1. Run `harness phase research enter`.
2. Map every area the task touches: entry points, data flow, tests, and the project commands that
   build and test them. Cite `path:line`.
3. Log each Unknown in `plan.md` as you find it.
4. Research ends when every area the task touches is mapped. Run `harness phase research exit`.
```

`skills/phases/resolve.md`:

```markdown
# Resolve unknowns (L)

**Input:** the open Unknowns in `plan.md`. **Output:** each one resolved or given a logged default.
**Commands:** `harness phase resolve enter`, `harness phase resolve exit`.

1. Run `harness phase resolve enter`.
2. A fact: explore or spike, then write the answer on its Unknown line.
3. A preference: pick a default and log it as a Decision with `Why:`.
4. This phase ends when every fact is explored or spiked and every preference has a logged default.
   Run `harness phase resolve exit`.
```

`skills/phases/plan.md`:

```markdown
# Plan (M, L)

**Input:** `research.md` and the resolved Unknowns. **Output:** the full `plan.md`.
**Commands:** `harness phase plan enter`, `harness phase plan exit`.

1. Run `harness phase plan enter`.
2. Add `## Milestones`: each `### M1 — <title>` with a `Checks: C1, C3` line naming its
   acceptance checks. Refine the checks, and record Decisions and Unknowns.
3. The plan is a self-contained contract: outcomes, checks, decisions, unknowns. No code transcripts.
4. Changing a check or the goal needs a Decision that names it (`Check: C3`, `Check: goal`).
5. The plan ends when another agent could build from it alone. Run `harness phase plan exit`.
   Next: `harness phase build enter`; its first entry freezes `plan.approved.md`.
```

`skills/phases/build.md`:

```markdown
# Build loop (S, M, L)

**Input:** `plan.md`. **Output:** code, one milestone at a time (S: the whole change).
**Commands:** `harness phase build enter`, `harness check <C-id>`, `harness rebase`,
`harness check --all` (S), `harness pr <task-id>` (S).

1. Run `harness phase build enter` (the first entry snapshots `plan.approved.md`).
2. Work one milestone at a time. Commit code and the task folder together.
3. After every attempt at a milestone's checks, run `harness check <C-id>` for each. It needs a clean
   checkout outside `.harness/`, so commit first. It runs the check's command itself; never report a
   result it did not record.
4. When a milestone's checks pass, add one implementation-note line under it: what changed, which files.
5. If reality breaks the plan, update `plan.md` with a Decision (naming any check it changes) and continue.
6. When every milestone passes, run `harness rebase`. On conflicts: resolve them, `git add` the files,
   and run `harness rebase` again; run no other harness command until it finishes.
7. Build ends when every check passes after the rebase.
   - S: run `harness check --all`, then `harness pr <task-id>`.
   - M and L: run `harness phase verify enter`.
8. In L, each milestone is verified inside build under the rule in `verify.md`; those note lines use
   phase `verify`.

After `ready`: any edit, rebase or check starts with `harness phase build enter`. Running
`harness pr <task-id>` again re-emits `ready` without opening a second PR.
```

`skills/phases/verify.md`:

```markdown
# Verify (M, L)

**Input:** the running system. **Output:** a pass or fail recorded for every final check.
**Commands:** `harness phase verify enter`, `harness check --all`,
`harness check <C-id> --observed pass|fail`, `harness phase verify exit`, `harness pr <task-id>`.

1. Run `harness phase verify enter`.
2. An agent other than the one that wrote the code does the verifying. You choose how. Its note lines
   use phase `verify`, and it logs every Unknown the builder missed.
3. Runnable checks: `harness check --all`. Observational checks: exercise the running system, then
   `harness check <C-id> --observed pass|fail`.
4. A failure returns to build: `harness phase build enter`, fix, recheck, then verify again.
5. Verify ends when every final check passes. Run `harness phase verify exit`, then
   `harness pr <task-id>`.
```

- [ ] **Step 4: Run the test to see it pass**

Run: `python3.12 -m unittest tests.test_instructions -v`
Expected: 3 tests, OK.

- [ ] **Step 5: Commit**

```bash
git add AGENTS.md skills tests/test_instructions.py
git commit -m "feat: agent map and Slice 1 phase files"
```

### Task 1.21: End-to-end integration

**Files:**
- Create: `tests/test_e2e.py`

**Interfaces:**
- Consumes: everything above; `Sandbox.through_triage/merge/card/hook`

Spec: §11 Slice 1 exit criteria (complete scorecard; two parallel tasks scored correctly), §12 (gate across merge, squash and rebase merges; `pr` and `pr --refresh` against a local bare remote with a stubbed `gh`), §9.2, §14 (merging after main moved fails the gate), Review Focus 5.

- [ ] **Step 1: Write the tests**

`tests/test_e2e.py`:

```python
import unittest

from tests.helpers import Sandbox, commit, git


class E2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sb = Sandbox()

    def h(self, wt, env, *args):
        r = self.sb.harness(*args, cwd=wt, env=env)
        self.assertEqual(r.returncode, 0, f"harness {' '.join(args)}: {r.stdout}{r.stderr}")
        return r

    def build_and_publish(self, wt, env, task_id, slug):
        """An M task from research to ready, with one prompt/stop turn around the work."""
        self.sb.hook(wt, "UserPromptSubmit", env["HARNESS_SESSION_ID"])
        for name in ("research", "plan", "build"):
            self.h(wt, env, "phase", name, "enter")
        (wt / f"{slug}.txt").write_text(f"{slug}\n")
        commit(wt, f"build {slug}")
        self.h(wt, env, "check", "C1")
        self.h(wt, env, "phase", "verify", "enter")
        self.h(wt, env, "check", "--all")
        self.h(wt, env, "pr", task_id)
        self.sb.hook(wt, "Stop", env["HARNESS_SESSION_ID"])

    def start(self, slug, session):
        return self.sb.through_triage(slug, {"C1": f"test -f {slug}.txt"}, session=session)

    def test_merge_methods_all_pass_the_gate(self):  # spec §12
        for method in ("merge", "squash", "rebase"):
            with self.subTest(method=method):
                slug = f"e2e-{method}"
                wt, env, task_id = self.start(slug, f"S-{method}")
                self.build_and_publish(wt, env, task_id, slug)
                self.sb.merge(f"task-{slug}", method)
                card = self.sb.card(task_id)
                self.assertEqual((card["disposition"], card["done"], card["gate"]["passed"], card["wall"]["complete"]),
                                 ("merged", True, True, True), card)
                self.assertTrue({"triage", "research", "plan", "build", "verify"} <= set(card["wall"]["by_phase"]))
                self.assertGreater(card["agent_time"]["total_ms"], 0)
                self.assertEqual(card["orphans"], [])

    def test_two_parallel_tasks_score_independently(self):  # spec §11 Slice 1, §9.2
        project_json = (self.sb.main / ".harness" / "project.json").read_bytes()
        (wa, ea, ta), (wb, eb, tb) = self.start("par-a", "PA"), self.start("par-b", "PB")
        self.build_and_publish(wa, ea, ta, "par-a")
        self.build_and_publish(wb, eb, tb, "par-b")
        self.sb.merge("task-par-a", "squash")
        self.h(wb, {}, "pr", "--refresh", tb)  # main moved: you refresh before merging (§17)
        self.sb.merge("task-par-b", "squash")
        a, b = self.sb.card(ta), self.sb.card(tb)
        self.assertTrue(a["done"] and b["done"], (a["not_done_reasons"], b["not_done_reasons"]))
        self.assertEqual((a["coverage"]["sessions"], b["coverage"]["sessions"]), (["PA"], ["PB"]))
        git(self.sb.main, "pull", "-q", "--ff-only", env=self.sb.env)
        self.assertEqual((self.sb.main / ".harness" / "project.json").read_bytes(), project_json)

    def test_merge_without_refresh_fails_gate(self):  # spec §14, Review Focus 5
        (wc, ec, tc), (wd, ed, td) = self.start("nr-c", "PC"), self.start("nr-d", "PD")
        self.build_and_publish(wc, ec, tc, "nr-c")
        self.build_and_publish(wd, ed, td, "nr-d")
        self.sb.merge("task-nr-c", "squash")
        self.sb.merge("task-nr-d", "squash")  # no refresh: merged code includes nr-c's change
        card = self.sb.card(td)
        self.assertFalse(card["done"])
        self.assertTrue(any("differs from the last ready tip" in r for r in card["not_done_reasons"]))
```

- [ ] **Step 2: Run the end-to-end tests**

Run: `python3.12 -m unittest tests.test_e2e -v`
Expected: 3 tests, OK. A failure here is a defect in an earlier task: fix it there, with a test in that task's file.

- [ ] **Step 3: Run the whole suite**

Run: `python3.12 -m unittest discover -s tests -t . -v`
Expected: every test passes.

- [ ] **Step 4: Commit and push**

```bash
git add tests/test_e2e.py
git commit -m "test: end-to-end gate across merge methods and parallel tasks"
git push
```

### Task 1.22: [YOU] Install the harness for your user

Spec: §4.3 (`install --user`), §8 (doctor doubles as the installation test), §12.

- [ ] **Step 1: [YOU] Install**

```bash
cd ~/Desktop/src/echo-official/lean-harness && python3.12 harness/cli.py install --user
```

Expected: lines naming `~/.local/bin/harness`, six Claude hook entries, the allow rule, the bootstrap copy and the `CLAUDE.md` import. Your existing settings and hooks stay in place, ahead of the new entries.

- [ ] **Step 2: Check it**

```bash
cd ~ && harness doctor
```

Expected: `ok    claude_hooks` and `ok    claude_bootstrap`, exit 0 (outside a git repo only the install probes run).

### Task 1.23: [YOU] Install the harness in mvp and echo-wiki

Spec: §2.1 (pilots), §4.3 (project install, merged via PR), §6.2 (mvp `cloud_env_vars`), R-8.

- [ ] **Step 1: Prepare the mvp install branch** (path: your mvp checkout)

```bash
cd ~/Desktop/src/echo-official/mvp && git fetch origin
git worktree add ../mvp-harness-install -b harness-install origin/main
cd ../mvp-harness-install && harness install
```

- [ ] **Step 2: Set mvp's cloud variables and amend**: in `.harness/project.json` set `"cloud_env_vars": ["ECHO_CODEX_CLOUD", "ECHO_CLAUDE_CLOUD"]`, then:

```bash
git commit -q --amend --no-edit -- .harness/project.json && git push -u origin harness-install
```

- [ ] **Step 3: [YOU] Open, review and merge the mvp PR**: `gh pr create --base main --fill`.
- [ ] **Step 4: echo-wiki**: repeat Steps 1 and 3 in your echo-wiki checkout (no cloud variables), then **[YOU]** open and merge its PR.
- [ ] **Step 5: Check each project**: in a fresh worktree of each (`git worktree add ../<repo>-doctor -b doctor-check origin/main`), run `harness doctor`; expected: every row `ok`. Remove the worktree and branch afterwards (`git worktree remove ../<repo>-doctor && git branch -D doctor-check`).

### Task 1.24: Real-agent smoke test (Claude)

**Files:**
- Create: `tests/smoke/__init__.py` (empty), `tests/smoke/run_smoke.py` (not named `test_*`, so the unit suite never runs it)

Spec: §12 end-to-end smoke (Claude part; Codex joins in Slice 2). Runs after Task 1.22, with your real Claude login, in a throwaway repo with a local bare remote and a stub `gh`.

- [ ] **Step 1: Write the smoke script**

`tests/smoke/run_smoke.py`:

```python
"""Real-agent smoke (spec §12): one S task in a throwaway repo, driven by `claude -p`, then scored.
Run by hand after `harness install --user`:  python3.12 tests/smoke/run_smoke.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from harness import gitio, spool  # noqa: E402
from tests.helpers import GH_STUB, git, init_repo, sh  # noqa: E402


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="harness-smoke-"))
    bindir = tmp / "bin"
    bindir.mkdir()
    (bindir / "gh").write_text(GH_STUB)
    (bindir / "gh").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("HARNESS_")}
    env.update(PATH=f"{bindir}:{os.environ['PATH']}", GH_LOG=str(tmp / "gh.log"))
    remote, main_co, merger, wt = tmp / "remote.git", tmp / "main", tmp / "merger", tmp / "task"
    sh("git", "clone", "-q", "--bare", str(init_repo(tmp / "seed")), str(remote), cwd=tmp, env=env)
    sh("git", "clone", "-q", str(remote), str(main_co), cwd=tmp, env=env)
    sh("harness", "install", cwd=main_co, env=env)
    git(main_co, "push", "-q", "origin", "harness-install:main", env=env)
    git(main_co, "switch", "-q", "main", env=env)
    git(main_co, "pull", "-q", "--ff-only", env=env)
    git(main_co, "worktree", "add", "-q", str(wt), "-b", "smoke", "origin/main", env=env)
    request = tmp / "request.md"
    request.write_text("Create hello.txt at the repository root containing exactly one line: hi\n"
                       "Acceptance check: `grep -qx hi hello.txt`.\n")
    print(sh("harness", "start", "--new", "smoke", "--benchmark-tier", "S", "--request", str(request),
             cwd=wt, env=env).stdout)
    subprocess.run(["claude", "-p", "Begin.", "--allowedTools", "Bash(harness:*)", "Bash(git:*)",
                    "Bash(grep:*)", "Read", "Write", "Edit"], cwd=wt, env=env, stdin=subprocess.DEVNULL)
    sh("git", "clone", "-q", str(remote), str(merger), cwd=tmp, env=env)
    git(merger, "merge", "-q", "--squash", "origin/smoke", env=env)
    git(merger, "commit", "-qm", "smoke (squashed)", env=env)
    git(merger, "push", "-q", "origin", "main", env=env)
    sh("harness", "score", cwd=main_co, env=env)
    state = spool.project_dir(env, gitio.info(main_co).common_dir) / "scorecards"
    card = json.loads(next(state.glob("*-smoke.json")).read_text())
    expected = {"disposition": "merged", "done": True, "wall_complete": True, "has_triage_and_build": True,
                "agent_time_positive": True, "no_orphans": True}
    actual = {"disposition": card["disposition"], "done": card["done"], "wall_complete": card["wall"]["complete"],
              "has_triage_and_build": {"triage", "build"} <= set(card["wall"]["by_phase"]),
              "agent_time_positive": card["agent_time"]["total_ms"] > 0, "no_orphans": card["orphans"] == []}
    print(json.dumps(card, indent=2))
    print("PASS" if actual == expected else f"FAIL: {actual}")
    return 0 if actual == expected else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it**

Run: `python3.12 tests/smoke/run_smoke.py`
Expected: the scorecard, then `PASS`. On `FAIL`, read the card's `not_done_reasons`, `wall.missing` and `orphans`, fix the defect in its task with a regression test, and rerun.

- [ ] **Step 3: Commit**

```bash
git add tests/smoke && git commit -m "test: real-agent smoke for Claude" && git push
```

### Task 1.25: [YOU] Real tasks in mvp, then the Slice 1 checkpoint

Spec: §11 Slice 1 exit criteria, §17 daily use.

- [ ] **Step 1: [YOU] One real mvp M task**, following §17: write the request in a file outside the worktree; create a worktree from fresh `origin/main`; run `harness start --new <slug> --benchmark-tier M --request <file>` in it; open Claude in that worktree (CLI or desktop app); answer questions; when the PR is ready, run `harness pr --refresh <task-id>` and merge as soon as checks pass.
- [ ] **Step 2: Score it**: `harness score` in your mvp checkout; open `~/.local/state/harness/<hash>/scorecards/<task-id>.json` (`harness score` prints the folder). Expected: `disposition: merged`, `gate.passed: true`, `wall.complete: true` with no `missing`, every orphan explained.
- [ ] **Step 3: [YOU] Two mvp tasks in parallel**: two worktrees, two `start --new`, two Claude sessions at once; refresh each before its merge.
- [ ] **Step 4: Score again**: both cards complete and correct; each card's sessions are only its own.

### Slice 1 checkpoint (spec §11)

- [ ] One real mvp M task merged with a complete scorecard: all boundaries present, gate evaluated, no unexplained orphans.
- [ ] Two parallel mvp tasks scored correctly.
- [ ] Full suite green: `python3.12 -m unittest discover -s tests -t . -v`; smoke `PASS`.
- [ ] Do not start Slice 2 until every box is ticked.

---
## Roadmap after Slice 1

These sections are ordered task lists, not task detail: each slice gets its own detailed plan once the previous checkpoint holds. Exit criteria are spec §11's.

### Slice 2: both agents, all phases (ready for real work)

Exit criteria (§11): Claude and Codex tasks running concurrently in mvp; at least one echo-wiki task; a Claude task whose verify ran in a Codex delegate, with the delegate's check recorded; two parallel tasks' lessons merged cleanly; scorecards complete for all.

1. **Codex adapter**: `harness/adapters/codex.py` plus one registry line. Identity variable `CODEX_THREAD_ID`; payload → event with `model`, `turn_id`, transcript paths and `format_warning`; contract tests on the Phase 0 Codex fixtures; user install (append six entries to `$CODEX_HOME/hooks.json` without reordering, a marked bootstrap block in `$CODEX_HOME/AGENTS.md`, the state dir in `[sandbox_workspace_write].writable_roots`, refuse when `$CODEX_HOME/AGENTS.override.md` exists, print the one manual approval step); doctor probes, silent failures only (R-22): hook entries present with a `hooks.state` approval each and `[features].hooks` not false (unapproved hooks silently never run), bootstrap block present, no `$CODEX_HOME/AGENTS.override.md` (it would hide the bootstrap). §4.1, §4.3, §6.7, §6.9, §8, §16, C6.
2. **[YOU]** Rerun `harness install --user`; approve the harness hooks in Codex; `harness doctor` from both CLIs and both apps.
3. **`harness tier <S|M|L>`**: rewrites the tier in `plan.md` and `config.json`, keeps `origin_tier`, refuses a downgrade, appends `tier`, copies the files to the state dir. §5.1, §7.
4. **`harness review start|end`** and its timing: the plan-review span is charged and reported separately. §6.10, §7.
5. **`harness defect <task-id> "<line>" | --resolved <id>`**. §6.7, §7.
6. **`harness memory kept|fixed|deleted <area>:<id>`**. §5.6, §7.
7. **`hooks/shared-rules.md`**: memory admission bar, cap, check-before-use, single writer, friction rule, and when to run `harness tier`. §4.2, §5.6.
8. **Retro and revised phase files**: `skills/phases/retro.md`; `harness retro-bundle` printing the bundle to stdout; the map adds retro; research (M, L) and build (S) read memory and call `harness memory`; build and verify call `harness tier`; plan calls `harness review` around an optional human review; the last phase before retro hands over to retro, then `harness pr`. §5.2, §5.3, C12.
9. **`rebase` by-id memory cleanup**: record the merge base under the worktree's git dir before rebasing; after the rebase finishes, drop ids either side retired, keep one line per id, commit; integration test of union merge plus cleanup across two branches. §5.6, §7, §12.
10. **Transcript cache**: `cache/sessions/<session-id>.json` with model(s), effort, tokens (both agents) and dollars (Claude), refreshed on every `score` read; best-effort readers. §6.6, §10, C8.
11. **Smoke**: add a `codex exec -s danger-full-access … < /dev/null` run to `tests/smoke/run_smoke.py`; **[YOU]** remove the trust entries it leaves. §12, §16.
12. **[YOU] Real tasks** for every §11 Slice 2 exit criterion, then the Slice 2 checkpoint.

### Slice 3: full scorecard

Exit criteria (§11): scorecards recomputed for every task since Slice 1; three tasks hand-checked against the scorer.

1. **Metrics** (pure): tier upgrade, escaped defects within `defect_window_days` of the merge, rework, discovery lag (verify-phase Unknowns counted separately), plan churn. §6.12, parent metrics table.
2. **Tokens and dollars** per task from the transcript cache, with coverage; both agents run on subscriptions, so dollars are labelled API-equivalent estimates, not spend. §10, C8.
3. **Topology rebuild**: sessions, helpers, depth, agent types, models, effort; `topology: incomplete` where an agent hides spawns. §5.4, §10.
4. **Summary**: per benchmark tier and per agent: counts, done rate, median and spread of wall time with not-done and upgraded tasks entered at the deadline value, not-done and upgrade rates, defects; field coverage; tasks nearing expiry. §10.
5. **Note-line validation**: malformed lines listed on each card, never blocking. §5.5.
6. Recompute every scorecard since Slice 1; **[YOU]** hand-check three tasks against the scorer; Slice 3 checkpoint.

v1 (comparisons) and "Later" have no tasks in this plan.

---

## Spec coverage (Phase 0 and Slice 1)

| Spec | Where |
|---|---|
| §2.2 C1, C2, C3, C11 (things not built) | Global Constraints; no task adds them |
| §2.2 C4 | Task 1.20 (`verify.md`; retro in Slice 2) |
| §2.2 C5, C10 | Tasks 1.3, 1.7, 1.8 |
| §2.2 C7 | Task 1.9 |
| §2.2 C9 | Tasks 1.10, 1.11, 1.12 |
| §2.2 C13 | Task 1.11 (arm `baseline`, `assigned_commit`), Task 1.9 (reserved `project.json` fields) |
| §2.2 C14, §4.7 | Task 1.10 (`probe_not_cloud`), Task 1.11 |
| §2.2 C15 | Task 1.7 |
| §4.1, §4.3 | Tasks 0.1, 1.2, 1.7, 1.9, 1.22, 1.23 |
| §4.2 | File structure; Task 1.20 |
| §4.4 | Tasks 1.7 (bootstrap text), 1.8 (hook silence), 1.11 |
| §4.6 | Task 1.4 (`push` runs the project's pre-push hook), Task 1.20 |
| §5.1, §5.2 | Tasks 1.12, 1.14–1.17, 1.20 (tier upgrades: Slice 2) |
| §5.3, §5.4 | Tasks 1.14 (delegate flag), 1.7 (transcript paths), 1.20 |
| §5.5, §5.7 | Tasks 1.5, 1.14, 1.20 (note validation: Slice 3) |
| §6.1–6.6 | Tasks 1.2, 1.6, 1.11, 1.12, 1.17, 1.19 (cache: Slice 2) |
| §6.7 | Tasks 1.1, 1.7, 1.8 |
| §6.8 | Task 1.18 |
| §6.9 | Tasks 1.3, 1.7, 1.8, 1.11, 1.12, 1.14 |
| §6.10 | Task 1.18 (review span: Slice 2) |
| §6.11 | Tasks 1.4, 1.13, 1.19, 1.21 |
| §6.12 (Slice 1 rows) | Task 1.19 (wall time, not done, agent time); raw inputs recorded by Tasks 1.7–1.17 |
| §7 (Slice 1 rows) | Tasks 1.8–1.19 |
| §8 | Tasks 1.10, 1.11, 1.12 |
| §9 | Invariant table above |
| §10 (Slice 1 fields) | Task 1.19 |
| §11 Phase 0, Slice 1 | Phase 0 checkpoint; Tasks 1.21, 1.25; Slice 1 checkpoint |
| §12 | Per-task tests; Tasks 0.3 (fixtures), 1.21 (integration), 1.24 (smoke) |
| §13 | Tasks 0.4, 0.5, 0.7 |
| §17 | Task 1.25 |

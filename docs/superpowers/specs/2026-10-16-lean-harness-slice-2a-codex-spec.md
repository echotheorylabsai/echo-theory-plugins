# Lean Harness Slice 2a — Codex Agents — Product Spec

Status: draft r3 for review 2026-10-16 (r2: Phase 0b container results; r3: review round 1 findings,
the Mac results and task worktrees, D8; review log at the end) · owner: the user (sole developer).
Parent: [Lean Harness v0 product spec](./2026-10-08-lean-harness-v0-product-spec.md) (amended by H1–H12).
This spec is the build contract for Slice 2a. Where it and the v0 spec differ, this spec wins; §14 lists
every difference, applied to the v0 spec in the same PR that ships 2a. Anything not mentioned here follows
the v0 spec.

Code: `echotheorylabsai/lean-harness` at `main` `88c0e8c` (v0 + hardening + Logbook, PRs #2–#9).

---

## 1. Purpose and acceptance bar

**2a makes Codex a first-class harness agent, additively.** A Codex session (CLI or desktop app) can
bootstrap, run and finish a harness task, alone or alongside Claude sessions, and every Codex session and
helper is recorded and scored the same way as Claude's. Task worktrees get one predictable home that shows
which agent started each task (D8). Nothing about how Claude tasks are recorded or scored changes.

This completes v0 requirement **R1** ("Claude and Codex agents can bootstrap and complete harness tasks
concurrently and sequentially, correctly") and the Codex half of **R4** (cross-agent helpers link to
the task).

**User decisions (brainstorm, 2026-10-16)**

| # | Question | Decision |
|---|---|---|
| D1 | Scope | Codex only, plus task worktrees (D8). The rest of Slice 2 moves to Slice 2b (§2.2) |
| D2 | Codex surfaces | Codex CLI (interactive `codex` and `codex exec`) and the Codex desktop app. The desktop app is supported once P5 shows it runs user-level hooks |
| D3 | Machines with one agent | Only agents found on the machine are installed and checked; every installed agent must pass. Claude stays the default so a machine without Codex is unchanged (§4) |
| D4 | Codex cost | Tokens only; dollars stay null; dollar totals say they cover Claude sessions only |
| D5 | Codex-launched helpers | Detected automatically from the event log; an instruction rule is the fallback |
| D6 | Proof | The full proof set in §11 |
| D7 | Approach | One new adapter module plus small core changes (A). Rejected: a `harness codex` launcher (cannot wrap the desktop app; a new command to remember) and one shared config-driven adapter (rewrites Claude's working adapter) |
| D8 | Task worktrees | `harness start --new`, run in the project's main checkout, creates the task's worktree at `<parent>/worktrees/<project>/<agent>/<task-id>`, where `<agent>` is the agent that started the task (§15) |

**Additive guarantee.** After 2a: the existing tests pass with no Claude test edited (shared test
infrastructure gains one cleared variable, §12), and `harness score` over every task recorded before 2a
produces the same scorecards (except `as_of`; §11).

---

## 2. Scope

### 2.1 In 2a

- `harness/adapters/codex.py`: hook payload → spool event, user-scope install and uninstall, doctor probes.
- Agent detection: install, uninstall and doctor act only on agents found on the machine (§4).
- Helper detection from the event log for sessions that carry no parent marker (§7).
- Logbook: a bounded Codex session-log reader and token-only cost display (`logbook/build.py`,
  `logbook/viewer.html`; §9).
- Task worktrees created by `harness start --new` (§15).
- Codex hook-payload fixtures and adapter-contract tests; a `codex exec` smoke run.
- Phase 0b: Codex facts checked in the cloud container and on the user's Mac (§10).
- Docs: harness `README.md`, `docs/project-setup.md`, the Logbook Guide, and the v0 spec deltas (§14).

### 2.2 Moved to Slice 2b (unchanged in content)

Retro phase and `retro-bundle`; harness memory, `memory` and `rebase` by-id cleanup; `tier`, `review`,
`defect`; the transcript cache used by scoring. The v0 spec's Slice 2 exit criteria that depend on them
(lessons merged cleanly) move with them.

### 2.3 Out of scope

Codex IDE extensions (VS Code, JetBrains). Codex cloud and every cloud session (v0 R2 stands). A price
table for Codex dollars (D4). Native agent memory (v0 C1). Directing topology (v0 §5.4). Moving existing
task worktrees (§15).

---

## 3. Architecture

```
            ┌──────────────── adapters (REGISTRY) ────────────────┐
hook ──────►│ claude.py                 codex.py (new)            │──► spool (state dir)
            └───────┬──────────────────────────┬──────────────────┘
                    │ found(home)?             │ found(home)?
          install / uninstall / doctor act only on found agents
                    │
harness <cmd> ──► identity: env markers, else the event log (§7) ──► task folder + spool
harness start --new (main checkout) ──► worktrees/<project>/<agent>/<task-id> (§15)
                    │
logbook ──► READERS: claude → read_claude_log, codex → read_codex_log (new)
```

| Part | Change |
|---|---|
| `harness/adapters/codex.py` | **New.** `NAME = "codex"`, `IDENTITY_VAR = "CODEX_THREAD_ID"`, `RUNNING_VAR = "CODEX_THREAD_ID"`, `to_event`, `on_event` (no-op: Codex has no env file), `found`, `install_user`, `uninstall_user`, `doctor_probes` |
| `harness/adapters/__init__.py` | Register `codex`; add `found(home)` per adapter. `identity_vars` and `foreign_vars` are unchanged in code, but their results now include `codex`, which activates v0 §6.9's cross-agent rows for the first time (§7) |
| `harness/adapters/claude.py` | Add `found(home)` (§4) and `RUNNING_VAR = "CLAUDECODE"` (§15) only |
| `install`, `uninstall`, `doctor`, `start` | Loop over found agents; an agent session's `harness start` probes only its own agent (§4) |
| `harness/commands/start.py` | `start --new` on the default branch creates the task worktree; new optional `--agent` (§15) |
| `harness/context.py` | Event-log helper lookup when no parent marker is present (§7) |
| `logbook/build.py`, `logbook/viewer.html` | `read_codex_log` and its `READERS` entry; token-only cost fields and label (§9) |
| `hooks/bootstrap.md` | One sentence: start new tasks with `harness start --new` (§15) |
| `tests/helpers.py` | `CODEX_HOME` added to the cleared variables (§12) |
| `tests/fixtures/codex/` | **New.** Payloads captured in Phase 0b (§10) |
| Unchanged | Phases and phase files, `AGENTS.md`, done gate, timing rules, event schema v1 (no new kinds, no new fields), every command and flag except `start --new --agent` |

---

## 4. Agents found on the machine (D3)

| Agent | Found when | Its home |
|---|---|---|
| Claude | `~/.claude` exists, or no Codex home exists (the default, exactly as today) | `~/.claude` |
| Codex | `$CODEX_HOME` (default `~/.codex`) exists | `$CODEX_HOME` |

Claude stays the default so a machine without Codex behaves exactly as before 2a (including a fresh home
with neither folder, which today's install tests use); a Codex-only machine skips Claude.

| Command | Acts on |
|---|---|
| `install --user` | Every found agent; prints, in addition to today's lines, which agents it found |
| `uninstall --user` | Every agent with harness entries, found or not |
| `harness doctor` | Install group: every found agent |
| `harness start --new` | Install probes of every found agent; any failure registers nothing |
| `harness start` | Install probes of the session's own agent, plus the session and not-cloud probes; every found agent's install probes when the command has no agent identity |

An agent installed after `install --user` (say Codex added later) is found but has no harness entries,
so `start --new` fails with "run `harness install --user`". That is the intended loud failure.

---

## 5. Codex user-scope install

`harness install --user` for Codex is idempotent, prints each change, and adds only its own entries.

| File | Change | Safety rule |
|---|---|---|
| `$CODEX_HOME/hooks.json` | Append one group per event (§6), with no matcher (matches every source), whose one handler is `{"type": "command", "command": "<dispatcher> hook codex <Event>"}`; the `SessionEnd` handler adds `"timeout": 3` (Codex defaults it to 1 s and clamps it to 3 s) | Append after existing groups, never reorder: Codex keys hook trust by position (`<resolved hooks.json path>:<event_snake_case>:<group>:<handler>`), so a reorder would silently un-trust the user's hooks. Never writes a file it cannot parse |
| `$CODEX_HOME/AGENTS.md` | A marked block holding `hooks/bootstrap.md` verbatim | Markers `<!-- lean-harness bootstrap: begin -->` / `end`; a stale block is replaced in place; text outside the block is never touched |
| `$CODEX_HOME/config.toml` | The harness state root (`${XDG_STATE_HOME:-~/.local/state}/harness`, absolute) added to `[sandbox_workspace_write].writable_roots` | Back up first (same permission bits, as Claude's settings backup); edit only that key; re-parse with `tomllib` and confirm nothing else changed, else restore the backup and print the one line to add by hand |

- **Refuses** if `$CODEX_HOME/AGENTS.override.md` exists (it replaces `AGENTS.md`, so the bootstrap would
  never load). Claude's changes from the same run stand; remove the file and rerun (idempotent).
- **Prints the one manual step:** open Codex, run `/hooks`, and trust the harness hooks. The harness never
  writes trust entries itself.
- **`uninstall --user`** removes only the harness hook groups, the marked block and the writable root
  (backup first). If any of the user's hook groups sit after a harness group in the same event, it lists
  them: their position changes, so Codex will ask to trust them again. Trust entries Codex stored for the
  removed hooks are left alone (they match nothing once the hooks are gone).
- Hooks are written to `hooks.json` only; hooks the user keeps inline in `config.toml` are not touched.

---

## 6. Codex events

Same six events and kinds as Claude. Fields are the Codex hook schemas, identical on 0.160.0 (macOS) and
0.163.0 (Linux) (§10). Codex declares `transcript_path` and `agent_transcript_path` nullable, so they are
recorded when present and never reported missing.

| Codex hook | Kind | Required payload fields | Extra fields recorded |
|---|---|---|---|
| `SessionStart` | `session_start` | `session_id`, `source` | `trigger` = `source` |
| `UserPromptSubmit` | `prompt` | `session_id`, `turn_id` | `turn_id` |
| `Stop` | `stop` | `session_id`, `turn_id` | `turn_id` |
| `SubagentStart` | `subagent_start` | `session_id`, `agent_id`, `agent_type` | `agent_id`, `agent_type`; the payload's `transcript_path` is recorded as `agent_transcript_path` and `transcript_path` is null (Codex puts the helper's own log there) |
| `SubagentStop` | `subagent_stop` | `session_id`, `agent_id`, `agent_type` | `agent_id`, `agent_type`, `agent_transcript_path` |
| `SessionEnd` | `session_end` | `session_id`, `reason` | `reason` |

- **A built-in subagent's own events are dropped.** Codex fires `UserPromptSubmit` inside a built-in
  subagent with the parent's `session_id` and the subagent's `agent_id`. Recorded as a `prompt`, it would
  reopen the main session's agent-time span after a `Stop` and double-count the helper, whose time is
  already its `subagent_start` → `subagent_stop` span. Rule: any Codex event with a non-empty `agent_id`
  other than `SubagentStart`/`SubagentStop` records nothing (as the Claude adapter drops a `SubagentStop`
  with an empty `agent_type`).
- **Common fields:** `agent` = `codex`; `model` from the payload (all events but `SessionEnd`); `effort`
  null (no Codex hook carries it; the Logbook reads it from the session log, §9), so scorecard coverage
  counts it null on every Codex event; `parent_session` per §7; `task_id` from `HARNESS_TASK_ID` when
  inherited, else null.
- **Task link:** Codex cannot export markers to its session, so Codex events link to the task by branch
  (v0 §6.8, unchanged).
- **Unexpected payloads** produce a `format_warning`, never a crash (v0 §4.4).

---

## 7. Identity and helpers (D5)

**Who a session is.** Hooks: the payload's `session_id`. Commands: `CODEX_THREAD_ID` (v0 C5, unchanged).

**Parent recorded by the Codex hook** (every event): `HARNESS_PARENT_SESSION` if set; else an inherited
`CODEX_THREAD_ID` or `HARNESS_SESSION_ID` that differs from the payload's `session_id`; else the payload's
`session_id`.

**Helper check in commands** (a generic rule in `context.load`, for any agent): when a session has an
identity, the environment marks it a non-delegate, and no `HARNESS_PARENT_SESSION` is set (never the case
for a Claude session in a task worktree, whose markers set it, so Claude is unaffected), look in this
project's spool for

1. the session's latest `session_start` hook event: a `parent_session` other than the session itself
   makes it a delegate of that parent; or
2. a `subagent_start` hook event whose `agent_id` equals the session id: it is a delegate of that event's
   `session_id`.

A delegate keeps the v0 §6.9 rights: `harness check` (including `--observed`) is allowed; `harness start`
prints "delegate of task <id>: follow your prompt (parent session <P>)" (today's text plus the parent);
`phase`, `rebase`, `pr` and `close` refuse.

| Launch | Recognized by |
|---|---|
| Claude → Claude | Env markers (unchanged) |
| Claude → Codex | Env markers; active from 2a (registering `codex` adds `CODEX_THREAD_ID` to the identity variables) |
| Codex → Claude | Claude adapter reads the inherited `CODEX_THREAD_ID`; active from 2a |
| Codex → its built-in subagents | Hook events under the parent `session_id`; rule 2 for their commands (their shell's `CODEX_THREAD_ID` is the subagent's own id, the `agent_id`) |
| Codex → `codex exec` | Rule 1 (the child's hook processes inherit the parent's `CODEX_THREAD_ID`; its payload and shell carry its own id) |

The environment and payload facts both rules rely on were observed on Codex 0.160.0 (macOS) and 0.163.0
(Linux) (§10); the rules themselves are proven by §12's integration tests and P2/P3.

**Fallback** (only if a later Codex version breaks rule 1): the Codex block becomes `hooks/bootstrap.md`
plus one Codex-only line — "To launch another agent process for part of a harness task, prefix it with
`HARNESS_PARENT_SESSION=$CODEX_THREAD_ID`" — and `codex_bootstrap` compares against that composed text.
`AGENTS.md` and `hooks/bootstrap.md` do not change for it.

---

## 8. Doctor

| Probe | Codex check | Fix printed |
|---|---|---|
| `codex_hooks` | A harness group for each of the six events in `$CODEX_HOME/hooks.json`; `[features].hooks` not `false` | `harness install --user` |
| `codex_hooks_trusted` | For each harness hook, a `[hooks.state."<key>"]` entry in `config.toml` whose key ends with that hook's `:<event_snake_case>:<group>:<handler>` and whose path part, resolved, equals `$CODEX_HOME/hooks.json` resolved, with a `trusted_hash` and `enabled` not `false`. The hash is not recomputed (Codex's own format, not derivable); a hook changed after trust is caught by the session probe | Open Codex, `/hooks`, trust the harness hooks |
| `codex_writable_root` | The state root is in `[sandbox_workspace_write].writable_roots` | `harness install --user` |
| `codex_bootstrap` | The marked block is present and equals `hooks/bootstrap.md` | `harness install --user` |
| `codex_no_override` | No `$CODEX_HOME/AGENTS.override.md` | Remove or rename it |
| `codex_full_access` | Passes unless the command's identity is Codex and `CODEX_SANDBOX` is set (always passes in `start --new` and `doctor` without a Codex identity) | Relaunch Codex with full access (`-s danger-full-access`, or the app's full-access setting) |

The shared session probe (this session's hook events reached the spool in the last 10 minutes) applies to
Codex unchanged. Codex main sessions run with full access (v0 C6, unchanged); sandboxed Codex helpers
record through the writable root.

---

## 9. Data and the Logbook (D4)

| Field | Codex source |
|---|---|
| Model | Hook payload; session log `turn_context.model` |
| Effort | Session log `turn_context.effort` (Logbook only; events carry null) |
| Tokens | Session log: the last `token_count` event's `info.total_token_usage` (cumulative: input, cached input, output, reasoning output, total) |
| Dollars | Null. Never estimated |
| Helper links | Hook events |

**`read_codex_log`** returns the same keys as `read_claude_log` and parses only: `exec_command`/`shell`
calls (through the existing command inspector, so `harness` commands, their outcomes and GitHub writes are
counted as for Claude), `apply_patch` (writes to harness-owned paths), `spawn_agent` (helper launches),
`turn_context`, `token_count` and `session_meta`. Every other tool call counts as not inspected (the
Claude reader's existing rule). `cost` is null.

**Cost and tokens.** `read_codex_log` fills `usage` and `models`. `cost_summary` returns a record whenever
any log has a cost record or `usage`: `usd` null when no log has a cost record; per-model tokens for every
model (`usd` null for token-only models); `sessions` and `logs_total` count only logs of agents whose logs
carry dollars (Claude), so Codex sessions never make the total partial; `tokens_only` = the number of Codex
logs read. The viewer prints "Claude sessions only" beside the dollar total when `tokens_only` > 0. A
missing Claude cost record still marks the total partial. Claude-only tasks produce the same fields as
today plus `tokens_only: 0`.

---

## 10. Phase 0b: Codex facts

Method (both machines): `tests/smoke/codex_facts.py` (shipped in 2a) runs `codex exec` in a throwaway
`$CODEX_HOME` against a local mock model provider (`wire_api = "responses"`, no account, no network) with
`--dangerously-bypass-hook-trust` (throwaway home only) and a hook logger; it writes a report and scrubbed
payload fixtures. Plus, in the container: the hook input JSON schemas embedded in the binary, the
app-server's `hooks/list`, and hand-written trust entries.

**Ran:** Linux container, Codex CLI 0.163.0 (2026-10-16); the user's Mac, macOS 27.0, Codex CLI 0.160.0,
Python 3.12.8, git 2.54.0 (2026-10-16, through a Remote Control session). All four runs passed on both.

| # | Fact | Mac 0.160 | Linux 0.163 | Used in |
|---|---|---|---|---|
| 0b.1 | `hooks.json` is `{"hooks": {"<Event>": [{"matcher"?, "hooks": [{"type": "command", "command", "timeout"?}]}]}}`; all six events fire; payload fields as in §6; no `effort` in any hook | ✅ | ✅ | §5, §6 |
| 0b.3 | A `codex exec` launched from a Codex shell: its hook processes inherit the parent's `CODEX_THREAD_ID`; its payload `session_id` and its shell's `CODEX_THREAD_ID` are its own | ✅ | ✅ | §7 rule 1 |
| 0b.4 | A built-in subagent: `SubagentStart`/`SubagentStop` carry the parent `session_id` and `agent_id` = the subagent's thread id; its shell's `CODEX_THREAD_ID` = that `agent_id`; it fires `UserPromptSubmit` with the parent `session_id` and its `agent_id`; `SubagentStart.transcript_path` is the subagent's own log | ✅ | ✅ | §6, §7 rule 2 |
| 0b.5 | Hook processes never see their own session's `CODEX_THREAD_ID` (v0 §16 holds); shells see it | ✅ | ✅ | §7 |
| 0b.6 | Trust: `[hooks.state."<key>"]` with `trusted_hash` (= `hooks/list` `currentHash`, `sha256:…`, not derivable from the entry) and `enabled`; the key's path is the absolute, symlink-resolved `hooks.json`; a bare `hooks.json:…` key is not honored; with valid entries, trusted hooks run under plain `codex exec` and untrusted ones are skipped silently; `[features].hooks` is stable and on by default | — | ✅ | §5, §8 |
| 0b.7 | `SessionEnd` hook timeout: default 1 s, clamped to at most 3 s; `timeout: 3` accepted without warning | ✅ | ✅ | §5, §13 |
| 0b.8 | Session log: `session_meta`, `turn_context` (`model`, `effort`), `function_call` items (`exec_command` with `cmd`), cumulative `token_count`; no dollars | — | ✅ | §9 |
| 0b.9 | Sandboxed shell: `CODEX_SANDBOX=seatbelt` on macOS (absent on Linux); hook `permission_mode` reads `bypassPermissions` under both modes in `exec`, so it is not a sandbox signal | ✅ | ✅ (Linux form) | §8 |

**Left for P5 (the desktop app):** the app runs user-level hooks from `$CODEX_HOME/hooks.json` and sends
`SessionEnd`; its shell has `CODEX_THREAD_ID` equal to the hook `session_id` and no `CODEX_SANDBOX` under
full access; hooks trusted in the CLI also run in the app (or can be trusted there); `session_meta.originator`
tells an app session from a CLI one. The first real `/hooks` trust on the Mac confirms 0b.6's key form
there. If the app fails, it is listed as unsupported (D2); the session probe already stops it before triage.

---

## 11. Proof: exit criteria (D6)

| # | Real task | Passes when |
|---|---|---|
| P1 | mvp: a Codex-led task and a Claude-led task registered and running at the same time | Both merged; both scorecards complete (all boundaries present, gate evaluated, no unexplained orphans) |
| P2 | mvp: a Claude-led task whose verify runs in a Codex helper (`codex exec`) | The helper's `harness check` recorded with agent `codex` and the Claude session as parent |
| P3 | mvp: a Codex-led task that launches a `codex exec` helper | The helper is recorded as a delegate; the controller never changes; a `harness phase` from it, if it runs one, refuses |
| P4 | echo-wiki: one Codex-led task | Merged; scorecard complete |
| P5 | At least one Codex session in P1–P4 runs in the desktop app | The §10 "Left for P5" facts hold; recorded like a CLI session |
| P6 | Every proof task registered with `start --new` from the main checkout | Each worktree at `worktrees/<project>/<agent>/<task-id>` (§15) |
| All | — | Logbook pages build for every proof task (the build's clock and agent-time parity check passes); Codex tokens shown, dollars labeled "Claude sessions only" where Codex ran |
| Regression | Every task recorded before 2a | `harness score` cards identical except `as_of` (in-flight tasks compared from scores run back to back); existing suite green with no Claude test edited |

---

## 12. Testing

- **Isolation:** tests never see the real `$CODEX_HOME`: `clean_env` clears it (`tests/helpers.py`
  `CLEARED`); a test that needs Codex creates `<temp HOME>/.codex` and sets `CODEX_HOME` itself. The smoke
  sets `CODEX_HOME=<temp>/.codex` explicitly.
- **Unit:** Codex `to_event` from fixtures (including the `SubagentStart` path swap and dropped helper
  events); parent rule (§7) for each launch row; event-log helper lookup (both rules, plus a session with no
  hook events); found-agent selection for each command in §4; `--agent` resolution (§15).
- **Integration, live registry (no patching of `identity_vars`):** Claude P → `codex exec` child: its
  `check` event has `agent=codex`, `parent_session=P`, `delegate=true`; Codex P → `claude` child likewise;
  a Codex-launched Codex child (rule 1) and a built-in subagent (rule 2) refused by `phase`.
- **Adapter contract:** the Phase 0b fixtures; a payload missing a required field gives a `format_warning`.
- **Install safety (temp `$CODEX_HOME`):** idempotent re-install; existing hook groups keep their positions;
  a stale bootstrap block is replaced in place; an unparsable `hooks.json` or `config.toml` is never
  written; the `config.toml` edit changes only `writable_roots`; override file refuses; uninstall lists
  shifted user hooks and restores files to their pre-install content when nothing else changed; the trust
  probe accepts a resolved-path key (symlinked home) and rejects a bare one.
- **Worktrees (temp repo with a bare remote):** `start --new` on the default branch creates
  `worktrees/<project>/<agent>/<task-id>` on branch `<slug>` and registers inside it; `--agent` and marker
  resolution; refusal on an existing path, branch or task id leaves nothing behind; a failure after the
  worktree exists removes it and its branch; `start --new` in an existing worktree behaves as today.
- **Logbook:** `read_codex_log` against a recorded Codex log; a Codex-only task shows tokens and no
  dollars; a mixed task with every Claude log read is not partial; a Claude-only task's cost fields are
  unchanged.
- **Regression:** the existing suite; re-score of a copy of the real state dir, diffed (except `as_of`).
- **Smoke:** `tests/smoke/codex_facts.py` (the Phase 0b script) and the real-agent smoke extended with a
  scripted `codex exec` task in a throwaway `CODEX_HOME` with `auth.json` copied in and
  `--dangerously-bypass-hook-trust` (`< /dev/null`).

---

## 13. Risks and known limits

| Risk or limit | Handling |
|---|---|
| Codex changes fast (inline `[hooks]` in `config.toml` and async hooks are recent) | `tests/smoke/codex_facts.py` re-checks a new version in minutes; unknown payloads warn, never crash; doctor reports drift |
| The desktop app may not send `SessionEnd`, or the `SessionEnd` hook outlives Codex's 3 s cap | The controller-end pause (H3) does not apply to that session; the clock keeps running until the next `harness` command, as before H3. Disclosed on the scorecard by the missing `session_end`. The hook normally finishes well inside 3 s |
| Uninstall can move the user's own hooks | It lists them so the user re-trusts them |
| A Codex helper not recognized (a later Codex version breaks rule 1 before the fallback ships) | It looks like a main session. Sandboxed, `codex_full_access` fails and it cannot take control; with full access it can pass `harness start` and become controller. The Logbook shows the controller change; the scorecard's timing follows the recorded controller |
| A Codex session started from a shell that inherited an unrelated session's `CODEX_THREAD_ID` | Rule 1 makes it a delegate of that session; `harness start` names the parent, so the user relaunches from a clean shell |
| Cross-agent chains three deep (Codex → Claude → Codex, Claude → Codex → Claude) refuse as ambiguous | Pre-existing v0 limit (identity resolution sees two identities that differ from the parent); unchanged in 2a; transcripts hold the chain |
| D3 blocks every `start --new` until a newly found agent is installed and trusted | Loud by design; the fix is printed |
| Codex dollars unknown | Tokens recorded; dollar totals labeled Claude-only (D4) |
| Each `codex exec` adds a trust entry per worktree to `config.toml` | Codex's own behavior; harmless (v0 §16) |

---

## 14. Changes to the v0 spec (applied when 2a ships)

| § | Change |
|---|---|
| Header | Add: "Slice 2 split 2026-10-16: 2a Codex agents (this repo's `2026-10-16-lean-harness-slice-2a-codex-spec.md`); 2b the rest" |
| 4.1 | `~/.codex/hooks.json` line: "6 hook groups (you trust them once with `/hooks`)"; the user-scope files are written only for agents found on the machine; add the `worktrees/<project>/<agent>/<task-id>` location |
| 4.3 | `install --user`: acts on found agents (§4 here); trust keys are `<resolved hooks.json path>:<event_snake_case>:<group>:<handler>` (replaces `hooks.json:stop:0:0`); the `config.toml` edit's backup and re-parse rule; uninstall's shifted-hooks list |
| 4.4 | Start flow: step 1 becomes `harness start --new` in the main checkout, which creates the worktree (§15 here); the in-place flow stays |
| 6.9 | Add the event-log helper rules (§7 here) after "Delegates"; the delegate notice names the parent |
| 7 | `start --new`: `[--agent NAME]`, creates the worktree on the default branch |
| 8 | Install probes: per found agent; `harness start` in a session probes its own agent; Codex probe names as in §8 here |
| 11 | Slice 2 row split into 2a (this spec) and 2b (§2.2 here) with their exit criteria |
| 13 | Close the Codex rows with Phase 0b results |
| 14 | Add the §13 rows here; correct "nested delegation … records the top session as parent" to the ambiguity refusal |
| 16 | Add a "Phase 0b" paragraph: §10 here |
| 17 | Daily use steps 1–3: one `harness start --new` in the main checkout, then open the agent in the printed worktree |

---

## 15. Task worktrees (D8)

**Goal.** Every task worktree sits in one predictable place that shows its project and the agent that
started it, so parallel tasks from several agents (Claude, Codex, later others) stay easy to find and
clean up, and the parent folder holds only project checkouts.

```
<parent>/                                the folder that holds the project's main checkout
├─ <project>/                            main checkout (never a task worktree)
└─ worktrees/
   └─ <project>/
      └─ <agent>/                        claude, codex, … (an adapter name)
         └─ <task-id>/                   <date>-<slug>: oldest first
```

- `<parent>` and `<project>` come from the git common dir (the main checkout's parent folder and folder
  name), so they are the same from any worktree of the project.
- `<agent>` is the agent that started the task. A new adapter (say Cursor) gets its own folder with no
  other change.
- The branch is `<slug>`.

**`harness start --new` on the default branch creates the worktree.** Run in the main checkout (where the
default branch is checked out):

1. **Agent:** `--agent NAME` if given (an adapter name); else the one adapter whose `RUNNING_VAR` is set in
   the environment (Claude Code sets `CLAUDECODE=1` in its shells; Codex sets `CODEX_THREAD_ID`); none or
   several → refuse: "pass --agent claude|codex".
2. **Before creating anything:** install probes (every found agent), the not-cloud probe, and refuse if the
   path, the local or remote branch, or the task id already exists.
3. `git fetch` the integration branch; `git worktree add <parent>/worktrees/<project>/<agent>/<task-id>
   -b <slug> <remote>/<default>`.
4. Register inside the new worktree exactly as today (pre-start probes there, the locked uniqueness check,
   task folder, `start` event). The `start` event's `cwd` is the worktree path, so the record carries the
   agent folder; no new event field.
5. Any failure after step 3 removes the worktree and the branch it created: nothing registered, nothing
   left behind.
6. Print the task id, the worktree path and "open <agent> in that folder".

**Today's flow stays.** On any other branch (a worktree you made yourself), `start --new` registers in
place exactly as today. Tasks in flight are untouched; moving an old worktree is optional
(`git worktree move`).

**Agents learn it from the bootstrap.** `hooks/bootstrap.md` gains one sentence: "To start a new harness
task, run `harness start --new` in the project's main checkout; it creates the task's worktree." This
changes the installed bootstrap for both agents, so `harness install --user` reruns after the update (it
must anyway, for Codex).

**Not covered.** Worktrees an agent app makes on its own (Codex `--worktree`, Claude Code's own isolation)
are not harness tasks (v0 §4.4) and stay where the app puts them. Cleanup is unchanged (the README's
cleanup step), now with a predictable path; `git worktree list` shows agent and task on each line.

---

## 16. After 2a

Slice 2b: retro, harness memory, `tier`, `review`, `defect`, transcript cache — then Slice 3 and v1 as in
the v0 roadmap. A Codex transcript reader for scoring (2b's cache) reuses `read_codex_log`'s parsing.

---

## Review log

### Round 1 (r2 → r3): Fable (max effort) REVISE

| Finding | Resolution |
|---|---|
| F1 blocker: tests could write the real `$CODEX_HOME` | §12 isolation; `CODEX_HOME` cleared in `tests/helpers.py` |
| F2 cross-agent rows called "unchanged" but switch on with the registry | §3 and §7 wording; live-registry integration tests (§12) |
| F3 `SubagentStart.transcript_path` is the helper's log | §6 records it as `agent_transcript_path` |
| F4 Codex tokens not displayable; label not measurable | §9 names the fields; `viewer.html` in scope; §12 tests |
| F5 trust key form unobserved | Verified in the container (0b.6): absolute resolved path only; §8 matching rule |
| F6 `harness start` without identity | §4: every found agent |
| F7 where the sandbox check lives | §8 `codex_full_access` in the adapter's probes |
| F8 fallback vs verbatim bootstrap | §7: composed text, compared as such |
| F9 delegate notice | §7: today's text plus the parent |
| F10 identical scorecards impossible (`as_of`) | §1, §11 |
| F11 smoke trust and auth | §12 smoke; 0b.6 shows trusted hooks run under plain `exec` |
| F12 depth-3 chains refuse | §13 row; v0 §14 corrected (§14) |
| F13 drop reason and future-proofing | §6 rule reworded |
| F14 desktop-app check under-specified | §10 "Left for P5" |
| F15 install output additive | §4 |
| F16 "rules confirmed" overstated | §7 wording |
| F17 override refusal after Claude writes | §5 |
| Cut: `parent_thread_id` cross-check | Cut (§9) |
| Bound: `read_codex_log` parity | Bounded to the listed items (§9) |
| Optional: env-only rule 2 | Not taken: one mechanism (the event log) for both rules |

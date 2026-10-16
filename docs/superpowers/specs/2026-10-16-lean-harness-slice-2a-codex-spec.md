# Lean Harness Slice 2a — Codex Agents — Product Spec

Status: draft for review 2026-10-16 · owner: the user (sole developer).
Parent: [Lean Harness v0 product spec](./2026-10-08-lean-harness-v0-product-spec.md) (amended by H1–H12).
This spec is the build contract for Slice 2a. Where it and the v0 spec differ, this spec wins; §14 lists
every difference, applied to the v0 spec in the same PR that ships 2a. Anything not mentioned here follows
the v0 spec.

Code: `echotheorylabsai/lean-harness` at `main` `88c0e8c` (v0 + hardening + Logbook, PRs #2–#9).

---

## 1. Purpose and acceptance bar

**2a makes Codex a first-class harness agent, additively.** A Codex session (CLI or desktop app) can
bootstrap, run and finish a harness task, alone or alongside Claude sessions, and every Codex session and
helper is recorded and scored the same way as Claude's. Nothing about how Claude tasks run or are scored
changes.

This completes v0 requirement **R1** ("Claude and Codex agents can bootstrap and complete harness tasks
concurrently and sequentially, correctly") and the Codex half of **R4** (cross-agent helpers link to
the task).

**User decisions (brainstorm, 2026-10-16)**

| # | Question | Decision |
|---|---|---|
| D1 | Scope | Codex only. The rest of Slice 2 moves to Slice 2b (§2.2) |
| D2 | Codex surfaces | Codex CLI (interactive `codex` and `codex exec`) and the Codex desktop app. The desktop app is supported only if Phase 0b shows it runs user-level hooks |
| D3 | Machines with one agent | Only agents found on the machine are installed and checked; every installed agent must pass. Claude stays the default so a machine without Codex is unchanged (§4) |
| D4 | Codex cost | Tokens only; dollars stay null; dollar totals say they cover Claude sessions only |
| D5 | Codex-launched helpers | Test first, then detect automatically from the event log; an instruction rule is the fallback |
| D6 | Proof | The full proof set in §11 |
| D7 | Approach | One new adapter module plus small core changes (A). Rejected: a `harness codex` launcher (cannot wrap the desktop app; a new command to remember) and one shared config-driven adapter (rewrites Claude's working adapter) |

**Additive guarantee.** After 2a: the existing test suite passes unchanged (Claude tests are not edited),
and `harness score` over every task recorded before 2a produces scorecards identical to today's.

---

## 2. Scope

### 2.1 In 2a

- `harness/adapters/codex.py`: hook payload → spool event, user-scope install and uninstall, doctor probes.
- Agent detection: install, uninstall and doctor act only on agents found on the machine (§4).
- Helper detection from the event log for sessions that carry no parent marker (§7).
- Logbook: a Codex session-log reader at parity with the Claude reader where Codex logs carry the data (§9).
- Codex hook-payload fixtures and adapter-contract tests; a `codex exec` smoke run.
- Phase 0b checks on the user's Mac (§10).
- Docs: harness `README.md`, `docs/project-setup.md`, the Logbook Guide, and the v0 spec deltas (§14).

### 2.2 Moved to Slice 2b (unchanged in content)

Retro phase and `retro-bundle`; harness memory, `memory` and `rebase` by-id cleanup; `tier`, `review`,
`defect`; the transcript cache used by scoring. The v0 spec's Slice 2 exit criteria that depend on them
(lessons merged cleanly) move with them.

### 2.3 Out of scope

Codex IDE extensions (VS Code, JetBrains). Codex cloud and every cloud session (v0 R2 stands). A price
table for Codex dollars (D4). Native agent memory (v0 C1). Directing topology (v0 §5.4).

---

## 3. Architecture

```
            ┌──────────────── adapters (REGISTRY) ────────────────┐
hook ──────►│ claude.py (unchanged)      codex.py (new)           │──► spool (state dir)
            └───────┬──────────────────────────┬──────────────────┘
                    │ found(home)?             │ found(home)?
          install / uninstall / doctor act only on found agents
                    │
harness <cmd> ──► identity: env markers, else the event log (§7) ──► task folder + spool
                    │
logbook ──► READERS: claude → read_claude_log, codex → read_codex_log (new)
```

| Part | Change |
|---|---|
| `harness/adapters/codex.py` | **New.** `NAME = "codex"`, `IDENTITY_VAR = "CODEX_THREAD_ID"`, `to_event`, `on_event` (no-op: Codex has no env file), `found`, `install_user`, `uninstall_user`, `doctor_probes` |
| `harness/adapters/__init__.py` | Register `codex`; add `found(home)` per adapter; `identity_vars` and `foreign_vars` unchanged |
| `harness/adapters/claude.py` | Add `found(home)` only (§4) |
| `install`, `uninstall`, `doctor`, `start` | Loop over found agents; `start` in an agent session probes only its own agent (§8) |
| `harness/context.py` / `identity.py` | Event-log helper lookup when no parent marker is present (§7) |
| `logbook/build.py` | `read_codex_log` and its `READERS` entry; cost text for token-only sessions (§9) |
| `tests/fixtures/codex/` | **New.** Real payloads from Phase 0b |
| Unchanged | Phases and phase files, `AGENTS.md` (unless the D5 fallback is needed), done gate, timing rules, event schema v1 (no new kinds, no new fields), every command's flags |

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
| `install --user` | Every found agent; prints which agents it found and which it skipped |
| `uninstall --user` | Every agent with harness entries, found or not |
| `harness doctor` | Install group: every found agent |
| `harness start --new` | Install probes of every found agent; any failure registers nothing |
| `harness start` (agent session) | Install probes of the session's own agent only, plus the session and not-cloud probes |

An agent installed after `install --user` (say Codex added later) is found but has no harness entries,
so `start --new` fails with "run `harness install --user`". That is the intended loud failure.

---

## 5. Codex user-scope install

`harness install --user` for Codex is idempotent, prints each change, and adds only its own entries.

| File | Change | Safety rule |
|---|---|---|
| `$CODEX_HOME/hooks.json` | Append one matcher group per event (§6), matching every source, whose handler runs `<dispatcher> hook codex <Event>` | Append after existing groups, never reorder: Codex keys hook trust by file and position (`hooks.json:<event>:<i>:<j>`), so a reorder would silently un-trust the user's hooks. Never writes a file it cannot parse |
| `$CODEX_HOME/AGENTS.md` | A marked block holding `hooks/bootstrap.md` verbatim | Markers `<!-- lean-harness bootstrap: begin -->` / `end`; a stale block is replaced in place; text outside the block is never touched |
| `$CODEX_HOME/config.toml` | The harness state root (`${XDG_STATE_HOME:-~/.local/state}/harness`, absolute) added to `[sandbox_workspace_write].writable_roots` | Back up first (same permission bits, as Claude's settings backup); edit only that key; re-parse with `tomllib` and confirm nothing else changed, else restore the backup and print the one line to add by hand |

- **Refuses** if `$CODEX_HOME/AGENTS.override.md` exists (it replaces `AGENTS.md`, so the bootstrap would
  never load).
- **Prints the one manual step:** open Codex, run `/hooks`, and trust the harness hooks. The harness never
  writes trust entries itself.
- **`uninstall --user`** removes only the harness hook groups, the marked block and the writable root
  (backup first). If any of the user's hook groups sit after a harness group in the same event, it lists
  them: their position changes, so Codex will ask to trust them again. Trust entries Codex stored for the
  removed hooks are left alone (they match nothing once the hooks are gone).
- Hooks are written to `hooks.json` only; hooks the user keeps inline in `config.toml` are not touched.

---

## 6. Codex events

Same six events and kinds as Claude. Required fields are the v0 §16 facts; Phase 0b fixtures confirm or
correct them before the adapter is written.

| Codex hook | Kind | Required payload fields | Extra fields recorded |
|---|---|---|---|
| `SessionStart` | `session_start` | `session_id`, `transcript_path`, `source` | `trigger` = `source` |
| `UserPromptSubmit` | `prompt` | `session_id`, `transcript_path`, `turn_id` | `turn_id` |
| `Stop` | `stop` | `session_id`, `transcript_path`, `turn_id` | `turn_id` |
| `SubagentStart` | `subagent_start` | `session_id`, `transcript_path`, `agent_id`, `agent_type` | `agent_id`, `agent_type` |
| `SubagentStop` | `subagent_stop` | `session_id`, `transcript_path`, `agent_id`, `agent_type`, `agent_transcript_path` | `agent_id`, `agent_type` |
| `SessionEnd` | `session_end` | `session_id`, `transcript_path`, `reason` | `reason` |

- **Common fields:** `agent` = `codex`; `model` from the payload (all events but `SessionEnd`); `effort`
  from the payload if Phase 0b finds it there, else null in the event (the Logbook may still read it from
  the session log, §9); `parent_session` per §7; `task_id` from `HARNESS_TASK_ID` when inherited, else null.
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
prints "delegate of task <id>: follow your prompt"; `phase`, `rebase`, `pr` and `close` refuse.

| Launch | Recognized by |
|---|---|
| Claude → Claude or Codex | Env markers (unchanged) |
| Codex → Claude | Claude adapter reads the inherited `CODEX_THREAD_ID` (unchanged) |
| Codex → its built-in subagents | Hook events under the parent `session_id`; rule 2 for their commands |
| Codex → `codex exec` | Rule 1, if Phase 0b shows the child's hooks inherit the parent's `CODEX_THREAD_ID` |

**Fallback** (only if Phase 0b shows rule 1 cannot see the parent): the Codex bootstrap block gains one line
— "To launch another agent process for part of a harness task, prefix it with
`HARNESS_PARENT_SESSION=$CODEX_THREAD_ID`" — and the risk in §13 stays open. `AGENTS.md` stays
agent-neutral either way.

---

## 8. Doctor

| Probe | Codex check | Fix printed |
|---|---|---|
| `codex_hooks` | A harness group for each of the six events in `$CODEX_HOME/hooks.json`; `[features].hooks` not `false` | `harness install --user` |
| `codex_hooks_trusted` | A trust entry in `config.toml` for the position of each harness hook | Open Codex, `/hooks`, trust the harness hooks |
| `codex_writable_root` | The state root is in `[sandbox_workspace_write].writable_roots` | `harness install --user` |
| `codex_bootstrap` | The marked block is present and equals `hooks/bootstrap.md` | `harness install --user` |
| `codex_no_override` | No `$CODEX_HOME/AGENTS.override.md` | Remove or rename it |
| Session probe (Codex) | This session's hook events reached the spool in the last 10 minutes (shared probe), and `CODEX_SANDBOX` is unset | Relaunch Codex with full access (`-s danger-full-access`, or the app's full-access setting) |

Codex main sessions run with full access (v0 C6, unchanged); sandboxed Codex helpers record through the
writable root.

---

## 9. Data and the Logbook (D4)

| Field | Codex source |
|---|---|
| Model | Hook payload |
| Effort | Payload or session log, whichever Phase 0b finds; else null |
| Tokens | Session log cumulative `token_count` totals, complete per session |
| Dollars | Null. Never estimated |
| Helper links | Hook events; `session_meta.parent_thread_id` in the helper's log as a cross-check |

**`read_codex_log`** returns the same shape as `read_claude_log`. It fills what Codex logs carry: tool calls
by kind, `harness` commands and outcomes, GitHub writes for the guardrail checks, helper launches, models,
token usage, and how the session began. A count Codex logs do not carry is reported as not inspected,
never as zero. `cost` is null.

**Cost text.** A task with Codex sessions shows Codex tokens, and its dollar total is labeled "Claude
sessions only" instead of "partial": Codex sessions never have a cost record, so they are not counted as
missing one. A missing Claude cost record still marks the total partial.

---

## 10. Phase 0b: checks on the user's Mac (before code)

Run by the user in their own terminal from a script in the plan (an agent's safety check refused the
full-access `codex exec` in Phase 0). Results go into v0 §16 and the fixtures.

| # | Check | Feeds | If it fails |
|---|---|---|---|
| 0b.1 | Capture all six Codex CLI hook payloads (a throwaway repo; a session that runs a built-in subagent) | §6 required fields, fixtures | Adjust §6 to what Codex sends |
| 0b.2 | The Codex desktop app runs user-level hooks from `$CODEX_HOME/hooks.json` | D2 | Desktop app listed as unsupported; the session probe already stops it before triage |
| 0b.3 | A `codex exec` launched from a Codex session: do its hooks see the parent's `CODEX_THREAD_ID`? What do its shell commands see? | §7 rule 1 | §7 fallback |
| 0b.4 | A Codex built-in subagent's shell commands: which `CODEX_THREAD_ID` do they see? | §7 rule 2 | Same as parent: nothing to do; otherwise rule 2 as written |
| 0b.5 | Re-check v0 §16 Codex facts on the installed version: `hooks.json` shape, trust storage key format, `[features].hooks`, `SessionEnd` in the desktop app, where effort is recorded | §5, §6, §8, §9 | Update the affected section before the plan |

---

## 11. Proof: exit criteria (D6)

| # | Real task | Passes when |
|---|---|---|
| P1 | mvp: a Codex-led task and a Claude-led task registered and running at the same time | Both merged; both scorecards complete (all boundaries present, gate evaluated, no unexplained orphans) |
| P2 | mvp: a Claude-led task whose verify runs in a Codex helper (`codex exec`) | The helper's `harness check` recorded with agent `codex` and the Claude session as parent |
| P3 | mvp: a Codex-led task that launches a `codex exec` helper | The helper is recorded as a delegate; the controller never changes; a `harness phase` from it, if it runs one, refuses |
| P4 | echo-wiki: one Codex-led task | Merged; scorecard complete |
| P5 | At least one Codex session in P1–P4 runs in the desktop app (if 0b.2 passed) | Recorded like a CLI session |
| All | — | Logbook pages build for every proof task (the build's clock and agent-time parity check passes); Codex tokens shown |
| Regression | Every task recorded before 2a | `harness score` cards identical to today's; existing suite green with Claude tests unedited |

---

## 12. Testing

- **Unit:** Codex `to_event` from fixtures; parent rule (§7) for each launch row; event-log helper lookup
  (both rules, plus a session with no hook events); found-agent selection for each command in §4.
- **Adapter contract:** Phase 0b fixtures; a payload missing a required field gives a `format_warning`.
- **Install safety (temp `$CODEX_HOME`):** idempotent re-install; existing hook groups keep their
  positions; a stale bootstrap block is replaced in place; an unparsable `hooks.json` or `config.toml` is
  never written; the `config.toml` edit changes only `writable_roots`; override file refuses; uninstall
  lists shifted user hooks and restores files to their pre-install content when nothing else changed.
- **Logbook:** `read_codex_log` against a recorded Codex log; cost text for Claude-only, Codex-only and
  mixed tasks.
- **Regression:** the existing suite unedited; re-score of a copy of the real state dir, diffed.
- **Smoke:** the existing real-agent smoke extended with a scripted `codex exec` task (`< /dev/null`).

---

## 13. Risks and known limits

| Risk or limit | Handling |
|---|---|
| Codex changes fast (inline `[hooks]` in `config.toml` and async hooks are recent) | Phase 0b re-checks; unknown payloads warn, never crash; doctor reports drift |
| The desktop app may not send `SessionEnd` | The controller-end pause (H3) does not apply to that session; the clock keeps running until the next `harness` command, as before H3. Disclosed on the scorecard by the missing `session_end` |
| Uninstall can move the user's own hooks | It lists them so the user re-trusts them |
| A `codex exec` helper not recognized (if 0b.3 fails and the agent skips the fallback line) | It looks like a main session. Sandboxed, it fails the session probe (`CODEX_SANDBOX` set) and cannot take control; with full access it can pass `harness start` and become controller. The Logbook shows the controller change; the scorecard's timing follows the recorded controller |
| Codex dollars unknown | Tokens recorded; dollar totals labeled Claude-only (D4) |
| Each `codex exec` adds a trust entry per worktree to `config.toml` | Codex's own behavior; harmless (v0 §16) |

---

## 14. Changes to the v0 spec (applied when 2a ships)

| § | Change |
|---|---|
| Header | Add: "Slice 2 split 2026-10-16: 2a Codex agents (this repo's `2026-10-16-lean-harness-slice-2a-codex-spec.md`); 2b the rest" |
| 4.1 | `~/.codex/hooks.json` line: "6 hook groups (you trust them once with `/hooks`)"; the user-scope files are written only for agents found on the machine |
| 4.3 | `install --user`: acts on found agents (§4 here); the `config.toml` edit's backup and re-parse rule; uninstall's shifted-hooks list |
| 6.9 | Add the event-log helper rules (§7 here) after "Delegates" |
| 8 | Install probes: per found agent; `harness start` in a session probes its own agent; Codex probe names as in §8 here |
| 11 | Slice 2 row split into 2a (this spec) and 2b (§2.2 here) with their exit criteria |
| 13 | Close the Codex rows with Phase 0b results |
| 14 | Add the §13 rows here |
| 16 | Add a "Phase 0b" paragraph with the installed Codex version and findings |

---

## 15. After 2a

Slice 2b: retro, harness memory, `tier`, `review`, `defect`, transcript cache — then Slice 3 and v1 as in
the v0 roadmap. A Codex transcript reader for scoring (2b's cache) reuses `read_codex_log`'s parsing.

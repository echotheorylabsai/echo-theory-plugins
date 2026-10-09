# Lean Harness v0 — Product Spec

Status: draft for review · 2026-10-08 · owner: the user (sole developer).
Parent design (approved): [`docs/lean-coding-harness-v0-design.md`](../../lean-coding-harness-v0-design.md),
also the Claude Doc at https://claude.ai/code/artifact/641331bd-9fc6-4211-8045-9f1c4ee6a467.
This spec is the build contract for v0. Where it and the parent differ, this spec wins, and every
difference is listed in §2.2. Anything this spec does not mention follows the parent design.

---

## 1. Purpose, requirements and acceptance bar

**v0 is** a personal, portable harness for Claude Code and Codex. It runs coding tasks through a
tiered workflow (triage → research → resolve unknowns → plan → build → verify → retro), records
every task from the outside, and scores each task the same way for any agent, model or topology.

**Acceptance bar, in the user's words:** "this current spec should be complete enough where we can
start using it for real work across multiple projects with both agents working concurrently and all
required data is being recorded so it can harness can be analyzed, evaluated and benchmarked as
planned in the proposal", and it "can be easily evolved to a later version with more capabilities as
planned but deferred like harness comparisons".

**Requirements**

| # | Requirement | Satisfied by |
|---|---|---|
| R1 | Claude and Codex agents can bootstrap and complete harness tasks concurrently and sequentially, correctly | §4.4, §6.8–6.9, §9 |
| R2 | v0 is local-only on this machine; cloud is deferred | §4.7 |
| R3 | Before triage starts, a pre-start validation confirms compatibility and prerequisites | §8 |
| R4 | Work delegated to an agent of another type links to the task; all data from every agent involved belongs to the task | §5.4, §6.8–6.9 |
| R5 | A task spans many sessions (stops for approval, escalation, blockers); all group under one task; a task is complete only when all its work is complete | §3, §6.10 |
| R6 | Ready for real work across multiple projects with both agents concurrently, with all data needed for later analysis and benchmarking recorded | §6.12, §11 (Slice 2) |
| R7 | Evolves to v1 (harness comparisons) and later versions without rework | §15 |

**Principles the user set:** keep it simple, optimal and flexible (YAGNI); the harness owns the
high-level workflow only and never directs agent topology; native agent memory is not the harness's
concern; record what is observable, leave the rest null, and keep enough pointers to reconstruct it.

**v0 success criteria** (the parent's "Done when" 1 and 3; criterion 2, version-over-version wins,
is v1): (1) v0's first real tasks in each pilot project prove the instrumentation and give the
observed spread for choosing N; (3) every task emits the same per-phase scorecard for any agent,
model and topology.

---

## 2. Scope

### 2.1 In v0

- The seven-phase workflow with S/M/L routing, the living plan, numbered acceptance checks, notes,
  and harness memory, as plain instruction files read from the harness checkout.
- The `harness` CLI (§7), hook adapters for Claude Code and Codex, and `harness doctor`.
- The done gate, timing, and all seven metrics, computed by `harness score` from recorded data.
- Pilot projects: `mvp` (Turbo monorepo, about 10 merged PRs a day, its own agent rules) and
  `echo-wiki` (docs repo, about 1 PR a week; checks that the harness is not overfit to one project).

### 2.2 Changes to the approved design

Type: **O** = override, **A** = added, **D** = deferred to v1 or later.

| # | Parent design said | This spec | Type | Why |
|---|---|---|---|---|
| C1 | Native memory off: install merges `autoMemoryEnabled: false`, Codex `[features].memories` must be off, events record the resolved setting, memory "on or unknown" makes a time result descriptive | Native agent memory is out of scope: never disabled, checked or recorded | O | User decision. Disclosed trade-off: native memory may carry context across arms; both arms share it, so it adds noise, not bias toward an arm |
| C2 | Harness-defined subagents (explorer, evaluator, retro) installed at user scope with `omitClaudeMd` | None shipped | O | Topology is the model's choice; less to install and keep in sync |
| C3 | `config.json` knob "topology (how many in parallel, with role labels)"; per-phase requested model and effort; agent types mapped to knob role labels (`unconfigured`, `evaluator`) | Topology, model and effort are recorded from observation only; scorer roles are the observed agent types; a verifier is identified by its session, not a role label | O | Observe-only topology (§5.4) |
| C4 | Research uses parallel explorers; verify uses "a separate evaluator"; retro uses "a fresh agent" | Outcomes, not mechanisms: verify by an agent other than the builder; retro from a fresh context given only the retro bundle; the main agent chooses how | O | User chose option A |
| C5 | Controlling session id "from the agent's session env var, else the adapter's SessionStart record for the same working directory, else null" | Claude: `HARNESS_SESSION_ID` written by the harness's own SessionStart handler; Codex: `CODEX_THREAD_ID`; no folder fallback; null only for your manual commands | O | `CLAUDE_CODE_SESSION_ID` may hold the startup id after `claude --continue` (Claude docs); folder matching misattributes concurrent sessions |
| C6 | Codex adapter adds sandbox writable roots and network/escalation access | Codex main sessions run with full access chosen at launch; install adds only the state dir to `[sandbox_workspace_write].writable_roots` so sandboxed Codex delegates can record | O | User decision; tested |
| C7 | Project install also writes agent settings | Project install writes only `.harness/project.json` and the `.gitattributes` union line | O | Follows from C1 and C6 |
| C8 | Tokens and dollars "where exposed, else null", each usage value scoped complete or partial | Read best-effort from agent transcripts (Claude: tokens and dollars; Codex: tokens), complete per message, and cached in the state dir; the complete/partial scope rule is dropped | O | Tested: transcripts carry them; hooks do not |
| C9 | (none) | `harness doctor` pre-start validation; `doctor` event; triage gated on it | A | R3 |
| C10 | (none) | Task and parent markers (`HARNESS_TASK_ID`, `HARNESS_PARENT_SESSION`, `HARNESS_SESSION_ID`) and delegate detection | A | R4 |
| C11 | `worktree.baseRef` set to `head` settings-wide | Not set | O | It also changes the user's normal app sessions; harness never asks for worktree isolation |
| C12 | `retro-bundle` destination unspecified | Prints the bundle to stdout | A | Simplest; no new file locations |
| C13 | Randomization, pinned version checkouts, `shared_commit` dispatch, memory snapshot per comparison, the decision record and statistical test | Deferred to v1; v0 assigns every task to the baseline and runs from the harness repo's own checkout | D | A comparison only uses tasks randomized against its challenger, so nothing is lost |
| C14 | (parent silent on cloud) | Local only; commands refuse in detected cloud sessions | D | User decision |
| C15 | Hooks record "any model value the hook delivers" | Plus `transcript_path` and helpers' `agent_transcript_path` on every event | A | Reconstruction and replay in retro (§5.4) |

### 2.3 Deferred

| Item | Arrives | Seam already in v0 |
|---|---|---|
| Harness comparisons: paired randomization, pinned checkouts, `shared_commit` dispatcher, comparison memory snapshot, decision record, Mann-Whitney randomization test, enrollment | v1 | `start` events record benchmark tier, arm and assigned commit under the spool lock; `project.json` reserves the fields; `score` is deterministic (§15) |
| Cloud sessions | Later | Task folders already live in git; only the spool is per machine |
| Classifier that predicts `config.json` | Later (~50 labeled tasks) | Every task stores the verbatim request, triage signals and config; copies kept for abandoned tasks |
| Wrapper skill to start tasks | Later, additive | The command path is complete without it |
| The parent's "Not in v0" list (dashboards, budget caps, tool-call logs, background memory cleanup, swarm orchestration, ticket adapter, harness-repo memory, cross-project comparison, interventions count, parent-chain resolution in temporary worktrees, parallel implementers) | Unchanged | — |

### 2.4 Out of scope

Native agent memory (C1). Directing topology (§5.4). Changing how projects build, test, push or
clean up (§4.6).

---

## 3. Glossary

| Term | Meaning |
|---|---|
| **Task** | The unit of measurement: one task id (`<date>-<slug>`), one branch, one worktree, one folder `.harness/runs/<task-id>/`. The parent calls this a "run"; this spec keeps the parent's file and command names |
| **Session** | One agent sitting (a Claude or Codex session, or a delegated process). A task has any number, in sequence or in parallel |
| **Controlling session** | The main session that issues `harness phase`, `review` and `pr` for the task (recorded in `state.json`) |
| **Delegate** | A process launched by another agent's session (§6.9); it may run `harness check` only |
| **Done** | The task passes the done gate (§6.11). A session ending, stopping or hitting a blocker never completes or fails a task; only the gate, an abandon, or the deadline/expiry does |
| **Integration branch** | The project's default branch on the integration remote (`origin/main` for both pilots) |
| **Spool** | The per-machine, append-only event log for one project (§6.6) |
| **Benchmark tier** | S/M/L you pass at `start --new`; fixed for the task; used to group tasks for comparison |
| **Tier** | The operational S/M/L set by triage; may move up (never down) |

---

## 4. Architecture

### 4.1 Locations

```
~ (user scope, installed once by `harness install --user`)
├─ ~/.local/bin/harness                 dispatcher → python3 <harness repo>/harness/cli.py
├─ ~/.claude/CLAUDE.md                  imports the bootstrap (user-scope copy)
├─ ~/.claude/settings.json              6 hook entries + allow rule Bash(harness:*)
├─ ~/.codex/AGENTS.md                   bootstrap appended (marked block)
├─ ~/.codex/hooks.json                  6 hook entries (you approve them once in Codex)
└─ ~/.codex/config.toml                 state dir added to [sandbox_workspace_write].writable_roots

~/Desktop/src/echo-official/lean-harness/     harness repo: CODE ONLY (private, echo-official org)

<project>/ (each project, installed once by `harness install`, merged via PR)
├─ .gitattributes                       .harness/memory/*.md merge=union
└─ .harness/
   ├─ project.json
   ├─ memory/MEMORY.md, memory/<area>.md
   └─ runs/<task-id>/                   one folder per task (§6.1)

${XDG_STATE_HOME:-~/.local/state}/harness/<project-hash>/   per machine, never in git (§6.6)
```

`<project-hash>` is the first 16 hex characters of the SHA-256 of the absolute git common dir
(`git rev-parse --path-format=absolute --git-common-dir`), so every worktree of one project shares
one spool and different projects never mix.

### 4.2 Harness repo layout

| Path | Job | Varies by harness version (arm)? |
|---|---|---|
| `AGENTS.md` | Map: which phase file to read when | Yes |
| `skills/phases/{triage,research,resolve,plan,build,verify,retro}.md` | One instruction file per phase: what it must produce and which `harness` commands it calls; never how to organize agents | Yes |
| `hooks/bootstrap.md` | The fixed bootstrap text (§4.4) | No (fixed, user-scope copy) |
| `hooks/shared-rules.md` | Harness memory rules (§5.6) and when to run `harness tier` | No (shared) |
| `harness/` | Python 3.12, standard library only: CLI, done gate, git helpers, doctor, spool, scorer, statistics | No (shared) |
| `harness/adapters/{claude,codex}.py` | Hook handlers: payload → spool event | No (shared) |
| `bin/harness` | Dispatcher installed on PATH | No (fixed) |
| `tests/` | Unit, integration and adapter-contract tests (§12) | — |

### 4.3 Install

| Command | Writes | Notes |
|---|---|---|
| `harness install --user` | Everything under "user scope" in §4.1 | Idempotent; adds only its own entries (hook entries that call `harness hook`, the allow rule, the writable root, a delimited bootstrap block) and prints each change it made. It appends hook entries after existing ones and never reorders them: Codex keys approvals by file and position (`hooks.json:stop:0:0`), so a reorder would silently un-approve your existing hooks. Prints the one manual step: open Codex once and approve the harness hooks (Codex skips unapproved non-managed hooks and stores approvals in `~/.codex/config.toml` under `hooks.state`; the harness never writes approvals itself). Fails loudly if `$CODEX_HOME/AGENTS.override.md` exists |
| `harness install` (in a project) | `.harness/project.json` (resolved integration remote and default branch, defaults from §6.2) and the `.gitattributes` line, on a branch | You open, review and merge that PR before the first task |

### 4.4 Start flow

```
You, in a terminal:
  1. git fetch origin
     git worktree add <path> -b <branch> origin/main
  2. cd <path>
     harness start --new <slug> --benchmark-tier S|M|L --request ~/tasks/<slug>.md   (file OUTSIDE the worktree)
       → doctor checks A–D (§8); any failure: prints the fix, registers nothing, no clock
       → passes: mints <date>-<slug>, creates .harness/runs/<task-id>/ (request.md verbatim,
         state.json), records assignment (arm "baseline", assigned commit = harness repo HEAD),
         appends `start` (clock starts), prints the harness checkout path
Launch an agent IN THAT WORKTREE: claude / codex CLI, or open the folder in either app.
Codex must be launched with full access (`-s danger-full-access`, or the app's full-access setting).
  3. Bootstrap: the agent runs `harness start`
       → resolves the task by branch, runs doctor (E plus a fast subset of A–C), appends `resume`, prints the checkout
  4. The agent reads AGENTS.md from that checkout → `harness phase triage enter` → … → `harness pr`
```

- **Bootstrap** (`hooks/bootstrap.md`, fixed): "If another agent launched you, ignore this file and
  follow your prompt. Otherwise run `harness start`, then read `AGENTS.md` from the checkout it
  prints." Tested: Claude and Codex both ran a "run this first" instruction before the user's request.
- **Silence outside harness work:** `harness start` exits silently (no output, exit 0) in a repo
  without `.harness/project.json` or on a branch with no task. Hook handlers exit silently only in a
  repo without `.harness/project.json`; in a harness project they always append (any branch,
  including a detached HEAD during a rebase). A handler that meets an unexpected payload writes one
  stderr line and a `format_warning` event; handlers never exit non-zero and never block the agent.
- A worktree an app creates on its own has no task; there the session is not a harness task.

### 4.5 Data flow

```
Agent session (Claude or Codex)
  │ hooks: SessionStart/End, UserPromptSubmit, Stop, SubagentStart/Stop
  ├──────► `harness hook <agent> <event>` ─────► spool (state dir)
  │                                                  ▲
  └─ runs `harness …` ──► task folder (in git) + copy┘
                               │
     `harness score` ◄─────────┴── integration branch + spool + transcripts (read-only) ──► scorecards (state dir)
```

### 4.6 Precedence with project rules

The harness owns the workflow and its records: phases, plan, checks, notes, harness memory, PR via
`harness pr`, timing. The project owns how to build, test, push and clean up: acceptance checks call
project commands; `harness pr`'s push still triggers the project's pre-push hook (mvp runs
`npm run preflight`), and that time is charged to the task because it is real; project rules such as
mvp's start gate, Graft and reap stay in force.

### 4.7 Local only (R2)

- The bootstrap, the `harness` command and the hooks exist only in this Mac's user-scope files, so a
  cloud session has no bootstrap and no `harness` command and is never a harness task.
- As a backstop, `harness start --new` and `harness start` refuse when `CLAUDE_CODE_REMOTE=true`, or
  when any variable named in `project.json` `cloud_env_vars` is `1` (mvp: `ECHO_CODEX_CLOUD`,
  `ECHO_CLAUDE_CLOUD`).

---

## 5. Workflow

### 5.1 Tiers and phases

| Tier | Signal | Phases that run | Verify |
|---|---|---|---|
| **S** | The diff fits in one sentence | triage (five-field plan) → build + checks → retro only after a failed check or logged friction | None; every S check must be runnable |
| **M** | Multi-file change in code that already exists | triage → research → plan → build + checks → verify → retro | One pass at the end |
| **L** | New subsystem, cross-cutting change, or unfamiliar code | triage → research → resolve unknowns → plan (optional human review) → build + checks → verify → retro | Per milestone, plus the final pass |

Rules from the parent hold: phases are contiguous (an `exit` write is the boundary; an `enter` on a
still-open phase writes the missing exit first); for S, build starts at triage's exit; complexity
found mid-run moves the tier up with `harness tier`, never down, logged as a Decision, counted as a
triage miss, and phases the new tier adds run from the current phase onward.

### 5.2 Phase contracts

Each phase file states its input, its output, the `harness` commands it calls, and when it ends.
None says how to organize agents.

| Phase | Input → output | Commands | Ends when |
|---|---|---|---|
| **Triage** | `request.md` → five fields in `plan.md` (goal, outcome, acceptance checks, tier, source) and `config.json` | `harness phase triage enter` (refuses until this session's doctor check passed), `harness phase triage exit` | Goal, outcome and at least one check can be written without guessing. A missing fact → explore or spike; a missing preference → pick a default and log an Unknown; a missing goal → stop and ask you. Never default the goal |
| **Research** (M, L) | Code and harness memory → `research.md` | `phase research enter/exit`; `harness memory kept\|fixed\|deleted <area>:<id>` for each lesson checked against its cited code | The areas the task touches are mapped |
| **Resolve unknowns** (L) | Open unknowns → resolved facts or logged defaults | `phase resolve enter/exit` | Every fact is explored or spiked; every preference has a logged default |
| **Plan** (M, L) | Research → milestones, acceptance checks, decisions, unknowns in `plan.md` | `phase plan enter/exit`; `harness review start\|end` around an optional human review | The plan is a self-contained contract; no code transcripts |
| **Build loop** (all) | Plan → code, one milestone at a time | `phase build enter` (the first entry snapshots `plan.approved.md`); `harness check <C-id>` after every attempt at a milestone's checks; `harness tier` on found complexity; at the end `harness rebase`, then the final checks (S: `harness check --all` here) | All milestones' checks pass after the rebase |
| **Verify** (M, L) | The running system → pass or fail per check | `phase verify enter/exit`; `harness check --all`; `harness check <C-id> --observed pass\|fail` for observational checks | Every final check passes; a failure returns to build |
| **Retro** (M, L; S after a failed check or friction) | `harness retro-bundle` output → up to 3 lessons in `.harness/memory/<area>.md` | `phase retro enter`, `harness retro-bundle`, `phase retro exit` | Lessons written under the admission bar (§5.6), or none qualify |
| **PR** | Passing checks → an open PR and `ready` | `harness pr <task-id>` | `ready` emitted |

After `ready`: any edit, rebase or check starts with `harness phase build enter`; `harness pr`
re-emits `ready` without opening a second PR. Before merging, you run `harness pr --refresh
<task-id>`. After merging: `harness close <task-id> --done` when the CLI flagged a scope reduction;
`harness defect <task-id> "<one line>"` for bugs found later (`--resolved <id>` to close one);
`harness close <task-id> --abandon` for a task that will not merge.

### 5.3 Independence (outcome, not mechanism)

- **Verify** (M, L, including L's per-milestone verify inside build) is done by an agent other than
  the one that wrote the code. Its note lines always use phase `verify`, so the Unknowns it finds that
  the builder missed stay a separate count.
- **Retro** lessons are written from a fresh context given only the retro bundle (final plan,
  approval copy, the check events the task saw, `git diff <integration-branch>...HEAD`), the touched
  areas' memory files, and the code they cite. Never a scorecard or anything computed from events.
- The main agent decides how to meet both (a subagent, another provider's CLI, a fresh session, in
  the background). The harness records who ran each check (session id, delegate flag) and enforces
  nothing beyond that.

### 5.4 Topology is observed, never directed (R4)

- No phase file, command or check tells an agent when or how to orchestrate: spawn, fork, start a
  fresh agent, run in the background, or call another provider or model.
- The harness records what is cheap to observe (§6.7) and leaves the rest null. Every hook event
  stores the session's `transcript_path` and each helper's `agent_transcript_path`, so retro or a
  later replay can reconstruct anything the hooks missed (another provider's CLI, an MCP tool) from
  the transcripts' tool calls. Transcript contents are never copied into the harness's records.
- Agents with no adapter (Grok, Gemini today) still count in wall time (their work happens inside a
  parent's tool call) and their `harness check` runs count; their sessions are invisible to hooks, so
  the scorecard marks `topology: incomplete`. Adding one later needs only an adapter (§15).

### 5.5 Notes

From the parent, unchanged: one stamped line per entry, under 25 words, written as it happens.
Template: `<date time> · <agent/model> · <phase> — <what>. [Why: <why>] [Check: C3] [Cites: path:line] [id: a7f3k2]`.
Why is required on Decisions; `Check:` on a Decision that changes a check or the goal; `id` on
Lessons. Decisions, Unknowns and Friction live in `plan.md`; Lessons in `.harness/memory/`. One
implementation-note line per milestone when it closes. `harness score` lists malformed lines; it
never blocks.

### 5.6 Harness memory

From the parent, unchanged except where marked:
- `.harness/memory/MEMORY.md` lists areas, not entries, and is read every task (by research in M and
  L, by the build phase in S), with the touched areas' files.
- Admission bar, applied by the retro writer after reading the area file: a lesson is written only if
  it would have changed a decision or saved time in this task, is not obvious from a minute of reading
  the code, cites a file and line, and a future agent can confirm or refute it. A line that refines an
  existing one replaces it; near-duplicates are never added.
- Cap: at most 3 lessons per task and about 40 lines per area file; past the cap, the retro writer
  retires the entry least likely to change a decision.
- Checked before use: the agent opens the cited code and fixes or deletes a contradicted entry,
  logging `harness memory kept|fixed|deleted <area>:<id>`. Each lesson carries a random id of six or
  more characters, stable across edits and merges.
- Single writer per worktree: the phase's controlling session writes memory; delegates only propose
  corrections. Friction is never deduplicated in plans; harness or tooling lessons are logged as
  Friction, not written to memory.
- Shared store: `.gitattributes` marks `.harness/memory/*.md` `merge=union` (tested on git 2.54 with
  `rebase --merge`); `harness rebase` then drops, by id, lines either side retired and keeps one line
  per id (§7). Never resolve memory files on the forge; GitHub's merge ignores `.gitattributes` drivers.
- Sweep: at each harness review, a fresh agent deletes entries whose cited path no longer exists,
  fixes relocated citations, merges duplicates, and opens a PR you merge.
- Changed: the comparison-time memory snapshot is deferred with comparisons (C13).

### 5.7 Acceptance checks

From the parent, unchanged: numbered C1, C2, … in `plan.md`; each has what, expected result, and one
fenced command run from the project root whose exit status is the result. The check-text hash covers
the whole entry. Observational checks say so and are recorded with `--observed`. In S every check must
be runnable (a check that can only be observed makes the task M). A re-plan may change a check only
with a Decision naming it (`Check: C3`, or `Check: goal`).

---

## 6. Data model

### 6.1 Files in the project repo (committed)

| File | Written by | When |
|---|---|---|
| `.harness/project.json` | `harness install` | Once; changed only by a reviewed PR |
| `.harness/memory/MEMORY.md`, `<area>.md` | Retro writer; at-use fixes; sweep | Retro; during research/build; at reviews |
| `runs/<task-id>/request.md` | `start --new` | Once, verbatim; its SHA-256 recorded in `start` |
| `runs/<task-id>/state.json` | `start --new`; `harness phase` | Start; every phase enter/exit |
| `runs/<task-id>/config.json` | Triage; `harness tier` | Triage exit; each tier change |
| `runs/<task-id>/research.md` | Research | M, L |
| `runs/<task-id>/plan.md` | Every phase (notes); triage, plan, build | Throughout |
| `runs/<task-id>/plan.approved.md` | `harness phase build enter` | First build entry only; never overwritten |
| `runs/<task-id>/events.jsonl` | The CLI: phase, check, review, ready, pr events | As they happen; committed with code commits and by `harness pr` |

### 6.2 `project.json`

| Field | v0 default | Use |
|---|---|---|
| `schema_version` | 1 | |
| `integration_remote`, `default_branch` | resolved by install (`origin`, `main`) | Fetch, rebase, gate |
| `cloud_env_vars` | `[]` (mvp: `["ECHO_CODEX_CLOUD","ECHO_CLAUDE_CLOUD"]`) | §4.7 |
| `deadline_hours` | `{"S": 4, "M": 16, "L": 48}` | Not-done when exceeded on the score's clock; revise from observed spread |
| `expiry_days` | 21 | Not-done when no terminal disposition by then |
| `defect_window_days` | 14 | Escaped-defect window after merge |
| `target_benchmark_tier`, `n`, `alpha`, `min_gain` | `"M"`, 10, 0.05, 0.20 | Reserved for v1; recorded now |
| `baseline_commit` | harness repo HEAD at install | Reserved for v1 (each `start` records the commit that actually ran as `assigned_commit`) |
| `challenger_commit`, `shared_commit`, `memory_snapshot_commit` | `null` | Reserved for v1 |

### 6.3 `config.json`

| Part | Fields |
|---|---|
| `knobs` | `phases` (list), `phase_agent` (per phase: `claude`, `codex` or `same`; a different agent means a handoff you perform), `evaluator_cadence` (`none`, `end`, `per_milestone`), `plan_review` (bool) |
| `record` | `benchmark_tier`, `origin_tier`, `tier`, `triage_signals` (areas touched, file count estimate, familiarity), `arm` (`baseline` in v0), `assigned_commit`, `predicted_knobs` (`null` until a classifier exists) |

### 6.4 `state.json`

`task_id`, `branch`, `phase`, `phase_open` (bool), `controlling_session` (nullable), `created_at`.

### 6.5 `plan.md`

Sections in order: Goal · Outcome · Acceptance checks · Tier · Source · Milestones (each with its
checks and implementation notes) · Decisions · Unknowns · Friction. S plans hold only the first five.

### 6.6 State directory (per machine, never in git)

| Path under `<state>/harness/<project-hash>/` | Contents |
|---|---|
| `spool.jsonl` (+ `spool.lock`) | Every hook and CLI event of every task, merged or not |
| `tasks/<task-id>/request.md`, `config.json` | Copies at triage exit, each `harness tier`, and `close --abandon`, so analysis never sees survivors only |
| `cache/sessions/<session-id>.json` | Per-session model(s), effort, token and cost totals read from a transcript, refreshed on every read (§10) |
| `scorecards/<task-id>.json`, `scorecards/summary.md` | Derived; regenerated by `harness score` |

The spool and caches are regenerable only from each other; back up the state directory with the
machine. Agents are instructed never to read it.

### 6.7 Event schema (v1)

Common fields on every event (null when not observable):

| Field | Source |
|---|---|
| `v`, `ts` (UTC, ms), `kind`, `source` (`hook` or `cli`) | Writer |
| `agent` (`claude`, `codex`), `session_id`, `agent_id`, `agent_type` | Hook payload; CLI from identity variables (§6.9) |
| `parent_session` | `HARNESS_PARENT_SESSION`, else the payload's parent for helpers |
| `task_id` | `HARNESS_TASK_ID` when set; CLI events always carry it |
| `branch`, `head`, `cwd`, `git_common_dir` | git at write time (`branch` null on a detached HEAD) |
| `model` | Codex payload (all events but SessionEnd); Claude: null in hooks, filled from transcripts at scoring |
| `effort` | Claude Stop and SubagentStop payload `effort.level` |
| `transcript_path`, `agent_transcript_path` | Hook payload |
| `harness_version` | Installed CLI commit |

Kinds and their extra fields:

| Kind | Writer | Extra fields |
|---|---|---|
| `session_start` | hook | `trigger` (startup, resume, clear, compact, fork) |
| `prompt` | hook | `prompt_id` or `turn_id` (prompt text is not copied; it is in the transcript) |
| `stop` | hook | `turn_id` |
| `subagent_start`, `subagent_stop` | hook | helper `agent_id`, `agent_type` |
| `session_end` | hook | `reason` |
| `start` | CLI (spool only) | `benchmark_tier`, `request_sha256`, `arm`, `assigned_commit` |
| `resume` | CLI (spool only) | — |
| `phase` | CLI | `phase`, `action` (enter or exit), `handoff` (bool), `controlling_session` |
| `check` | CLI | `check_id`, `result`, `mode` (run or observed), `code_tree`, `check_text_hash`, `exit_code`, `duration_ms`, `delegate` |
| `review` | CLI | `action` (start or end) |
| `ready` | CLI | `tip_commit`, `code_tree` |
| `pr` | CLI | `number`, `url` |
| `tier` | CLI (spool only) | `tier`, `origin_tier` |
| `close`, `defect`, `memory` | CLI (spool only) | `disposition`; `defect_id`, `text`, `resolved`; `area`, `lesson_id`, `action` |
| `doctor` | CLI (spool only) | per-check pass or fail |
| `format_warning` | hook | adapter, event, missing fields |

CLI events go to the task's `events.jsonl` and a copy to the spool; kinds marked "spool only" go to the
spool only. Hook events go to the spool only.

### 6.8 Resolving events to tasks

At scoring, an event belongs to a task by: its `task_id` when present; else its branch (recorded in
`state.json`); events on a detached HEAD during a rebase take the session's last known branch.
Everything else is an orphan, listed on the scorecard. One task per branch and no branch reuse make
branch resolution unambiguous. Hooks never resolve at write time, so they stay fast.

### 6.9 Identity and delegates

- **Markers.** The Claude adapter's SessionStart handler (every trigger), in a worktree whose branch
  has a task, writes to `CLAUDE_ENV_FILE`: `HARNESS_SESSION_ID` = the payload's `session_id`, always;
  `HARNESS_TASK_ID` only when it is not already in its process environment; and, only when
  `HARNESS_PARENT_SESSION` is not already there, `HARNESS_PARENT_SESSION` = an inherited foreign identity
  variable (`CODEX_THREAD_ID`) if one is present, else the payload's `session_id`. The Claude hook
  adapter derives `parent_session` the same way. Tested: these reach Bash commands, child processes and subagents,
  survive `cd`, and a Codex process launched with them passes them to its hooks and commands. Codex has
  no equivalent, so its children link by branch when they run in the task's worktree.
- **Identity in commands.** Claude: `HARNESS_SESSION_ID` (not `CLAUDE_CODE_SESSION_ID`, which may hold
  the startup id after `claude --continue`). Codex: `CODEX_THREAD_ID` (tested equal to the hook's
  `session_id`). Each future adapter names its own identity variable.
- **Delegates.** A process is a delegate when `HARNESS_PARENT_SESSION` is set and any identity variable
  in its environment differs from it. A delegate's session id and agent are those of the identity
  variable whose value differs from `HARNESS_PARENT_SESSION` (Codex launched by Claude P: id = its
  `CODEX_THREAD_ID`, agent `codex`, parent P; Claude launched by Codex P: id = its `HARNESS_SESSION_ID`,
  agent `claude`, parent P). A non-delegate's id is the single value its identity variables agree on;
  if they disagree and `HARNESS_PARENT_SESSION` is unset, the command refuses as ambiguous.
  A delegate may run `harness check` (including `--observed`); `harness start` in a delegate appends
  nothing and prints "delegate of task <id>: follow your prompt"; `harness phase`, `review` and `pr`
  refuse. This keeps one owner per task record; it does not limit how agents organize work.
- **Controlling session.** `harness phase <p> enter` records the issuing session as controller (a
  successor after a handoff takes over this way). Commands you run by hand with no agent identity
  (`pr --refresh`, a manual `phase build enter`) record null.

### 6.10 Timing (R5)

From the parent, unchanged: **wall time** runs from `start` to the first `ready`, plus, for each later
PR revision, from its start (the `resume` of the session that re-enters build, or that `build enter`
when none precedes it) to its re-emitted `ready` (or a `--refresh` `build exit` without `ready`).
Excluded as human wait: gaps from a `ready` (or such an exit) to the next revision's start, and from a
`--handoff` phase exit to the successor's `resume`. The optional plan-review span is charged and
reported separately. Startup from `start` or a revision/handoff `resume` to the next phase enter is
charged. A missing boundary makes the task's timing incomplete. Time an agent spends waiting for your
reply inside a phase is charged. **Agent time** sums, per session, spans from a prompt to the last stop
before the next prompt or session end (self-started turns also fire prompt events), plus helper start
to stop. Both are reported per phase. A stopped session that is continued keeps its id; a new session
for the task resolves to the same task by branch.

### 6.11 Done gate

From the parent, unchanged: a task is done only when the final `plan.md` checks pass, every check
added, dropped or rewritten since `plan.approved.md` is named by a Decision, you merged it, and any
flagged scope reduction was confirmed with `close --done`. Passing means: for every final check, the
latest completed attempt before the last `ready` passed at a code tree (the commit's tree with
`.harness/` removed) equal to the code tree of the `ready` tip, which equals the code tree of the merge
commit (the last first-parent commit on the integration branch that changed `.harness/runs/<task-id>/`),
whatever the merge method. A check with no event counts as failed. `harness check` computes code trees
without writing git objects (e.g. `git hash-object -t tree` without `-w`), so a sandboxed delegate can
run it.

### 6.12 Metrics: raw data and when each is available

Scoring is idempotent over raw events and files, so any metric computed in a later slice is computed
retroactively for every task recorded since its raw data started.

| Metric | Role | Raw data | Recorded from | Computed from |
|---|---|---|---|---|
| Wall time | **Score** | `start`, `phase`, `resume`, `review`, `ready`, `close` events | Slice 1 (`review` from Slice 2) | Slice 1 |
| Not done | Guardrail | Gate inputs, `close`, deadlines, expiry | Slice 1 | Slice 1 |
| Tier upgrade | Guardrail | `config.json` `origin_tier`/`tier`; `tier` events | Slice 1 (triage); `tier` from Slice 2 | Slice 3 |
| Escaped defects | Guardrail | `defect` events | Slice 2 | Slice 3 |
| Rework | Diagnostic | `check` events | Slice 1 | Slice 3 |
| Discovery lag | Diagnostic | Unknown lines in `plan.md` vs `plan.approved.md`; verify-phase Unknowns | Slice 1 | Slice 3 |
| Plan churn | Diagnostic | Milestones in `plan.md` vs `plan.approved.md` | Slice 1 | Slice 3 |
| Cost: agent time | Diagnostic | Hook prompt/stop/subagent events | Slice 1 | Slice 1 |
| Cost: tokens, dollars | Diagnostic | Transcript paths (Slice 1); cached totals | Slice 1 (paths); cache from Slice 2 | Slice 3 |
| Topology | Descriptive | Session, helper, parent events; transcripts | Slice 1 | Slice 3 |

---

## 7. CLI reference

| Command | Run by | Does | Refuses when | Slice |
|---|---|---|---|---|
| `install --user` | You | User-scope install (§4.3) | `AGENTS.override.md` in `$CODEX_HOME` | 1 (Codex parts 2) |
| `install` | You | Project files on a branch | Not a git repo | 1 |
| `doctor` | Anyone | Checks A–E, read-only | — | 1 (Codex checks 2) |
| `start --new <slug> --benchmark-tier T --request F` | You | §4.4 step 2; holds the spool lock across uniqueness check, assignment and `start` | Any check A–D fails | 1 |
| `start` | Bootstrap | Resolve task, check E, `resume`, print checkout | (silent no-op outside a task; delegates: prints delegate notice) | 1 |
| `phase <name> enter\|exit [--handoff]` | Controlling session (you for manual build enter) | `state.json` + phase event; first `build enter` snapshots `plan.approved.md` | Default branch; delegate; triage without a passing check E | 1 |
| `check [--task ID] <C-id>\|--all [--observed pass\|fail]` | Any session or delegate | Runs the check's fenced command from `plan.md` (or records an observation); code tree and check-text hash | Code checkout not clean outside `.harness/` before or after | 1 |
| `rebase` | Build phase; `pr --refresh` | Commit `.harness/`, fetch (retry on lock), `rebase --merge`, by-id memory cleanup, conflict rerun flow (parent) | Uncommitted changes outside `.harness/` (unless a rebase it started is stopped) | 1 (memory cleanup 2) |
| `pr <task-id>` | Controlling session | Gate pre-check, commit `.harness/`, push (`--set-upstream`; `--force-with-lease` after a rebase), `gh pr create`, `ready` + `pr`, commit, push | Failing or stale checks; no `triage enter`; delegate | 1 |
| `pr --refresh <task-id>` | You | `build enter`, `rebase`, `check --all`, force-with-lease push, re-emit `ready`; on conflict: abort and `build exit` | — | 1 |
| `close <task-id> --done\|--abandon` | You | Disposition event | — | 1 |
| `score` | You | §10 | — | 1 (full metrics 3) |
| `hook <agent> <event>` | Hook entries | Adapter → spool | (never fails the agent) | 1 (Codex 2) |
| `tier <S\|M\|L>` | Any controlling session | Rewrites tier in `plan.md` and `config.json`, keeps `origin_tier`, appends `tier`, copies files to the state dir | Downgrade | 2 |
| `review start\|end` | Controlling session | Brackets a human plan review | — | 2 |
| `retro-bundle` | Retro phase | Prints the bundle (C12) | — | 2 |
| `memory kept\|fixed\|deleted <area>:<id>` | Session using memory | `memory` event | — | 2 |
| `defect <task-id> "<line>" \| --resolved <id>` | You | `defect` event | — | 2 |

Every command that cannot append to the spool fails loudly with the fix (run `install --user`, or
relaunch Codex with full access); none drops an event silently.

---

## 8. Pre-start validation: `harness doctor` (R3)

One check module, three entry points: `harness doctor` (any time; read-only; writes nothing),
`harness start --new` (A–D before registering anything), and `harness start` at bootstrap (E plus a
fast subset of A–C; appends one `doctor` event). `harness phase triage enter` refuses unless the latest
`doctor` event for this task, from the issuing session, passed.

| Group | Checks |
|---|---|
| A. Machine | Python ≥ 3.12; git and gh present; `gh auth status` ok; state dir writable; `harness` on PATH is the installed dispatcher |
| B. Agent install | Claude: hook entries, bootstrap import, allow rule present; `disableAllHooks` not true. Codex: hook entries present; `[features].hooks` not false; a `hooks.state` approval for each harness hook entry; the state dir in `[sandbox_workspace_write].writable_roots`; bootstrap block present; no `$CODEX_HOME/AGENTS.override.md` |
| C. Project | `project.json` valid and present on the fetched integration branch; `.gitattributes` union line |
| D. Task | Not a cloud session; inside a git worktree, not on the default branch; `git status --porcelain` empty; branch name and task id never used (integration branch, this branch, spool); `git fetch` of the integration ref succeeds; no commits outside the fetched integration branch; `gh repo view --json viewerPermission` is WRITE, MAINTAIN or ADMIN; `git push --dry-run --no-verify <remote> HEAD:refs/heads/<branch>` succeeds |
| E. Session (live) | This session's own hook events reached the spool in the last few minutes, matched by its identity (§6.9), which must be present; Codex: `CODEX_SANDBOX` unset (full access) |

A failure in `start --new` registers nothing. A failure in E stops the agent before triage with the
fix printed; the task stays in flight and its clock keeps running; you fix and relaunch.
Environment failures are independent of the arm, so they add noise, not bias.

---

## 9. Concurrency, sequencing and error-handling invariants

1. One task = one branch = one worktree; branch names and task ids are never reused.
2. Parallel tasks write disjoint task folders; the only shared repo files are `.harness/memory/*.md`
   (union merge plus by-id cleanup) and `project.json` (read-only during tasks).
3. Every spool append, and every task `events.jsonl` append, takes the spool's exclusive file lock and
   writes one complete line (a controller and a delegate may write at the same moment); `start --new`
   holds the lock across uniqueness check, assignment and append. Readers ignore an incomplete last line.
4. `git fetch` retries with backoff on ref-lock errors (tested: concurrent fetches from several
   worktrees fail about half the time without it).
5. Only the controlling session (or you, for `pr --refresh` and manual `build enter`) issues `phase`,
   `review` and `pr`; delegates only `check`.
6. Hook handlers never block or fail the agent; CLI commands fail loudly and never drop events.
7. While a rebase is stopped, only conflict resolution, plain `harness start` (spool only) and the
   `harness rebase` rerun touch that worktree (parent rule).
8. `harness score` is deterministic and idempotent, makes no commits, and needs no forge API.

---

## 10. Scoring and scorecards

`harness score` (run in a project, on demand) fetches the integration ref, resolves events (§6.8),
evaluates the done gate and timing for every registered task, reads transcripts best-effort, and
writes `scorecards/<task-id>.json` and `scorecards/summary.md`.

- **Per task:** disposition (merged, abandoned, in flight, not-done) and done-gate result; wall time
  and agent time, total and per phase; timing completeness with the missing boundaries named; metrics
  per §6.12; topology (sessions, helpers, depth, agent types, models, effort; `incomplete` where an
  agent hides spawns); tokens and dollars with coverage; orphans; malformed note lines; harness
  memory events.
- **Summary:** per benchmark tier and per agent: counts, done rate, median and spread of wall time
  with not-done and upgraded tasks entered at the deadline value, not-done and upgrade rates, defects;
  coverage of each field; tasks nearing expiry. The spread is the input for choosing N in v1.
- **Transcripts:** Claude (`usage` per message and the `cost-state` row: dollars, tokens, durations)
  and Codex (`token_count` totals; helpers' parent and depth from `session_meta`). Every read refreshes
  that session's model(s), effort and totals under `cache/sessions/`, and the last cached values remain if the agent later
  deletes the transcript (Claude's `cleanupPeriodDays`), so run `score` at least weekly. Unreadable or changed
  formats leave fields null and raise the scorecard's coverage warning.
- No agent sees scorecards; no phase file reads the state directory.

---

## 11. Roadmap

Each slice ends with real tasks run through it and scored; a slice's exit criteria must hold before the
next starts.

| Stage | Adds | Records | Exit criteria |
|---|---|---|---|
| **Phase 0** (short) | `install --user` dry run on a throwaway repo; confirm Claude desktop and Codex app sessions run the user-level hooks; confirm `git hash-object -t tree` runs inside a sandboxed `codex exec` | — | Each item confirmed, or its fallback chosen and written into this spec |
| **Slice 1: one measured task (Claude)** | Spool, event schema v1, Claude adapter, `install`, `doctor` (A–E, Claude), `start`, `phase`, `check`, `rebase` (no memory cleanup), `pr`, `pr --refresh`, `close`, `score` (resolution, gate, timing, agent time, coverage); phase files triage, research, resolve, plan, build, verify; `AGENTS.md` | Every raw input in §6.12 except `tier`, `defect` and harness memory events | One real mvp M task merged with a complete scorecard (all boundaries present, gate evaluated, no unexplained orphans); two tasks in parallel in mvp scored correctly |
| **Slice 2: both agents, all phases (ready for real work)** | Codex adapter and install (hooks, approval step, writable root, bootstrap); retro phase, `retro-bundle`, harness memory, `memory`, `rebase` by-id cleanup; `tier`, `review`, `defect`; transcript cache | Everything in §6.12 | Claude and Codex tasks running concurrently in mvp; at least one echo-wiki task; a Claude task whose verify ran in a Codex delegate, with the delegate's check recorded; two parallel tasks' lessons merged cleanly; scorecards complete for all |
| **Slice 3: full scorecard** | All seven metrics, tokens and dollars, topology rebuild, summary with spread per tier, note-line validation | — | Scorecards recomputed for every task since Slice 1; three tasks hand-checked against the scorer |
| **v1: comparisons** | §2.3 first row | — | Parent design's Fair comparison rules |
| **Later** | Cloud, classifier, wrapper skill, more adapters | — | — |

**Ready for real work** is the end of Slice 2: from then on every task records all raw data the parent's
benchmarking needs, and Slice 3 computes the remaining metrics retroactively. Slice 1 tasks lack retro
spans and memory events; they prove the instrumentation and stay outside any v1 comparison anyway.

---

## 12. Testing

- **Unit (stdlib `unittest`):** event building and validation, identity and delegate rules, task
  resolution, timing spans and exclusions, done-gate evaluation, plan and note parsing, metric math,
  statistics (v1).
- **Integration (temporary git repos):** `start --new` uniqueness under concurrent calls; spool locking
  under parallel appends; fetch retry under concurrent fetches; union merge plus by-id cleanup across
  two branches; `rebase` conflict stop and rerun; `pr` and `pr --refresh` against a local bare remote
  with a stubbed `gh`; gate across merge, squash and rebase merges.
- **Adapter contract:** recorded Claude and Codex hook payloads (captured on 2026-10-08) as fixtures;
  a changed payload must produce a `format_warning`, never a crash.
- **End-to-end smoke:** one scripted task in a throwaway repo driven by real `claude -p` and
  `codex exec` (with `< /dev/null`), scored, with the scorecard compared to expected values.
- `harness doctor` doubles as the installation test on each machine.

---

## 13. Unknowns

**Resolved by tests on 2026-10-08** (Claude Code 2.1.295, Codex 0.160.0, git 2.54; details in §16):
hooks fire with the fields used here in both agents; Codex skips unapproved hooks and records
approvals; `CODEX_THREAD_ID` equals the hook `session_id`; markers reach Bash, children, subagents and
Codex processes and survive `cd`; Codex project `sandbox_mode` applies only when the project path is
already trusted at session start, and full access at launch works; a user-level writable root lets a
sandboxed Codex write the state dir; Claude ignores project allow rules in untrusted worktree paths;
`Bash(x:*)` respects word boundaries; both agents follow a "run this first" instruction; transcripts
carry tokens (both) and dollars (Claude); union merge works under `rebase --merge`; concurrent fetches
collide; the account is ADMIN on both pilots. Also resolved after review: in mvp, Codex loads the global
`~/.codex/AGENTS.md` alongside mvp's project `AGENTS.override.md`; a sandboxed Codex can lock and append
to a file in a writable root; after `claude --resume`, SessionStart fires again and the marker is current.

**Remaining, each with its safety net:**

| Unknown | Safety net |
|---|---|
| Whether the Codex desktop app (and the Claude desktop app) run user-level hooks | Phase 0 checks it; at runtime check E fails before triage if this session's hooks never reach the spool |
| `git hash-object -t tree` inside a seatbelt sandbox | Phase 0; the fallback is to compute the tree hash in Python |
| Transcript formats change | Readers are best-effort; fields go null and coverage drops; nothing else depends on them |

---

## 14. Risks and known limits

| Risk or limit | Handling |
|---|---|
| Hands-off assumptions compound, the evaluator approves weak work, a wrong lesson spreads, memory fills with noise, a lean config under-plans | Parent's guardrails, unchanged |
| Native agent memory blurs differences between harness versions | Accepted (C1) |
| Nested delegation across agents more than one level deep records the top session as parent | Exact chain reconstructable from transcripts |
| Children launched by a Codex session outside the task's worktree are unlinked | Listed as orphans; transcripts hold the link |
| Concurrent tasks share machine, test slots and provider quotas | Disclosed, as in the parent |
| Operator knows the arm (v1) | Disclosed, as in the parent |
| You forget `pr --refresh`, merge after `main` moved, or use GitHub's "Update branch" | The gate marks the task not-done (the merged tree differs from the `ready` tree); the scorecard says why. mvp's branch protection (strict status checks) blocks such merges; echo-wiki has none, so follow §17 there |
| The per-machine state directory is lost | Back it up with the machine |

---

## 15. Evolution seams

- **v1 comparisons plug in without changing recorded data:** `start --new` already holds the spool lock
  while assigning, so paired randomization replaces "always baseline" in one place; `start` events
  already carry benchmark tier, arm and assigned commit; `project.json` reserves `challenger_commit`,
  `shared_commit`, `memory_snapshot_commit`, `n`, `alpha`, `min_gain`; the dispatcher gains pinned
  checkouts; `score` adds the decision without touching existing scorecards. As the parent requires,
  v0 tasks never enter a comparison; they only inform N.
- **New agents:** an adapter in `harness/adapters/` that emits the §6.7 schema and names its identity
  variable; nothing else changes.
- **Cloud:** move the spool's role into committed per-task event files or a remote store; task folders
  already live in git.
- **Classifier:** trains on `request.md`, triage signals and `config.json` (plus state-dir copies), and
  writes `config.json`'s knobs; the harness already runs from that file.

---

## 16. Verified platform facts (2026-10-08)

**Claude Code 2.1.295.** Hooks fired for SessionStart, UserPromptSubmit, SubagentStart/Stop, Stop and
SessionEnd, even in an untrusted folder; payloads carry `session_id` and `transcript_path`; subagent
events carry the parent `session_id` plus `agent_id` and `agent_type`; SubagentStop has
`agent_transcript_path`; `effort.level` appears on Stop and SubagentStop; SessionStart carried no
`model`. `CLAUDE_EFFORT` in a hook's environment can be stale; trust the payload. A SessionStart hook's
exports in `CLAUDE_ENV_FILE` reach Bash, grandchild processes and subagents and survive `cd`. Project
`permissions.allow` is ignored until the folder is trusted; each worktree path is trusted separately.
`Bash(hprobe:*)` did not match `hprobe2`. Transcripts hold the model per message, `usage`, every tool
call, subagent files under `<session>/subagents/`, and a `cost-state` row with dollars, per-model tokens
(including thinking and cache) and durations.

**Codex 0.160.0.** `codex exec` waits on stdin unless given `< /dev/null`. Non-managed hooks silently
do not run until approved; approvals live in `~/.codex/config.toml` as
`[hooks.state."<file>:<event>:<i>:<j>"] trusted_hash`. Hook payloads carry `session_id` (the thread
id), `model` (all events but SessionEnd), `transcript_path`, `turn_id`; helper events carry `agent_id`,
`agent_type` and, on stop, `agent_transcript_path`, under the parent `session_id`. Hook processes
inherit the launcher's environment but do not see `CODEX_THREAD_ID`; shell commands do, along with
`CODEX_SANDBOX=seatbelt` when sandboxed. The default `workspace-write` sandbox blocks `.git` writes and
writes to `~/.local/state`; a user-level `sandbox_workspace_write.writable_roots` entry makes a
directory writable while the sandbox stays on. Full access works at launch (`-s danger-full-access`),
or from a project's `.codex/config.toml` only when that path was already trusted at session start.
Every `codex exec` run persists a `trust_level = "trusted"` entry for its working directory into the
user's `~/.codex/config.toml`, so Codex delegates launched with `codex exec` in task worktrees leave one
entry per worktree (harmless; Codex's own behavior). In mvp, the global `~/.codex/AGENTS.md` loads together
with the project's `AGENTS.override.md`. A sandboxed process can `flock` and append inside a writable root. Rollouts hold cumulative `token_count` totals (no dollars) and, for helpers, `session_meta`
with `parent_thread_id` and depth.

**git 2.54 and GitHub.** `rebase --merge` honors `merge=union`; concurrent fetches across worktrees of
one repo fail on ref locks about half the time; the account is ADMIN on `echotheorylabsai/mvp` and
`echotheorylabsai/echo-wiki`.

---

## 17. Daily use

1. Write the task in a file outside the worktree. Create a worktree from fresh `origin/main`.
2. In the worktree, right before launching the agent (the clock starts here):
   `harness start --new <slug> --benchmark-tier S|M|L --request <file>`.
3. Open Claude or Codex (Codex with full access) in that worktree; it bootstraps itself.
4. Answer questions when asked; stops and resumes are fine (any number of sessions).
5. When the PR is ready: review it; run `harness pr --refresh <task-id>`; merge as soon as its checks
   pass. If `main` moves first, refresh again. Never use GitHub's "Update branch" button: it changes the
   branch without a `ready`, so the merged code no longer matches and the task fails the gate.
6. Afterwards: `harness close <task-id> --done` if the PR flagged a scope reduction;
   `harness defect <task-id> "<line>"` if a bug surfaces; `harness close <task-id> --abandon` for a
   task that will not merge.
7. Every few days: `harness score`; read the summary; change one thing per harness commit (v1 makes
   that a formal comparison).

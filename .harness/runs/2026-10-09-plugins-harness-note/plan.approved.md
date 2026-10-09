# Plan — 2026-10-09-plugins-harness-note

## Goal

Tell contributors, in `README.md`, that agent work here runs as lean-harness tasks and where each task's record lives.

## Outcome

`README.md` gains a section titled `## Agent tasks (lean harness)`, placed just before `## Contributing`, of two to four sentences: agent work runs as lean-harness tasks; each task's record lives in `.harness/runs/<task-id>/`; it links `docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md`. Nothing else changes.

## Acceptance checks

### C1 — README section has the chosen title, sits just before Contributing, and names the record folder and spec
Expected: exit 0
```sh
python3 -I -c "import re,sys; t=open('README.md').read(); h=re.findall(r'^## .*$', t, re.M); i=h.index('## Agent tasks (lean harness)'); assert h[i+1]=='## Contributing', h; s=t.split('## Agent tasks (lean harness)')[1].split('## Contributing')[0]; assert '.harness/runs/<task-id>/' in s; assert '(./docs/superpowers/specs/2026-10-08-lean-harness-v0-product-spec.md)' in s"
```

### C2 — Only README.md changes outside the task folder
Expected: exit 0
```sh
test "$(git diff --name-only "$(git merge-base HEAD origin/main)" HEAD -- . ':(exclude).harness/runs')" = "README.md"
```

## Tier

S

## Source

prompt

## Decisions

- 2026-10-09 · claude/opus-5.5 · triage — Section title is "Agent tasks (lean harness)". Why: the user chose option B when asked, as request.md requires.

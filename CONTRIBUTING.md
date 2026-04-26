# Contributing

Thanks for your interest. Contributions are welcome — bug fixes, skill improvements, and new plugins.

## What lives here

| Path | Purpose |
|---|---|
| `echo-marketing/` | The installable plugin (canonical artifact) |
| `echo-marketing/skills/<skill>/SKILL.md` | Skill definition and workflow |
| `echo-marketing/skills/<skill>/references/` | Reference files loaded on demand by the skill |
| `brand/` | Echo Theory Labs' brand config — working example for plugin consumers |
| `evals/` | Eval rubrics (`evals/rubrics/`) and test input fixtures (`evals/fixtures/`) |
| `skills/_trigger-evals/` | Trigger invocation eval configs and run results |
| `skills/body-evals-workspace/` | Body quality benchmark runs (before/after comparisons) |

## Making changes

### Editing an existing skill

1. Edit `echo-marketing/skills/<skill>/SKILL.md` (or a file in `references/`).
2. If you changed the `description` frontmatter, run the trigger evals:
   ```bash
   python skills/_trigger-evals/direct_eval.py
   ```
3. If you changed the skill body, run the body evals and include updated results in your PR.
4. Open a PR with a clear description of what changed and why.

### Adding a new plugin

1. Create a top-level directory for the plugin: `<plugin-name>/`
2. Add `.claude-plugin/plugin.json` — see `echo-marketing/.claude-plugin/plugin.json` for the schema.
3. Add skills under `<plugin-name>/skills/<skill-name>/SKILL.md`.
4. Register the plugin in `.claude-plugin/marketplace.json`.
5. Add a `README.md` at the plugin root documenting the skills, prerequisites, and example prompts.
6. Open a PR.

## Code of conduct

Be direct and respectful. We review PRs on a best-effort basis.

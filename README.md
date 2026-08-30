# Echo Theory Labs — Claude Code Plugin Marketplace

A public marketplace of [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code/plugins) built and maintained by [Echo Theory Labs](https://www.echotheory.ai). Each plugin packages a set of skills that extend Claude's behavior for specific workflows.

---

## Available Plugins

| Plugin | Description |
|---|---|
| [`echo-marketing`](./echo-marketing/) | Brand-aware marketing skills: draft blog and Twitter/X content, review copy against brand guidelines, and author voice documents. |
| [`echo-linear`](./echo-linear/) | Turn approved specs and plans into Linear projects, milestones and issues written in product language — then deliver them, issue by issue, test-first. Requires the Linear MCP. |

---

## Installation

### Add this marketplace to Claude Code

```bash
claude plugin marketplace add echotheorylabsai/echo-theory-plugins
```

### Install a plugin

```bash
# Project-scoped (recommended)
claude plugin install echo-marketing --scope project

# User-wide
claude plugin install echo-marketing --scope user
```

### Session-local (no installation)

```bash
claude --plugin-dir /path/to/echo-marketing
```

---

## Repository Layout

```
echo-theory-plugins/
├── .claude-plugin/
│   └── marketplace.json            ← marketplace manifest
├── echo-marketing/                 ← installable plugin
│   ├── .claude-plugin/
│   │   └── plugin.json             ← plugin manifest
│   ├── skills/                     ← skill definitions
│   └── README.md
├── echo-linear/                    ← installable plugin (needs the Linear MCP)
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/                     ← linear-sync, linear-implement
│   └── README.md
├── docs/
│   ├── brand/                      ← Echo's brand config (example for consumers)
│   └── design/                     ← design docs behind each skill
└── skill-evals/
    ├── evals/                      ← eval rubrics and test fixtures
    ├── _trigger-evals/             ← trigger invocation eval configs and results
    └── body-evals-workspace/       ← body quality benchmark runs
```

**`docs/brand/`** is Echo Theory Labs' own brand configuration, included as a working example. The `echo-marketing` skills expect a `brand/` directory in your project — copy and adapt `docs/brand/` as a starting point.

---

## Contributing

Bug reports and skill improvements welcome. Open an issue or PR.

- Each plugin lives in its own top-level directory with a `.claude-plugin/plugin.json` manifest.
- Skill source is in `echo-marketing/skills/<skill-name>/SKILL.md`.
- Eval rubrics live in `skill-evals/evals/rubrics/`; fixtures in `skill-evals/evals/fixtures/`.

---

## License

MIT — see [LICENSE](./LICENSE).

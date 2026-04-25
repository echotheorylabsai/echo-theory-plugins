# Marketing skills — generic pattern

A reusable two-skill pattern for brand-aware marketing content, driven by project-level brand config. Apply it to any company, client, or personal brand by filling in `brand/`.

## Structure

```
<project-root>/
├── brand/                      project config — single source of truth
│   ├── voice.md                personality, attributes, pillars, tone
│   └── style-guide.md          grammar, formatting, terminology
└── skills/
    ├── draft-content/          generate new marketing content
    └── brand-review/           evaluate existing content + author voice doc
```

## The two skills

- **`draft-content`** — generates new content (blog, social, email, landing pages). Reads `brand/voice.md` and `brand/style-guide.md`; loads channel-specific references on demand.
- **`brand-review`** — audits existing content against voice, style, and universal compliance flags. Also guides the user through authoring or revising `brand/voice.md` itself via `voice-doc-framework.md`.

Verbs are orthogonal: **create** vs. **evaluate**. The two skills never overlap.

## The `brand/` config

Both skills read `brand/voice.md` and `brand/style-guide.md` as their source of truth. If missing, each skill offers to help author them. All brand customization happens here — the skill files themselves are company-agnostic.

## Reusing the pattern

For a new company, client, or project:

1. Copy `brand/`, `skills/draft-content/`, `skills/brand-review/` into the new project root.
2. Fill out `brand/voice.md` (or ask `brand-review` to walk you through it).
3. Override defaults in `brand/style-guide.md` as needed.
4. Start drafting and reviewing — the skills will pick up the new config automatically.

## Design commitments

- **Progressive disclosure** — SKILL.md files stay thin; details live in `references/` and load only when needed.
- **Single responsibility** — each skill owns one verb; `brand/` owns the data.
- **No cross-skill dependencies** — both skills read `brand/`; neither imports from the other.
- **skill-creator compatible** — frontmatter uses only validator-approved keys (`name`, `description`).
- **Extensible** — new channels drop in as `skills/draft-content/references/channel-*.md`; industry-specific compliance can slot under `skills/brand-review/references/compliance-modules/` when needed.

## Out of scope (for now)

- `brand/personas.md`, `brand/facts.md`, `brand/context.md` — architecture accommodates them; add when you have content to populate them.
- Voice variants (`brand/voice/*.md`) — add when a second voice use case appears.
- Deterministic scripts (terminology checkers, readability scorers) — add when a fragile check shows up in practice.
- Industry compliance modules — add under `skills/brand-review/references/compliance-modules/` per industry when needed.

# echo-marketing Plugin

Three Claude skills for Echo Theory Labs marketing work: draft content, review content, and author brand voice guidelines.

---

## Architecture

```
echo-marketing/
├── .claude-plugin/
│   └── plugin.json          ← plugin manifest (name, version, author)
├── skills/
│   ├── draft-content/       ← generate blog + Twitter/X content
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── channel-blog.md
│   │       ├── channel-social-twitter.md
│   │       ├── cta-patterns.md
│   │       ├── headline-patterns.md
│   │       └── seo-patterns.md
│   ├── brand-review/        ← audit content against brand standards
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── review-rubric.md
│   │       └── legal-compliance.md
│   └── brand-voice-authoring/  ← create or revise brand/voice.md
│       ├── SKILL.md
│       └── references/
│           └── voice-doc-framework.md
└── README.md
```

**How skills load**: Claude reads the `SKILL.md` frontmatter (name + description) at session start to know when a skill applies. When invoked, it loads the full `SKILL.md` body. Reference files under `references/` are loaded on demand — only when the skill's workflow reaches the step that needs them. This keeps context lean.

**Shared brand config**: All three skills read live brand configuration from `./brand/` in the user's project directory at invocation time — they do not bundle it. The brand config is intentionally kept separate so it can evolve without touching the skills.

---

## Prerequisites: `brand/` directory

Before using any skill, your project must contain a `./brand/` directory with these files:

| File | Purpose |
|---|---|
| `voice.md` | Voice attributes, audience, messaging pillars, tone by channel and situation |
| `facts.md` | Locked positioning facts and "what the brand is not" |
| `personas.md` | Audience personas with role, seniority, and pain points |
| `anti-patterns.md` | Banned phrases, idioms, and content patterns |
| `style-guide.md` | Grammar conventions, formatting rules, Echo-specific terminology |

If a file is missing, the skill will ask whether to (a) point to it, (b) author it using `brand-voice-authoring`, or (c) proceed with a generic fallback.

---

## Skills

### `draft-content`

**Invoked when**: the user asks to draft, write, compose, repurpose, or get headline/hook options for blog or Twitter/X content.

**Not for**: reviewing or auditing existing content — use `brand-review` for that.

**What it generates**:
- A full blog post or Twitter/X thread, applying the brand's voice, facts, persona, anti-patterns, and style guide
- 2–3 headline or opening-hook options
- SEO recommendations (blog only): primary keyword, meta description, linking suggestions
- A note on which brand config and channel tone were applied

**How it works**:
1. Reads all five `brand/` files to load brand context
2. Determines the channel (blog or Twitter/X) and loads the matching channel reference file
3. Loads headline patterns and proposes 2–3 options for the user to choose
4. For blogs: runs the SEO keyword placement checklist
5. Adds a research-distribution CTA (never lead-gen)
6. Drafts the content, enforcing citation recency (no external stats older than 90 days)

**Example prompts**:
```
"Write a blog post about agent evaluation failure modes, targeting senior engineers"
"Draft a Twitter thread on MCP server hardening risks"
"Give me 3 headline options for a post on trajectory analysis"
"Repurpose this methodology note into a Twitter/X thread"
```

---

### `brand-review`

**Invoked when**: the user asks to audit, check, proof, critique, or revise existing copy, or wants severity-graded findings with before/after revisions.

**Not for**: creating new content — use `draft-content` for that.

**Accepts**:
- Text pasted directly into the conversation
- A file path
- A URL to a published page
- Multiple pieces for a batch review

**What it generates**:
1. **Summary** — overall brand alignment score, top strengths, top improvements
2. **Detailed findings** — severity-graded table (High / Medium / Low) with location, issue, and suggested fix
3. **Revised sections** — before/after for the top 3–5 highest-severity issues
4. **Legal/compliance flags** — separate section for lead-gen CTAs, citation fabrication, named-competitor disparagement, and other compliance concerns

**Severity scale**:
- **High** — contradicts brand voice, compliance risk, significantly undermines messaging, or cites a stat older than 90 days
- **Medium** — inconsistent with guidelines but not damaging
- **Low** — minor style or preference deviation

**Example prompts**:
```
"Review this blog draft against our brand guidelines"
"Audit this LinkedIn post for anti-patterns"
"Check this Twitter thread for compliance issues"
"Proof this blog post before we publish"
```

---

### `brand-voice-authoring`

**Invoked when**: the user wants to create, draft, populate, define, revise, or update a brand voice document.

**Not for**: reviewing content (`brand-review`) or drafting marketing copy (`draft-content`).

**What it generates**: a fully populated `brand/voice.md` with 7 sections:
1. Brand personality
2. Voice attributes (positioned on spectrums)
3. Audience awareness
4. Messaging pillars
5. Tone by channel and by situation
6. Brand-specific terminology
7. Voice anti-patterns

**How it works**:
1. Checks if `brand/voice.md` exists. If missing, scaffolds it with placeholders. If present and populated, asks whether to revise sections, restart one from scratch, or do a full rebuild.
2. Loads `references/voice-doc-framework.md` for section-by-section interview prompts and spectrum definitions.
3. Walks the user through sections in order (earlier sections constrain later ones).
4. After each section: prompts → captures the user's answer → reflects it back → confirms → writes to file.
5. After the final section, runs a coherence check and flags contradictions for the user to resolve.

**Example prompts**:
```
"Let's define our brand voice from scratch"
"I want to revise section 2 of our brand voice document"
"Help me author our tone guidelines"
"Our brand personality has changed — let's update the voice doc"
```

---

## Skill relationships

The three skills form a natural workflow — author the voice first, then draft and review content with it:

```
brand-voice-authoring ──creates──► brand/voice.md
                                         │
                              reads at invocation
                              ┌────────────────┐
                              ▼                ▼
                       draft-content    brand-review
                    (drafts new copy)  (audits existing copy)
```

You can run them in any order. A common loop: draft → review → revise → review again.

---

## Installation

### Session-local (for testing or one-off use)

Pass the plugin directory to `--plugin-dir`. This loads the plugin for that session only — no global installation required:

```bash
claude --plugin-dir /path/to/echo-marketing
```

### Persistent installation

For project-scoped or user-wide persistent installation, the plugin needs to be registered via a marketplace. See the [Claude Code plugin documentation](https://docs.anthropic.com/en/docs/claude-code/plugins) for how to register a local or private marketplace and install from it.

Quick path for team-wide use: host this directory in a git repository, add it as a Claude Code marketplace, then install with:

```bash
claude plugin install echo-marketing@<your-marketplace> --scope project  # or --scope user
```

---

## Developing and updating skills

Each skill lives in `skills/<skill-name>/`. The entry point is `SKILL.md`:

- **Frontmatter** (`name`, `description`) controls when Claude invokes the skill. The `description` is the primary trigger — write it to match how users actually phrase requests.
- **Body** contains the workflow Claude follows. Keep it under ~500 lines; move heavy reference content into `references/`.
- **`references/` files** are loaded on demand. Each `SKILL.md` step that needs a reference file calls it out explicitly.

**Eval artifacts** for validating skill changes live at `../skills/_trigger-evals/` (trigger invocation tests) and `../skills/body-evals-workspace/` (body quality benchmarks). Run trigger evals after changing the `description` frontmatter; run body evals after changing the workflow.

**Brand config** (`../brand/`) is out of scope for skill edits — changes there flow automatically to all skills at invocation time.

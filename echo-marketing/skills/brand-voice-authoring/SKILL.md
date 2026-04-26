---
name: brand-voice-authoring
description: Author or revise a brand voice document (`brand/voice.md`) using a structured framework that walks the user through brand personality, voice attributes (positioned on spectrums), audience awareness, messaging pillars, tone-by-channel and tone-by-situation matrices, brand-specific terminology, and voice anti-patterns. Use when the user wants to create, draft, populate, define, revise, or update a brand voice doc, voice guidelines, or tone-of-voice document. Do NOT use for reviewing existing content (use brand-review) or drafting marketing content (use draft-content).
---

# Brand Voice Authoring

Guide the user through authoring or revising `brand/voice.md`. The framework helps the user articulate voice decisions; the skill captures their answers rather than inventing voice content on their behalf.

## Workflow

1. Check whether `brand/voice.md` exists.
   - If missing, scaffold it with `<to be defined>` placeholders for sections 1–7 of the framework. Exclude the "Using this framework" meta-section — it is workflow guidance, not a content section.
   - If present and fully populated (no `<to be defined>` placeholders), ask whether the user wants to (a) revise specific sections in-place, (b) restart a section from scratch (clear and re-prompt), or (c) do a full rebuild.
   - If present with placeholders remaining, ask which sections to complete.

2. Load `references/voice-doc-framework.md` for section-by-section prompts, spectrum definitions, example outputs, and the "Using this framework" workflow at the bottom.

3. Walk the user through one section at a time, in framework order. Earlier sections inform later ones — do not skip ahead unless the user explicitly directs.

4. For each section: prompt → capture the user's answer → reflect it back → confirm → write into `brand/voice.md`.

5. After the final section, run a coherence check. Write the updated `brand/voice.md` first, then flag any contradictions for the user to resolve. Check: (a) no two voice attributes are mutually contradictory without explicit situational guidance; (b) every major tone-by-channel entry maps to at least one messaging pillar; (c) no anti-pattern entry contradicts a stated voice attribute. Present contradictions as a numbered list with a suggested resolution for each.

## After authoring

Ask the user: "Would you like me to:
- Test the new voice by running an existing piece of content through the brand-review skill to see whether it now conforms to the updated guidelines?
- Draft a sample piece of content using the draft-content skill (you'll need to provide a topic, channel, and key messages)?
- Revise any section we just captured?"

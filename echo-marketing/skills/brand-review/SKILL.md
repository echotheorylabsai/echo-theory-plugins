---
name: brand-review
description: Evaluate existing marketing content (pasted, file-path, or URL) against brand voice, facts, personas, anti-patterns, style guide, and universal legal/compliance flags. Use when the user asks to audit, check, proof, critique, or revise existing copy, or wants severity-graded findings with before/after revisions. Do NOT use for creating new content from scratch (use draft-content) or for authoring a brand voice document (use brand-voice-authoring).
---

# Brand Review

Review content against brand voice, facts, personas, anti-patterns, style guide, messaging pillars, and universal compliance flags. Flag deviations by severity and provide specific improvement suggestions.

## Brand config resolution

Before reviewing, resolve brand context in this order:

1. Read `./brand/voice.md` — voice attributes, audience pointer, messaging pillars, tone by channel.
2. Read `./brand/facts.md` — positioning facts; flag any drift from the locked pillars, capabilities, or "what the brand is not".
3. Read `./brand/personas.md` — flag persona-mismatched copy (wrong register for the intended reader).
4. Read `./brand/anti-patterns.md` — the canonical "never" list. Every item is a flag-on-sight.
5. Read `./brand/style-guide.md` — grammar, formatting, brand-specific terminology and capitalization.
6. If any file is missing, ask the user: "I could not find `brand/<file>`. Would you like to (a) point me to it, (b) author it now using the brand-voice-authoring skill, or (c) proceed with a generic review for clarity, consistency, professionalism, and universal compliance only?"

## Inputs

Accept content in any of these forms:
- Pasted directly into the conversation.
- A file path.
- A URL to a published page.
- Multiple pieces for batch review.

If a URL is provided, attempt to retrieve its content. If the URL is inaccessible (auth-required, 404, timeout, or non-text response), ask the user: "I was unable to retrieve the content at `<URL>`. Would you like to (a) paste the content directly, (b) provide a local file path, or (c) cancel the review?"

## Workflow

1. Load `references/review-rubric.md` for severity definitions and output format.

2. Evaluate the content across these dimensions. If `brand/*` files are populated, use them; otherwise apply the generic-review fallback in the rubric.

   - **Voice and tone** — match to attributes in `brand/voice.md`; flag inconsistent shifts and persona-mismatched register per `brand/personas.md`.
   - **Positioning and facts** — alignment with `brand/facts.md`; flag drift from named pillars, capabilities, or "what the brand is not" claims. Flag any external statistic or numerical claim from a source older than 90 days from the content creation date as **High** severity — stale stats are especially damaging in AI content where the field moves fast.
   - **Anti-patterns** — every item in `brand/anti-patterns.md` is a flag-on-sight. Surface each instance.
   - **Terminology and language** — brand-specific terms and capitalization from `brand/style-guide.md`; jargon misfit for the audience persona; product/feature/pillar name capitalization.
   - **Style compliance** — grammar, formatting, numbers/dates/percent conventions per `brand/style-guide.md`.
   - **Clarity, consistency, professionalism** — per the rubric.

3. Always load `references/legal-compliance.md` and run the universal flag checks regardless of whether brand config is present.

4. Produce findings using the format defined in `references/review-rubric.md`.

## Output

Follow the output format from `references/review-rubric.md`. The output has four sections:

1. **Summary** — overall alignment, top strengths, top improvements.
2. **Detailed findings** — severity-graded table of issues.
3. **Revised sections** — before/after for the top 3–5 highest-severity issues.
4. **Legal / compliance flags** — separate list of compliance concerns with recommended actions. Lead-gen CTA misalignment, citation fabrication, and named-competitor disparagement route here, not into detailed findings.

## After review

Ask the user: "Would you like me to:
- Revise the full content with all suggestions applied?
- Fix only the high-severity issues?
- Review additional content against the same guidelines?
- Update or expand your brand voice document (use the brand-voice-authoring skill)?"

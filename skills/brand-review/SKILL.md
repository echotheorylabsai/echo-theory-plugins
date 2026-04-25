---
name: brand-review
description: Evaluate existing marketing content against brand voice, facts, personas, anti-patterns, style guide, and universal legal/compliance flags. Use when the user wants to audit, check, proof, or revise drafted or published copy. Produces severity-graded findings plus before/after revisions. Also use when the user wants to author or revise their brand voice document. Do NOT use for creating new content from scratch — use the draft-content skill for that.
---

# Brand Review

Review content against brand voice, facts, personas, anti-patterns, style guide, messaging pillars, and universal compliance flags. Flag deviations by severity and provide specific improvement suggestions.

## Trigger

Use this skill when the user asks to review, check, audit, proof, or revise existing content — whether pasted in, referenced by file path, or linked by URL. Also use when the user asks for help authoring or revising their brand voice document.

## Brand config resolution

Before reviewing, resolve brand context in this order:

1. Read `./brand/voice.md` — voice attributes, audience pointer, messaging pillars, tone by channel.
2. Read `./brand/facts.md` — positioning facts; flag any drift from the locked pillars, capabilities, or "what the brand is not".
3. Read `./brand/personas.md` — flag persona-mismatched copy (wrong register for the intended reader).
4. Read `./brand/anti-patterns.md` — the canonical "never" list. Every item is a flag-on-sight.
5. Read `./brand/style-guide.md` — grammar, formatting, brand-specific terminology and capitalization.
6. If any file is missing, ask the user: "I could not find `brand/<file>`. Would you like to (a) point me to it, (b) author it now using `references/voice-doc-framework.md`, or (c) proceed with a generic review for clarity, consistency, professionalism, and universal compliance only?"
7. If the user asks to author or revise the voice document itself, load `references/voice-doc-framework.md` and guide them through populating `brand/voice.md`. Do not perform a content review in this branch.

## Inputs

Accept content in any of these forms:
- Pasted directly into the conversation.
- A file path.
- A URL to a published page.
- Multiple pieces for batch review.

## Workflow

1. Determine the branch:
   - **Branch A — Content review** (default). Proceed to steps 2–5.
   - **Branch B — Voice-doc authoring or revision**. Load `references/voice-doc-framework.md` and help the user fill or revise `brand/voice.md`. Stop here for this branch.

2. Load `references/review-rubric.md` for severity definitions and output format.

3. Evaluate the content across these dimensions. If `brand/*` files are populated, use them; otherwise apply the generic-review fallback in the rubric.

   - **Voice and tone** — match to attributes in `brand/voice.md`; flag inconsistent shifts and persona-mismatched register per `brand/personas.md`.
   - **Positioning and facts** — alignment with `brand/facts.md`; flag drift from named pillars, capabilities, or "what the brand is not" claims.
   - **Anti-patterns** — every item in `brand/anti-patterns.md` is a flag-on-sight. Surface each instance.
   - **Terminology and language** — brand-specific terms and capitalization from `brand/style-guide.md`; jargon misfit for the audience persona; product/feature/pillar name capitalization.
   - **Style compliance** — grammar, formatting, numbers/dates/percent conventions per `brand/style-guide.md`.
   - **Clarity, consistency, professionalism** — per the rubric.

4. Always load `references/legal-compliance.md` and run the universal flag checks regardless of whether brand config is present.

5. Produce findings using the format defined in `references/review-rubric.md`.

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
- Help you document or revise your brand voice (using `references/voice-doc-framework.md`)?"

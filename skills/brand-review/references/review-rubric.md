# Review Rubric

Severity definitions and output format used by the `brand-review` skill.

## Severity definitions

- **High** — contradicts brand voice, contains compliance risk, or significantly undermines messaging.
- **Medium** — inconsistent with guidelines but not damaging.
- **Low** — minor style or preference issue.

## Output format

Structure the review output as four sections, in this order.

### 1. Summary

- Overall assessment: how well the content aligns with brand standards (or general quality if brand config is not available).
- 1–2 sentences on the biggest strengths.
- 1–2 sentences on the most important improvements.

### 2. Detailed findings

Produce a table:

| Issue | Location | Severity | Suggestion |
|---|---|---|---|

- **Issue** — short description of the problem.
- **Location** — quote the offending text or cite the section/line.
- **Severity** — High / Medium / Low per definitions above.
- **Suggestion** — specific change to make.

### 3. Revised sections

For the top 3–5 highest-severity issues, show:

- **Before**: the original text.
- **After**: the suggested revision.

### 4. Legal / compliance flags

List any issues surfaced from `legal-compliance.md` separately. For each, state the concern and the recommended action (add a disclaimer, substantiate a claim, remove a comparison, route to legal review, etc.).

## Generic-review fallback

If `brand/voice.md` is not available, substitute these dimensions for Voice/Terminology/Messaging:

- **Clarity** — is the main message clear in the first paragraph? Are sentences concise? Is the structure logical? Are there ambiguous statements?
- **Consistency** — is the tone consistent? Are terms used consistently (no switching between synonyms)? Is formatting consistent?
- **Professionalism** — typos, grammatical errors, awkward phrasing? Is the tone appropriate for the intended audience? Are claims supported?

Style compliance against `brand/style-guide.md` and legal-compliance checks still run in the fallback path.

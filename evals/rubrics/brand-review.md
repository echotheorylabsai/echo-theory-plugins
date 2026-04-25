# Eval rubric — `brand-review` (Echo Theory Labs, Phase 1)

Binary pass/fail per check. No partial credit. LLM-as-judge (skill-creator) scores during Invocation B; the user (HITL) is final arbiter.

Fixture-to-check mapping:
- `flawed-01-hype-superlatives.md` → check 1.
- `flawed-02-lead-gen-and-fake-personal.md` → checks 2 + 3.
- `flawed-03-citation-issues.md` → check 4.
- Check 5 is verified across the full set of three review outputs (structural cross-cut, no dedicated fixture).

---

## Check 1 — Flags hype superlatives without evidence

**Pass** if the review surfaces every unsubstantiated superlative seeded in `flawed-01-hype-superlatives.md` (5 instances: "industry-leading", "best-in-class", "most advanced", "unparalleled", "#1") and recommends substantiation, qualification, or removal.

**Fail** if any seeded superlative is missed, or if the review flags only some without naming the specific terms.

## Check 2 — Flags lead-gen CTAs, exclamation marks, and named-competitor disparagement

**Pass** if the review on `flawed-02-lead-gen-and-fake-personal.md`:
- Identifies all 2 lead-gen CTAs and recommends Echo-appropriate research-distribution alternatives.
- Flags any exclamation marks present in production copy.
- Identifies the 1 named-competitor disparagement and recommends rephrasing or removal.

**Fail** if any of the three sub-flags is missed.

## Check 3 — Flags fake-personal-story opener and "we're excited" energy

**Pass** if the review on `flawed-02-lead-gen-and-fake-personal.md`:
- Identifies the fake-personal-story opener and recommends an Echo-style declarative or evidence-led replacement.
- Identifies the "we're excited to announce" line and flags the announcement-marketing tone.

**Fail** if either is missed.

## Check 4 — Flags citation issues

**Pass** if the review on `flawed-03-citation-issues.md`:
- Identifies all 3 stat claims with stripped citations and recommends restoring sources.
- Identifies the 1 fabricated statistic with the invented source name and flags it as fabricated or unverifiable.

**Fail** if any seeded citation issue is missed, or if the fabricated stat is treated as legitimate.

## Check 5 — Routing and severity calibration (structural cross-cut)

Verified across all three flawed-draft review outputs together.

**Pass** if **both** hold:
- Compliance and legal-class issues (lead-gen CTA misalignment, citation fabrication, named-competitor disparagement, etc.) are routed to the `Legal / compliance flags` section of the review output, not buried in `Detailed findings`.
- Severity grading across the three reviews is internally consistent and calibrated to the severity definitions in `skills/brand-review/references/review-rubric.md`. Not all issues are graded High; not all are graded Low. The most severe issues per fixture (e.g., fabricated citation) are graded above the least severe (e.g., a single missed style-guide rule).

**Fail** if compliance issues appear only in detailed findings, or if severity grading is uniform across all issues regardless of impact.

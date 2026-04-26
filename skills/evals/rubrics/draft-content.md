# Eval rubric — `draft-content` (Echo Theory Labs, Phase 1)

Binary pass/fail per check. No partial credit, no weighted scoring. LLM-as-judge (skill-creator) scores during Invocation B; the user (HITL) is final arbiter.

Channel scoring map:
- **Blog fixture**: scored on checks 1, 2, 3, 4.
- **Twitter/X fixture**: scored on checks 1, 2, 3, 5.

---

## Check 1 — Voice attributes are visible (universal)

**Pass** if a blind read of the draft would let a reviewer identify all three Echo voice attributes from `brand/voice.md` §2:
- Declarative and category-defining (load-bearing claims, no qualifier-stacking).
- Evidence-led (third-party citations or explicit "in our testing" qualifiers on every load-bearing stat).
- Technical-peer authority (precise technical terminology, no 101-level explainer register).

**Fail** if any one attribute is absent or actively contradicted.

## Check 2 — No anti-patterns appear (universal)

**Pass** if the draft contains zero items from `brand/anti-patterns.md`:
- No hype superlatives without evidence.
- No fake-personal-story openers.
- No lead-gen CTAs.
- No "we're excited to announce" energy.
- No exclamation marks.
- No named-competitor disparagement.
- No unqualified absolutes.
- No use of the deprecated phrase "context engineering" as a pillar name.

**Fail** if any single anti-pattern appears.

## Check 3 — Headline matches Echo formula (universal)

**Pass** if the headline (or, for Twitter, the opening hook of the lead tweet) matches a declarative or contrarian formula from `skills/draft-content/references/headline-patterns.md`. Examples of pass-class formulas:
- Naming a discipline or failure mode.
- Stating a load-bearing claim ("The engineering discipline to make agents production-grade barely exists").
- Contrarian-by-data ("Why most agent eval pipelines fail under production load").

**Fail** if the headline is a generic listicle ("7 Ways to..."), a how-to-without-obstacle formula, or marketing-puffery framing.

## Check 4 — SEO keyword placement (blog only)

**Pass** if the primary keyword from the brief (or the primary Echo term most relevant to the topic) appears in **all three** of: headline, first paragraph, meta description.

**Fail** if any one of those three placements is missing.

## Check 5 — Twitter/X community register (twitter only)

**Pass** if **all** of the following hold:
- Hook is evidence-first (statistic, named failure mode, or declarative claim) — not generic punchiness.
- Tone fits AI R&D community discourse (technical-peer, no marketing energy).
- If the post or thread links to a blog, the link convention from `skills/draft-content/references/channel-social-twitter.md` is followed (numbered thread tweets if multi-tweet, link placement consistent).

**Fail** if any one sub-condition is violated.

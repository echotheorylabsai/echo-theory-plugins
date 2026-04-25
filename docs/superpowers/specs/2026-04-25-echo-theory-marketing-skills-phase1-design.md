# Phase 1 — Echo Theory Labs marketing skills customization

**Date**: 2026-04-25
**Status**: Design — ready for execution
**Scope**: Customize the existing generic marketing skills (`draft-content`, `brand-review`) for Echo Theory Labs. Phase 1 is intentionally minimal: blog and Twitter/X channels only, with a tight rubric-based evaluation loop driven by `skill-creator`.

---

## 0. Operator instructions (read before executing)

This spec is written to be executed by an agent in a fresh Claude session with no prior conversation context. If you are that agent, follow this orientation before touching anything.

**Working directory**: `/Users/shubh/Desktop/src/echo-skills/`. All relative paths in this spec resolve against this directory.

**Read order before starting Section 8**:
1. This spec — full read, top to bottom.
2. `echo-theory-labs-vision.md` (repo root) — primary input data for all `brand/*` content.
3. `brand/voice.md` and `brand/style-guide.md` — current generic templates that will be rewritten.
4. `skills/draft-content/SKILL.md` and `skills/brand-review/SKILL.md` — current generic skills that will be edited.
5. `README.md` (repo root) — pattern overview for context.

**Critical HITL boundary** (full detail in Sections 4 and 5): The executing agent does **NOT** invoke `Skill: document-skills:skill-creator`. The user is the human-in-the-loop. For execution-sequence steps 6 and 7, the agent prepares a handoff packet (verbatim invocation prompt + context summary + review checklist) and presents it to the user. The user invokes skill-creator. The user reviews skill-creator's outputs, approves or rejects proposed patches, and signs off on the HITL checklists. The agent applies user-approved patches to skill files but never runs skill-creator itself. This boundary has no exceptions.

**Entry point for execution**: Section 8 (Execution sequence). Begin with step 1 only after the read order above is complete.

**Exit point**: Phase 1 is complete only when every item in Section 9 (Phase 1 exit criteria) holds, including the user's explicit sign-off on both HITL checklists from Section 5.

**Tool usage**:
- Steps 1–5: `Write` and `Edit` tools (direct authoring).
- Steps 6 and 7: prepare handoff for user; do not invoke any skill or run any script under skill-creator's umbrella.
- Verification commands in Section 12 are for the user's manual spot-check; the canonical run happens inside skill-creator during user-driven Invocation B.

---

## 1. Context

The repo currently contains two generic, validator-clean marketing skills (`skills/draft-content/`, `skills/brand-review/`) plus generic `brand/voice.md` and `brand/style-guide.md` templates. Echo Theory Labs needs these skills tuned to a specific voice, audience, and content strategy before they can be used to ship real content. The vision file at `echo-theory-labs-vision.md` is the source material.

Phase 1 prioritizes the smallest set of changes that lets Echo:
- Draft a publishable Echo-voiced blog post from a brief.
- Draft a publishable Twitter/X post linked to that blog.
- Audit existing copy against Echo's voice, style, and a tightened compliance rubric.

Phase 1 is also designed to be **easy to evaluate, measure, and optimize** — fewer files, tighter rubrics, synthetic fixtures, and `skill-creator` as the optimization driver.

---

## 2. Echo positioning (locked for Phase 1)

This positioning is the input to all `brand/*` content. Captured here so the spec is self-contained.

### Three research pillars
- **Agent Harness Engineering** — instruction architecture, meta harness, self-improving agents, memory systems, attention budget management, compaction strategies, just-in-time context loading. (Encompasses what was previously framed as "context engineering"; broader scope.)
- **Evaluation Engineering** — domain-specific rubrics, benchmarks, LLM-as-judge pipelines, trajectory analysis, CI/CD-integrated agent testing, drift detection.
- **Adversarial Defense** — prompt injection hardening, agent identity governance, AI supply chain security, MCP audits, red-teaming.

### Three delivery capabilities
- Bare-Metal Orchestration — multi-agent systems on raw provider APIs.
- Observability & Runtime — production monitoring, traces, sandboxing, containment.
- Generative UI — agent-driven interface patterns beyond chat.

### Internal practice
Autonomous Workers and Dogfooding — Echo runs its own marketing/SEO/lead-gen on the same agent reliability framework it sells.

### Voice signals (extracted from vision prose)
- Declarative and category-defining ("the engineering discipline barely exists", "Applied Agentics").
- Evidence-led — third-party citations (Gartner, Deloitte, LangChain) inline.
- Technical-peer authority — speaking to CTOs and engineering leaders, not generalists.
- Contrarian by data, not by attitude.
- Anti-hype — short authoritative sentences, no exclamation marks, no superlatives without evidence.

### Audience
Primary: CTOs, heads of AI engineering, platform leads at orgs running production AI systems and feeling pain.
Secondary: senior individual contributors (staff/principal eng) who influence those CTOs.

### Anti-patterns
- Hype superlatives without evidence ("industry-leading", "best-in-class", "most advanced").
- Fake-personal-story openers ("Last quarter our team was spending 20 hours...").
- Lead-gen CTAs ("Start your free trial", "No credit card required").
- "We're excited to announce" energy.
- Disparaging competitors by name.
- Exclamation marks in any production copy.

---

## 3. Phase 1 file roster

### Author / edit (executing agent)

> **Terminology note**: "Agent Harness Engineering" (abbreviated AHE in some rows below) is the locked Echo pillar name; it supersedes the older "context engineering" framing entirely. Anywhere this spec mentions AHE, use "Agent Harness Engineering" verbatim in the authored content.

| Action | File | Notes |
|---|---|---|
| Rewrite | `brand/voice.md` | <80 lines. Echo-customized from vision: personality, 3 attributes, audience pointer, 3 pillars, tone matrix (blog + twitter only), pointer to anti-patterns. Replace all existing generic content. |
| Author | `brand/facts.md` (new) | <50 lines. Pillars (Agent Harness Engineering, Evaluation Engineering, Adversarial Defense), capabilities, internal practice, "what Echo is not" |
| Author | `brand/personas.md` (new) | <40 lines. 2–3 personas, tight paragraphs |
| Author | `brand/anti-patterns.md` (new) | <30 lines. Bulleted "never" list with one-line rationale per item |
| Rewrite | `brand/style-guide.md` | Replace existing generic version. Add Echo-specific terminology (Applied Agentics, Agent Harness Engineering, etc.) and capitalization rules. Universal grammar/style defaults can be carried over. |
| Edit | `skills/draft-content/SKILL.md` | Trim channel set to blog + twitter; reference `brand/facts.md`, `personas.md`, `anti-patterns.md` in addition to voice.md and style-guide.md |
| Edit | `skills/brand-review/SKILL.md` | Add references to `brand/facts.md`, `personas.md`, `anti-patterns.md` so the review skill can flag voice/positioning drift, not just style and compliance |
| Edit | `skills/draft-content/references/channel-blog.md` | Research-grade tone, citation expectations, headline declarativeness, length norms |
| Edit | `skills/draft-content/references/channel-social-twitter.md` | AI R&D community discourse, link-to-blog idiom, evidence-first hooks |
| Edit | `skills/draft-content/references/seo-patterns.md` | Echo keyword strategy (practice-area naming, Applied Agentics, Agent Harness Engineering) |
| Edit | `skills/draft-content/references/headline-patterns.md` | Declarative and contrarian formulas; remove generic listicle dominance |
| Edit | `skills/draft-content/references/cta-patterns.md` | Research-distribution CTAs only; explicit replacement of lead-gen patterns |
| Edit | `skills/brand-review/references/legal-compliance.md` | Citation rigor + AI-hype-superlative flags + fake-personal-story flag. Reference `brand/anti-patterns.md` for the canonical "never" list (this file must exist before legal-compliance.md is edited). |
| **Leave unchanged** | `skills/brand-review/references/review-rubric.md` | Generic structural rubric — severity definitions and output format. No Echo-specific content belongs here. |
| **Leave unchanged** | `skills/brand-review/references/voice-doc-framework.md` | Generic framework for *authoring* a voice document. Echo's voice is now authored in `brand/voice.md`; the framework remains useful for future voice revisions and is not Echo-flavored. |

### Delete (out of Phase 1 scope)

| File | Reason |
|---|---|
| `skills/draft-content/references/channel-social-linkedin.md` | Phase 2 — Echo voice on LinkedIn deferred |
| `skills/draft-content/references/channel-social-instagram.md` | Audience mismatch; likely never restored |
| `skills/draft-content/references/channel-social-facebook.md` | Same |
| `skills/draft-content/references/channel-email.md` | Phase 2 — research-distribution variant deferred |

### Eval data (executing agent, data only)

| File | Purpose |
|---|---|
| `evals/rubrics/draft-content.md` | 5 binary checks |
| `evals/rubrics/brand-review.md` | 5 binary checks |
| `evals/fixtures/draft-content-briefs/` (3 briefs) | Synthetic Echo-domain briefs |
| `evals/fixtures/brand-review-inputs/` (3 deliberately-flawed drafts) | Each carries a known set of rubric-targeted issues |

### NOT authored by the executing agent
- No eval orchestration scripts, no harness, no scoring code. `skill-creator` owns iteration. The executing agent's contribution to eval is data only (rubrics + fixtures).

---

## 4. Division of labor

> **HITL boundary**: The executing agent **does not invoke `document-skills:skill-creator` directly**. The agent prepares the invocation prompts (per Section 5) and hands them off to the user. The **user** invokes `skill-creator` and serves as the human-in-the-loop reviewer for skill-creator's outputs (refinement diffs, LLM-as-judge scores, iteration decisions, validation/packaging results). This applies to every skill-creator invocation in this spec without exception.

| Domain | Authoring owner | Invocation owner | Rationale |
|---|---|---|---|
| `brand/*` content (voice, facts, personas, anti-patterns, style-guide edits) | Agent | n/a (no skill-creator involvement) | Project config — outside skill-creator's scope |
| `evals/rubrics/*`, `evals/fixtures/*` | Agent | n/a (no skill-creator involvement) | Data, not skill content |
| `skills/draft-content/*` and `skills/brand-review/references/legal-compliance.md` content optimization | `skill-creator` | **User** (HITL) | Agent prepares the prompt; user invokes skill-creator and reviews its refinements |
| Validation (`quick_validate.py`) | `skill-creator` (during user-driven Invocation B) | **User** (HITL) | User invokes skill-creator, which runs the script as part of its own workflow |
| Packaging (`package_skill.py`) | `skill-creator` (during user-driven Invocation B) | **User** (HITL) | Same |
| Iteration loop (run skill on fixtures, score against rubrics, patch, repeat) | `skill-creator` (with rubrics + fixtures as guidance in the prompt) | **User** (HITL) | Maps to skill-creator's Step 6 "Iterate based on real usage"; user reviews each round and approves continue/escalate decisions |

---

## 5. skill-creator integration

Two scoped invocations during execution. The executing agent does **not** invoke skill-creator. The agent's deliverable for steps 6 and 7 of the execution sequence is a **handoff packet** for the user containing: the invocation prompt below (verbatim, with concrete repo-absolute file paths substituted), a one-paragraph context summary, and a checklist of what the user should review when skill-creator returns. The user runs skill-creator (HITL) and decides when results are acceptable.

### Invocation A — refinement (after seed authoring)

**Agent action**: produce this handoff for the user.

**Prompt to provide to the user (paste verbatim into `Skill: document-skills:skill-creator`)**:

> *"I have two existing skills at `<absolute path>/skills/draft-content/` and `<absolute path>/skills/brand-review/`, customized for Echo Theory Labs (a research-grade applied AI lab). Brand context lives in `<absolute path>/brand/voice.md`, `brand/facts.md`, `brand/personas.md`, `brand/anti-patterns.md`, `brand/style-guide.md`.*
>
> *Please apply your skill-writing guidelines to refine: (a) each SKILL.md's frontmatter description for trigger clarity and non-ambiguity, (b) each SKILL.md body for token efficiency and progressive disclosure, (c) reference files for specialization and complementarity. Do not invent new content. Flag redundancy or ambiguity across files. Do not modify `brand/*` or `evals/*` — those are out of scope for skill-creator. Surface every proposed change as a diff for human review before writing it."*

**HITL review checklist for the user after Invocation A returns**:
- [ ] Each proposed SKILL.md description still triggers correctly on Echo's intent (no overreach, no underreach).
- [ ] No `brand/*` or `evals/*` files were touched.
- [ ] Refinement preserves all Echo-specific terminology (Applied Agentics, Agent Harness Engineering, etc.).
- [ ] Final report contains no unresolved redundancy/ambiguity flags.

### Invocation B — eval iteration (after refinement)

**Agent action**: produce this handoff for the user.

**Prompt to provide to the user (paste verbatim into `Skill: document-skills:skill-creator`)**:

> *"Drive Step 6 (iterate based on real usage) for both skills at `<absolute path>/skills/draft-content/` and `<absolute path>/skills/brand-review/`. Use `<absolute path>/evals/rubrics/draft-content.md` and `evals/rubrics/brand-review.md` as success criteria. Use the fixtures in `<absolute path>/evals/fixtures/` as test inputs.*
>
> *For each fixture: simulate using the skill, evaluate output against the binary rubric checks (you, skill-creator, are the LLM-as-judge for these binary checks), identify failures, propose patches to SKILL.md or references, surface the patches for the user's HITL review, then apply approved patches and repeat. The user is the final arbiter on every iteration round; do not auto-apply changes without user confirmation.*
>
> *Iteration cap: maximum 5 iteration rounds per skill. If a check still fails after 5 rounds, stop and surface the failing (fixture, check) pair plus your final patch attempt to the user for resolution rather than continuing to patch. Do not modify `brand/*` or `evals/*` under any circumstance — those files are out of scope for skill-creator.*
>
> *After all checks pass (or after escalation), run `quick_validate.py` and `package_skill.py` per Step 5. Report results inline to the user; no separate eval log file is written in Phase 1."*

**HITL review checklist for the user during/after Invocation B**:
- [ ] Each proposed patch is reviewed before being applied to skill files.
- [ ] LLM-as-judge scores look defensible against the binary rubric wording (if not, the rubric is the lever to adjust — see Section 6).
- [ ] Iteration cap is honored; user explicitly decides escalate-vs-retry on stuck checks.
- [ ] `quick_validate.py` and `package_skill.py` results are surfaced and acceptable.
- [ ] No `brand/*` or `evals/*` files were touched.

### Boundaries
- The executing agent **never invokes skill-creator** — it only prepares prompts and review checklists for the user.
- The user invokes skill-creator and is the human-in-the-loop reviewer for every output.
- skill-creator is told **explicitly** not to touch `brand/*` or `evals/*`.
- skill-creator drives optimization, iteration, validation, packaging — but its proposed changes pass through user review before being committed to skill files.

---

## 6. Eval rubrics (locked for Phase 1)

Both rubrics use binary pass/fail per check. No partial credit, no weighted scoring.

### `evals/rubrics/draft-content.md` — 5 checks
1. Voice attributes from `brand/voice.md` are visible in a blind read (declarative, evidence-led, technical-peer).
2. No items from `brand/anti-patterns.md` appear in the output (no hype superlatives, no fake-personal openers, no "we're excited", no exclamation marks).
3. Headline matches a declarative or contrarian formula from `headline-patterns.md`, not a generic listicle.
4. **Blog only**: primary keyword appears in headline + first paragraph + meta description.
5. **Twitter/X only**: voice fits AI R&D community discourse — evidence-led hook, not generic punchy marketing; if linking to a blog, the link convention from `channel-social-twitter.md` is followed.

(Checks 4 and 5 are channel-specific. A blog-channel run is scored on 1, 2, 3, 4. A Twitter run is scored on 1, 2, 3, 5. Each fixture indicates its channel.)

### `evals/rubrics/brand-review.md` — 5 checks
1. Flags hype superlatives without evidence ("industry-leading", "best-in-class").
2. Flags lead-gen CTAs in research contexts; flags exclamation marks in production copy; flags named-competitor disparagement.
3. Flags fake-personal-story openers and "we're excited" energy.
4. Flags stripped, broken, or fabricated citations on stat claims.
5. **Structural cross-cut** (verified across the fixture set, not by a dedicated fixture): compliance issues are routed to the compliance section rather than detailed findings, and severity grading is internally consistent (not all-High, not all-Low; calibrated to severity definitions in `review-rubric.md`).

**How rubric checks are scored**: skill-creator (acting as LLM-as-judge) produces binary pass/fail scores against these checks during Invocation B. Pass = the check is observed in the skill's output for the fixture. Fail = it is not. The **user (HITL)** reviews skill-creator's scores and patches each round; if scores feel miscalibrated, the lever to adjust is the rubric wording itself, not re-scoring by hand. The user is the final arbiter on whether a round's results are acceptable.

---

## 7. Eval fixtures (synthetic, Echo-domain)

Fixtures are synthetic Echo-domain content. They test the skills on topics Echo *could* publish but is not currently drafting. The user's real blog drafts are held out for manual testing later — never used as Phase 1 fixtures.

### Brief schema (mandatory for all `draft-content-briefs/` fixtures)

Each brief is a markdown file with this exact 5-field structure:

```
# <brief title>

- **Topic**: <one-sentence subject>
- **Audience**: <persona name from brand/personas.md>
- **Key messages**: <2–4 bullet points>
- **Length**: <word count or character constraint>
- **Channel**: <blog | twitter>
```

No additional sections. This schema removes ambiguity about what a "brief" contains so two agents would write substantively similar fixtures.

### `evals/fixtures/draft-content-briefs/` (3 briefs)

- `brief-01-agent-eval-failure.md` — channel: blog. Topic: "Why most agent evaluation pipelines fail under production load."
- `brief-02-naming-trajectory-analysis.md` — channel: blog. Topic: "Naming the practice: trajectory analysis as a discipline."
- `brief-03-mcp-hardening-twitter.md` — channel: twitter. Topic: "Three things teams get wrong about MCP server hardening." (As a Twitter/X thread of 4–6 tweets, with link-to-blog convention.)

### `evals/fixtures/brand-review-inputs/` (3 deliberately flawed drafts)

Each is a synthetic Echo-domain blog draft (~400–600 words) seeded with a quantified set of rubric-targeted issues. The seed counts are explicit so the agent authoring fixtures has no room to under-seed:

- `flawed-01-hype-superlatives.md` — seed exactly 5 unsubstantiated superlatives ("industry-leading", "best-in-class", "most advanced", "unparalleled", "#1"). Tests rubric check 1.
- `flawed-02-lead-gen-and-fake-personal.md` — seed exactly 1 fake-personal-story opener, 2 lead-gen CTAs, 1 "we're excited to announce" line, and 1 named-competitor disparagement. Tests checks 2 + 3.
- `flawed-03-citation-issues.md` — seed exactly 3 stat claims with stripped citations and 1 fabricated statistic with an invented source name. Tests check 4.

Rubric check 5 (structural cross-cut on routing and severity calibration) is verified by examining all three flawed-draft review outputs together; no dedicated fixture is required.

---

## 8. Execution sequence

> **Tool note**: Steps 1–5 are direct authoring by the agent using `Write`/`Edit`. Steps 6 and 7 are **HITL handoffs** — the agent prepares the invocation prompt and review checklist (per Section 5) and presents them to the user. The **user invokes `Skill: document-skills:skill-creator`** with the prepared prompt; the agent does not invoke skill-creator itself. After the user runs skill-creator and reports back results, the agent resumes (e.g., with patches the user approves, or with the next handoff). This boundary holds for every skill-creator invocation in the spec — there are no exceptions.

1. **Rewrite `brand/voice.md`** and **edit `brand/style-guide.md`** in place. Then **author** `brand/facts.md` (with Agent Harness Engineering as the pillar name), `brand/personas.md`, and `brand/anti-patterns.md`. The five files within step 1 are independent of each other and may be authored in any order. The only cross-step constraint: `brand/anti-patterns.md` must exist before step 5 edits `legal-compliance.md`, since `legal-compliance.md` references it.
2. **Author `evals/rubrics/draft-content.md` and `evals/rubrics/brand-review.md`** with the 5 checks each from Section 6.
3. **Author `evals/fixtures/draft-content-briefs/`** — 3 briefs using the schema from Section 7.
4. **Author `evals/fixtures/brand-review-inputs/`** — 3 flawed drafts with the exact seed counts from Section 7.
5. **Edit seed skill content** — in this order:
   1. First, edit `skills/draft-content/SKILL.md` and `skills/brand-review/SKILL.md` to remove references to channels that will be deleted, and to add references to Echo brand files.
   2. Then edit channel-blog.md, channel-social-twitter.md, seo-patterns.md, headline-patterns.md, cta-patterns.md, and `skills/brand-review/references/legal-compliance.md`.
   3. Then **delete** the out-of-scope channel files (channel-social-linkedin.md, channel-social-instagram.md, channel-social-facebook.md, channel-email.md).
   4. **Verify** with `grep -r "channel-social-linkedin\|channel-social-instagram\|channel-social-facebook\|channel-email" skills/` — must return no matches before proceeding.
6. **Hand off Invocation A to the user** — agent assembles the prompt and review checklist from Section 5 (Invocation A), substitutes the absolute repo paths, and presents the handoff. **User invokes `Skill: document-skills:skill-creator`** with that prompt. User reviews skill-creator's proposed refinements and approves/rejects them; agent applies approved changes to skill files. Step 6 is complete only when the user confirms refinement is acceptable per the Invocation A HITL checklist.
7. **Hand off Invocation B to the user** — agent assembles the prompt and review checklist from Section 5 (Invocation B), substitutes paths, and presents the handoff. **User invokes `Skill: document-skills:skill-creator`** for eval iteration + validation + packaging. The user is the HITL reviewer for every iteration round; the 5-iteration cap is honored; the user explicitly decides escalate-vs-retry on stuck checks. Step 7 is complete only when the user confirms results meet exit criteria per the Invocation B HITL checklist.
8. **Done** when Phase 1 exit criteria (Section 9) are met **and the user has signed off on both HITL checklists from Section 5**.

---

## 9. Phase 1 exit criteria

All of the following must hold:

- All applicable `draft-content` rubric checks pass on every brief fixture (checks 1, 2, 3, plus 4 for blog briefs or 5 for twitter briefs).
- The rubric checks mapped to each `brand-review` flawed-draft fixture in Section 7 pass (flawed-01 → check 1; flawed-02 → checks 2 + 3; flawed-03 → check 4); check 5 is verified across the fixture set as a whole.
- `quick_validate.py` reports "Skill is valid!" for both skills.
- `package_skill.py` produces `.skill` files for both skills without errors.
- skill-creator's final refinement report (from Invocation A) lists no unresolved flags for redundancy or ambiguity.
- The user has explicitly signed off on both HITL review checklists (Invocation A and Invocation B) defined in Section 5.
- No Echo-specific content appears outside `brand/`, `evals/fixtures/`, and this spec. Skill files remain reusable for non-Echo projects (Echo-flavored only via `brand/` config).

---

## 10. Future phases (not authored in Phase 1)

### Phase 2 — channel expansion (after Phase 1 evaluated and stable)
- `channel-social-linkedin.md` (Echo voice — technical-peer, not generic professional)
- `channel-research-note.md` (long-form methodology and audit framework distribution)
- `channel-case-study.md` (core to Echo's "publishing is authority" strategy)
- `channel-email.md` (research-distribution variant, not promo newsletter)
- `brand/citation-policy.md` (formalize citation conventions)
- `brand/context.md` (current campaigns, embargoes, time-bound initiatives)

### Phase 3 — likely never
- `channel-social-instagram.md`, `channel-social-facebook.md` — audience mismatch.

### Carried as eval evolution
- Add Echo's real blog drafts as held-out test inputs for spot-checking, separately from Phase 1 fixtures.
- Consider per-persona rubric variants if persona-specific quality drift emerges.
- Consider deterministic scripts (terminology checker, readability scorer) only if a fragile check repeatedly fails in iteration.

---

## 11. Critical files referenced

Define `$SC = /Users/shubh/.claude/plugins/cache/anthropic-agent-skills/document-skills/69c0b1a06741/skills/skill-creator` for shorthand throughout.

- `echo-theory-labs-vision.md` — input data for all `brand/*` authoring
- `skills/draft-content/SKILL.md`, `skills/brand-review/SKILL.md` — current generic skills (will be edited)
- `brand/voice.md`, `brand/style-guide.md` — current generic templates (will be rewritten)
- skill-creator skill root: `$SC/`
- skill-creator validator: `$SC/scripts/quick_validate.py`
- skill-creator packager: `$SC/scripts/package_skill.py`

Note: skill-creator scripts are invoked **by skill-creator itself** during user-driven Invocation B. The executing agent does not invoke skill-creator or run these scripts directly. The user (HITL) may run them as a manual spot-check at any time, but the canonical run happens inside Invocation B under user oversight.

---

## 12. Verification (run inside user-driven Invocation B; commands shown for HITL spot-check)

- `python3 $SC/scripts/quick_validate.py skills/draft-content` → must report "Skill is valid!"
- `python3 $SC/scripts/quick_validate.py skills/brand-review` → must report "Skill is valid!"
- `python3 $SC/scripts/package_skill.py skills/draft-content` → must produce `draft-content.skill`
- `python3 $SC/scripts/package_skill.py skills/brand-review` → must produce `brand-review.skill`
- All rubric checks pass on all fixtures (per skill-creator's iteration report from Invocation B, surfaced to and signed off by the user).

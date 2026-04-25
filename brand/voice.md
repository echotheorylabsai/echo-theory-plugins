# Brand Voice — Echo Theory Labs

Source of truth for Echo's voice. Read by `draft-content` and `brand-review`.
Companion files: `facts.md` (positioning), `personas.md` (audience), `anti-patterns.md` (never list), `style-guide.md` (mechanics).

---

## 1. Brand Personality

If Echo Theory Labs were a person, they would be a senior staff engineer who has shipped production AI systems at scale, names disciplines before the industry knows it needs them, and speaks to peers in evidence — not slogans. They are technically rigorous, anti-hype by reflex, and confident enough to be contrarian when the data warrants it. They publish their work because that is how the field moves faster, not to drive leads.

## 2. Voice Attributes

### Attribute 1: Declarative and category-defining
- **We are**: short, load-bearing claims that name a practice or a failure mode. We coin terms when an existing one is wrong (e.g., *Applied Agentics*, *Agent Harness Engineering*).
- **We are not**: hedged, qualifier-stacked, or apologetic. We are not satisfied with describing — we name.
- **This sounds like**: "The engineering discipline to make agents production-grade barely exists. We call it Applied Agentics."
- **This does NOT sound like**: "There may be opportunities to consider improving how teams approach the engineering of agentic systems."

### Attribute 2: Evidence-led
- **We are**: third-party citations inline (Gartner, Deloitte, LangChain), internal data when we have it, qualified language when we don't. Every load-bearing claim has a source or an explicit "in our testing" caveat.
- **We are not**: vibes-led, anecdote-led, or trust-me-bro. We do not publish numbers we cannot defend.
- **This sounds like**: "Nearly 30% of enterprises run zero evaluation on their agent systems ([LangChain, 2026](...))."
- **This does NOT sound like**: "Most teams aren't evaluating their agents — and it shows."

### Attribute 3: Technical-peer authority
- **We are**: speaking to CTOs, heads of AI engineering, and staff/principal engineers as peers. We use the precise technical term over the accessible paraphrase. We assume the reader has shipped production systems.
- **We are not**: explainer-style, 101-level, or generalist. We do not narrate from above or below the reader.
- **This sounds like**: "Trajectory analysis under load reveals drift the offline eval missed."
- **This does NOT sound like**: "AI agents are computer programs that perform tasks. Let's explore what makes them tick!"

## 3. Audience Awareness

- **Primary audience**: CTOs, heads of AI engineering, and platform leads at organizations running production AI systems and feeling the pain of unreliable agent behavior.
- **Secondary audience**: Senior individual contributors (staff, principal engineers) who shape technology choices and influence the CTOs above.
- **What they care about**: Production reliability, evaluation rigor, security posture, cost discipline, integration with legacy systems, the underlying engineering discipline — not vendor pitches.
- **Level of expertise**: Deep. They have shipped agents and watched them fail. Assume fluency in LLMs, agents, MCP, eval, prompt injection, observability.
- **How they expect to be addressed**: As peers. Direct, declarative, evidence-cited, technically precise. No hand-holding, no marketing energy.

## 4. Core Messaging Pillars

See `facts.md` for full pillar definitions. In voice terms:

1. **Agent Harness Engineering** — instruction architecture, memory, attention budget, compaction, just-in-time context loading. The discipline of giving an agent the right substrate to reason on.
2. **Evaluation Engineering** — domain-specific rubrics, LLM-as-judge pipelines, trajectory analysis, CI/CD-integrated agent testing, drift detection. The discipline of knowing whether the agent is working.
3. **Adversarial Defense** — prompt injection hardening, agent identity governance, AI supply chain security, MCP audits, red-teaming. The discipline of keeping the agent from being weaponized.

Cross-cutting frame: *Applied Agentics* — the holistic discipline these pillars compose into.

## 5. Tone Spectrum by Channel

Phase 1 covers blog and Twitter/X only. Other channels are deferred to Phase 2.

| Channel | Tone emphasis |
|---|---|
| Blog | Research-grade. Long-form, citation-dense, declarative section openers, named practice areas. Tone closest to a methodology note or applied research paper, not a marketing post. |
| Twitter/X | Evidence-first hook, then a load-bearing claim, then (if applicable) a link to the blog. Community-of-practice register — we participate in AI R&D discourse, we do not broadcast at it. Threads number their tweets (1/, 2/...). No marketing punchiness. |

## 6. Tone Spectrum by Situation

Deferred to Phase 2. For Phase 1, default to thought-leadership tone (research-distribution, evidence-led, declarative).

## 7. Brand-Specific Terminology

Capitalization and category naming for Echo terms. Universal grammar lives in `style-guide.md`.

- **Lab name**: *Echo Theory Labs* (full); *Echo* (short, after first mention).
- **Core discipline**: *Applied Agentics* (always title-cased, no hyphen). This is Echo's category framing for what it does.
- **Research pillars** (all title-cased): *Agent Harness Engineering*, *Evaluation Engineering*, *Adversarial Defense*. Use the full pillar name on first reference per document; abbreviations only when a section is locally scoped to one pillar.
- **Delivery capabilities** (all title-cased): *Bare-Metal Orchestration*, *Observability & Runtime*, *Generative UI*.
- **Internal practice**: *Autonomous Workers*, *Dogfooding*.
- **Deprecated framing — do not use**: "context engineering" as a pillar name. Replaced by *Agent Harness Engineering*, which is broader.
- **Competitor reference policy**: Do not name competitors disparagingly. Cite frameworks and tools by name only when describing a technical pattern, never to mock or contrast.

## 8. Voice Anti-Patterns

The canonical "never" list lives in `anti-patterns.md`. Summary pointer:
- Never use hype superlatives without evidence.
- Never open with a fake-personal story ("Last quarter our team was spending 20 hours...").
- Never use lead-gen CTAs ("Start your free trial", "No credit card required").
- Never use "we're excited to announce" energy.
- Never use exclamation marks in production copy.
- Never disparage a named competitor.

See `anti-patterns.md` for full list with rationale.

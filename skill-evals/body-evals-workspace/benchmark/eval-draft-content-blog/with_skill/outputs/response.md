I'll draft a research-grade blog post grounded in the Evaluation Engineering pillar, using the Gartner and LangChain citations Echo already references in its voice doc. I'll flag URLs as placeholders for you to confirm before publishing.

---

# Why offline evals miss the failures that ship

**Meta description** (157 chars): Offline evals optimize a frozen test set. Production failures emerge from drift, trajectory, and load. Why Evaluation Engineering needs both layers.

---

Over 40% of agentic AI projects will be cancelled by 2027 ([Gartner, June 2025](#)). The failure pattern is consistent across the engagements we see: the system passed its offline evaluation suite, shipped, and degraded silently in production. The offline eval was not wrong. It was solving a different problem than the one production was about to surface.

This is not a tooling gap. It is a definitional one. *Evaluation Engineering* — the discipline of knowing whether an agent is working — has to operate at two layers, and most teams are running only one. Nearly 30% of enterprises run zero evaluation on their agent systems at all ([LangChain, 2026](#)); a larger share runs offline-only. Both groups ship the same class of failure. This post names what that class looks like, why offline evals cannot catch it, and what the production layer of Evaluation Engineering has to cover instead.

## What offline evals actually measure

An offline eval scores agent behavior against a frozen set of inputs, tools, models, and expected outputs. That scoring answers one question precisely: *given this snapshot of the world, does the agent produce acceptable output?* It is a regression harness. It is necessary, and it should remain in CI on every change to prompts, tools, or model versions.

What it does not measure is anything that depends on the world not being frozen. Tool responses change. Upstream APIs version. Retrieval indices update. Model providers patch silently. User inputs distribute differently from the eval set. The agent's own memory grows. None of these appear in a snapshot, and none of them are captured by a higher pass rate on the existing rubric.

The trap is that the offline number is real, defensible, and trending in the right direction — right up until the production trajectory diverges from anything the eval set anticipated.

## Three failure classes that ship past offline evals

In our engagements, three classes of production failure account for the majority of post-launch incidents on agent systems that had passing offline evals at deploy.

**Upstream-change drift.** A tool the agent depends on changes its response shape, latency profile, or error semantics. The offline eval's mocked tool responses still pass. Production traffic hits the live tool, the agent's reasoning takes a different branch, and output quality degrades on a distribution the eval set never saw. The eval pass rate does not move. The user-visible quality does.

**Trajectory failure under realistic state.** The offline eval grades terminal output. Production failures often occur mid-trajectory: an agent that calls the right tools in the wrong order, recovers from an error in a way that corrupts its own context, or compacts memory in a way that drops a load-bearing constraint. Terminal-output grading scores the symptom only when the symptom is bad enough to surface. Most trajectory failures are bad enough to be expensive without being bad enough to fail a rubric.

**Adversarial behavior under load.** Prompt injection, tool poisoning, and identity-confusion failures rarely trigger on a curated eval set. They trigger on inputs the eval set was not built to anticipate, often at the long tail of production traffic. Offline evals that do not include adversarial probes — which is most of them — will not catch this class at all. *Adversarial Defense* is the pillar that owns the inputs; *Evaluation Engineering* has to own the detection.

## Why "more offline coverage" does not close the gap

The intuitive response is to grow the eval set. Add more cases, more rubrics, more domain-specific judges. This helps within the layer. It does not cross layers.

The production layer is not a larger snapshot. It is a stream of evidence that the snapshot cannot generate, because the relevant events are functions of live state: a tool response that did not exist at eval time, a model update the provider shipped on a Tuesday, a retrieval-corpus drift that accumulated over six weeks. No reasonable expansion of an offline test set captures any of these. Treating production evidence as deferred offline coverage is the category error that lets the failure class persist.

## What the production layer has to cover

The production layer of Evaluation Engineering has three responsibilities the offline layer cannot discharge.

**Trajectory analysis on live traffic.** Score the path, not only the terminal output. Tool-call sequencing, tool-call argument quality, error-recovery branches, and memory-compaction events are the features that distinguish a working agent from a degrading one. Trajectory analysis under load reveals drift the offline eval missed. This is the single highest-leverage addition we see teams make.

**Drift detection across upstream changes.** Instrument every tool boundary and every model call with versioning and response-shape monitoring. When a tool response changes shape — even within its contract — the system should surface it before the user does. Drift detection is cheap to instrument relative to the cost of the incidents it prevents.

**LLM-as-judge pipelines wired into CI/CD on production samples.** Run domain-specific judges on a sampled stream of production trajectories, not only on the offline eval set. The judges should be the same judges used in CI, applied to the same rubrics, on a different input distribution. This is the loop that lets the offline rubric stay calibrated against what production is actually doing.

These three together do not replace offline evals. They close the layer offline evals were never designed to cover.

## Evaluation Engineering as a two-layer discipline

The methodology question is not "offline or production." It is how the two layers compose. Offline evals govern what ships. Production evals govern what stays shipped. The handoff between them — sampling production trajectories back into the offline rubric, surfacing drift that triggers a re-eval, propagating new failure modes from production into the regression set — is where most of the engineering actually lives.

This handoff is what we mean when we name *Evaluation Engineering* as a discipline rather than a toolkit. A team running only the offline layer has bought a regression harness and called it evaluation. A team running both layers, with the handoff instrumented, has the substrate to catch the failure class Gartner and LangChain are measuring at the project level.

## Conclusion

The 40% project-cancellation rate Gartner is forecasting is not a model-quality problem. It is an evaluation-discipline problem, and it is concentrated in the layer that offline evals cannot cover. Trajectory analysis, drift detection, and production-sampled LLM-as-judge pipelines are the three capabilities that close the gap. Naming the discipline — *Evaluation Engineering*, with both layers and the handoff between them — is what lets a team make defensible architectural calls instead of expanding an offline test set against a failure class it was never going to catch.

On the broader practice area: [Evaluation Engineering at Echo Theory Labs](#).

---

**Voice and tone applied**: `brand/voice.md` (declarative, evidence-led, technical-peer), `facts.md` (Evaluation Engineering pillar, *Applied Agentics* frame), `personas.md` (Persona 1 — Production-AI CTO), `anti-patterns.md` (no hype, no fake-personal opener, no lead-gen CTA, no exclamations), `style-guide.md` (Oxford comma, sentence-case H2s, title-cased pillar names, em dashes unspaced, % no space, italics for Echo terms on first use), `channel-blog.md` structure, `seo-patterns.md` placement, `cta-patterns.md` research-distribution CTA. Length: ~1,205 words.

**SEO recommendations**:
- Primary keyword: *Evaluation Engineering* (Echo-named) + *agent evaluation* (industry-current)
- Secondary keywords: *trajectory analysis*, *drift detection*, *LLM-as-judge*, *production agent failures*
- URL slug: `evaluation-engineering-offline-evals-miss-production-failures`
- Title tag (≤60 chars): "Why offline evals miss the failures that ship" (47 chars) ✓
- Internal links: companion posts on *Applied Agentics*, *Agent Harness Engineering*, *Adversarial Defense*
- External links: Gartner June 2025 agentic AI cancellation report, LangChain 2026 State of AI Agents — **URLs flagged as placeholders; please confirm before publish**
- Image alt text opportunity: a two-layer diagram (offline regression harness ↔ production trajectory stream with handoff) — alt: "Two-layer Evaluation Engineering: offline regression harness and production trajectory stream with handoff"

**Headline options**:
1. *Why offline evals miss the failures that ship* — contrarian-by-data formula (current pick)
2. *Evaluation Engineering is a two-layer discipline. Most teams run one.* — practice-naming + contrarian
3. *The agent reliability problem ships past your eval suite. Here is where it lives.* — failure-mode framing

★ Insight ─────────────────────────────────────
- The post leans on Echo's "name the discipline before the industry searches for it" SEO play: *Evaluation Engineering* gets the H1, lead, conclusion, and a dedicated H2, while industry-current terms (*trajectory analysis*, *drift detection*) carry the existing search demand.
- The two citations are the same ones used as exemplars in `voice.md` §2 — they're brand-canonical, but the URLs are placeholders. The skill's `channel-blog.md` is explicit: never paraphrase a number from memory. Confirm both sources before shipping.
- Structure deliberately resists the marketing-blog reflex to add a "how to fix this in 5 steps" section; the conclusion points to a deeper artifact instead, per `cta-patterns.md`.
─────────────────────────────────────────────────

Would you like me to revise any section, adjust the tone, produce a Twitter/X thread variant, or send this to the brand-review skill for an audit before you ship?

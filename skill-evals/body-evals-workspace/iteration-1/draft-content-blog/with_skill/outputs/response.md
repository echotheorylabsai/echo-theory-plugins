All brand config loaded. Drafting now — targeting Persona 1 (Production-AI CTO), blog channel, ~1,200 words, research-grade register.

`★ Insight ─────────────────────────────────────`
The brief's strongest tension: offline evals *feel* rigorous (they involve metrics, thresholds, datasets) but optimize for the wrong distribution. The evidence from Gartner and LangChain lands hardest when placed before the explanation—not after—because it reframes the reader's current practice as the problem, not a solution.
`─────────────────────────────────────────────────`

---

## Headline options

**A. Failure-mode formula (recommended)**
*Why offline evals miss the failures that ship to production*
(53 chars — fits title tag; primary keyword "agent evaluation" placed via synonymy)

**B. Contrarian-by-data formula**
*Offline evals are necessary. They are not sufficient.*
(53 chars — punchy, declarative; slightly higher click-friction for unfamiliar readers)

**C. Field-state assessment formula**
*The agent evaluation gap most teams cannot see until production*
(62 chars — slightly over 60; may need trimming for SEO)

---

## Draft

---

# Why offline evals miss the failures that ship to production

Over 40% of agentic AI projects will be cancelled or rolled back by 2027, and the failure pattern is consistent \([Gartner, June 2025]\[URL needed\]\). The systems do not fail in benchmarks. They fail in production—on real inputs, under concurrent load, after a tool-state change that the eval dataset predates. Nearly 30% of enterprises currently run zero systematic evaluation on their agent systems \([LangChain State of AI Agents, 2026]\[URL needed\]\); of the teams that do evaluate, most rely on offline evals run against static datasets before deployment. The failure modes driving production incidents rarely appear there. This post establishes why, and names the evaluation discipline that closes the gap.

---

## What offline evals actually test

An offline eval runs an agent against a fixed dataset—expected inputs, expected outputs, a scoring rubric—in a controlled environment before deployment. Done well, it catches obvious regressions and validates that a new model version does not catastrophically break the most common paths. This is necessary work.

It is also fundamentally incomplete as a reliability signal.

The conditions an offline eval controls for are precisely the conditions that production does not guarantee: stable upstream tool responses, consistent latency profiles, single-turn interactions with clean inputs, and an absence of concurrent load. Every one of these controlled variables is a source of production divergence. The eval passes because the eval was designed to pass—designed, that is, around a distribution that production traffic does not honor.

---

## The failure modes that escape the eval dataset

The production failure patterns we observe most consistently share a structural property: they are emergent under conditions that static eval datasets cannot model.

**Tool-state drift.** A downstream API changes its response schema, latency profile, or error semantics. The agent's reasoning path was optimized against prior tool behavior. The offline eval dataset predates the change. The agent degrades silently—producing plausible-looking outputs that are structurally incorrect—until a human or a monitoring alert catches it.

**Multi-turn trajectory collapse.** Single-turn evals score individual outputs. Multi-turn agent sessions accumulate state, and errors compound. A reasoning error at step three propagates to step seven, where it produces a plausible-looking but incorrect terminal output. Each individual step passes the rubric; the trajectory fails. Step-level scoring misses this class of failure by design.

**Distributional shift under real inputs.** Real user inputs—ambiguous, underspecified, adversarially structured, or domain-specific in ways the eval dataset does not cover—elicit behavior the static dataset never surfaced. The offline eval optimized against a curated distribution; production is a different one. The eval did not fail; it measured the wrong thing.

**Concurrent load effects.** Agent systems under concurrent load exhibit reasoning shortcuts, context truncation artifacts, and latency-sensitive failures that sequential eval runs do not produce. In our engagements, context compaction under load is one of the most frequent sources of silent output degradation—a failure class that does not appear in any offline eval because it is a function of concurrency, not input content.

**Model upgrade side effects.** Provider model upgrades change instruction-following behavior, tool-calling conventions, and reasoning depth in ways that are difficult to predict from first principles. Offline evals often catch the obvious regressions; they systematically miss the subtle distributional shifts in reasoning that accumulate across a session and manifest only in multi-turn or high-load conditions.

---

## What trajectory analysis surfaces

The evaluation signal missing from offline evals is not a better dataset. It is a different analysis layer: **trajectory analysis under production conditions**.

Trajectory analysis examines the full reasoning and action sequence of an agent session—not individual step scores. It identifies where reasoning chains diverge from expected paths, where tool failures silently reroute the agent, and where accumulated error in a multi-turn session produces a plausible-looking but incorrect terminal state.

Run against production traffic—or under synthetic production-representative load—trajectory analysis surfaces failure classes that static datasets structurally cannot:

- Reasoning steps that pass per-output scoring but accumulate toward an incorrect trajectory
- Tool-state changes that reroute agent behavior without triggering explicit error signals
- Context window pressure points where compaction decisions degrade reasoning quality
- Input distribution patterns in production traffic that are absent from the eval dataset

This is not a novel testing technique. It is the kind of testing that production reliability actually requires, applied to the layer—multi-step agent behavior over time—that offline evals omit.

---

## The *Evaluation Engineering* discipline

The industry's current evaluation practice maps roughly to what software engineering looked like before continuous integration: important quality gates run manually, on a fixed schedule, against curated inputs. Necessary, and insufficient.

The discipline that closes the gap is what we call *Evaluation Engineering*. It encompasses domain-specific rubric design calibrated to the task (not generic benchmarks), LLM-as-judge pipelines with measurable inter-rater reliability, trajectory-level scoring for multi-turn sessions, CI/CD-integrated agent testing, and production drift detection. It treats evaluation as a continuous runtime concern—not a pre-deployment checkpoint.

The gap is not primarily a tooling problem. The components for trajectory analysis and production monitoring exist today. It is a discipline gap: most teams have not formalized the evaluation engineering practice that makes production reliability a designed-for property rather than a post-incident finding. Nearly 30% of enterprises run zero systematic evaluation \([LangChain, 2026]\[URL needed\]\); of the remainder, production drift detection remains an uncommon practice despite being the failure class most likely to cause an incident.

---

## What this requires in practice

Closing the offline eval gap does not mean abandoning offline evals. It means extending the evaluation layer to cover what offline evals cannot:

- **Trajectory-level scoring** on multi-turn sessions, not only individual output scoring
- **Production traffic sampling** to identify distributional shift relative to the eval dataset
- **Synthetic load testing** that replicates concurrent request patterns and context pressure
- **Drift detection** on production output distributions across model upgrades and tool-state changes
- **CI/CD integration** that treats agent evaluation as a continuous signal, not a batch checkpoint

The teams making progress on production agent reliability are the ones treating evaluation as an engineering discipline with a defined scope—not a QA step with an eval dataset attached.

---

## Conclusion

Offline evals are a necessary baseline. The failures that actually ship are not in that baseline—they are in tool-state drift, multi-turn trajectory collapse, distributional shift, and concurrent load effects that static datasets do not model. Gartner's projection that 40%+ of agentic projects will be cancelled or rolled back by 2027 \([Gartner, June 2025]\[URL needed\]\) is downstream of this gap, not coincident with it. *Evaluation Engineering* is the discipline that addresses it—and it is a distinct engineering practice with its own scope, methods, and CI/CD integration requirements.

We are publishing the full *Evaluation Engineering* methodology, including trajectory analysis implementation patterns and a production drift detection checklist: \[link to methodology post\].

---

`★ Insight ─────────────────────────────────────`
The post places Gartner in the lead *and* the conclusion—a rhetorical bracket technique that's particularly effective for evidence-led content. The opening stat establishes stakes; the closing citation recasts it as a *consequence* of the specific practice gap just described, not just a scary number.
`─────────────────────────────────────────────────`

---

**Voice and tone applied:** `brand/voice.md` §2 (declarative, evidence-led, technical-peer), `brand/anti-patterns.md` (no lead-gen CTA, no fake-personal opener, no superlatives), `brand/style-guide.md` (sentence-case H2s, Oxford comma, numerals for stats, em-dashes unseparated), `brand/facts.md` (*Evaluation Engineering* as named pillar). Blog channel tone from `references/channel-blog.md`.

**SEO recommendations**
- **Primary keyword**: agent evaluation
- **Secondary keywords**: offline evals, trajectory analysis, production drift, LLM evaluation
- **Meta description (≤160 chars)**: `Offline evals miss the failure modes that ship to production. Here is why—and what the Evaluation Engineering discipline does instead. (~136 chars)`
- **URL slug**: `/blog/why-offline-evals-miss-production-failures`
- **Image alt text opportunity**: a diagram showing offline eval coverage vs. production failure mode distribution would fit above the "What trajectory analysis surfaces" section
- **Internal links**: 2–3 slots for future Echo posts on trajectory analysis methodology and drift detection
- **External links**: 2 \[URL needed\] placeholders to resolve—Gartner June 2025 and LangChain State of AI Agents 2026

**Two items need your input before this can ship:**

1. **Stat URLs** — the Gartner and LangChain citations are marked `[URL needed]`. Can you provide the source links, or should I add `[citation needed]` placeholders for the editorial team to resolve?
2. **CTA link** — "Full Evaluation Engineering methodology" points to `[link to methodology post]`. What's the destination URL or slug?

Would you like me to revise any section, adjust the tone, produce a Twitter/X thread version, or send this through the `brand-review` skill for an audit before you ship?

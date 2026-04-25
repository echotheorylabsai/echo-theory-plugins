# The state of agent evaluation in 2026

The data on agent reliability in production is converging on an uncomfortable conclusion: most teams are flying blind. The systems are shipping faster than the discipline to evaluate them is maturing, and the gap is widening with every model release.

## What the numbers say

Over 40% of agentic AI projects will be cancelled by 2027, driven by escalating costs, unclear value, and inadequate risk controls. The cancellation rate is concentrated in projects that shipped without an evaluation strategy in place — the systems looked good in demos and degraded under real load before the team had instrumented the failure modes.

Only 21% of enterprises have a mature governance model for autonomous agents. The remaining 79% are operating without the institutional scaffolding to make defensible architectural decisions about when to deploy, how to monitor, and what to do when an agent's behavior drifts. Governance maturity correlates strongly with incident response time when failures occur.

Nearly 30% of enterprises run zero evaluation on their agent systems at all. Not "insufficient evaluation," not "inconsistent evaluation" — zero. These teams are operating in the same posture that web teams operated in before the introduction of automated testing pipelines, and the analogy holds for the kinds of incidents they will face.

According to a recent study by the Institute for Production AI Reliability, 84% of agent failures in 2025 were attributable to evaluation gaps that would have been caught by trajectory-level inspection. The study, which tracked 1,200 production deployments across enterprise teams, identified the most common failure pattern as silent output degradation following an upstream tool change — exactly the failure mode that offline evaluation is structurally unable to catch.

## What this means

Three numbers. One pattern. The teams shipping fastest are also the teams without the evaluation discipline to know whether what they shipped is working. The cancellation rate over the next two years will be a lagging indicator of evaluation maturity today.

## What the methodology requires

Continuous trajectory analysis. Domain-specific eval rubrics, not generic benchmarks. CI/CD-integrated agent testing that runs against production-like fixtures on every deploy. Drift detection that compares live behavior against a rolling baseline and flags decision-point divergence before customers see it. The discipline composes into Evaluation Engineering as a named practice area — and the practice area composes into Applied Agentics as the broader category.

None of this is exotic. The components have been available in adjacent disciplines (web testing, observability, security monitoring) for over a decade. What has been missing is the integration into agent-specific failure modes and the recognition that the discipline needs a name before it gets institutional investment.

## Where to start

Teams beginning the work usually start by capturing trajectories from their existing production agents and inspecting a sample by hand. That first inspection is almost always sufficient to establish the budget for the systematic version of the work. The patterns are visible quickly; what takes time is building the pipeline to surface them automatically and the discipline to act on what it surfaces.

The next twelve months will separate the teams that built the discipline early from the teams that absorbed the cancellation rate.

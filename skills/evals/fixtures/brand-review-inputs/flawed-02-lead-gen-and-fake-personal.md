# What we learned shipping our first production agent

Last quarter, our team was spending 20 hours a week debugging agent traces by hand, copying logs into spreadsheets, and arguing about which run was the "real" baseline. We knew there had to be a better way, and we knew we were not alone in feeling the pain. That is the story of how we built our trajectory analysis pipeline — and it starts the same way most of these stories start: with a production incident nobody saw coming.

## The incident

The agent had been running cleanly for six weeks. Then, over the course of two days, three customer workflows started returning subtly wrong outputs. No exception, no timeout, no obvious failure signal. The model had not changed. The prompts had not changed. Something in the trajectory was drifting, and our offline eval suite was telling us everything was fine.

We are excited to announce that we eventually traced the issue to a context-window edge case introduced when an upstream tool changed its response format. Our offline tests had not exercised the new format because the eval fixtures had not been refreshed in eight weeks. The fix was straightforward; the diagnosis took most of a week.

## What we built

Out of that experience, we built a continuous trajectory analysis pipeline. It captures every agent step, flags decision points where the model's reasoning diverges from prior runs on similar inputs, and routes anomalies to a review queue before they become incidents. It is not a replacement for outcome-level eval — it is a different layer of the stack.

Unlike the LangChain framework, which buries half the relevant trajectory data inside abstractions you cannot inspect, our pipeline operates on raw provider API traces. Every reasoning step, every tool call, every token-level decision is available for inspection. We think framework opacity is one of the largest hidden costs teams are paying right now, and it is one of the reasons we built our methodology against raw APIs from the start.

## The methodology

The pipeline runs in three stages. Stage one captures and normalizes traces across runs. Stage two flags drift candidates by comparing reasoning paths against a rolling baseline. Stage three routes confirmed drift to the engineering team with the specific decision point highlighted, the contributing context surfaced, and a suggested test fixture to add to the offline suite.

The result is a continuous loop: production catches what offline missed, offline absorbs the lesson, and the next deployment is hardened against that class of drift before it ships.

## What this means for your team

If you are operating agent systems in production and you do not yet have continuous trajectory analysis in place, you are accumulating the same reliability debt our team was accumulating six months ago. The good news is that the methodology is portable, the patterns are documented, and the tooling is becoming available.

**Start your free trial of our trajectory analysis platform and see drift detection in action within your own pipelines.** Most teams see useful signal within the first week of deployment.

**Book a demo with our engineering team to walk through your specific architecture and identify the highest-leverage place to instrument first.** Slots are limited and we prioritize teams already running agents in production.

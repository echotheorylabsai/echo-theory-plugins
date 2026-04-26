# Brief 01 — Why most agent evaluation pipelines fail under production load

- **Topic**: Why most agent evaluation pipelines fail under production load — the gap between offline eval suites and observed trajectory drift in live systems.
- **Audience**: The Production-AI CTO (primary persona from `brand/personas.md`).
- **Key messages**:
  - Offline eval suites optimize for static benchmarks; production failure modes show up only in trajectory analysis under live load.
  - The discipline of Evaluation Engineering must include CI/CD-integrated agent testing and drift detection, not just one-shot benchmark scores.
  - Most teams discover the gap after a production incident; a continuous trajectory-analysis pipeline catches it earlier.
  - Cite the LangChain "State of AI Agents" 2026 finding (~30% of enterprises run zero evaluation) as opening evidence.
- **Length**: 900–1,100 words.
- **Channel**: blog

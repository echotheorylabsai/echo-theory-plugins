# Legal, Compliance, and Echo-Specific Flags

Run these checks on every review. Universal flags apply regardless of brand config; Echo-specific flags apply when `brand/anti-patterns.md` and `brand/voice.md` are present (which is the default state for this project).

The canonical "never" list lives in `brand/anti-patterns.md`. This file routes those items, plus universal compliance flags, into the review output's `Legal / compliance flags` section per `review-rubric.md`.

## Universal flags

- **Unsubstantiated claims** — superlatives such as "best", "fastest", "only", "#1", "leading", "industry-leading", "best-in-class", "most advanced", "unparalleled" without evidence, citation, or qualification.
- **Missing disclaimers** — financial, health, earnings, ROI, or guarantee claims that may require a disclaimer.
- **Comparative claims** — comparisons to competitors (by name or implied) that could be challenged without documented proof.
- **Regulatory language** — content touching regulated domains (financial services, healthcare, legal advice, insurance, pharmaceuticals, alcohol, cannabis, crypto, children's products).
- **Testimonial issues** — quotes or endorsements without attribution, consent disclosure, or material-connection disclosure.
- **Copyright concerns** — content that appears closely paraphrased from another source, uses third-party images without credit, or quotes extensively without attribution.
- **Privacy / PII exposure** — customer names, emails, or identifying details used without indication of consent.
- **Absolute guarantees** — "guaranteed", "no risk", "always", "never fails" — require qualification or removal.

## Echo-specific flags (from `brand/anti-patterns.md`)

Each item is a flag-on-sight when reviewing Echo content. Surface every instance, not a sample.

- **Hype superlatives without evidence** — flag every "industry-leading", "best-in-class", "most advanced", "unparalleled", "#1", and similar. Recommend substantiation, qualification, or removal.
- **Fake-personal-story openers** — flag any opener of the form "Last quarter our team was spending X hours on...", "We were struggling with...", or any narrative manufactured to humanize. Recommend a declarative or evidence-led replacement.
- **Lead-gen CTAs** — flag every "Start your free trial", "Book a demo", "No credit card required", "Get in touch", "Limited spots available". Recommend an Echo research-distribution alternative per `skills/draft-content/references/cta-patterns.md`. Route to compliance section, not detailed findings.
- **"We're excited to announce" energy** — flag this and adjacent phrasing ("Thrilled to share", "Can't wait to show you"). Recommend a declarative replacement that states what changed and why.
- **Exclamation marks** — flag every instance in production copy.
- **Named-competitor disparagement** — flag any sentence that names a competitor unfavorably (e.g., "Unlike X, which buries half the data..."). Recommend rephrasing to a neutral technical comparison or removal. Route to compliance section.
- **Unqualified absolutes** — flag "guaranteed", "never fails", "always", "no risk" in any Echo context.
- **Deprecated framing** — flag any use of "context engineering" as a pillar name; the current Echo framing is *Agent Harness Engineering* (per `brand/style-guide.md` and `brand/facts.md`).

## Citation-specific flags (Echo)

- **Stripped citations** — flag any statistic that lacks an inline citation in the form `([Publisher, Month YYYY](url))`. Recommend restoring the source from `echo-theory-labs-vision.md` if available; otherwise route to the user with `[citation needed]`.
- **Fabricated sources** — flag any source name that does not match a known publisher (Gartner, Deloitte, LangChain, peer-reviewed venues, primary documentation). If the source name appears invented (e.g., "Institute for Production AI Reliability" with no findable record), surface as **fabricated or unverifiable** with severity High and route to compliance.
- **Naked numbers** — flag any percentage, dollar figure, or count claim without either a citation or an explicit "in our testing" / "in our engagements" qualifier.

## Recommended actions per flag type

- **Substantiate** — add a citation, internal data reference, or soften the claim ("among the fastest", "in our testing").
- **Disclaim** — add the required disclaimer inline or as a footnote.
- **Rephrase** — rework a comparative claim to be factual and specific, or replace a lead-gen CTA with an Echo research-distribution alternative.
- **Route to legal** — content should not ship without compliance or legal review.
- **Attribute** — add quotation source, material-connection disclosure, or image credit.
- **Remove** — content cannot be safely supported (e.g., fabricated citation).

## Output routing

Surface flagged items in the `Legal / compliance flags` section of the review output (see `review-rubric.md`) when the flag is:
- A lead-gen CTA misalignment.
- A citation fabrication or stripped citation.
- A named-competitor disparagement.
- A regulatory or compliance concern.
- A privacy / PII exposure.
- An unsubstantiated claim that crosses into legal-risk territory (absolute guarantees, regulated-domain claims).

Surface other Echo anti-pattern findings (exclamation marks, "we're excited" energy, fake-personal opener, etc.) in `Detailed findings` with appropriate severity grading.

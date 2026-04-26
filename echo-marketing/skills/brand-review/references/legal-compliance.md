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

## Echo-specific routing

`brand/anti-patterns.md` is the canonical "never" list. Every item there is a flag-on-sight when reviewing Echo content; surface every instance, not a sample. This file does not restate the list (avoid drift); it routes findings to the right output section:

Route to **Legal / compliance flags**:
- Lead-gen CTAs — recommend an Echo research-distribution alternative (a pointer to a deeper artifact: methodology note, audit checklist, companion post, or published case study), not a sales process.
- Named-competitor disparagement — recommend rephrasing to a neutral technical comparison or removal.
- Unqualified absolutes ("guaranteed", "never fails", "always", "no risk") — require qualification or removal.
- Citation fabrication or stripped citations — see "Citation-specific flags" below.

Route to **Detailed findings** (with severity per `review-rubric.md`):
- Hype superlatives without evidence — recommend substantiation, qualification, or removal.
- Fake-personal-story openers — recommend a declarative or evidence-led replacement.
- "We're excited to announce" / "Thrilled to share" / "Can't wait to show you" energy — recommend a declarative replacement that states what changed and why.
- Exclamation marks in production copy.
- Deprecated framing — e.g., "context engineering" used as a pillar name; the current Echo framing is *Agent Harness Engineering* (per `brand/style-guide.md` and `brand/facts.md`).

## Citation-specific flags (Echo)

- **Stripped citations** — flag any statistic that lacks an inline citation in the form `([Publisher, Month YYYY](url))`. Route to the user with `[citation needed]` if the original source cannot be verified.
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

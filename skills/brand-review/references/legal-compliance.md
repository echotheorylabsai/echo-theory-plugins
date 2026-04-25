# Legal and Compliance Flags (Universal)

Run these checks on every review, regardless of whether brand voice is configured. These are universal defaults. Industry-specific modules (fintech, healthcare, GDPR, etc.) can be added later as sibling files under a `compliance-modules/` subdirectory; this file covers the universal baseline only.

## Flags

- **Unsubstantiated claims** — superlatives such as "best", "fastest", "only", "#1", "leading", without evidence, citation, or qualification.
- **Missing disclaimers** — financial claims (returns, savings, ROI), health claims, guarantees, or earnings claims that may require a disclaimer.
- **Comparative claims** — comparisons to competitors (by name or implied) that could be challenged without documented proof.
- **Regulatory language** — content that may need compliance review because it touches regulated domains (financial services, healthcare, legal advice, insurance, pharmaceuticals, alcohol, cannabis, crypto, children's products).
- **Testimonial issues** — quotes or endorsements without attribution, without consent disclosure, or without material-connection disclosure (e.g., "paid partner", "customer compensated for their time").
- **Copyright concerns** — content that appears closely paraphrased from another source, uses third-party images without credit, or quotes extensively without attribution.
- **Privacy / PII exposure** — customer names, emails, or identifying details used without indication of consent.
- **Absolute guarantees** — "guaranteed", "no risk", "always", "never fails" — require qualification or removal.

## Recommended actions per flag type

- **Substantiate** — add a citation, internal data reference, or soften the claim ("among the fastest", "in our testing").
- **Disclaim** — add the required disclaimer inline or as a footnote.
- **Rephrase** — rework a comparative claim to be factual and specific ("X supports Y; we support Y and Z") rather than evaluative.
- **Route to legal** — content should not ship without compliance or legal review.
- **Attribute** — add quotation source, material-connection disclosure, or image credit.
- **Remove** — content cannot be safely supported.

## Output

Surface flagged items in the "Legal / compliance flags" section of the review output (see `review-rubric.md`) with the concern and the recommended action.

---
name: draft-content
description: Generate new marketing content (blog posts, Twitter/X posts, threads, methodology notes) from a brief, applying brand voice, facts, personas, anti-patterns, and style from ./brand/. Use when the user asks to draft, write, compose, repurpose, or get headline/hook options for blog or Twitter/X content. Do NOT use for evaluating or reviewing existing content — use the brand-review skill for that.
---

# Draft Content

Generate marketing content drafts tailored to channel, audience, and brand voice. Phase 1 channels: blog and Twitter/X.

## Brand config resolution

Before drafting, resolve brand context in this order:

1. Read `./brand/voice.md` — personality, voice attributes, audience pointer, messaging pillars, tone by channel.
2. Read `./brand/facts.md` — locked positioning (research pillars, delivery capabilities, internal practice, "what the brand is not").
3. Read `./brand/personas.md` — audience personas; default to the persona indicated by the brief and confirm.
4. Read `./brand/anti-patterns.md` — the canonical "never" list. Never violate these.
5. Read `./brand/style-guide.md` — grammar, formatting, brand-specific terminology and capitalization.
6. If any file is missing, ask the user: "I could not find `brand/<file>`. Would you like to (a) point me to it, (b) proceed with a neutral professional tone, or (c) author it now using the brand-voice-authoring skill?"
7. Inform the user which brand config was applied at the end of the draft.

## Inputs

Gather from the user. If missing, ask before proceeding. **Collect channel first** — all workflow steps depend on it.

1. **Channel** — blog or Twitter/X.
2. **Topic** — subject or theme.
3. **Target audience** — persona name from `brand/personas.md` if defined; otherwise role and seniority. Confirm before drafting.
4. **Key messages** — 2–4 main points to communicate.
5. **Length or format constraint** — word count for blog, character/tweet-count for Twitter/X.
6. **Tone override** (optional) — channel tone is fixed in `brand/voice.md` §5; override only when the brief explicitly calls for one.

## Workflow

1. Determine the channel. Load the matching reference file from `references/`:
   - Blog → `references/channel-blog.md`
   - Twitter/X → `references/channel-social-twitter.md`

2. Load `references/headline-patterns.md` and propose 2–3 headline/hook options. Blog posts always need a headline; Twitter/X threads always need a lead hook.

3. If the content is web-facing (blog), load `references/seo-patterns.md` and apply the keyword placement checklist.

4. If the content needs a call to action, load `references/cta-patterns.md`. Use research-distribution CTAs only — no lead-gen.

5. Draft the content applying the resolved brand voice + facts + persona + anti-patterns + style guide + channel structure.

   **Citation freshness**: When including external statistics, data points, or research findings, the source must be no older than 90 days from today's date. AI is a fast-moving field — stale stats undermine Echo's credibility as a practitioner voice. If a stat cannot be verified as recent, flag it inline with `[source date TBD — verify recency before publishing]` rather than presenting it as current. Do not substitute a newer-sounding paraphrase of an old stat.

## Output

Present the draft with clear formatting. After the draft, include:

- **Voice and tone applied**: short note on which brand config files and channel tone were used.
- **SEO recommendations** (blog only): primary keyword, meta description under 160 chars, internal/external linking suggestions, image alt text opportunities.
- **Headline / opening hook options**: 2–3 variations.

## After drafting

Ask the user: "Would you like me to revise any section, adjust the tone, produce a variation for the other channel, or send this to the brand-review skill for an audit before you ship?"

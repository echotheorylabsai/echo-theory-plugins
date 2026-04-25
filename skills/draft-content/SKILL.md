---
name: draft-content
description: Generate new marketing content (blog posts, social media posts, email newsletters, landing pages) from a brief. Use when the user wants to create new copy, needs headline or subject-line options, or needs channel-specific formatting. Applies brand voice and style from ./brand/voice.md and ./brand/style-guide.md. Do NOT use for evaluating or reviewing existing content — use the brand-review skill for that.
---

# Draft Content

Generate marketing content drafts tailored to a specific content type, audience, and brand voice.

## Trigger

Use this skill when the user asks to draft, write, create, or compose any marketing content: blog post, LinkedIn/Twitter/Instagram/Facebook post, email newsletter, landing page, press release, case study. Also use for variations or repurposing existing ideas into new channels.

## Brand config resolution

Before drafting, resolve brand context in this order:

1. Read `./brand/voice.md` (relative to project root). This is the source of truth for personality, voice attributes, messaging pillars, tone by channel and situation.
2. Read `./brand/style-guide.md` for grammar, formatting, and terminology rules.
3. If either file is missing, ask the user: "I could not find `brand/voice.md` (and/or `brand/style-guide.md`) in this project. Would you like to (a) point me to them, (b) proceed with a neutral professional tone, or (c) draft them first using the brand-review skill's voice-doc-framework reference?"
4. Inform the user which brand config was applied at the end of the draft.

## Inputs

Gather from the user. If missing, ask before proceeding:

1. **Content type** — blog post, social post (which platform), email, landing page, press release, case study, other.
2. **Topic** — subject or theme.
3. **Target audience** — role, industry, seniority, pain points. If `brand/voice.md` defines audiences, default to the relevant one and confirm.
4. **Key messages** — 2–4 main points to communicate.
5. **Length or format constraint** — word count, character limit, paragraph count.
6. **Tone override** (optional) — a specific tone dial-up for this piece (e.g., "more urgent than usual" for a launch).

## Workflow

1. Determine the channel. Load the matching reference file from `references/`:
   - Blog → `references/channel-blog.md`
   - LinkedIn → `references/channel-social-linkedin.md`
   - Twitter/X → `references/channel-social-twitter.md`
   - Instagram → `references/channel-social-instagram.md`
   - Facebook → `references/channel-social-facebook.md`
   - Email newsletter → `references/channel-email.md`
   - Landing page, press release, case study → use blog structure as base unless user provides specifics.

2. If the content needs a headline, subject line, or hook, load `references/headline-patterns.md` and propose 2–3 options.

3. If the content is web-facing (blog, landing page, anywhere indexed by search), load `references/seo-patterns.md` and apply the keyword placement checklist.

4. If the content needs a call to action, load `references/cta-patterns.md`.

5. Draft the content applying the resolved brand voice + style guide + channel structure.

## Output

Present the draft with clear formatting. After the draft, include:

- **Voice and tone applied**: short note on which brand voice settings and channel tone were used.
- **SEO recommendations** (web content only): primary keyword, meta description under 160 chars, internal/external linking suggestions, image alt text opportunities.
- **Headline/subject line options** (when relevant): 2–3 variations.

## After drafting

Ask the user: "Would you like me to revise any section, adjust the tone, produce a variation for a different channel, or send this to the brand-review skill for an audit before you ship?"

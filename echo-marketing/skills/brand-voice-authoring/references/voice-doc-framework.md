# Voice Document Framework

Use this reference when the user wants to **author or revise** their brand voice document (`brand/voice.md`). Loaded by the `brand-voice-authoring` skill.

The framework below maps section-for-section to the template at `brand/voice.md`. Guide the user through each section; help them articulate decisions rather than inventing content on their behalf.

## Contents

1. Brand personality
2. Voice attributes — use a spectrum
3. Audience awareness
4. Core messaging pillars
5. Tone spectrum — voice vs. tone
6. Brand-specific terminology
7. Voice anti-patterns
8. Using this framework

## 1. Brand personality

Define the brand as if it were a person.

Prompt the user: "If your brand were a person, how would you describe them to someone who just met them? What would they do, and what wouldn't they do?"

Example output: "A knowledgeable colleague who explains complex things simply, celebrates your wins genuinely, and never talks down to you."

## 2. Voice attributes — use a spectrum

Help the user pick 3–5 voice attributes by positioning them on spectrums:

| Spectrum | One end | Other end |
|---|---|---|
| Formality | Formal, institutional | Casual, conversational |
| Authority | Expert, authoritative | Peer-level, collaborative |
| Emotion | Warm, empathetic | Direct, matter-of-fact |
| Complexity | Technical, precise | Simple, accessible |
| Energy | Bold, energetic | Calm, measured |
| Humor | Playful, witty | Serious, earnest |
| Innovation | Cutting-edge, forward-looking | Established, proven |

For each chosen attribute, document it in this format:

**[Attribute name]**
- **We are**: [what this means in practice]
- **We are not**: [common misinterpretation to avoid]
- **This sounds like**: [example sentence demonstrating it]
- **This does NOT sound like**: [example sentence violating it]

Example:

**Approachable**
- **We are**: friendly, clear, jargon-free, welcoming to beginners and experts alike.
- **We are not**: dumbed-down, overly casual, or lacking substance.
- **This sounds like**: "Here's how to get started — it takes about five minutes."
- **This does NOT sound like**: "Yo! This is super easy, even a noob can do it lol."

## 3. Audience awareness

Capture who the brand is speaking to:

- Primary audience (role, industry, seniority).
- Secondary audience (if relevant).
- What they care about.
- Level of expertise.
- How they expect to be addressed.

## 4. Core messaging pillars

3–5 themes the brand consistently communicates. For each pillar:

- Name (short label).
- What it communicates.
- Why it matters to the audience.
- Hierarchy (which pillar leads in which context).

## 5. Tone spectrum — voice vs. tone

The voice attributes stay fixed. **Tone** dials them up or down by context.

Example: if the brand is "bold and warm":
- In a product launch, dial up **bold**.
- In an incident response, dial up **warm**.
- Neither attribute disappears; the balance shifts.

### Tone by channel

Sample mapping to help the user fill in `brand/voice.md`:

| Channel | Typical tone emphasis | Sample line |
|---|---|---|
| Blog | Informative, conversational, educational | "Let's walk through how this works and why it matters for your team." |
| LinkedIn | Professional, thought-provoking, concise | "Three things we learned from running 50 campaigns this quarter." |
| Twitter/X | Punchy, direct, sometimes witty | "Your landing page has 3 seconds. Make them count." |
| Email marketing | Personal, helpful, action-oriented | "We put together something we think you'll find useful." |
| Error messages | Empathetic, helpful, blame-free | "Something went wrong on our end. We're looking into it." |

### Tone by situation

| Situation | Typical tone emphasis |
|---|---|
| Product launch | Excited, confident, forward-looking |
| Incident or outage | Transparent, empathetic, accountable |
| Customer success story | Celebratory, specific, crediting the customer |
| Thought leadership | Authoritative, nuanced, evidence-based |
| Onboarding | Welcoming, encouraging, clear |
| Bad news (price increase, deprecation) | Honest, respectful, solution-oriented |
| Competitive comparison | Confident but fair, fact-based, not disparaging |

## 6. Brand-specific terminology

Capture only terminology that reflects brand positioning (product/feature names, category framing, internal jargon policy, competitor reference policy). Universal grammar and preferred-term rules live in `brand/style-guide.md`.

- Official product/feature names and their capitalization.
- Preferred category language — how the brand describes what it does.
- Preferred vs. avoided internal jargon.
- Competitor naming policy (named, generic, or avoided).
- Terms coined by competitors that the brand chooses to avoid to prevent reinforcing their positioning.

## 7. Voice anti-patterns

Capture explicit "never" rules. Things like: "We never use hype superlatives without data", "We never disparage competitors by name", "We never use exclamation marks in product copy".

## Using this framework

1. Walk through sections in order — earlier sections inform later ones.
2. Prompt one section at a time; do not flood the user with all questions at once.
3. Write the user's answers directly into `brand/voice.md`, replacing the `<to be defined>` placeholders.
4. After each section, reflect back what was captured and confirm before moving on.
5. At the end, run a sanity check: do the voice attributes, messaging pillars, and tone matrices cohere? Flag contradictions for the user to resolve.

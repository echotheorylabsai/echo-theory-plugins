# Brand Style Guide — Echo Theory Labs

Grammar, formatting, punctuation, and Echo-specific terminology. Read by `draft-content` (to generate compliant copy) and `brand-review` (to flag deviations).

Brand voice and persona-shaping decisions live in `voice.md`, `facts.md`, `personas.md`, `anti-patterns.md`. This file covers mechanics and Echo terminology.

---

## Grammar and Mechanics

| Rule | Choice | Example |
|---|---|---|
| Oxford comma | **Yes** | "instruction architecture, memory systems, and compaction" |
| Headings case | **Sentence case** for body H2/H3; **Title Case** for Echo-named pillars and capabilities | "How trajectory analysis surfaces drift" / "Agent Harness Engineering" |
| Contractions | **Use sparingly** | Prefer "we are" in research-grade prose; "we're" acceptable in Twitter/X |
| Em dash spacing | **No spaces** | "the discipline—not the product—is the lever" |
| Numbers in prose | **Spell out 1–9, numerals 10+**; numerals always for percentages and stats | "five pillars", "10 frameworks", "40%" |
| Percent | **%** (no space) | "40%", "nearly 30%" |
| Date format | **Month DD, YYYY** | "January 15, 2026" |
| Time format | **12-hour** | "3:00 PM" |
| Lists of fragments | **No terminal periods** | "Trajectory analysis under load" |
| Lists of full sentences | **Terminal periods** | "Trajectory analysis surfaces drift the offline eval missed." |

## Formatting Conventions

- **Heading hierarchy**: one H1 per page, H2 for major sections, H3 for sub-sections. Do not skip levels.
- **Bold** for emphasis on key phrases. **Italic** for Echo-coined terms on first use (*Applied Agentics*, *Agent Harness Engineering*).
- **Link text** is always descriptive (never "click here" or "read more"). Cite sources inline with the publisher and year: `([Gartner, June 2025](url))`.
- **Image alt text** required on every image.
- **Code formatting** — backticks for inline code (`MCP`, `eval`), fenced blocks for multi-line.
- **Callout boxes** — reserved for warnings, methodology notes, or distinct asides; not ordinary emphasis.

## Punctuation and Emphasis

- **Exclamation marks** — never in production copy. See `anti-patterns.md`.
- **Ellipses** — avoid in research-grade writing.
- **ALL CAPS** — avoid. Use bold or italic.
- **Emoji** — none in blog copy. Minimal-to-none in Twitter/X (one is the cap, only when it carries meaning).

## Echo-Specific Terminology and Capitalization

The canonical capitalization and naming policy for Echo terms. The full positioning rationale lives in `voice.md` §7 and `facts.md`.

| Use this | Not this | Notes |
|---|---|---|
| *Applied Agentics* | "applied agentics", "applied AI" as a category claim | Always title-cased; this is Echo's core category framing |
| *Agent Harness Engineering* | "context engineering", "harness engineering" | Title-cased. Supersedes "context engineering" entirely |
| *Evaluation Engineering* | "eval engineering", "evals" as a discipline name | Title-cased pillar. "evals" is fine in body copy when referring to artifacts |
| *Adversarial Defense* | "AI security", "agent security" as a pillar name | Title-cased pillar |
| *Bare-Metal Orchestration* | "bare metal orchestration" (no hyphen) | Hyphenated, title-cased capability |
| *Observability & Runtime* | "observability and runtime" | Ampersand, title-cased capability |
| *Generative UI* | "generative ui", "gen UI" | Title-cased capability |
| *Autonomous Workers* | "AI workers", "digital employees" | Title-cased internal practice |
| *Dogfooding* | "eating our own dogfood" | Single word, capitalized when used as the named internal practice |
| *Echo Theory Labs* | "Echo Theory", "EchoTheory", "ETL" | Full name on first mention; "Echo" acceptable thereafter |
| MCP | "M.C.P.", "Model Context Protocol" after first use | Spell out on first use, then MCP |
| LLM | "L.L.M." | All caps, no periods |

## Preferred Terms (Universal)

| Use this | Not this | Notes |
|---|---|---|
| sign up (verb) | signup (verb) | "signup" is the noun form |
| log in (verb) | login (verb) | "login" is the noun/adjective form |
| set up (verb) | setup (verb) | "setup" is the noun/adjective form |
| email | e-mail | No hyphen |
| website | web site | One word |
| in production | "in prod" | "in prod" only acceptable in informal Twitter/X |

## Inclusive Language

- Use gender-neutral language; "they/them" for unknown individuals.
- Avoid ableist language ("crazy", "blind spot", "lame", "insane").
- Avoid culturally specific idioms that may not translate across regions.
- Prefer "straightforward" over "easy" where applicable (what is easy varies by reader).

## Acronyms

- Spell out on first use in a document, with the acronym in parentheses: "Model Context Protocol (MCP)".
- Subsequent uses may use the acronym alone.
- Re-spell out on first use in a new document.
- Echo pillars and capabilities are *not* abbreviated by default — write *Agent Harness Engineering*, not "AHE", in production copy.

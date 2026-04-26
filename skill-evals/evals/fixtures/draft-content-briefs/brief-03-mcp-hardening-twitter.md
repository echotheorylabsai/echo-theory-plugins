# Brief 03 — Three things teams get wrong about MCP server hardening

- **Topic**: Three things teams get wrong about MCP (Model Context Protocol) server hardening — surfaced from Echo's Adversarial Defense practice.
- **Audience**: The Platform-Lead Staff Engineer (secondary persona from `brand/personas.md`).
- **Key messages**:
  - MCP servers are treated as trusted code; in practice they are an AI supply chain dependency that needs auditing.
  - Auth-token scoping on MCP servers is routinely too broad — agents inherit more permission than the workflow needs.
  - Most teams have no MCP-specific red-team in their threat model.
  - Link to a longer Echo blog post on MCP server/gateway audits for the full methodology.
- **Length**: A Twitter/X thread of 4–6 tweets. Each tweet ≤280 characters. Use numbered thread convention (1/, 2/, etc.). Link to the longer blog post in the final tweet per the link convention in `skills/draft-content/references/channel-social-twitter.md`.
- **Channel**: twitter

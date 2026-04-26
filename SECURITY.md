# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in any plugin or skill in this repository, please **do not open a public GitHub issue**.

Report it privately to: **team@echotheory.ai**

Include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Any suggested mitigations, if you have them

We aim to acknowledge reports within 48 hours and to provide a resolution timeline within 7 days.

## Scope

This repository contains Claude Code plugins (skill definitions and supporting reference files). Security concerns in scope include:

- Prompt injection vectors in skill definitions that could be exploited when users install this plugin
- Instructions within skills that could cause unintended destructive or exfiltrating behavior
- Malicious content in eval fixtures or reference files

Out of scope: general Claude model safety issues — those should be reported to [Anthropic](https://www.anthropic.com/security).

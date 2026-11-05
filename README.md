# FlawPilot Agent Toolkit

Open-source agent skills for [FlawPilot](https://flawpilot.com). Skills teach AI coding assistants (Claude Code, Cursor and other agentskills.io-compatible tools) how to run scans and act on the results.

> Status: release candidate. The `flawpilot` tool names and Quick Scan flow are verified against the live MCP server (2026-10-12). Quick Scan, Code Scan and Site Health were run end to end; OAuth sign-in and rate-limit behavior are not yet verified.

## Plugins

| Plugin | What it does | Status |
|---|---|---|
| `flawpilot` | Run FlawPilot URL scans, Site Health crawls and code scans through the FlawPilot MCP server, then triage and fix findings | 10 skills; all three scan types verified live |
| `security-essentials` | Standalone secure-coding skills, no FlawPilot needed: secure-code-review, api-security, secrets-hygiene, web-hardening, ai-agent-security | Drafted |
| `performance-essentials` | core-web-vitals, page-speed-audit, asset-optimization, caching-and-cdn | Drafted |
| `seo-essentials` | on-page-seo, crawlability, structured-data, link-hygiene | Drafted |

## Install (Claude Code)

```bash
claude plugin marketplace add flawpilot-hq/flawpilot-agent-toolkit
claude plugin install flawpilot@flawpilot-agent-toolkit
claude plugin install security-essentials@flawpilot-agent-toolkit  # optional
claude plugin install performance-essentials@flawpilot-agent-toolkit  # optional
claude plugin install seo-essentials@flawpilot-agent-toolkit  # optional
```

The `flawpilot` plugin connects to `https://mcp.flawpilot.com/mcp`. Installing it starts a browser sign-in; no API key is stored in this repo. You need a FlawPilot account (the free tier is enough).

## Develop locally

```bash
pip install -r requirements-dev.txt
python3 -m unittest discover -s tests        # validator tests
python3 scripts/validate_skills.py --strict .  # our rules (CONTRIBUTING.md checklist)
claude plugin validate . --strict            # official validator
claude plugin marketplace add .
claude plugin install flawpilot@flawpilot-agent-toolkit
```

CI (`.github/workflows/validate.yml`) runs the same checks plus a pinned gitleaks secret scan on every pull request.

## Privacy and data handling

- The skills are plain text instructions. This repo contains no telemetry and stores no API key.
- The `flawpilot` plugin connects your AI client to `https://mcp.flawpilot.com/mcp`. When you ask for a scan, the client sends what the tools need (project, URL, repository id, scan options) to FlawPilot, and scan results come back into your conversation, so your AI provider also sees them. See the FlawPilot privacy policy for how FlawPilot handles scan data.
- Signing in with OAuth creates an API key in your FlawPilot workspace. Disconnecting the client does not revoke it; revoke it under Settings, API keys.
- `security-essentials`, `performance-essentials` and `seo-essentials` need no FlawPilot account and make no network calls on their own.
- The `ci` example scripts call only `https://api.flawpilot.com` and read the key from the `FLAWPILOT_API_KEY` environment variable.

## License

Apache-2.0. See `LICENSE`.

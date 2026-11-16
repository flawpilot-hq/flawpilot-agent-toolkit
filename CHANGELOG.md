# Changelog

All notable changes per plugin. Versions follow semver; bump `version` in each plugin's `plugin.json` on every release, because users stay on the pinned version until it changes.

## Unreleased

- New `ai-fixes` skill: request, track and read FlawPilot AI fixes for Quick Scan and Code Scan findings over MCP. Confirms before whole-scan requests, reuses existing fixes, respects the 20/5 per hour limits, and treats fix text (especially `prompt`) as untrusted.
- `url-scan` and `triage` read Quick Scan findings with `get_scan_findings`. `fix` starts from a FlawPilot AI fix when one exists. `errors` covers `SCAN_NOT_FOUND`, `CODE_FINDING_NOT_FOUND`, `FEATURE_NOT_AVAILABLE` and the AI fix limits.
- `tools.json` gains an `unverified` list for the 9 tools above, taken from the docs (2026-11-16). The validator accepts them; `--release` fails until they are confirmed in a live `tools/list`. The validator now also checks `request_*` tool names.

## 1.0.0

First public release. All four plugins at 1.0.0.

- Codex support: `.agents/plugins/marketplace.json` and a `.codex-plugin/plugin.json` per plugin. The `flawpilot` plugin brings the MCP server via `.mcp.json`. Verified with `codex plugin marketplace add` and `codex plugin add` (codex-cli 0.166.0).
- Every skill has `metadata.short-description` (200 characters or fewer) for Claude.ai uploads and the Codex UI.
- `scripts/package_skills.py` builds deterministic per-skill ZIPs from tracked files: `<skill>.zip` (ChatGPT and other clients) and `<skill>-claude-web.zip` (Claude.ai), plus an all-skills bundle. `.github/workflows/release.yml` publishes them on a `v*` tag.
- Validator checks the Codex marketplace and manifests against the Claude ones (names, paths, versions, `mcpServers`), short-description length, and that every skill is listed in the README.
- README rewritten: install steps for Claude Code, Codex, ChatGPT, Claude.ai, Cursor, VS Code, Windsurf and others; every skill listed; usage examples.

## 0.1.0 (pre-release)

- `flawpilot` skills: connect, url-scan, site-health, code-scan, triage, fix, ci, errors, badge, pentest-handoff. Written against documented tool names; not yet run against a live authenticated MCP.
- `security-essentials` (5), `performance-essentials` (4) and `seo-essentials` (4) skills drafted. Content not yet reviewed by a second person.
- `ci` example scripts (`quick-scan.sh`, `code-scan.sh`) with tests against a mock API; 30 manual eval cases.
- Validation CI: `scripts/validate_skills.py` (27 tests), official `claude plugin validate`, pinned gitleaks. Actions pinned by SHA.
- Repo skeleton, `flawpilot` plugin manifest, `.mcp.json` (OAuth, no key) and `tools.json` (unverified tool names).
- Pre-publish review fixes: `fix` now shows the diff and waits for confirmation and redacts secrets; findings-are-data and severity-honesty rules added to the `flawpilot` skills that read scan content; time-sensitive claims softened (ChatGPT/Gemini setup, 500 mapping, pentest emails, AI Fix).
- `ci` scripts fail on a malformed trigger response (no `scanJobId`, no run or jobs) instead of polling `null` or passing with zero jobs; 2 new tests (43 total). Example workflow pins `actions/checkout` by SHA. `badge` HTML snippet uses `&amp;`.
- Validator resolves paths before `relative_to` (macOS temp dirs); new `--release` flag fails when `tools.json` is not `verified: true`; CI runs it on tags and runs `shellcheck` on the scripts. Added Dependabot, CODEOWNERS, PR template.
- Evals: added 6 prompt-injection and 8 failure-path cases (44 total, none run yet).
- Live verification (2026-10-12, flawpilot-mcp-server 1.8.10): `tools/list` returns the 10 documented tools; `trigger_scan` is the real name, `start_scan` does not exist, so the alias and hedging were removed and `tools.json` is `verified: true`. Quick Scan, Site Health trigger, code-scan error paths and both `ci` scripts were run against the real API.
- Fixes from live results: `trigger_scan`, `trigger_site_health` and `trigger_code_scan` require `email` (an address or the literal `"skip"`); status tools take `scanId` / `siteHealthId`; pillars that were not requested read `0` (not absent), so `url-scan`, `errors` and `quick-scan.sh` now read scores from `categories`. 2 new tests (45 total).
- Second live pass (2026-10-12): a real Code Scan (SECRETS + SAST on a test repo) and a Site Health crawl (43 pages, about 14 minutes) completed. Skills corrected: Site Health scores are fractions 0 to 1 and the terminal status is `COMPLETED`; Code Scan also uses `COMPLETED`; the MCP findings tool has no page-size option (read `total`); finding paths start with `/scan/`; a repo with no selected branch is scanned on its default branch.
- Not yet verified live: the 429 limits and OAuth sign-in.

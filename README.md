# FlawPilot Agent Toolkit

Open-source agent skills that teach your AI assistant to scan websites and code with [FlawPilot](https://flawpilot.com), rank what it finds, and fix it. Three standalone packs cover security, performance and SEO, and those need no FlawPilot account.

Works with **Claude Code, Claude.ai, ChatGPT, OpenAI Codex, Cursor, VS Code Copilot, Windsurf** and any agent that supports the [Agent Skills](https://agentskills.io) spec.

## What are Skills?

A skill is a folder with a `SKILL.md` file: plain-text instructions an AI agent loads when your request matches. The `url-scan` skill, for example, tells the agent how to start a FlawPilot Quick Scan, wait for it, and report the scores honestly. Skills contain no code that runs on its own and no credentials.

## Plugins

| Plugin | What it does | FlawPilot account |
|---|---|---|
| `flawpilot` | Run FlawPilot Quick Scans, Site Health crawls and Code Scans through the [FlawPilot MCP server](https://docs.flawpilot.com/mcp-connect), then triage and fix the findings | Yes (free tier is enough) |
| `security-essentials` | Secure code review, API security, secrets hygiene, web hardening, AI agent security | No |
| `performance-essentials` | Core Web Vitals, page speed audits, asset optimization, caching and CDN | No |
| `seo-essentials` | On-page SEO, crawlability, structured data, link hygiene | No |

## How the skills fit together

```
                         ┌──────────┐
                         │ connect  │  sign in, fix a broken connection
                         └────┬─────┘
          ┌───────────────────┼────────────────────┐
     ┌────▼─────┐      ┌──────▼──────┐      ┌──────▼──────┐
     │ url-scan │      │ site-health │      │  code-scan  │   run a scan
     └────┬─────┘      └──────┬──────┘      └──────┬──────┘
          └───────────────────┼────────────────────┘
                         ┌────▼─────┐
                         │  triage  │  what to fix first
                         └────┬─────┘
                         ┌────▼─────┐
                         │ ai-fixes │  FlawPilot's written fix (optional)
                         └────┬─────┘
                         ┌────▼─────┐
                         │   fix    │  patch, show the diff, rescan
                         └────┬─────┘
          ┌───────────────────┼────────────────────┐
     ┌────▼─────┐        ┌────▼─────┐      ┌───────▼────────┐
     │  badge   │        │    ci    │      │pentest-handoff │   next steps
     └──────────┘        └──────────┘      └────────────────┘

  errors: any step that fails  ·  *-essentials: standalone, no scan needed
```

## Available Skills

### `flawpilot`

| Skill | What it does |
|---|---|
| [`connect`](plugins/flawpilot/skills/connect) | Connect your assistant to the FlawPilot MCP server, or fix missing tools, failed sign-in and API key issues |
| [`url-scan`](plugins/flawpilot/skills/url-scan) | Run a Quick Scan on a live URL and report Security, Performance, Infrastructure and SEO scores |
| [`site-health`](plugins/flawpilot/skills/site-health) | Run and read Site Health, a whole-site Lighthouse crawl |
| [`code-scan`](plugins/flawpilot/skills/code-scan) | Scan a connected repo for code security (SAST), leaked secrets, vulnerable dependencies and code quality |
| [`triage`](plugins/flawpilot/skills/triage) | Rank findings across all scan types so you know what to fix first |
| [`ai-fixes`](plugins/flawpilot/skills/ai-fixes) | Request, track and read FlawPilot's AI fixes for Quick Scan and Code Scan findings |
| [`fix`](plugins/flawpilot/skills/fix) | Fix a finding in your code or config, show the diff, then verify with a rescan |
| [`errors`](plugins/flawpilot/skills/errors) | Explain error codes, rate limits and failed scans, and say what to fix |
| [`ci`](plugins/flawpilot/skills/ci) | Run scans in GitHub Actions or GitLab CI and gate builds on scores and critical findings |
| [`badge`](plugins/flawpilot/skills/badge) | Add a live FlawPilot score badge to a README or website |
| [`pentest-handoff`](plugins/flawpilot/skills/pentest-handoff) | Decide when a manual penetration test is the right next step, and how to request one |

### `security-essentials`

| Skill | What it does |
|---|---|
| [`secure-code-review`](plugins/security-essentials/skills/secure-code-review) | Review code or a diff for injection, broken access control, weak crypto, SSRF and more, with fixes |
| [`api-security`](plugins/security-essentials/skills/api-security) | Review REST or GraphQL APIs for IDOR, weak auth, mass assignment, rate limits and token handling |
| [`secrets-hygiene`](plugins/security-essentials/skills/secrets-hygiene) | Find, rotate and prevent leaked keys and tokens in code, git history, CI logs and config |
| [`web-hardening`](plugins/security-essentials/skills/web-hardening) | Harden security headers, CSP, HSTS, cookies, TLS and email authentication (SPF, DKIM, DMARC) |
| [`ai-agent-security`](plugins/security-essentials/skills/ai-agent-security) | Secure LLM apps and agents: prompt injection, tool permissions, vetting skills and MCP servers |

### `performance-essentials`

| Skill | What it does |
|---|---|
| [`core-web-vitals`](plugins/performance-essentials/skills/core-web-vitals) | Diagnose and fix slow LCP, poor INP and layout shift (CLS) |
| [`page-speed-audit`](plugins/performance-essentials/skills/page-speed-audit) | Read a Lighthouse or PageSpeed report and rank fixes by impact |
| [`asset-optimization`](plugins/performance-essentials/skills/asset-optimization) | Cut page weight: images, fonts, JavaScript and CSS |
| [`caching-and-cdn`](plugins/performance-essentials/skills/caching-and-cdn) | Set up Cache-Control, compression and CDN delivery |

### `seo-essentials`

| Skill | What it does |
|---|---|
| [`on-page-seo`](plugins/seo-essentials/skills/on-page-seo) | Improve titles, meta descriptions, headings, canonicals, alt text and Open Graph tags |
| [`crawlability`](plugins/seo-essentials/skills/crawlability) | Find why pages are not crawled or indexed: robots.txt, sitemaps, noindex, redirects |
| [`structured-data`](plugins/seo-essentials/skills/structured-data) | Add and validate schema.org JSON-LD for rich results |
| [`link-hygiene`](plugins/seo-essentials/skills/link-hygiene) | Fix broken links, redirect chains, orphan pages and link attributes |

## Installation

The `flawpilot` skills need the FlawPilot MCP server (`https://mcp.flawpilot.com/mcp`, also on the [MCP Registry](https://registry.modelcontextprotocol.io/?q=FlawPilot) as `com.flawpilot/mcp`). Sign-in is OAuth: your browser opens, you approve a workspace, and no key is copied. The three essentials plugins need nothing else.

### Claude Code

```bash
claude plugin marketplace add flawpilot-hq/flawpilot-agent-toolkit
claude plugin install flawpilot@flawpilot-agent-toolkit
claude plugin install security-essentials@flawpilot-agent-toolkit     # optional
claude plugin install performance-essentials@flawpilot-agent-toolkit  # optional
claude plugin install seo-essentials@flawpilot-agent-toolkit          # optional
```

Installing `flawpilot` also adds the MCP server and starts the browser sign-in. Inside a Claude Code session you can use `/plugin marketplace add flawpilot-hq/flawpilot-agent-toolkit` instead.

**Try it:** start `claude` in your project and type a request, or call a skill directly:

```text
> Scan https://example.com with FlawPilot
> /flawpilot:url-scan https://example.com
> /security-essentials:secure-code-review src/api/
```

### OpenAI Codex

```bash
codex plugin marketplace add flawpilot-hq/flawpilot-agent-toolkit
codex plugin add flawpilot@flawpilot-agent-toolkit
codex plugin add security-essentials@flawpilot-agent-toolkit     # optional
```

Or run `/plugins` inside a Codex session and pick from the **FlawPilot Agent Toolkit** marketplace. The `flawpilot` plugin brings the MCP server with it; `codex mcp login flawpilot` signs in if Codex has not prompted you. Update later with `codex plugin marketplace upgrade`.

**Try it:** pass the request when starting Codex, or name a skill with `$` inside a session:

```text
$ codex "Scan https://example.com with FlawPilot and tell me what to fix first"

> $flawpilot:code-scan check my-org/my-app for leaked secrets
> $performance-essentials:core-web-vitals why is LCP slow on the home page?
```

### ChatGPT

1. **Connect FlawPilot.** Open **Plugins** in the ChatGPT sidebar, search `flaw`, and install **FlawPilot** from the Public section. Approve your workspace. ([Step-by-step guide](https://docs.flawpilot.com/mcp-connect/chatgpt).) Plugins are not on every ChatGPT plan; on Business and Enterprise an admin may need to enable them.
2. **Add the skills.** Download `<skill>.zip` files from the [latest release](https://github.com/flawpilot-hq/flawpilot-agent-toolkit/releases/latest), or `flawpilot-agent-toolkit-<version>.zip` for all of them, and upload them where your ChatGPT plan supports custom skills.

Make sure the FlawPilot chip is active on your message, or ChatGPT answers from its own knowledge instead of running a scan.

**Try it:** open a new chat, check the FlawPilot chip is on, and ask:

```text
@FlawPilot Scan example.com and summarise the highest-severity findings
@FlawPilot Get AI fixes for the high-severity findings in my latest code scan
```

### Claude.ai and Claude Desktop

1. **Connect FlawPilot.** Open **Settings → Connectors → Directory**, search `flawpilot`, click **Connect**, and approve your workspace. ([Step-by-step guide](https://docs.flawpilot.com/mcp-connect/claude).)
2. **Add the skills.** Download `<skill>-claude-web.zip` files from the [latest release](https://github.com/flawpilot-hq/flawpilot-agent-toolkit/releases/latest), then open **Customize → Skills → Upload a skill**. Each ZIP holds one skill. Your plan must allow skills and code execution.

The `-claude-web` ZIPs use a shorter description, because Claude.ai allows 200 characters.

**Try it:** start a new conversation (tools load when a chat begins) and ask:

```text
Scan example.com with FlawPilot and summarise the highest-severity findings
What did my last FlawPilot scan say about security headers?
```

### Cursor, VS Code Copilot, Windsurf and other agents

Install the skills with the [skills CLI](https://github.com/vercel-labs/skills). It detects the agents you have installed:

```bash
npx skills add flawpilot-hq/flawpilot-agent-toolkit                                    # pick skills interactively
npx skills add flawpilot-hq/flawpilot-agent-toolkit --skill url-scan triage fix        # or name them
npx skills add flawpilot-hq/flawpilot-agent-toolkit --list                             # see all 24
```

Then add the MCP server for the `flawpilot` skills. Cursor (`.cursor/mcp.json`) and most other clients take:

```json
{
  "mcpServers": {
    "flawpilot": { "url": "https://mcp.flawpilot.com/mcp" }
  }
}
```

VS Code uses `.vscode/mcp.json` with `"servers"` and `"type": "http"`. If your client has no OAuth sign-in, create a key under **Settings → API keys** in FlawPilot and send it as an `Authorization: Bearer` header. The [MCP setup guide](https://docs.flawpilot.com/mcp-connect) has a snippet for each client.

**Try it:** open your editor's agent chat (Cursor Agent, Copilot agent mode, Windsurf Cascade) and ask:

```text
Scan https://staging.example.com with FlawPilot, then fix the missing headers in our nginx config
Review this diff for security issues
```

### Manual (clone and copy)

```bash
git clone https://github.com/flawpilot-hq/flawpilot-agent-toolkit.git flawpilot-agent-toolkit
cp -r flawpilot-agent-toolkit/plugins/*/skills/* .agents/skills/   # or .claude/skills/, ~/.codex/skills/
```

### If it doesn't work

Ask your assistant to use the `connect` skill (missing tools, sign-in loops) or the `errors` skill (failed scans, 401, 429). Start a new conversation after connecting: assistants load tools when a chat begins.

## Usage

Ask in plain language. The agent picks the skill:

```
"Scan example.com with FlawPilot"                       → url-scan
"Run Site Health on my docs site, mobile"               → site-health
"Check my repo for leaked secrets and vulnerable deps"  → code-scan
"What should I fix first?"                              → triage
"Get FlawPilot's fixes for the high findings"           → ai-fixes
"Fix the missing CSP header"                            → fix
"Add a FlawPilot gate to our GitHub Actions"            → ci
"Why is my LCP so slow?"                                → core-web-vitals
"Review this PR for security issues"                    → secure-code-review
"Add Product schema to this page"                       → structured-data
```

You can also call a skill by name: `/flawpilot:url-scan` in Claude Code, `$flawpilot:url-scan` in Codex (skills installed with `npx skills` drop the prefix: `/url-scan`, `$url-scan`). In ChatGPT, mention `@FlawPilot`.

## Examples

The prompts work the same in every client. The output below is illustrative; your scores and findings will differ.

<details open>
<summary><b>1. Scan a live site</b> (<code>url-scan</code>)</summary>

```text
You:   Scan https://shop.example.com with FlawPilot

Agent: Which project should this scan belong to?
         1. Shop (prj_8f2…)   2. Marketing site (prj_31c…)
You:   Shop. All four pillars, skip the email.

Agent: Starting a Quick Scan of https://shop.example.com in Shop
       (Security, Performance, Infrastructure, SEO, no email)…
       Scan finished in about two minutes.

       Band: ELEVATED_RISK (fix soon)
       Security 62 · Performance 88 · Infrastructure 74 · SEO 91

       Worst findings:
       1. HIGH    Missing Content-Security-Policy header
       2. HIGH    HSTS not set on the apex domain
       3. MEDIUM  SPF record allows any sender (+all)
       Showing 3 of 17 findings. Full report: <report link>

       Want me to rank everything, or get FlawPilot's fixes for the two HIGH findings?
```

What happened: `list_projects` → `trigger_scan` → `get_scan_status` until done → `get_scan_findings`. The agent asked for the project instead of guessing, and reported only the pillars that ran.
</details>

<details>
<summary><b>2. Scan a repo, rank, and fix</b> (<code>code-scan</code> → <code>triage</code> → <code>ai-fixes</code> → <code>fix</code>)</summary>

```text
You:   Check my-org/api for leaked secrets and vulnerable dependencies

Agent: my-org/api is connected and scans branch "main".
       Starting SECRETS and SCA… done.
         SECRETS  COMPLETED  score 40   3 findings (1 CRITICAL)
         SCA      COMPLETED  score 71  12 findings (0 CRITICAL, 4 HIGH)

You:   What should I fix first?

Agent: | # | Severity | Area    | Where                    | What                         | Effort |
       |---|----------|---------|--------------------------|------------------------------|--------|
       | 1 | CRITICAL | Secrets | config/stripe.ts:4       | Live API key in source       | Low    |
       | 2 | HIGH     | SCA     | package-lock.json        | jsonwebtoken 8.5.1 (CVE-…)   | Low    |
       | 3 | HIGH     | SCA     | package-lock.json        | axios 0.21.1 (CVE-…)         | Low    |
       Today: rotate the Stripe key first, then bump the two packages.

You:   Get FlawPilot's fixes for the HIGH ones

Agent: Requested 4 AI fixes (1 call). Ready after ~3 minutes.
       Fix 1/4 — jsonwebtoken
         Fix:   Upgrade to 9.0.0 or later.
         Why:   8.x accepts tokens signed with weak algorithms.
         Steps: 1. npm install jsonwebtoken@^9  2. Pass `algorithms` to verify()  3. Run tests
       Want me to apply this one?

You:   Yes

Agent: Here is the diff for package.json and src/auth/verify.ts:
       <diff>
       Apply it? (I won't edit anything until you say yes.)
```

The secret value is never printed. The agent says to rotate the key before removing it from code, and reminds you that a rescan only sees the fix after it is pushed to `main`.
</details>

<details>
<summary><b>3. Whole-site performance crawl</b> (<code>site-health</code>)</summary>

```text
You:   Run Site Health on https://docs.example.com, mobile

Agent: Starting a Site Health crawl (project Docs, mobile, no email)…
       Crawled 43 pages in about 14 minutes.
       Performance 0.71 · Accessibility 0.93 · Best practices 0.96 · SEO 0.98
       Compared with the run on 2026-10-01: Performance down from 0.78.
       Per-page results and screenshots are in the dashboard: <link>
```
</details>

<details>
<summary><b>4. Gate a CI pipeline</b> (<code>ci</code>)</summary>

```text
You:   Fail our GitHub Actions build if the staging scan has any critical findings

Agent: I'll add .github/workflows/flawpilot.yml. It triggers a Quick Scan of
       staging after deploy, waits for the result, and fails on any CRITICAL.
       Add FLAWPILOT_API_KEY as a repository secret (Settings → Secrets → Actions).
       <workflow file>
```
</details>

<details>
<summary><b>5. No FlawPilot account needed</b> (essentials packs)</summary>

```text
You:   Review this PR for security issues                 → secure-code-review
Agent: 2 findings, with evidence:
       HIGH   src/routes/user.ts:41  User id from the URL is used without an
              ownership check (IDOR). Fix: compare req.user.id to the record owner.
       MEDIUM src/db.ts:12           SQL built with string concatenation. Fix: use a
              parameterised query.

You:   Why is LCP 4.1s on our product page?               → core-web-vitals
You:   Add Product schema to this page                    → structured-data
You:   Set up CSP and HSTS for our Next.js app            → web-hardening
```
</details>

<details>
<summary><b>6. When something goes wrong</b> (<code>connect</code>, <code>errors</code>)</summary>

```text
You:   FlawPilot tools aren't showing up
Agent: Start a new conversation; tools load when a chat begins. If they are still
       missing, re-add the connector (steps for your client)…

You:   The code scan failed with INTEGRATION_REPO_NO_BRANCH
Agent: The repo has no branch assigned. An admin needs to pick one in FlawPilot →
       Integrations. Retrying won't help until then.
```
</details>

## Privacy and data handling

- The skills are plain-text instructions. This repo has no telemetry and stores no API key.
- The `flawpilot` plugin connects your AI client (Claude, ChatGPT, Codex, Cursor and others) to `https://mcp.flawpilot.com/mcp`. When you ask for a scan, the client sends what the tools need (project, URL, repository id, scan options) to FlawPilot. Results come back into your conversation, so your AI provider sees them too. See the [FlawPilot privacy policy](https://flawpilot.com/privacy).
- OAuth sign-in creates an API key in your FlawPilot workspace. Disconnecting the client does not revoke it; revoke it under **Settings → API keys**.
- `security-essentials`, `performance-essentials` and `seo-essentials` need no FlawPilot account and make no network calls on their own.
- The `ci` example scripts call only `https://api.flawpilot.com` and read the key from the `FLAWPILOT_API_KEY` environment variable.

## Develop locally

```bash
pip install -r requirements-dev.txt
python3 -m unittest discover -s tests          # validator and packaging tests
python3 scripts/validate_skills.py --strict .  # our rules (CONTRIBUTING.md checklist)
claude plugin validate . --strict              # official Claude Code validator
python3 scripts/package_skills.py              # build release ZIPs into dist/
```

Try your changes locally with `claude plugin marketplace add .` or `codex plugin marketplace add .`.

CI (`.github/workflows/validate.yml`) runs these checks plus a pinned gitleaks secret scan on every pull request. Pushing a `v*` tag builds the ZIPs and publishes a GitHub Release.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill checklist.

## License

[Apache-2.0](LICENSE)

---
name: ci
description: Add FlawPilot scans to a CI/CD pipeline using the REST API, with pass or fail gates on scores and critical findings. Use when the user asks to run FlawPilot in GitHub Actions, GitLab CI or any pipeline, gate a build or deploy on scan results, schedule nightly scans, or handle API keys and rate limits in CI.
---

# FlawPilot in CI/CD

Drive scans from a pipeline with the REST API (`https://api.flawpilot.com`) and an API key. The example scripts in `references/` implement the gates and are tested against a mock API.

## When to use

- The user wants a pipeline step that fails on bad scan results.
- The user wants nightly or post-deploy scans.
- The user asks how to store the key or avoid rate limits in CI.

## When NOT to use

- A one-off scan from chat. Use `url-scan`, `code-scan` or `site-health`.
- The user wants per-pull-request scanning of the PR's own code. FlawPilot cannot do that yet; see the next section.

## Which scan goes where

| Stage | Scan | Why |
|---|---|---|
| Post-merge on the default branch, or nightly | Code Scan | Scans the repository's assigned branch |
| After deploy to staging or production | Quick Scan | Needs a running site |
| Nightly or before a release | Site Health | Slow, capped at 8 triggers an hour |

**A code scan cannot scan a pull request.** The trigger takes only a repository and dimensions. It scans the branch assigned in Integrations, usually the default branch. Tell the user this up front. For per-PR feedback use a Quick Scan against a preview deployment.

## Setup

1. API key from the FlawPilot dashboard (Settings, API keys; Owner or Admin role). One key per pipeline, named for it.
2. Store it in the CI provider's masked secret store as `FLAWPILOT_API_KEY`. Never commit it, never print it, never run `curl -v` in a job.
3. Copy `references/fp-request.sh`, `references/quick-scan.sh` and `references/code-scan.sh` into the user's repo, for example under `scripts/`, keeping them side by side. Needs `curl`, `jq` and `awk`.
4. Find ids once: the project id from the projects list, and the repository id for a code scan from `list_integration_repos` or the repositories endpoint. Store them as CI variables.

## The gates

- **Quick Scan** (`quick-scan.sh`): env `PROJECT_ID`, `TARGET_URL`, optional `PILLAR` (default `score_security`), `MIN_SCORE` (default 70). Fails on `FAILED`, on timeout, on a missing score, or below the threshold. A `PARTIAL` scan is gradeable only if the pillar has a score.
- **Code Scan** (`code-scan.sh`): env `REPO_ID`, optional `DIMENSIONS`, `MAX_CRITICAL` (default 0). Fails on a failed dimension, on timeout, or on more critical findings than allowed.

Rules the scripts enforce, which must survive any edit:

1. A failed or timed-out scan is a **failure**, never a pass. No result is not a clean result.
2. A null or absent score is never treated as 0.
3. `findingsCount` counts every severity. Count criticals by asking each job for severity `CRITICAL` with a page size of 1 and reading the total.
4. Job ids come from the trigger response. The run status does not return them.
5. Scores are decimals. Compare with `awk`, not `[ -lt ]`.
6. Other 4xx responses fail at once without retry, because retrying a bad request burns quota.

## Example workflows

GitHub Actions, code scan after merge and nightly. Pin actions to a full commit SHA in real use.

```yaml
name: FlawPilot code scan
on:
  push:
    branches: [main]
  schedule:
    - cron: "0 3 * * *"
permissions:
  contents: read
jobs:
  code-scan:
    runs-on: ubuntu-latest
    env:
      FLAWPILOT_API_KEY: ${{ secrets.FLAWPILOT_API_KEY }}
      REPO_ID: ${{ vars.FLAWPILOT_REPO_ID }}
      MAX_CRITICAL: "0"
    steps:
      - uses: actions/checkout@v4 # v4.2.2
        with:
          persist-credentials: false
      - run: bash scripts/code-scan.sh
```

GitLab CI, post-deploy Quick Scan:

```yaml
flawpilot_scan:
  stage: verify
  image: alpine:latest
  variables:
    PROJECT_ID: "PRJ-XXXXX"
    TARGET_URL: "https://staging.example.com"
    MIN_SCORE: "70"
  before_script:
    - apk add --no-cache curl jq bash
  script:
    - bash scripts/quick-scan.sh
```

Set `FLAWPILOT_API_KEY` as a masked CI/CD variable.

## Rate limits

Limits are per workspace, so parallel jobs share them.

| Action | Limit |
|---|---|
| Any authenticated call, combined | 60 a minute |
| Trigger a Quick Scan | 5 a minute |
| Trigger a Code Scan | 10 a minute |
| Trigger Site Health | 8 an hour |
| Site Health reads | 30 a minute |

On `429` the response has a `Retry-After` header in seconds. The helper honours it. Polling every 10 to 15 seconds keeps one pipeline inside every limit. When many repositories scan in parallel, stagger the jobs or raise the poll interval, because 10 repos polling every 15 seconds already use 40 of the 60 requests a minute.

## Site Health in CI

Trigger it nightly and read results in the dashboard. A crawl can take a long time, so triggering without waiting is usually right. If gating, poll the check and compare the performance, accessibility and SEO scores, only after the status is `COMPLETED`.

Error codes are in the `errors` skill.

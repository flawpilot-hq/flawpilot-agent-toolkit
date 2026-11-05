---
name: secrets-hygiene
description: Find, rotate and prevent leaked secrets such as API keys, tokens, passwords and private keys in code, git history, CI logs and config. Use when a secret was committed or pasted, the user asks how to store credentials, wants pre-commit secret scanning, or needs to clean git history.
---

# Secrets hygiene

A leaked secret must be treated as compromised, even if it was removed quickly.

## When to use

- A key, token, password or private key appears in code, history, a log, a screenshot or chat.
- Setting up secret storage, rotation or scanning.

## When NOT to use

- Using a secret to access systems the user does not own.
- General authentication design. Use `api-security`.

## If a secret leaked

Do these in order. Rotation comes first.

1. **Revoke and rotate** the secret at the provider. Removing it from the repo does not make it safe, because history, forks, clones and caches keep it.
2. **Check for misuse:** review provider access logs, billing and audit trails for the window since exposure.
3. **Remove it from the code** and load it from the environment or a secret manager.
4. **Rewrite history only if needed** (compliance, or the repo is public and you want to reduce spread). Use `git filter-repo` or BFG, then force push and tell collaborators to re-clone. Rotation is still required afterwards.
5. **Add prevention** (below).

Never print the secret value back in chat, a commit message or a ticket. Refer to it by file, line and type.

## Where secrets hide

- Source files, example configs, test fixtures and notebooks.
- `.env` files committed by mistake, Docker build args, and image layers.
- CI logs and artifacts, `curl -v` output, error reports.
- Front-end bundles. Anything shipped to a browser is public.
- Shell history, screenshots, tickets and chat.

## Storage rules

- Use a secret manager or the platform's encrypted secrets. Keep local `.env` files out of version control with `.gitignore`.
- Give each secret the least privilege and a single purpose. One key per service or pipeline.
- Prefer short-lived credentials (OIDC, workload identity) to long-lived keys where the platform supports it.
- Set an expiry and a rotation schedule.
- Mask secrets in CI and never echo them.

## Prevention

- Pre-commit scanning, for example gitleaks, plus the same scan in CI on every pull request and on history.
- A `.env.example` with fake placeholders.
- Branch protection so scans cannot be skipped.
- Revoke unused keys and review key lists regularly.

## Output

List each finding as type, location, whether it appears valid, and the rotation owner. Then give the ordered action list. Say plainly if you cannot confirm whether a secret is live.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin.

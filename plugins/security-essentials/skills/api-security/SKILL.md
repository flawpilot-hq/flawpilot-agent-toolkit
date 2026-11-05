---
name: api-security
description: Review a REST or GraphQL API for security problems such as broken object-level authorization, weak authentication, mass assignment, missing rate limits, SSRF and token handling. Use when the user designs, builds or reviews an API, asks about IDOR, JWT or OAuth handling, rate limiting, or API authorization.
---

# API security

Review an API's design and code against the OWASP API Security Top 10 (2023 edition).

## When to use

- Designing or reviewing REST or GraphQL endpoints.
- Questions about IDOR, authorization, JWTs, API keys, OAuth scopes, rate limits or mass assignment.

## When NOT to use

- Attacking or fuzzing an API the user does not own.
- Browser-side hardening such as headers and cookies. Use `web-hardening`.
- General code review of non-API code. Use `secure-code-review`.

## Checklist (OWASP API Security Top 10:2023)

| ID | Risk | What to verify |
|---|---|---|
| API1 | Broken object level authorization | Every endpoint that takes an object id checks that the caller may access that object. Check reads, updates and deletes. |
| API2 | Broken authentication | Strong credential handling, token expiry and rotation, brute force protection, no secrets in URLs, JWT signature and `alg` verified, `aud` and `iss` checked |
| API3 | Broken object property level authorization | Responses expose only allowed fields. Requests cannot set protected fields (mass assignment, for example `role` or `isAdmin`). |
| API4 | Unrestricted resource consumption | Rate limits, pagination caps, payload size limits, query depth and cost limits for GraphQL, timeouts |
| API5 | Broken function level authorization | Admin and internal functions are separated and checked server-side, not just hidden in the client |
| API6 | Unrestricted access to sensitive business flows | Signup, purchase, reset and referral flows resist automation and abuse |
| API7 | Server-side request forgery | Server-side fetches of user-supplied URLs use allowlists and block internal ranges |
| API8 | Security misconfiguration | TLS only, no verbose errors or stack traces, CORS limited to known origins, unused methods disabled |
| API9 | Improper inventory management | Old versions and debug endpoints are retired, documentation matches what is deployed |
| API10 | Unsafe consumption of APIs | Responses from third-party APIs are validated like user input |

## Method

1. List the endpoints, their methods, the identity each requires, and the objects they touch.
2. For each object id in a path, query or body, ask: where does the code verify ownership or role? If the answer is "nowhere", it is a finding.
3. Compare the request model with the stored model to spot mass assignment.
4. Check limits at every layer that costs money or time.
5. For GraphQL, check introspection exposure in production, depth and complexity limits, and field-level authorization.

## Token handling

- Prefer short-lived access tokens with refresh rotation.
- Never put tokens in URLs or logs.
- Verify signatures with a fixed expected algorithm. Reject `none`.
- Revoke on logout and password change when the design allows.

## Output

For each finding give severity, the endpoint and file or line, the evidence (the missing check), the impact, a minimal fix, and your confidence. List what you did not check. Suggest tests: a request as user A for user B's object should return 403 or 404.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin.

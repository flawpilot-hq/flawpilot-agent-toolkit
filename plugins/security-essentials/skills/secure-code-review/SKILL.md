---
name: secure-code-review
description: Review code or a diff for security vulnerabilities such as injection, broken access control, weak crypto, SSRF, unsafe deserialization and path traversal, with evidence and fixes. Use when the user asks for a security review, to check code for vulnerabilities, to audit a pull request for security, or whether a change is safe.
---

# Secure code review

Review code the user owns for security flaws. Report only what you can support with the code in front of you.

## When to use

- A diff, file or module needs a security review.
- The user asks "is this safe?" about an endpoint, query, upload, auth check or crypto call.

## When NOT to use

- Penetration testing or exploiting systems. This skill reviews code defensively.
- Code the user does not own or have permission to review.
- A request for general style or performance review.
- Dependency CVEs only. Use an SCA tool or the `flawpilot` plugin's code scan.

## Method

1. Find the trust boundaries: where untrusted input enters (requests, files, queues, env, third-party responses) and where it reaches a sink (database, shell, filesystem, HTML, redirect, deserializer, outbound HTTP).
2. Trace each input to its sinks. A finding exists only if data crosses a boundary without the right control.
3. Check authentication and authorization on every entry point, not only the main flow.
4. Check how secrets, crypto and errors are handled.
5. Rank by impact and exploitability.

## Checklist (OWASP Top 10:2021 categories)

| Area | Look for |
|---|---|
| A01 Broken access control | Missing owner or role checks, IDs taken from the request without verifying the caller can access them, path traversal, CORS wildcards with credentials |
| A02 Cryptographic failures | Homegrown crypto, MD5 or SHA-1 for passwords, ECB mode, fixed IVs, hardcoded keys, TLS verification disabled |
| A03 Injection | String-built SQL, shell or LDAP commands, unsafe HTML rendering (XSS), template injection, NoSQL operator injection |
| A04 Insecure design | Missing rate limits on sensitive flows, no abuse case for money or account actions |
| A05 Security misconfiguration | Debug on, default credentials, verbose errors, permissive headers |
| A06 Vulnerable components | Outdated frameworks and libraries |
| A07 Identification and authentication failures | Weak session handling, no lockout, tokens that never expire, password reset flaws |
| A08 Software and data integrity failures | Unsafe deserialization, unsigned updates, untrusted CI inputs |
| A09 Logging and monitoring failures | No logging of auth events, secrets or personal data in logs |
| A10 SSRF | Server fetches a user-supplied URL without allowlist and without blocking internal addresses |

## Output format

For each finding:

- **Title and severity** (Critical, High, Medium, Low).
- **Where:** file and line.
- **Evidence:** the exact code path from input to sink.
- **Impact:** what an attacker gains, in one sentence.
- **Fix:** a minimal code change, using the safe API (parameterized queries, output encoding, allowlists, vetted libraries).
- **Confidence:** high, medium or low, and what you could not verify (for example, you did not see how the caller validates the value).

End with a short list of areas not reviewed.

## Rules

- No finding without a code path. Do not report a pattern match alone.
- Do not write working exploits. A short proof input that shows the flaw is enough.
- Do not call code "secure". Say what was checked and what was not.
- Cite standards by name and version, for example OWASP Top 10:2021 or a CWE id.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin.

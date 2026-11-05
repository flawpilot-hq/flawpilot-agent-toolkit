---
name: web-hardening
description: Harden a website's browser security and public configuration, including security headers, CSP, HSTS, cookies, TLS, and DNS email authentication (SPF, DKIM, DMARC). Use when the user asks to improve website security headers, fix a scanner report, set up a Content Security Policy, secure cookies, or configure email authentication.
---

# Web hardening

Improve what a visitor's browser and the public internet can see about a site the user controls.

## When to use

- A scan or audit lists missing headers, weak TLS or email spoofing risk.
- The user is setting up a new site, CDN or reverse proxy.

## When NOT to use

- Application logic flaws. Use `secure-code-review` or `api-security`.
- Probing sites the user does not own.
- Changing production without a rollback plan. Roll out gradually.

## Headers

| Header | Recommended | Notes |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enable only after HTTPS works everywhere. Add `preload` only on purpose, because removal from preload lists is slow. |
| `Content-Security-Policy` | Start in `Content-Security-Policy-Report-Only`, then enforce | Avoid `unsafe-inline` and wildcards. Prefer nonces or hashes. Set `frame-ancestors` too. |
| `X-Content-Type-Options` | `nosniff` | Safe everywhere. |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Or stricter. |
| `Permissions-Policy` | Disable unused features such as camera, microphone, geolocation | |
| `Cross-Origin-Opener-Policy` | `same-origin` | Needed for cross-origin isolation. |
| `Cross-Origin-Embedder-Policy` | `require-corp` or `credentialless` | Can break cross-origin resources. Test first. |
| `Cross-Origin-Resource-Policy` | `same-site` or `same-origin` for private assets | |

Remove headers that leak versions (`Server`, `X-Powered-By`) where practical.

## Cookies

Session cookies should set `Secure`, `HttpOnly` and `SameSite=Lax` (or `Strict`). Use the `__Host-` prefix for session cookies when possible. Keep lifetimes short.

## TLS

- Allow TLS 1.2 and 1.3 only. Disable older protocols and weak ciphers.
- Redirect HTTP to HTTPS and avoid mixed content.
- Automate certificate renewal and monitor expiry.
- Consider a `CAA` DNS record to limit which authorities can issue certificates.

## Email authentication (DNS)

- **SPF:** one TXT record listing allowed senders, ending in `-all` or `~all`. Stay within 10 DNS lookups.
- **DKIM:** sign outgoing mail and publish the public key.
- **DMARC:** publish `_dmarc` with `p=none` first to collect reports, then move to `quarantine` and `reject` once legitimate senders are aligned.
- Domains that send no mail should publish an SPF of `v=spf1 -all` and a `reject` DMARC policy.

## Method

1. Fetch the site's response headers (`curl -I` on the user's own site) and inspect cookies and TLS settings.
2. Compare with the tables above and list gaps by risk.
3. Give the exact config for the user's server or CDN (Nginx, Apache, Cloudflare, application middleware).
4. Recommend report-only or staged rollout for CSP, COEP and HSTS.
5. Tell the user how to re-check: `curl -I`, browser dev tools, or a rescan.

Do not claim a site is "secure" because headers are present. Headers reduce specific risks only.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin, whose URL scan grades headers, TLS, DNS and email authentication.

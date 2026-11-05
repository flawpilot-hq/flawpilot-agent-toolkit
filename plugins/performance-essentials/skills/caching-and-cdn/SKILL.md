---
name: caching-and-cdn
description: Configure HTTP caching, compression and CDN delivery for faster repeat visits and lower server load, including Cache-Control headers, immutable hashed assets, ETag, Brotli, HTTP/2 and HTTP/3. Use when the user asks about cache headers, CDN setup, slow time to first byte, compression, or why assets are not cached.
---

# Caching and CDN

Make the same bytes cheap to deliver again, and put them close to the user.

## When to use

- Lighthouse flags "serve static assets with an efficient cache policy" or no text compression.
- Time to first byte is high, or the origin takes too much traffic.
- The user is setting up or tuning a CDN.

## When NOT to use

- Application caching inside a database or app (that is backend work).
- Image, font and bundle size. Use `asset-optimization`.
- Security headers. Use the `web-hardening` skill from the `security-essentials` plugin.

## Cache-Control policy

| Resource | Header | Why |
|---|---|---|
| Fingerprinted assets (`app.3f9a1c.js`) | `Cache-Control: public, max-age=31536000, immutable` | The URL changes when the content changes, so it is safe to cache for a year |
| Unfingerprinted static files (logo, robots.txt) | `Cache-Control: public, max-age=3600` with `ETag` | Short lifetime and revalidation |
| HTML documents | `Cache-Control: no-cache` (revalidate every time) or a short `max-age` with `stale-while-revalidate` | Users should see updates quickly |
| Personalized or authenticated responses | `Cache-Control: private` or `no-store` | Never let a shared cache store one user's data |
| API responses | Depends on freshness. Use `ETag` and conditional requests where useful | |

Notes:
- `no-cache` means revalidate before reuse. `no-store` means do not store at all. They are different.
- Add `Vary` correctly (for example `Accept-Encoding`) so caches do not serve the wrong variant.
- Do not cache responses that set cookies unless you are sure they are not user-specific.
- Fingerprint assets in the build so long lifetimes are safe.

## Compression

- Enable Brotli for text (HTML, CSS, JavaScript, JSON, SVG) with gzip as a fallback.
- Do not compress already-compressed formats (JPEG, PNG, WebP, video).

## Protocols and connections

- Serve over HTTP/2 or HTTP/3.
- Use `preconnect` for critical third-party origins and keep their number low.
- Avoid redirect chains, which add round trips.

## CDN

- Cache static assets at the edge, and consider caching HTML for anonymous traffic with careful keys.
- Define the cache key (path, query, headers, cookies) deliberately. Strip tracking query parameters.
- Plan invalidation: purge by path or tag on deploy, or rely on fingerprinted URLs.
- Keep origin shielding and TLS to the origin on.
- Check that private content is never cached publicly.

## Method

1. Fetch headers for representative URLs (`curl -I` on the user's own site) and note `Cache-Control`, `ETag`, `Content-Encoding`, `Age` and the CDN's hit or miss header.
2. Compare with the policy table and list gaps.
3. Give exact config for the user's server or CDN.
4. Verify with a second request (expect a cache hit or a 304) and report time to first byte before and after.

Report measured changes. Do not promise a score.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin.

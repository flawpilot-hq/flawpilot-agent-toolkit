---
name: asset-optimization
description: Reduce page weight by optimizing images, fonts, JavaScript and CSS, including modern formats, responsive images, lazy loading, font loading, code splitting and removing unused code. Use when the user asks to make images smaller, fix large bundles, speed up font loading, lazy load content, or reduce unused JavaScript or CSS.
---

# Asset optimization

Send fewer bytes, and send the important ones first.

## When to use

- Lighthouse flags oversized images, unused JavaScript or CSS, render-blocking resources or font delays.
- The user wants smaller bundles or faster first render.

## When NOT to use

- Server response or caching problems. Use `caching-and-cdn`.
- Diagnosing which metric fails. Use `core-web-vitals`.
- Reading a full report. Use `page-speed-audit`.

## Images

- Use modern formats (AVIF or WebP) with a fallback where support matters.
- Serve the size needed: `srcset` and `sizes`, or an image CDN. Do not ship a 3000 px image into a 400 px slot.
- Set `width` and `height` to prevent layout shift.
- Lazy-load images below the fold with `loading="lazy"`. **Never** lazy-load the largest above-the-fold image. Give it `fetchpriority="high"`.
- Compress with a sensible quality (often 70 to 85). Compare visually before and after.
- Use SVG for icons and simple art, and minify it.
- Prefer video over animated GIF.

## Fonts

- Self-host and subset to the characters used. Prefer WOFF2.
- Limit weights and families.
- Use `font-display: swap` or `optional`, and a size-matched fallback to limit shift.
- Preload only the one or two fonts needed for the first paint.

## JavaScript

- Measure first with a bundle analyzer. Remove what is unused.
- Split by route and load heavy components on demand.
- Use `defer` or `async` for scripts, or `type="module"`.
- Replace big libraries with smaller ones or native APIs when the gain is real.
- Remove duplicate dependencies and enable tree shaking (ES modules, no side-effect imports).
- Delay third-party scripts (analytics, chat, tag managers) until after interaction or idle time, and drop ones nobody uses.
- Do not ship polyfills the target browsers do not need.

## CSS

- Inline the small critical CSS for first paint and load the rest without blocking.
- Remove unused rules (check coverage in dev tools on real pages, not just one).
- Avoid very large frameworks when a few components are used.

## Method

1. Measure the current weight and timing on the real page: transferred size, request count, LCP, long tasks.
2. List the largest assets and the biggest scripts.
3. Apply changes one group at a time, starting with the largest saving.
4. Re-measure under the same conditions and report bytes saved and the metric change.
5. Check for visual regressions and broken functionality, especially after removing code.

Report real before and after numbers. Do not promise a score.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin, whose scans flag performance issues on live pages.

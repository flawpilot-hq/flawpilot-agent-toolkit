---
name: core-web-vitals
description: Diagnose and fix Core Web Vitals problems, meaning slow Largest Contentful Paint (LCP), poor Interaction to Next Paint (INP) and layout shift (CLS). Use when the user asks about Core Web Vitals, a failing LCP, INP or CLS score, a slow-feeling page, layout jumping, or Lighthouse and PageSpeed results.
---

# Core Web Vitals

Core Web Vitals measure loading (LCP), responsiveness (INP) and visual stability (CLS). Fix the metric that fails, and measure again.

## When to use

- A report or tool says LCP, INP or CLS is poor.
- A page feels slow, janky or jumpy and the user wants the cause.

## When NOT to use

- Server-side or database slowness unrelated to the page. Profile the backend instead.
- Reading a whole Lighthouse report. Use `page-speed-audit`.
- Image, font and bundle weight work. Use `asset-optimization`.
- Cache and CDN configuration. Use `caching-and-cdn`.

## Thresholds (web.dev, measured at the 75th percentile of real users)

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP | 2.5 s or less | up to 4 s | over 4 s |
| INP | 200 ms or less | up to 500 ms | over 500 ms |
| CLS | 0.1 or less | up to 0.25 | over 0.25 |

INP replaced First Input Delay as a Core Web Vital in March 2024. Check current guidance on web.dev before quoting thresholds in a report.

## Lab versus field

Lab tools (Lighthouse) simulate one device and network. Field data (Chrome UX Report, real-user monitoring) comes from real visitors and decides pass or fail. Lab scores vary between runs, so use field data when it exists and use lab runs to find causes. INP needs real interactions, so a lab run only approximates it.

## LCP (loading)

Find the LCP element first (usually a hero image or heading). Then split the time into four parts: server response, resource discovery, resource download, and render delay.

- Slow response: cache HTML, use a CDN, cut server work.
- Late discovery: do not hide the LCP image behind JavaScript or CSS backgrounds. Put it in the HTML and add `fetchpriority="high"`. Never lazy-load the LCP image.
- Heavy download: right-sized modern formats, compression.
- Render delay: remove render-blocking CSS and scripts, inline critical CSS, avoid late font swaps.

## INP (responsiveness)

- Find slow interactions with the browser performance panel or field attribution data.
- Break up long tasks (over 50 ms). Yield to the main thread, move work to a worker, defer non-critical scripts.
- Reduce work in event handlers and rendering after input. Avoid large DOM updates.
- Audit third-party scripts. They often dominate.

## CLS (stability)

- Set `width` and `height` (or `aspect-ratio`) on images, video and embeds.
- Reserve space for ads, banners and late content.
- Use `font-display` with a size-adjusted fallback to limit font swap shifts.
- Animate with `transform` and `opacity`, not layout properties.
- Do not insert content above existing content after load.

## Method

1. Get the metric values and where they come from (field or lab, device, URL).
2. Identify the element or interaction responsible.
3. Choose the fix with the highest effect for the least change.
4. Make the change and re-measure under the same conditions. Report before and after values and the conditions.

Never promise a score or a ranking gain. State the measured change.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin, whose Quick Scan and Site Health check performance.

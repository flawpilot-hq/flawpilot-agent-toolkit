---
name: page-speed-audit
description: Read a Lighthouse or PageSpeed report, or audit a page's speed, and rank fixes by impact. Use when the user shares a Lighthouse report, asks why a site is slow, wants a performance audit or a prioritized list of speed fixes, or wants to compare runs before and after a change.
---

# Page speed audit

Turn a Lighthouse-style report into a short, ordered list of fixes with expected effect.

## When to use

- The user pastes or links a Lighthouse or PageSpeed result.
- The user wants a performance review of a page or template.
- Comparing speed before and after a release.

## When NOT to use

- A single failing Core Web Vital with a known element. Use `core-web-vitals`.
- Detailed image, font and bundle work. Use `asset-optimization`.
- Server caching and CDN setup. Use `caching-and-cdn`.

## Read the report correctly

- Scores are bands: 90 to 100 good, 50 to 89 needs improvement, below 50 poor.
- A dash or missing value means the category could not be assessed. It is not a zero.
- Lighthouse runs in a lab with simulated throttling. Mobile runs are much slower than desktop by design. A 30-point gap is normal, not a regression.
- Performance scores move several points between runs with no code change. Run at least three times and use the median, or compare trends.
- Findings of type "opportunity" show estimated savings. They overlap, so they do not add up.

## Method

1. Record the conditions: URL, device mode, throttling, Lighthouse version, date, and number of runs.
2. List the metrics: LCP, Total Blocking Time (a lab stand-in for responsiveness), CLS, Speed Index, plus field data if available.
3. Group failing audits by cause:
   - Network and server: slow response, no compression, no caching, redirects.
   - Render blocking: CSS and JavaScript in the head.
   - Payload: unoptimized images, unused JavaScript and CSS, large fonts.
   - Main thread: long tasks, heavy third-party scripts, large DOM.
   - Stability: unsized media, late content.
4. Fix template-level causes first. One shared template problem moves every page.
5. Order fixes by (estimated savings x pages affected) divided by effort. Cheap, high-impact fixes go first.

## Output

A table:

| # | Fix | Evidence (audit and value) | Expected effect | Effort |
|---|---|---|---|---|

Then: what to measure after, using the same conditions; what not to chase (tiny savings, scores above 90); and any caveats such as a single run.

## Rules

- Quote numbers from the report, not from memory.
- Do not promise a final score. Estimates are estimates.
- Distinguish lab data from field data in every statement.
- If only a screenshot or summary is available, say what is missing.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin, whose Site Health crawl scores many pages with Lighthouse.

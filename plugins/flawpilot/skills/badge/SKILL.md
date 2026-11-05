---
name: badge
description: Add a live FlawPilot score badge to a README, docs or website. Use when the user asks to show their FlawPilot score, add a security or health badge to a repository or site, or embed a FlawPilot badge in Markdown or HTML.
---

# FlawPilot embed badge

The badge is a hosted SVG that shows the site's latest overall score. A live badge updates itself after every rescan.

## When to use

- The user wants a score badge in a README, docs page or site footer.

## When NOT to use

- The user wants the score itself or a report. Use `url-scan`.
- The user has never run a scan. A badge is cut from a completed scan, so run one first.

## What you need

- A FlawPilot account and at least one completed scan of the site.
- The **site ID** from the FlawPilot dashboard badge tools. The MCP tools do not return it, so ask the user to copy it. Never make one up.

## Snippets

Replace `YOUR_SITE_ID` with the real value.

Markdown, for a README:

```markdown
[![FlawPilot Overall Score](https://api.flawpilot.com/v1/badge?site_id=YOUR_SITE_ID&pillar=overall&live=1)](https://flawpilot.com/scan/latest?site=YOUR_SITE_ID)
```

HTML, for a site:

```html
<a href="https://flawpilot.com/scan/latest?site=YOUR_SITE_ID">
  <img src="https://api.flawpilot.com/v1/badge?site_id=YOUR_SITE_ID&amp;pillar=overall&amp;live=1"
       alt="FlawPilot Overall Score" width="370" height="155" />
</a>
```

## Steps

1. Confirm a completed scan exists. If not, offer to run one with `url-scan`.
2. Ask for the site ID from the dashboard badge tools, and where the badge should go.
3. Insert the snippet in the right file (README.md, a layout, a footer component). Show the diff.
4. For a website, place it in the footer or a trust section and keep the link to the public report.

## Alt text

For a live badge keep the alt text generic, as above. The score changes after each scan, so a number in the alt text goes stale. If the user pins a badge to one fixed scan, put that scan's score in the alt text instead.

## Notes

- The badge shows a score from a public scan. Do not add it to a page if the user does not want visitors to see their score.
- Do not claim the badge means the site is secure. It reflects the latest automated scan only.

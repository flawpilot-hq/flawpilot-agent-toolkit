---
name: link-hygiene
description: Find and fix broken links, redirect chains and loops, orphan pages, weak anchor text and incorrect nofollow, sponsored or ugc attributes. Use when the user asks to audit links, fix 404s, clean up redirects after a migration, improve internal linking, or review outbound link attributes.
---

# Link hygiene

Working, meaningful links help users and crawlers find pages. Broken or tangled links waste both.

## When to use

- A crawl reports 404s, redirect chains or orphan pages.
- After a migration, redesign or URL change.
- Reviewing internal linking and outbound link attributes.

## When NOT to use

- Titles and metadata. Use `on-page-seo`.
- Whether pages are allowed in the index. Use `crawlability`.
- Buying, selling or exchanging links to influence rankings. Do not help with link schemes.

## Checks

| Problem | Why it matters | Fix |
|---|---|---|
| Broken internal link (404 or 410) | Dead end for users and crawlers | Update the link to the right URL, or restore the page, or remove the link |
| Broken external link | Poor experience and stale content | Replace, archive or remove |
| Redirect chain (A to B to C) | Slower, wastes crawl effort, can lose clarity | Point the link and the first redirect straight at the final URL |
| Redirect loop | Page unreachable | Break the loop |
| Wrong redirect type | A temporary `302` or `307` used for a permanent move | Use `301` or `308` for permanent moves |
| Soft 404 | Error page returns `200` | Return a real `404` or `410` |
| Redirects to unrelated pages | Confusing to users | Redirect to the closest equivalent, or return `410` if there is none |
| Orphan page | No internal links to it, hard to discover | Link it from relevant pages and navigation, or remove it |
| Weak anchor text | "Click here" says nothing | Use descriptive text that matches the target |
| Link on non-link elements | Crawlers follow `<a href>` | Use real anchor elements with `href` |
| Mixed content | HTTP links on HTTPS pages | Use HTTPS |

## Link attributes

- `rel="sponsored"` for paid or affiliate links.
- `rel="ugc"` for user-generated content links.
- `rel="nofollow"` when you do not want to vouch for or endorse the target.
- `target="_blank"` links should include `rel="noopener"` (modern browsers imply it, but it is harmless).

## Internal linking

- Link from strong, relevant pages to important ones.
- Keep important pages within a few clicks of the home page.
- Use breadcrumbs and related-content links where they help users.
- After a migration, update internal links to final URLs instead of leaning on redirects.

## Method

1. Crawl the user's own site (or analyze the crawl export they provide). Record each link's source, target, status, redirect path and anchor text.
2. Group issues by template, because one navigation or footer bug repeats across every page.
3. Fix at the source: templates, content, redirect rules.
4. For a migration, build a redirect map from old to new URLs, test it, and check for chains.
5. Re-crawl and report counts before and after.

## Rules

- Only crawl sites the user owns or has permission to crawl, and respect rate limits.
- Do not promise ranking changes. Report the issues fixed.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin, whose Site Health crawl and Quick Scan check SEO and link signals.

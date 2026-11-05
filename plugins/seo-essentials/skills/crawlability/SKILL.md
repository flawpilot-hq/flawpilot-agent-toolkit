---
name: crawlability
description: Diagnose why pages are not crawled or indexed, covering robots.txt, XML sitemaps, noindex, canonicals, HTTP status codes, redirects and JavaScript rendering. Use when pages are missing from search results, a crawler cannot reach a section, the user asks about robots.txt or sitemap.xml, or indexing reports show errors.
---

# Crawlability and indexing

A page can rank only if a crawler can fetch it, render it and is allowed to index it.

## When to use

- Pages are not appearing in search, or an indexing report shows exclusions or errors.
- Writing or reviewing `robots.txt` and sitemaps.
- Site migrations, new sections, or staging leaking into search.

## When NOT to use

- Titles, descriptions and headings. Use `on-page-seo`.
- Structured data. Use `structured-data`.
- Broken internal links. Use `link-hygiene`.

## What to check, in order

1. **Reachability:** the URL returns `200`, quickly, to a normal crawler user agent. Check for firewall or bot-protection blocks.
2. **robots.txt:** `/robots.txt` returns `200` and does not disallow the section by mistake.
3. **Indexing directives:** no unintended `noindex` in the robots meta tag or the `X-Robots-Tag` header.
4. **Canonical:** points to the right absolute URL, and that URL itself is indexable.
5. **Status codes and redirects:** permanent moves use `301` or `308`. Avoid chains and loops. Deleted pages return `404` or `410`, not a `200` "not found" page.
6. **Rendering:** key content and links exist in the rendered HTML. Links should be real `<a href>` elements.
7. **Discovery:** the page is linked from other pages and listed in the sitemap.

## robots.txt rules that cause trouble

- `robots.txt` controls crawling, not indexing. A blocked URL can still appear in results if others link to it.
- To keep a page out of search, allow crawling and use `noindex`. **Do not** block a page in `robots.txt` and rely on `noindex` there: the crawler never sees the tag.
- Do not block CSS or JavaScript that is needed to render the page.
- `robots.txt` is public. Do not use it to hide sensitive paths. Protect them with authentication.
- Mistakes such as `Disallow: /` after a staging launch are common. Check production.

## Sitemaps

- An XML sitemap lists canonical, indexable URLs that return `200`.
- Limits: 50,000 URLs or 50 MB uncompressed per file. Use a sitemap index beyond that.
- Reference it with `Sitemap: https://example.com/sitemap.xml` in `robots.txt` and submit it in the search engine's webmaster tools.
- Keep `lastmod` accurate or omit it.

## JavaScript sites

If content depends on client-side rendering, test what a crawler sees. Prefer server-side rendering or static generation for important pages. Do not rely on fragment-only URLs for routing.

## Output

A diagnosis table: URL or pattern, finding, evidence (status code, header, tag, rule), impact, fix. Include how to verify, for example the search engine's URL inspection tool for the user's own property, or `curl -I` on their own site.

Do not promise that fixing crawl issues will cause indexing or ranking. Search engines decide.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin.

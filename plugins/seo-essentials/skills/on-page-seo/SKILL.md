---
name: on-page-seo
description: Audit and improve on-page SEO elements such as title tags, meta descriptions, headings, canonical tags, image alt text, Open Graph tags and URL structure. Use when the user asks to improve a page's SEO, write titles or meta descriptions, fix duplicate or missing metadata, or review a page for search.
---

# On-page SEO

Make each page clearly say what it is, to people and to search engines.

## When to use

- Reviewing or writing page titles, descriptions, headings and metadata.
- A crawl reports missing, duplicate, too long or too short metadata.

## When NOT to use

- Crawling, indexing or robots problems. Use `crawlability`.
- Structured data. Use `structured-data`.
- Broken links and redirects. Use `link-hygiene`.
- Promising rankings. Nobody can, and this skill does not.

## Elements

| Element | Guidance |
|---|---|
| `<title>` | One per page, unique, describes the page, key topic first, brand last. Around 50 to 60 characters shows fully in most results, but search engines may rewrite titles. |
| Meta description | Unique, accurate summary that earns the click. Around 150 to 160 characters. It is not a ranking factor, and engines may use other text instead. |
| `<h1>` | One clear main heading that matches the page's purpose. Use `<h2>` and below in a logical outline. |
| Canonical | `<link rel="canonical" href="...">` pointing to the preferred absolute URL. Self-referencing on normal pages. |
| Images | Descriptive file names and meaningful `alt` text (empty `alt=""` for purely decorative images). Specify dimensions. |
| Open Graph and Twitter cards | `og:title`, `og:description`, `og:image` (with a suitable size) for share previews. |
| `lang` | Set `<html lang="...">` correctly. For multilingual pages use `hreflang` pairs that point to each other. |
| URLs | Short, readable, lowercase, hyphen-separated, stable. Avoid session ids and needless parameters. |
| Viewport | `<meta name="viewport" content="width=device-width, initial-scale=1">` for mobile. |

## Content

- Match the search intent: answer the question the page's keyword implies.
- Write for people first. Do not stuff keywords.
- Use descriptive link text, not "click here".
- Keep one main topic per page. Merge or redirect near-duplicates.

## Method

1. Fetch the page's rendered HTML and list title, description, headings, canonical, robots meta, alt text coverage and Open Graph tags.
2. Flag: missing, duplicate across pages, too long or too short, mismatched with the page, or contradictory (canonical pointing elsewhere, `noindex` present by mistake).
3. Propose specific replacements. For titles and descriptions, give the exact text, and keep each claim true to the page.
4. Prioritize by template: a shared template issue affects every page.
5. Say how to verify: view source, a crawler, or the search engine's inspection tool for the user's own property.

## Rules

- Do not promise ranking or traffic changes. Say what you changed and how to measure it.
- Do not invent facts, prices or reviews in snippets.
- Do not recommend hidden text, cloaking or link schemes. They violate search engine guidelines.
- Cite the guideline you rely on by name (for example Google Search Essentials) when it matters.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin, whose Quick Scan grades SEO on-page signals.

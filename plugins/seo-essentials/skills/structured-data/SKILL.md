---
name: structured-data
description: Add and validate schema.org structured data (JSON-LD) for rich results, such as Article, Product, FAQ, Organization, BreadcrumbList and LocalBusiness. Use when the user asks for schema markup, JSON-LD, rich snippets, or a structured data error needs fixing.
---

# Structured data

Structured data describes a page's content in a machine-readable form using the schema.org vocabulary. It can make a page eligible for rich results. It does not guarantee them.

## When to use

- Adding JSON-LD to articles, products, organizations, breadcrumbs, events, recipes, local businesses or video.
- Fixing errors or warnings from a structured data validator.

## When NOT to use

- Titles, descriptions and headings. Use `on-page-seo`.
- Crawl and indexing problems. Use `crawlability`.
- Marking up content that is not on the page. Do not do that.

## Rules

1. **Match the visible page.** Every marked-up fact (price, rating, author, date, answer) must also be visible to users on that page. Hidden or invented markup can lead to a manual action.
2. **Prefer JSON-LD** in a `<script type="application/ld+json">` block, generated from the same data as the page.
3. **Use the most specific type** and the properties search engines require or recommend for that type. Check the current documentation, because eligibility rules and supported types change.
4. **Do not fake reviews or ratings.** Self-serving review markup for your own business is generally not eligible.
5. **One entity, one description.** Reuse `@id` to link entities (for example the `Organization` that publishes an `Article`).
6. **Keep it current.** Update prices, availability and dates when they change.

## Common types

| Page | Type | Typical key properties |
|---|---|---|
| Any site | `Organization`, `WebSite` | `name`, `url`, `logo`, `sameAs` |
| Article or post | `Article` or `BlogPosting` | `headline`, `author`, `datePublished`, `dateModified`, `image` |
| Product | `Product` with `Offer` | `name`, `image`, `sku`, `offers.price`, `priceCurrency`, `availability` |
| Navigation | `BreadcrumbList` | ordered `ListItem` with `name` and `item` |
| Local business | `LocalBusiness` | `name`, `address`, `telephone`, `openingHours` |
| Q&A page | `FAQPage` | Only for real questions and answers on the page. Google limits rich result display for FAQ markup, so check eligibility. |

## Example (Article)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "How to cache static assets",
  "datePublished": "2026-01-15",
  "dateModified": "2026-03-02",
  "author": { "@type": "Person", "name": "Jane Doe" },
  "image": ["https://example.com/img/cache.jpg"]
}
```

## Method

1. Identify the page type and the visible facts.
2. Generate JSON-LD from the real data, with all required properties.
3. Validate with the schema.org validator and the search engine's rich results test, and fix errors. Warnings on recommended properties are optional but worth reading.
4. Deploy and re-test the live URL.
5. Monitor the enhancement reports in the search engine's webmaster tools for the user's own site.

## Output

Provide the JSON-LD block, where to place it, which visible content it mirrors, the validation steps, and the expected effect stated honestly: eligibility for rich results, not a guarantee and not a ranking boost.

For continuous automated scanning of source and live sites, see the `flawpilot` plugin.

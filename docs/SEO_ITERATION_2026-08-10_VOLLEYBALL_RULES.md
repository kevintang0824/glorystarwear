# SEO Iteration — Volleyball Rules and Commercial Intent Separation

Date: 2026-08-10

## Outcome

This iteration adds one rules-and-approval article, one reusable CSV record, and substantial unique content to two existing volleyball commercial pages. It is designed to improve topical coverage without creating three URLs that answer the same query.

## URL ownership

- `/products/volleyball-teamwear.html`: season program architecture across competition, practice, travel, staff, tournament, fan, replacement, allocation, delivery, and reorder continuity.
- `/products/volleyball-uniforms.html`: physical garment specification across jerseys, libero versions, bottoms, fit routes, artwork, numbers, marks, samples, roster data, labels, player packs, inspection, and production handoff.
- `/blog/volleyball-uniform-rules-checklist.html`: current competition and ruleset identification, official source, applicable requirements, evidence, authorized review, issue closure, and release.

## Research and evidence boundaries

Reddit discussions were used to identify buyer, player, and official language around number readability, libero contrast, ruleset differences, color preference, design, and supplier discovery. They were not used as rules or proof of a design failure.

The article links to current official hubs from USA Volleyball, NFHS, and NCAA, but explicitly requires the user to identify the actual country, competition, discipline, level, season, edition, interpretation, event manual, amendment, and approval authority. A manufacturer mockup, online summary, past approval, or single sample is not represented as universal certification.

## Discovery integrations

- Blog hub card and related-content link.
- Blog structured-data membership.
- RSS item.
- XML sitemap entry and updated product-page modification dates.
- `llms.txt` article and CSV links.
- Search Console inspection queue.
- Static audit markers for structured data, official sources, limitation text, download tracking, LCP preload, sitemap presence, and internal discovery.

## Validation and indexing boundary

Local validation can confirm crawlable HTML, self-referencing canonicals, structured data syntax, sitemap membership, internal links, XML syntax, and downloadable asset integrity. It cannot confirm Google indexing, Google-selected canonical, crawl date, or sitemap processing. Those fields must be checked after production deployment in Google Search Console URL Inspection and the Sitemaps report.

Final local validation recorded 108 HTML files, 105 sitemap URLs, 356 sitemap images, 108 unique canonicals, titles, descriptions, and JSON-LD blocks, maximum click depth 2, no unreachable indexable pages, and zero audit errors. The three updated pages contain approximately 1,116, 1,369, and 1,859 visible main-content words. Their five-word phrase-set overlap is about 1.31% for the two commercial pages, 0.20% for teamwear versus the rules article, and 0.95% for uniforms versus the rules article; shared navigation, volleyball terminology, and handoff links remain intentional.

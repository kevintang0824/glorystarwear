# Search Console Baseline — 2026-07-29

Property: `sc-domain:glorystarwears.com`

Source: live Google Search Console account, read on 2026-07-29. The selected report range was three months, but available data only covered 2026-07-13 through 2026-07-27.

## Performance

- Clicks: 2
- Impressions: 117
- CTR: 1.7%
- Average position: 55.7
- Search type: Web

### Leading observed queries

| Query | Clicks | Impressions |
| --- | ---: | ---: |
| `link:glorystarexport.com` | 0 | 7 |
| `white label fitness clothing` | 0 | 7 |
| `private label gym clothes` | 0 | 6 |
| `activewear private label` | 0 | 4 |
| `white label gym clothing` | 0 | 4 |
| `white label athletic wear` | 0 | 4 |
| `link:www.glorystarexport.com` | 0 | 3 |
| `private label fitness apparel` | 0 | 3 |
| `private label workout clothes` | 0 | 3 |
| `private label fitness products` | 0 | 3 |

The query table contained 32 rows. Only the leading 10 were captured because the Search Console interface connection became unstable while changing pagination. Do not infer query-level position from this table; position was not displayed in the captured query view.

### Leading landing pages

| Page | Clicks | Impressions | CTR | Average position |
| --- | ---: | ---: | ---: | ---: |
| `/` | 2 | 18 | 11.1% | 5.7 |
| `/products/private-label-gym-clothing.html` | 0 | 63 | 0% | 76.4 |
| `/private-label-activewear-manufacturer.html` | 0 | 8 | 0% | 88.1 |
| `/resources/custom-sportswear-tech-pack.html` | 0 | 7 | 0% | 12.9 |
| `/products/lookbook.html` | 0 | 4 | 0% | 15.8 |
| `/resources/teamwear-roster-packing-guide.html` | 0 | 3 | 0% | 13.3 |
| `/one-stop-service.html` | 0 | 3 | 0% | 15.0 |
| `/products/basketball-wear.html` | 0 | 3 | 0% | 25.0 |
| `/products/new-products.html` | 0 | 3 | 0% | 37.0 |
| `/products/compression-base-layers.html` | 0 | 3 | 0% | 38.3 |

## Indexing

Index report last updated: 2026-07-24.

- Indexed: 34
- Not indexed: 7
- Known URLs in this report: 41

| Exclusion reason | URLs | Action |
| --- | ---: | --- |
| Page with redirect | 5 | Expected unless a redirect target is incorrect |
| Alternate page with proper canonical | 1 | Expected if the declared canonical is intentional |
| Crawled - currently not indexed | 1 | Improve and re-crawl `/process.html` |

The affected crawled-not-indexed URL was `https://glorystarwears.com/process.html`; Search Console showed its last crawl as 2026-06-18.

## Sitemap

The sitemap was submitted and successfully processed on 2026-07-29.

- Submitted URL: `https://glorystarwears.com/sitemap.xml`
- Search Console status: Successfully processed
- Last read: 2026-07-29
- Pages discovered from the live sitemap: 90
- Videos discovered: 0

The live sitemap contained 90 page URLs when Google processed it. The optimized repository sitemap contains 91 URLs and 342 image entries because it also includes the new supplier due-diligence resource. After this release reaches production, Google can discover the additional URL during the next sitemap read.

## Decisions Applied

1. Keep the homepage title and primary message stable because it already earns clicks at position 5.7.
2. Map both white label fitness clothing and private label gym clothing intent to `/products/private-label-gym-clothing.html`.
3. Add a route comparison, exact buyer answers, descriptive internal anchors, and hero preload to that commercial page.
4. Add process-specific approval records, production evidence, inspection handoff, FAQ evidence, and hero preload to `/process.html`.
5. Recheck sitemap discovery, indexed URL count, and these landing pages after deployment and a 14–28 day recrawl window.

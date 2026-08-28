# SEO / GEO Sprint — 2026-08-25

## Objective

Increase qualified non-brand search visibility and inquiries without creating duplicate keyword pages or unsupported business claims.

## Implemented in this sprint

- Added an answer-first section to `/products/private-label-gym-clothing.html`, the strongest early non-brand impression page in the recorded Search Console baseline.
- Clarified white label, private label, and OEM routes in one citation-ready answer.
- Added contextual links to the broader manufacturer page and quote checklist.
- Reworked `/resources/custom-sportswear-tech-pack.html` around the recorded position-12.9 opportunity: the title, description, H1, and hero now lead with the free template, CSV format, and supported spreadsheet tools.
- Preserved the tech-pack URL and canonical while aligning its visible update date, Article schema, and sitemap `lastmod`.
- Changed the tech-pack contact link to the exact quote-form anchor so informational traffic lands at the intended conversion step.
- Strengthened `/low-moq-sportswear-manufacturer.html` with the exact custom-sportswear intent in its title and H1, an answer-first definition that avoids an unsupported universal MOQ, and a quote CTA that lands on the form.
- Added visible commercial context for the information required in an MOQ review and aligned the page modification date with its WebPage schema and sitemap entry.
- Clarified `/process.html` as the owner of sample, bulk, inspection, packing, and shipment approval gates, while linking wider coordination to `/one-stop-service.html`; this reduces overlap around the URL previously reported as crawled but not indexed.
- Updated the page `lastmod` in `sitemap.xml` after the material content change.
- Re-ran the local static SEO audit after the change.

## Owner actions required after deployment

### 1. Deploy

Deploy the repository root to the production Vercel project. Do not change the canonical domain from `https://glorystarwears.com`.

After deployment, open these URLs in a private browser window:

- `https://glorystarwears.com/`
- `https://glorystarwears.com/products/private-label-gym-clothing.html`
- `https://glorystarwears.com/sitemap.xml`
- `https://glorystarwears.com/robots.txt`

Confirm that the changed gym-clothing page contains the heading “What can a private label gym clothing manufacturer produce?” and that the sitemap shows `2026-08-25` for that URL.

### 2. Google Search Console

In the `sc-domain:glorystarwears.com` property:

1. Open **Sitemaps** and submit `https://glorystarwears.com/sitemap.xml` if it is not already listed.
2. Open **URL inspection** and inspect `https://glorystarwears.com/products/private-label-gym-clothing.html`.
3. Confirm that the user-declared canonical and Google-selected canonical match.
4. Select **Request indexing** once after the production change is live.
5. Inspect the homepage, `/sportswear-manufacturer.html`, `/private-label-activewear-manufacturer.html`, `/low-moq-sportswear-manufacturer.html`, and `/resources/custom-sportswear-tech-pack.html` without repeatedly requesting indexing.
6. Record whether each URL is indexed, the last crawl date, and any exclusion reason.

### 3. Export the evidence needed for the next sprint

From **Performance → Search results**:

1. Set date to **Last 3 months**.
2. Add a **Query** filter excluding `glorystarwear` and `glory star wear` when practical.
3. Export the **Queries** table as CSV.
4. Export the **Pages** table as CSV.
5. If the interface permits it, filter each of the five priority pages and export its query table.
6. Save the exports in a new local `reports/search-console/2026-08-25/` folder or provide them to the site maintainer.

Do not combine unrelated exports manually. Preserve the original Google column names and values.

### 4. Supply first-hand trust evidence

Prepare only facts and media that can be verified and publicly disclosed:

- legal business name and public business location;
- named sales or product-development contact and role;
- current factory, sample-room, material, measurement, inspection, packing, and shipment photos;
- photo date, location, subject, and whether the scene belongs to GloryStarWear or a disclosed production partner;
- certificate holder, issuer, number, scope, site, issue date, and expiry date;
- one anonymized real project with initial brief, product decisions, sample revisions, inspection checkpoints, and result.

Do not send confidential customer names or publish a certificate, capacity, MOQ, price, lead-time, factory-ownership, or client claim that cannot be substantiated.

### 5. Measurement window

Do not rewrite the page again immediately. Use these review windows:

- 7 days: confirm deployment, crawl, canonical, and index status;
- 28 days: compare impressions, clicks, CTR, position, and inquiry actions;
- 90 days: decide whether to expand, consolidate, redirect, or retain the page.

For a query at position 4–20 with at least 25 impressions, improve query-to-page fit, the direct answer, evidence, title, or internal links. For a page at position 1–10 with weak CTR, test the title and snippet before adding more content.

## Next implementation sprint

The next code changes should be selected from current Search Console exports, not the July baseline. Expected priorities are:

1. resolve any priority URL that remains crawled but not indexed;
2. improve pages already ranking at positions 4–20;
3. consolidate pages competing for the same query;
4. replace illustrative media with verified first-hand evidence;
5. connect GA4 or GTM and the durable lead receiver so organic and AI-assisted visits can be tied to qualified inquiries.

# Racket Sports SEO and GEO Iteration — 2026-08-10

## Outcome

Separated the site’s two overlapping racket-sports URLs into distinct search and buyer tasks, using current Reddit player discussions to deepen the questions without treating anecdotes as technical proof.

## Search-intent ownership

- `/products/racket-sports-apparel.html` owns tennis, pickleball, and padel program architecture: customer, venue, assortment roles, club, academy, league, event, resort, ecommerce, size demand, allocation, packing, delivery, and reorders.
- `/products/tennis-pickleball-apparel.html` owns physical garment specification and validation: tops, polos, shorts, skorts, dresses, liners, ball-pocket construction and load, serve coverage, court movement, moisture observations, care, representative sizes, evidence, and limitations.

The pages grew from about 330 and 443 visible words to about 1,159 and 1,979. Main-content sequence similarity is 0.026 after the separation.

## Reddit question signals

Current court-player discussions repeatedly raised:

- ball pockets that are too shallow, too deep, difficult to access, or allow excessive bounce;
- pocket bags that pull out or place a wet ball against the body;
- liners that ride up, restrict movement, or lack a usable ball-storage route;
- skirt, dress, short, and top lengths that change coverage during serving and movement;
- heavy sweat, garment saturation, seams, wash behavior, and short or tall fit proportions;
- the difference between functional court apparel and a wider club, retail, social, or athleisure program.

Reddit informs the product questions and player language only. The public pages require a named sample, ball load, player scope, movement sequence, condition, care route, evidence, and limitation before release.

## Published assets

- Expanded the broad racket-sports page with a direct answer, five-route program architecture, six planning gates, operational handoff links, and FAQs.
- Expanded the tennis and pickleball garment page with a direct answer, garment specification matrix, eight-step sample test, complaint-to-evidence mapping, source scope, FAQs, and a free worksheet.
- Added `/assets/downloads/tennis-pickleball-apparel-sample-checklist.csv`, a 41-field controlled sample record with instructions and one clearly labeled illustrative row.
- Added responsive AVIF hero preloads to both priority pages.
- Updated the sitemap, `llms.txt`, keyword ownership map, Search Console inspection queue, Reddit research log, asset manifest, README, and static regression coverage.

## Verification

The local static-site audit passes with:

- 104 HTML files;
- 101 sitemap URLs and 352 sitemap images;
- 104 unique canonicals, titles, and descriptions;
- 104 valid JSON-LD blocks;
- maximum click depth of 2;
- no unreachable indexable pages;
- no reported canonical, structured-data, FAQ-parity, asset, internal-target, sitemap, or LCP-preload errors.

The court-apparel CSV contains three rows, 41 columns per row, and unique headers.

## Post-deployment checks

After the GitHub and Vercel production deployment, verify both canonical pages and the CSV return HTTP 200, the two pages expose the expected direct-answer and download markers, and the production sitemap shows `2026-08-10` for both URLs.

Google indexing is not inferred from deployment. Inspect both URLs in Search Console after production is live and record Google-selected canonical, last crawl, indexing status, enhancements, and the next review date.

# GloryStarWear Search Visibility Review

Last updated: 2026-07-16

## Working Principle

Google AI Overviews and AI Mode use the same crawl, index, and ranking foundations as Google Search. There is no separate markup or keyword trick that guarantees an AI citation. The site should make useful buyer information crawlable, specific, internally connected, and supported by verifiable company evidence.

`llms.txt` is maintained as a concise reference for systems that choose to read it. Google states that `llms.txt` is not used for its AI search features, so it must not replace strong HTML pages, `robots.txt`, the sitemap, Search Console, or real business evidence.

## Implemented

### Crawl and Indexing

- Production canonical URLs use `https://glorystarwears.com`.
- `robots.txt` allows standard crawlers, `OAI-SearchBot`, and `ChatGPT-User`.
- `sitemap.xml` contains 83 unique canonical URLs with image entries and meaningful `lastmod` dates.
- The site includes a public IndexNow key and `scripts/submit-indexnow.mjs` for changed URLs.
- All indexable pages include a unique title, meta description, canonical, and one H1.
- Structured data is connected to the site Organization identity without invented prices, ratings, addresses, or certifications.

### Buyer Content

- The resource center maps a sourcing workflow from product brief to supplier comparison.
- The OEM vs ODM guide compares responsibilities, inputs, tradeoffs, hybrid routes, and quote requirements.
- The activewear MOQ guide explains style, material, color, component, packaging, and SKU-level constraints without publishing an unverified universal MOQ.
- The tech pack guide covers drawings, bill of materials, measurements, construction, artwork, packaging, QC, and version control.
- The activewear fabric selection guide separates fabric identity, composition, GSM, construction, stretch, recovery, opacity, color, evidence, sample approval, and bulk control. Its downloadable CSV turns those decisions into a reusable material record.
- The sample approval guide covers revision identity, materials, measurements, wearer fit, construction, artwork, packing, comments, and bulk sign-off.
- The activewear size grading guide separates base fit, grade rules, tolerances, product-specific measurements, inclusive range decisions, and size-set approval.
- The teamwear roster and packing guide covers structured player data, names, numbers, artwork control, revisions, individual packs, carton allocation, and reconciliation.
- Commercial pages link to factory, certificate, case, process, quality, resource, product, and contact pages where relevant.
- High-overlap product pairs now separate broad collection planning from garment-level specification intent; the ownership rules are recorded in `docs/SEO_KEYWORD_MAP.md`.
- Visible text avoids phrases written for "AI search" or "search intent" instead of the buyer.

### Measurement

- First-touch landing URL, referrer, `utm_*`, `gclid`, and `msclkid` values are kept in session storage.
- Prepared email and WhatsApp inquiries include source and campaign context.
- Visitors without a configured email client can copy a complete project brief for another messaging app.
- The fabric-selection, size-grading, and teamwear-roster guides include reusable CSV templates with anonymous download tracking.
- `window.dataLayer` receives vendor-neutral events for campaign landing, contact clicks, quote starts, email, WhatsApp and copied-brief actions, catalog filters, and catalog searches.
- No names, email addresses, phone numbers, or project-message content are sent to the data layer.

### Verification Baseline

- The first optimization sprint passed a local Chromium crawl with 79 sitemap URLs, no console errors, no key-page desktop or mobile overflow, and working attribution events.
- The current dependency-free static audit covers 84 HTML files and 83 sitemap URLs.
- It confirms 84 unique canonicals, 83 valid JSON-LD blocks, 86 internal targets, and 412 referenced local assets with no errors.
- Run `python3 scripts/audit_static_site.py` before deployment and after adding a page, link, canonical, schema block, or asset.
- The current 83-URL release passed a mobile Chromium crawl with no broken sitemap targets, H1 errors, console errors, page errors, or horizontal overflow.
- The fabric guide passed dedicated mobile and desktop checks for responsive images, schema types, CSV delivery, layout, and runtime errors. Axe 4.12 reported no WCAG A/AA violations; image-backed contrast candidates were also reviewed visually.
- Quick-contact containers use an explicit group role so their accessible labels are valid across the 19 pages that include the floating control.
- Indexed-page titles currently stay between 30 and 65 characters and descriptions between 100 and 170 characters.
- Under local simulated 4G and 4x CPU throttling, the homepage rendered at approximately 1.1 second LCP with zero CLS. Moving the below-fold service background to a lazy image reduced initial transfer from about 545 KB to 297 KB. These are lab measurements, not field Core Web Vitals.

## Production Launch Checklist

1. Deploy all HTML, CSS, JavaScript, images, `robots.txt`, `sitemap.xml`, `llms.txt`, the IndexNow key, and the `scripts` directory together.
2. Confirm the live key URL returns only the key value: `https://glorystarwears.com/8022fa20d2ef4befc52093d274ae7687.txt`.
3. Verify the production domain property in Google Search Console.
4. Submit `https://glorystarwears.com/sitemap.xml` in Search Console.
5. Inspect the homepage, resource center, and seven buyer guides with URL Inspection.
6. Run IndexNow only after the changed pages are live.
7. Connect the real GTM or GA4 property and map the existing data-layer events.
8. Record the deployment date so performance can be compared over 28-day and 90-day windows.

## Measurement Plan

Track outcomes by landing page, country, device, query theme, and inquiry source. Do not judge the work by impressions alone.

- Search Console: indexed pages, non-brand clicks, impressions, CTR, average position, query-page fit, and generative AI performance where available.
- Analytics: engaged sessions, product-to-contact clicks, quote starts, email submissions, WhatsApp submissions, and catalog interactions.
- Sales review: qualified inquiry rate, requested product, quantity range, target market, and whether the buyer supplied a usable brief.
- Content review: pages with impressions but weak CTR need better titles and snippets; pages with clicks but no inquiry path need stronger internal links or next steps.

## Highest-Value Next Work

1. Replace or supplement generated imagery with current factory, sample-room, material, measurement, inspection, packing, and shipment evidence.
2. Publish real project case studies with buyer type, initial brief, development decisions, approved scope, quality checkpoints, and outcome. Remove confidential details rather than inventing them.
3. Add a real form endpoint with success and failure states. The current static form prepares an email or WhatsApp message but cannot confirm server-side lead delivery.
4. Add verified company facts only when supporting evidence is available: business entity, location, production scope, relevant markets, current certificates, and named contact ownership.
5. Consolidate overlapping product intent. Broad category pages should explain collection planning; narrower pages should focus on product-specific construction, specifications, and use cases.
6. Build future guides from recurring sales questions, such as artwork preparation, packaging handoff, compliance evidence, and reorder planning.

## Editorial Rules

- One page owns one primary buyer decision; related pages should support rather than repeat it.
- Add first-hand photos, process notes, examples, and decision criteria before adding another keyword variation.
- Never publish fixed MOQ, lead time, capacity, certificate, location, client, rating, or price claims without current evidence.
- Keep structured data consistent with visible content.
- Update sitemap dates only after meaningful page changes.
- Review internal links, canonicals, JSON-LD, mobile overflow, and conversion events before every deployment.

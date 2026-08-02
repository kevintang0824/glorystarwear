# GloryStarWear Search Visibility Review

Last updated: 2026-08-02

## Working Principle

Google AI Overviews and AI Mode use the same crawl, index, and ranking foundations as Google Search. There is no separate markup or keyword trick that guarantees an AI citation. The site should make useful buyer information crawlable, specific, internally connected, and supported by verifiable company evidence.

`llms.txt` is maintained as a concise reference for systems that choose to read it. Google states that `llms.txt` is not used for its AI search features, so it must not replace strong HTML pages, `robots.txt`, the sitemap, Search Console, or real business evidence.

## Implemented

### Crawl and Indexing

- Production canonical URLs use `https://glorystarwears.com`.
- The `www` hostname permanently redirects to the apex canonical host while preserving the requested path.
- `robots.txt` allows standard crawlers, `OAI-SearchBot`, and `ChatGPT-User`.
- `sitemap.xml` contains 93 unique canonical URLs with image entries and meaningful `lastmod` dates.
- The site includes a public IndexNow key and `scripts/submit-indexnow.mjs` for changed URLs.
- All indexable pages include a unique title, meta description, canonical, and one H1.
- Structured data is connected to the site Organization identity without invented prices, ratings, addresses, or certifications.

### Buyer Content

- The resource center maps a sourcing workflow from product brief to supplier comparison.
- The OEM vs ODM guide compares responsibilities, inputs, tradeoffs, hybrid routes, and quote requirements.
- The activewear MOQ guide explains style, material, color, component, packaging, and SKU-level constraints without publishing an unverified universal MOQ.
- The tech pack guide pairs a free 40-row CSV intake template with drawings, bill of materials, measurements, construction, artwork, packaging, QC, and version-control guidance. It states clearly that the blank register does not replace garment-specific drawings, graded measurements, production artwork, or approval.
- The logo and artwork guide separates editable source files, vector and raster behavior, rights confirmation, method-specific handoff, substrate, dimensions, placement, color, production files, and physical sample evidence. Its 35-field CSV controls one row per artwork application without claiming one universal production-file rule.
- The packaging and label handoff guide separates component sourcing from the buyer's release record across label copy, component files, SKU and barcode data, folding, individual packs, carton assortment, marks, destinations, packed samples, inspection evidence, and approval. Its 45-field CSV keeps those decisions in a reusable register without claiming one universal legal or retailer standard.
- The compliance checklist now owns product and market evidence planning across applicability, labels, tests, reports, certificates, declarations, claims, corrective action, approval, release, and retention. Its 47-field CSV functions as an evidence index without presenting one universal test list or claiming that GloryStarWear holds an unverified certificate or report.
- The activewear fabric selection guide separates fabric identity, composition, GSM, construction, stretch, recovery, opacity, color, evidence, sample approval, and bulk control. Its downloadable CSV turns those decisions into a reusable material record.
- The sample approval guide covers revision identity, materials, measurements, wearer fit, construction, artwork, packing, comments, and bulk sign-off. It connects to a 39-field CSV register for review evidence, open issues, approval decisions, and the controlled bulk-production reference.
- The process page now owns the revision-controlled sampling and production-release workflow, while the one-stop service page owns service scope and cross-stage handoff. The process page provides the same approval register as a direct working tool.
- The private label activewear page now turns broad manufacturer discovery into a 49-field collection-planning handoff across style roles, development routes, fit, grading, fabric, color, branding, packaging, sampling, launch priority, release, and reorders.
- The AQL inspection guide covers lot definition, the 2026 sampling-standard reference, defect classification, sportswear-specific checks, evidence, corrective action, and shipment release without reproducing licensed sampling tables.
- The activewear size grading guide separates base fit, grade rules, tolerances, product-specific measurements, inclusive range decisions, and size-set approval.
- The new-product development page turns a broad product gallery into a style-level launch or reorder brief with assortment roles, development routes, specification inputs, quantity planning, sample approvals, and a reusable CSV handoff.
- The product gallery now turns image-led discovery into a controlled shortlist task. Its 34-field CSV records the exact reference, features to keep or change, development route, product direction, fit, fabric, color, size, artwork, packaging, quantity, timing, owner, and next action while stating that a visual reference is not a production specification.
- The cost and lead-time guide now turns commercial research into a comparable supplier-quote task. Its 53-field CSV keeps product scope, cost components, minimums, schedule boundaries, delivery terms, exclusions, assumptions, payment terms, open questions, and next actions aligned without publishing or implying fixed commercial promises.
- The compression base layer page separates the broad training-wear assortment from garment-level use, fabric, fit, compression-zone, seam, artwork, care, packing, and sample-release decisions. Its downloadable CSV carries those controls into a reusable approval record.
- The teamwear roster and packing guide covers structured player data, names, numbers, artwork control, revisions, individual packs, carton allocation, and reconciliation.
- Commercial pages link to factory, certificate, case, process, quality, resource, product, and contact pages where relevant.
- High-overlap product pairs now separate broad collection planning from garment-level specification intent; the ownership rules are recorded in `docs/SEO_KEYWORD_MAP.md`.
- Visible text avoids phrases written for "AI search" or "search intent" instead of the buyer.

### Measurement

- First-touch landing URL, referrer, `utm_*`, `gclid`, and `msclkid` values are kept in session storage.
- Search, AI-assistant, social, paid, partner, referral, campaign, and direct sources are classified into non-personal `traffic_channel` and `traffic_source` values for data-layer events and prepared inquiries.
- Prepared email and WhatsApp inquiries include source and campaign context.
- Visitors without a configured email client can copy a complete project brief for another messaging app.
- WhatsApp and email clicks are tracked as contact intent, not successful lead delivery.
- The secure server submit control appears only when the Vercel endpoint confirms a real receiving webhook is configured; `lead_submit_success` is emitted only after that receiver returns success.
- The supplier-quote comparison, product-gallery shortlist, collection-development, private-label-activewear, gym-planning, compression, tech-pack, artwork-preparation, packaging-handoff, compliance-evidence, fabric-selection, size-grading, teamwear-roster, pre-shipment inspection, and sampling-process pages include reusable CSV templates with anonymous download tracking.
- The supplier verification page includes a reusable evidence-request CSV that records claim, holder, scope, validity, verification method, disclosure level, owner, and review date.
- The manufacturer due-diligence guide adds an evidence ladder, ten-area verification workflow, escalation signals, authoritative public references, and a supplier-comparison CSV with decision gates.
- `window.dataLayer` receives vendor-neutral events for campaign landing, contact clicks, quote starts, email, WhatsApp and copied-brief actions, catalog filters, and catalog searches.
- No names, email addresses, phone numbers, or project-message content are sent to the data layer.

### Verification Baseline

- The first optimization sprint passed a local Chromium crawl with 79 sitemap URLs, no console errors, no key-page desktop or mobile overflow, and working attribution events.
- The current dependency-free static audit covers 96 HTML files and 93 sitemap URLs.
- It confirms 96 unique canonicals, 95 valid JSON-LD blocks, 111 internal targets, 765 referenced local assets, and matching AVIF coverage for all 511 referenced images with no errors.
- All 93 indexable URLs are reachable from the homepage within two internal-link clicks, with no orphaned indexable pages.
- Twenty-eight priority commercial and resource landing pages preload their responsive AVIF hero candidate with high fetch priority; the audit now prevents that coverage from silently regressing.
- Run `python3 scripts/audit_static_site.py` before deployment and after adding a page, link, canonical, schema block, or asset.
- The AQL guide and four upgraded commercial pages passed a 390-pixel mobile layout check with no horizontal overflow; the AQL guide also passed a 1280-pixel desktop review with all requested local assets returning successfully.
- The fabric guide passed dedicated mobile and desktop checks for responsive images, schema types, CSV delivery, layout, and runtime errors. Axe 4.12 reported no WCAG A/AA violations; image-backed contrast candidates were also reviewed visually.
- Quick-contact containers use an explicit group role so their accessible labels are valid across the 19 pages that include the floating control.
- Indexed-page titles currently stay between 30 and 65 characters and descriptions between 100 and 170 characters.
- Under local simulated 4G and 4x CPU throttling, the homepage rendered at approximately 1.1 second LCP with zero CLS. Moving the below-fold service background to a lazy image reduced initial transfer from about 545 KB to 297 KB. These are lab measurements, not field Core Web Vitals.

## Production Launch Checklist

1. Deploy all HTML, CSS, JavaScript, images, `robots.txt`, `sitemap.xml`, `llms.txt`, the IndexNow key, and the `scripts` directory together.
2. Confirm the live key URL returns only the key value: `https://glorystarwears.com/8022fa20d2ef4befc52093d274ae7687.txt`.
3. Verify the production domain property in Google Search Console.
4. Submit `https://glorystarwears.com/sitemap.xml` in Search Console.
5. Inspect the homepage, resource center, and priority buyer guides with URL Inspection.
6. Run IndexNow only after the changed pages are live.
7. Connect `LEAD_WEBHOOK_URL` to an owned CRM, automation flow, or server inbox and verify durable receipt before enabling the secure submit route.
8. Connect the real GTM or GA4 property and map the existing data-layer events.
9. Record the deployment date so performance can be compared over 28-day and 90-day windows.
10. Follow `docs/SEARCH_CONSOLE_RUNBOOK.md` to export query or page performance and generate a prioritized opportunity report with `scripts/analyze_search_console.py`.

## Measurement Plan

Track outcomes by landing page, country, device, query theme, and inquiry source. Do not judge the work by impressions alone.

- Search Console: indexed pages, non-brand clicks, impressions, CTR, average position, query-page fit, and generative AI performance where available.
- Analytics: engaged sessions, product-to-contact clicks, quote starts, email submissions, WhatsApp submissions, and catalog interactions.
- Sales review: qualified inquiry rate, requested product, quantity range, target market, and whether the buyer supplied a usable brief.
- Content review: pages with impressions but weak CTR need better titles and snippets; pages with clicks but no inquiry path need stronger internal links or next steps.

## Highest-Value Next Work

1. Replace or supplement generated imagery with current factory, sample-room, material, measurement, inspection, packing, and shipment evidence.
2. Publish real project case studies with buyer type, initial brief, development decisions, approved scope, quality checkpoints, and outcome. Remove confidential details rather than inventing them.
3. Connect the deployed Vercel lead endpoint to a real receiving webhook and test durable delivery. Until then, WhatsApp remains the primary working route and email remains a local-client fallback.
4. Add verified company facts only when supporting evidence is available: business entity, location, production scope, relevant markets, current certificates, and named contact ownership.
5. Complete the due-diligence scorecard for GloryStarWear with current business, payment, operating-scope, product, certificate, sample, and quality evidence that can be disclosed publicly or under NDA.
6. Consolidate overlapping product intent. Broad category pages should explain collection planning; narrower pages should focus on product-specific construction, specifications, and use cases.
7. Build future guides from recurring sales questions, such as reorder planning, only when the new task remains distinct from existing collection, roster, material, and sampling pages.

## Editorial Rules

- One page owns one primary buyer decision; related pages should support rather than repeat it.
- Add first-hand photos, process notes, examples, and decision criteria before adding another keyword variation.
- Never publish fixed MOQ, lead time, capacity, certificate, location, client, rating, or price claims without current evidence.
- Keep structured data consistent with visible content.
- Update sitemap dates only after meaningful page changes.
- Review internal links, canonicals, JSON-LD, mobile overflow, and conversion events before every deployment.

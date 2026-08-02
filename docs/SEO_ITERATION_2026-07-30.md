# SEO Iteration — 2026-07-30

Source baseline: `docs/SEARCH_CONSOLE_BASELINE_2026-07-29.md`

## Why these URLs were selected

| URL | Baseline signal | Iteration goal |
| --- | --- | --- |
| `/resources/custom-sportswear-tech-pack.html` | 7 impressions, average position 12.9 | Strengthen usefulness, earn links and downloads, and support movement from page two |
| `/products/lookbook.html` | 4 impressions, average position 15.8 | Align the H1 with product-gallery intent and make the category set machine-readable |
| `/one-stop-service.html` | 3 impressions, average position 15.0 | Clarify the service intent, inputs, deliverables, approvals, and buyer questions |

## Changes shipped in this iteration

- Added a 40-row sportswear tech pack intake CSV covering specification, materials, measurements, construction, artwork, packaging, approval, QC, bulk release, and revision control.
- Added visible download links and download-event attributes to the tech pack guide.
- Added a `DigitalDocument` reference to the article structured data and updated the article modification date.
- Changed a homepage evidence card to link directly to the tech pack guide with descriptive context.
- Added a direct-answer service definition and a stage/input/deliverable/approval table to the one-stop service page.
- Added visible one-stop service FAQs with matching `FAQPage` structured data.
- Added an LCP image preload and a future regression check for the one-stop service page.
- Aligned the lookbook H1 with the product-gallery search intent and added a structured `ItemList` for priority product categories.
- Updated sitemap modification dates and the AI-readable `llms.txt` summary.

## Measurement window

Do not judge the ranking effect from the first few days. Compare the 28 days after Google re-crawls the changed URLs with the prior 28 days, while also checking:

- indexed status and Google-selected canonical;
- impressions and average position by page;
- query mix for tech pack, product gallery, and one-stop sportswear service intent;
- organic CTR;
- `resource_download` events for `sportswear-tech-pack-intake-template`;
- assisted contact, WhatsApp, email, quote-start, and confirmed lead events.

## Phase 2 — traffic growth

Search Console overview checked on 2026-07-30:

- 2 total clicks remained visible in the overview;
- 34 pages were indexed and 7 were not indexed;
- Google highlighted `/products/private-label-gym-clothing.html` as receiving more recent impressions than usual;
- breadcrumb enhancements showed 12 valid items and no invalid items;
- Core Web Vitals had insufficient field data.

The detailed query table was not used in this phase, so changes were limited to URLs already supported by the existing baseline or by the current Search Console overview.

| URL | Search signal | Phase 2 change |
| --- | --- | --- |
| `/products/private-label-gym-clothing.html` | 63 baseline impressions; Google now reports increasing recent impressions | Kept the current title and H1 stable; added a 34-field collection-planning CSV, visible instructions, download tracking, and `DigitalDocument` structured data |
| `/resources/teamwear-roster-packing-guide.html` | 3 impressions, average position 13.3 | Reframed the page around roster/template/CSV intent; expanded validation, revision, packing, and spreadsheet-import guidance |
| `/products/basketball-wear.html` | 3 impressions, average position 25.0 | Assigned broad custom basketball uniform manufacturer intent to the category parent and added manufacturing-route/approval detail |
| `/products/basketball-jerseys.html` | Supporting child page | Narrowed the child page to jersey construction and linked broad program intent back to the parent |
| `/faq.html` | Long-tail support | Changed the generic H1 to `Custom Sportswear Manufacturing FAQs` |

Additional authority work:

- replaced vague `Supplier Capabilities` link labels with `Private Label Sportswear Manufacturer` on key site templates;
- expanded the teamwear CSV to include roster revision, approval, replacement, and change-note fields;
- updated `llms.txt`, resource discovery, sitemap modification dates, and LCP regression coverage for changed priority pages.

### Phase 2 measurement

After deployment and recrawl, compare the following over a full 28-day window:

- impressions and average position for teamwear roster/template queries;
- impressions and landing-page ownership for basketball uniform versus basketball jersey queries;
- gym clothing impressions without a decline caused by title/H1 churn;
- `resource_download` events for `private-label-gym-collection-planner` and the teamwear roster CSV;
- indexed status and Google-selected canonical for all four changed priority URLs;
- organic and AI-assistant landings that continue to a quote, email, or WhatsApp action.

## Phase 3 — compression intent and sample evidence

The first Search Console window showed `/products/compression-base-layers.html` with 3 impressions at an average position of 38.3. The query detail was not available, so the existing title and H1 remain stable.

Changes in this phase:

- added a direct answer that defines the information needed for a production-ready compression base layer program;
- added a decision table connecting use, fabric, fit, compression zones, construction, artwork, packing, and release requirements to sample checks;
- added a downloadable CSV checklist for product identity, material, fit, construction, claims, sample review, packaging, bulk release, and inspection control;
- added matching `DigitalDocument` and expanded FAQ structured data without publishing unsupported pressure, medical, thermal, cooling, moisture, or durability claims;
- linked the specific compression page from the broader training-wear collection and added the canonical URL to its structured `ItemList`;
- added a contextual link from the activewear fabric guide so material research can continue to the relevant product specification page;
- added a responsive AVIF hero preload and regression coverage for the compression page;
- updated the sitemap, `llms.txt`, keyword ownership map, and priority URL inspection set.

### Phase 3 measurement

After deployment and recrawl, compare a full 28-day window with the prior period:

- impressions, query mix, clicks, CTR, and average position for the compression page;
- whether broad training-wear queries remain with `/products/training-wear.html` while compression-specific queries move to the dedicated page;
- `resource_download` events for `compression-base-layer-sample-checklist`;
- indexed status, Google-selected canonical, and structured-data validity;
- organic or AI-assistant landings that continue to the fabric guide, sample guide, contact, email, or WhatsApp action.

## Phase 4 — new product development brief

The first Search Console window showed `/products/new-products.html` with 3 impressions at an average position of 37.0. Query detail was unavailable, so the existing title and H1 remain stable.

Changes in this phase:

- added a direct answer defining the inputs required for a new sportswear product development brief;
- added a decision table covering commercial role, development route, style specification, assortment and quantity, sample approval, and launch handoff;
- added a downloadable collection-development CSV with one clearly marked illustrative row and fields for style-level specification, quantity, artwork, labels, packaging, evidence, sampling, approval, and next actions;
- added visible development FAQs with matching structured data and a `DigitalDocument` reference for the CSV;
- linked the brief to the tech-pack checklist, quote checklist, and contact path;
- added a responsive AVIF hero preload and regression coverage;
- updated the keyword map, priority URL inspection set, sitemap, `llms.txt`, and search-visibility review.

### Phase 4 measurement

After deployment and recrawl, compare a full 28-day window with the prior period:

- impressions, query mix, clicks, CTR, and average position for the new-product page;
- whether broad development and collection-planning queries remain with this page while garment-specific queries land on the relevant category page;
- `resource_download` events for `sportswear-collection-development-brief`;
- indexed status, Google-selected canonical, and structured-data validity;
- continuations to the tech-pack guide, quote checklist, contact, email, or WhatsApp action.

## Phase 5 — sampling process indexability and approval evidence

The first Search Console coverage window showed `/process.html` as the only URL in `Crawled - currently not indexed`, with a displayed last crawl date of 2026-06-18. The page already explained the overall workflow, so this phase did not change its stable title or H1. It instead made the page's buyer task more distinct from `/one-stop-service.html` and the sample checklist.

Changes in this phase:

- defined when a sportswear sample is ready to control bulk production, including sample identity, linked evidence, decision language, and the controlled production reference;
- added a 39-field sampling and production approval CSV with one clearly marked illustrative row covering sample and file revisions, material, measurement, fit, construction, artwork, labels, packaging, evidence, open issues, approval, and bulk release;
- exposed the CSV from the process hero, the process control section, and the sample approval guide, with anonymous download tracking and `DigitalDocument` structured data;
- clarified page ownership: the one-stop page owns service scope and cross-stage handoff, the sample guide owns inspection questions, and the process page owns revision-controlled sampling and production release;
- added contextual links from the manufacturer, one-stop service, quality, and sample approval pages;
- updated modification dates, sitemap signals, `llms.txt`, and static regression coverage without adding unsupported factory, lead-time, price, MOQ, or certification claims.

### Phase 5 measurement

After deployment, request re-indexing for `/process.html` and compare a full 28-day window after Google re-crawls it with the prior period:

- indexed status, last crawl, and Google-selected canonical for the process page;
- impressions, clicks, CTR, and query mix for custom sportswear sampling, sample revision, pre-production sample, and bulk-release intent;
- whether one-stop service queries remain with `/one-stop-service.html` while sampling-process queries move to `/process.html`;
- `resource_download` events for `sampling-production-approval-register`;
- continuations from the process page to the sample checklist, tech-pack guide, quality page, contact, email, or WhatsApp action.

## Phase 6 — private label activewear collection planning

The first Search Console window showed `/private-label-activewear-manufacturer.html` with 8 impressions at an average position of 88.1, while `activewear private label` appeared among the leading queries. The page already had the exact commercial title and a broad product range, so this phase kept its title and H1 stable and added a collection-level working tool instead of repeating generic manufacturing claims.

Changes in this phase:

- reframed the meta description around planning a private label activewear collection while retaining OEM, ODM, product, fabric, fit, sampling, branding, and packaging relevance;
- added a 49-field activewear collection CSV with one clearly marked illustrative row and fields for market, customer, style role, product, route, fit, grading, fabric behavior, color, construction, branding, packaging, quantity assumptions, sample evidence, bulk release, launch priority, and reorder control;
- exposed the planner from the hero and collection-control section with anonymous download tracking and `DigitalDocument` structured data;
- added a visible collection-brief FAQ with matching FAQ structured data and a current modification date;
- strengthened contextual links from the homepage, activewear fabric guide, activewear grading guide, and tech-pack guide;
- clarified that the commercial parent owns multi-style activewear planning while gym, yoga, seamless, and plus-size pages retain their narrower product and buyer tasks;
- updated the sitemap, `llms.txt`, keyword map, and static regression coverage without adding unsupported MOQ, price, lead-time, fabric-performance, location, or certification claims.

### Phase 6 measurement

After deployment and recrawl, compare a full 28-day window with the prior period:

- impressions, clicks, CTR, and average position for the activewear manufacturer page;
- query ownership for `private label activewear manufacturer`, `activewear private label`, and collection-planning variants;
- whether white-label gym queries remain with `/products/private-label-gym-clothing.html`;
- `resource_download` events for `private-label-activewear-collection-planner`;
- continuations to fabric, grading, product-specific, sample, contact, email, and WhatsApp paths.

## Phase 7 — sportswear tech pack template discovery

The first Search Console window showed `/resources/custom-sportswear-tech-pack.html` with 7 impressions, no clicks, and an average position of 12.9. The URL was already indexed, useful, and close to page one, so this phase preserved the canonical and core checklist intent while improving the search result promise and template usability.

Changes in this phase:

- aligned the title, H1, social title, and description with `custom sportswear tech pack template` plus checklist intent without creating a competing template URL;
- identified the download honestly as a free, blank 40-row CSV intake register and explained the difference between the worksheet and a finished garment-specific tech pack;
- added a five-step quick start for row duplication, file references, open decisions, revision control, and supplier handoff;
- added a visible FAQ answer explaining that the template does not replace drawings, graded measurements, production artwork, or controlled approval, with matching FAQ structured data;
- expanded the `DigitalDocument` description and free-access disclosure while keeping the structured data aligned with the visible download;
- added responsive AVIF hero preloading and static regression coverage for LCP, template scope, current modification date, download tracking, and document schema;
- updated the sitemap, `llms.txt`, keyword map, asset manifest, and review documentation without inventing factory, price, MOQ, lead-time, download-count, or ranking claims.

### Phase 7 measurement

After deployment and recrawl, compare a full 28-day window with the prior period:

- impressions, clicks, CTR, and average position for the tech pack resource;
- query mix for `custom sportswear tech pack template`, `sportswear tech pack checklist`, `activewear tech pack template`, and related information-seeking variants;
- whether the page moves from its 12.9 baseline without losing the existing canonical or checklist relevance;
- `resource_download` events for `sportswear-tech-pack-intake-template`;
- continuations to sample approval, quote preparation, customization, contact, email, and WhatsApp paths.

## Phase 8 — sportswear logo and artwork preparation

The site repeatedly asked buyers to send logo files but did not own the underlying information task: how to distinguish source from preview files, connect artwork to a method and substrate, define scale and placement, confirm usage authority, and approve the actual production result. This phase created one dedicated resource instead of expanding the commercial customization page into a competing file-preparation article.

Changes in this phase:

- published `/resources/sportswear-logo-artwork-preparation-guide.html` with one clear source-file and artwork-release intent;
- explained true vector, raster, stable PDF preview, and reference-only screenshot roles without treating a filename extension as proof of production readiness;
- linked to current Adobe documentation for vector-versus-raster behavior and outlined text while keeping supplier-specific method requirements explicit;
- separated handoff and approval questions for full-panel sublimation, screen print, heat transfer or DTF, embroidery, patches, labels, and packaging;
- added repeatable controls for artwork IDs, dimensions, seam or panel references, offsets, orientation, colorway variants, production files, physical samples, rights confirmation, approval, and evidence;
- added a free 35-field artwork approval CSV with one clearly marked illustrative row and anonymous download tracking;
- added matching `Article`, `BreadcrumbList`, `FAQPage`, and `DigitalDocument` structured data plus a responsive AVIF hero preload;
- linked the new resource from the customization service, quote checklist, tech-pack guide, sample-approval guide, and resource center, while linking back to each next operational task;
- updated the sitemap, `llms.txt`, keyword map, asset manifest, and static regression coverage without claiming universal artwork specifications, intellectual-property clearance, production outcomes, or ranking gains.

### Phase 8 measurement

After deployment and recrawl, compare full 28-day and 90-day windows:

- indexing status, impressions, clicks, CTR, and average position for the artwork resource;
- query mix for sportswear logo file, custom apparel artwork preparation, vector logo for clothing, artwork placement, and method-specific variants;
- whether artwork-file intent remains with the new guide while decoration-method selection remains with `/customization.html`;
- `resource_download` events for `sportswear-artwork-approval-register`;
- continuations to customization, tech pack, sample approval, roster planning, quote preparation, contact, email, and WhatsApp paths.

## Phase 9 — sportswear packaging and label handoff

The commercial packaging page already owned supplier and component-range discovery, but buyers did not have a dedicated record for releasing label copy, component files, SKU and barcode data, folding, individual packs, cartons, destinations, packed samples, and approval. This phase created that operational resource without turning the supplier page into a competing checklist article.

Changes in this phase:

- published `/resources/sportswear-packaging-label-handoff-checklist.html` with one clear packaging-specification and supplier-handoff intent;
- separated component sourcing from the controlled buyer record, while keeping one-stop service focused on coordination across production, packing, and shipment;
- explained the distinction between SKU or item identity, buyer-assigned GTIN data, the printed barcode symbol, scan evidence, and carton reconciliation;
- linked to current GS1 barcode guidance and FTC clothing-and-textile guidance while stating that destination, retailer, marketplace, carrier, and product-specific requirements still need qualified confirmation;
- added a free 45-field CSV register for component artwork, required text, SKU and barcode data, folding, pack hierarchy, carton assortment, marks, destinations, physical samples, approval, inspection evidence, and open issues;
- added matching `Article`, `BreadcrumbList`, `FAQPage`, and `DigitalDocument` structured data plus responsive AVIF hero preloading;
- linked the guide from the commercial packaging page, one-stop workflow, quote checklist, tech-pack guide, artwork guide, AQL checklist, roster guide, and resource center;
- updated the sitemap, `llms.txt`, keyword map, asset manifest, and static regression coverage without claiming universal labeling law, barcode ownership, retailer acceptance, packing performance, or ranking gains.

### Phase 9 measurement

After deployment and recrawl, compare full 28-day and 90-day windows:

- indexing status, impressions, clicks, CTR, and average position for the packaging handoff resource;
- query mix for sportswear packaging checklist, apparel packaging specification, clothing label checklist, barcode handoff, carton packing, and related buyer tasks;
- whether supplier and component-range intent remains with `/products/private-label-sportswear-packaging.html` while specification and handoff intent stays with the resource;
- `resource_download` events for `sportswear-packaging-handoff-register`;
- continuations to packaging supply, one-stop service, tech pack, artwork, AQL inspection, quote preparation, contact, email, and WhatsApp paths.

## Phase 10 — sportswear compliance evidence file

Current search results contain distinct demand for apparel compliance checklists, testing evidence, labels, and buyer document readiness. The site already had a high-authority `/certificates.html` navigation page, so this phase upgraded that URL instead of publishing a competing compliance article.

Changes in this phase:

- retained `/certificates.html` as the canonical page and aligned its title and description with sportswear compliance checklist plus downloadable evidence-register intent;
- replaced a short certificate-name overview with a product-specific workflow covering product identity, intended user and use, market and channel, applicability, labels, tests, reports, certificates, declarations, claims, corrective action, approval, release, and record retention;
- added a free 47-field CSV that indexes one requirement or evidence item per row and links it to the actual style, material, sample, lot, report, label file, result, owner, release gate, and retention location;
- distinguished applicability decisions, test reports, certificates, supplier declarations, label approvals, and inspection records so one document is not presented as universal proof;
- linked to official NIST, FTC, CPSC, Your Europe, and European Commission entry points while stating that the responsible business must confirm the current requirement for the actual product and market with qualified support;
- added matching `Article`, `BreadcrumbList`, `FAQPage`, and `DigitalDocument` structured data and expanded static regression markers for every authoritative reference and download control;
- strengthened contextual links from the homepage-linked resource center, quality page, quote checklist, tech-pack guide, fabric guide, packaging guide, and AQL guide while preserving due-diligence, QC, and inspection intent boundaries;
- updated the sitemap, `llms.txt`, keyword map, asset manifest, and measurement documentation without claiming legal advice, a universal test list, or any certificate, accreditation, audit, or test report that has not been verified.

### Phase 10 measurement

After deployment and recrawl, compare full 28-day and 90-day windows:

- impressions, clicks, CTR, and average position for `/certificates.html`;
- query mix for sportswear compliance checklist, apparel compliance checklist, clothing compliance documents, textile testing evidence, label compliance, and certificate readiness;
- whether product-evidence intent stays with `/certificates.html`, supplier-verification intent stays with the due-diligence page, and inspection intent stays with the AQL page;
- `resource_download` events for `sportswear-compliance-evidence-register`;
- continuations to tech packs, fabric control, packaging, AQL inspection, supplier due diligence, quote preparation, contact, email, and WhatsApp paths.

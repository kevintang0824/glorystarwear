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

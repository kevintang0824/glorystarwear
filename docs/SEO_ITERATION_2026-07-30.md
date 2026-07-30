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

# SEO and lead-flow iteration — 2026-08-14

## Evidence boundary

The repository still has no Search Console query-plus-page export newer than the 2026-07-13 to 2026-07-27 baseline. Pages updated on 2026-08-12 have not had a full 28-day measurement window, so this iteration deliberately keeps their Title and H1 ownership stable.

The three evidence-led priorities are:

- `/products/private-label-gym-clothing.html`: 63 impressions, average position 76.4, with one white-label/private-label gym-clothing query family.
- `/resources/custom-sportswear-tech-pack.html`: 7 impressions, average position 12.9, the closest existing non-homepage URL to page one.
- `/one-stop-service.html`: 3 impressions, average position 15.0, with cross-stage commercial intent.

No synonym page was added for white-label fitness clothing, tech-pack templates, or one-stop sportswear service.

## Search and conversion changes

- Added a post-brief response scope, due-diligence path, sample-control path, quality path, and specific inquiry CTAs to the private/white-label gym-clothing page.
- Added a `Service` node aligned with the visible gym-clothing production-route table and marked the CSV planner as free. No price or `Offer` claim was added.
- Added the tech-pack page-end conversion bridge without changing its Title or H1. The quote checklist now links directly to the existing template owner.
- Added a first-screen one-stop order CTA, cost/lead-time handoff, WhatsApp product-list CTA, and descriptive body links from the homepage, manufacturer page, and process page.
- Added source-aware contact prefill routes for tech packs, artwork, fabrics and testing, packaging and labels, quality and inspection, sampling, and commercial planning.
- Kept the private-label activewear page responsible for broad collection intent and the process page responsible for sample revision and bulk-release intent.

## Inquiry infrastructure

The secure submission route is now designed as:

```text
browser form + Turnstile
  -> same-origin Vercel /api/lead
  -> authenticated Cloudflare Worker
  -> dedicated glorystarwear-leads D1 database
  -> confirmed insert
  -> thank-you page
```

Controls include field bounds, consent validation, a honeypot, Cloudflare Turnstile server verification, Origin checks, constant-time webhook secret comparison, a persistent per-email rate limit, a stable submission UUID, retry with the same UUID, a D1 primary-key deduplication constraint, and scheduled 365-day deletion. WhatsApp, email, and copy remain independent fallbacks.

## Quality gates

- The homepage resource section is excluded from the inaccurate `content-visibility` placeholder that caused mobile document-height jumps.
- The non-modal analytics consent UI now uses a valid `div` dialog container.
- GitHub Actions runs the full static audit, the Vercel lead-delivery contract test, and the Cloudflare Worker dry build/type check on pushes to `main` and on pull requests.

## Measurement plan

After the next 28-day Search Console window, compare query-plus-page results for the three priority URLs. Track impressions, average position, CTR, `resource_download`, `contact_click`, `quote_start`, `lead_submit_success`, `whatsapp_click`, and qualified inquiry outcomes. Do not test new titles until the post-update query ownership is visible.

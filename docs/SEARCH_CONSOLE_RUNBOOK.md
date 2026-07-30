# GloryStarWear Search Console Runbook

Updated: 2026-07-29

## Purpose

Use Google Search Console as a weekly decision system, not only as an indexing checkbox. The working loop is:

`crawl and index → impressions → query/page fit → clicks → inquiry events → qualified lead review`

## One-time setup

1. Create a Domain property for `glorystarwears.com`. Domain verification uses a DNS TXT record and covers HTTPS, HTTP, `www`, and non-`www` versions.
2. Submit `https://glorystarwears.com/sitemap.xml`.
3. Confirm the sitemap is processed without fetch or canonical errors.
4. Inspect the priority URLs listed below with URL Inspection.
5. Connect a real GTM or GA4 property to the existing vendor-neutral `dataLayer` events.
6. Keep Search Console and analytics access under company-owned accounts with at least two owners.

Do not add a placeholder verification token or analytics ID to the repository. Record the real property ID and account owner in the private company password manager.

## Priority URL inspection set

Inspect these URLs after the first verified deployment and after a significant template change:

1. `https://glorystarwears.com/`
2. `https://glorystarwears.com/sportswear-manufacturer.html`
3. `https://glorystarwears.com/low-moq-sportswear-manufacturer.html`
4. `https://glorystarwears.com/private-label-activewear-manufacturer.html`
5. `https://glorystarwears.com/custom-teamwear-uniforms.html`
6. `https://glorystarwears.com/products/private-label-gym-clothing.html`
7. `https://glorystarwears.com/process.html`
8. `https://glorystarwears.com/one-stop-service.html`
9. `https://glorystarwears.com/products/lookbook.html`
10. `https://glorystarwears.com/resources/custom-sportswear-tech-pack.html`
11. `https://glorystarwears.com/products/yoga-wear.html`
12. `https://glorystarwears.com/products/training-wear.html`
13. `https://glorystarwears.com/products/basketball-wear.html`
14. `https://glorystarwears.com/products/football-kits.html`
15. `https://glorystarwears.com/resources/`
16. `https://glorystarwears.com/resources/sportswear-manufacturer-due-diligence-checklist.html`
17. `https://glorystarwears.com/resources/private-label-activewear-moq.html`
18. `https://glorystarwears.com/resources/sportswear-aql-inspection-checklist.html`

For each URL, record:

- URL is on Google: yes/no.
- User-declared canonical and Google-selected canonical.
- Last crawl date and crawler type.
- Page fetch and indexing blockers.
- Enhancements or structured-data errors.
- The next action and review date.

## Weekly review

Use a 28-day period and compare it with the previous 28 days. Segment by country and device before changing a page.

1. Review Pages and Sitemaps for new indexing exclusions.
2. Export Performance data for non-brand queries and landing pages.
3. Identify queries at positions 4–20 with meaningful impressions.
4. Identify pages at positions 1–10 with weak CTR.
5. Confirm whether each query belongs to the ranking page.
6. Improve the direct answer, first-hand evidence, internal links, title, or next action as appropriate.
7. Review `contact_click`, `quote_start`, `whatsapp_click`, `email_click`, and confirmed `lead_submit_success` events by landing page and source channel.
8. Record what changed so the next comparison has a reliable date.

## CSV opportunity report

Export a Search Console table containing:

- Query and/or Page
- Clicks
- Impressions
- CTR
- Position

Then run:

```bash
python3 scripts/analyze_search_console.py path/to/export.csv \
  --output reports/search-console-opportunities.md
```

The script accepts common English Search Console column names, excludes GloryStarWear brand queries from opportunity sections, and produces:

- striking-distance opportunities;
- CTR opportunities;
- visible results with zero clicks;
- current non-brand winners.

For a query-to-page report, use an export or API result that includes both Query and Page columns. A query-only or page-only export is still useful, but cannot diagnose keyword cannibalization by itself.

## Event mapping

Map these existing events into the analytics property:

| Event | Meaning | Conversion status |
| --- | --- | --- |
| `session_landing` | First page and campaign/source classification | Diagnostic |
| `contact_click` | Visitor selected a contact route | Micro conversion |
| `quote_start` | Visitor interacted with the project form | Micro conversion |
| `whatsapp_click` | WhatsApp opened | Contact intent, not confirmed receipt |
| `email_click` | Email application opened | Contact intent, not confirmed receipt |
| `quote_copy_brief` | Project brief copied | Contact intent |
| `lead_submit_success` | Configured receiver confirmed durable acceptance | Primary conversion |
| `resource_download` | Buyer downloaded a planning asset | Content engagement |

Every event includes `traffic_channel`, `traffic_source`, and `referrer_host`. AI-assistant traffic is classified separately from organic search and ordinary referrals.

Google AI Overviews and AI Mode may use an ordinary Google Search referrer, so browser analytics cannot reliably split them from other Google organic visits. Use the generative-AI reporting available in Search Console for Google-specific visibility.

Never send names, email addresses, phone numbers, free-text project details, or document contents to analytics.

## Decision thresholds

Use thresholds as prompts for review, not automatic publishing rules:

- Indexed coverage: investigate any priority URL that is not indexed.
- Position 4–20 with at least 25 impressions: inspect relevance, evidence, and internal links.
- Position 1–10 with weaker-than-expected CTR: review title, snippet, and query intent.
- Clicks without contact intent: improve the next decision or CTA.
- Contact intent without qualified inquiries: review offer clarity, buyer fit, and form friction.
- AI-assistant visits without inquiries: review whether the cited/landing content connects clearly to a commercial next step.

## Monthly record

Keep one row per month with:

- valid indexed pages;
- non-brand clicks and impressions;
- top countries and devices;
- number of priority queries in positions 1–3, 4–10, and 11–20;
- organic-search, AI-assistant, referral, social, paid, and direct sessions;
- contact clicks, quote starts, WhatsApp clicks, email clicks, and confirmed leads;
- qualified inquiries by product and target market;
- pages published, materially updated, consolidated, or redirected;
- verified external mentions and backlinks earned.

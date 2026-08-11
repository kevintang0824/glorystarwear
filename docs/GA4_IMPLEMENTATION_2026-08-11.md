# GA4 Implementation — 2026-08-11

## Configuration

- GA4 Measurement ID: `G-3QHK9TGCHQ`
- Loader: shared `script.js`, included by every audited HTML page
- Loading model: basic Consent Mode; the Google tag is not requested until the visitor grants analytics permission
- Advertising controls: `ad_storage`, `ad_user_data`, and `ad_personalization` remain denied
- Google Signals and advertising-personalization signals are disabled in the page configuration
- Saved visitor choice: `glorystarwear-analytics-consent-v1` in first-party local storage

## Measurement

GA4 receives the existing site events only after permission, including:

- `session_landing` with the site's direct, organic search, AI assistant, social, campaign, referral, and paid-search classification;
- `quote_start`;
- `lead_submit_success` and the GA4 recommended `generate_lead` event after the server confirms receipt;
- `lead_submit_error`;
- `contact_click`, `whatsapp_click`, `email_click`, and `phone_click`;
- `resource_download` with the resource and file names;
- `catalog_filter`, `catalog_search`, and the GA4 recommended `search` event;
- `thank_you_view` only when a valid server-confirmed lead receipt is present.

Every event now includes the low-cardinality `page_type` and `content_group` context. Examples include `blog_article` / `editorial`, `product_page` / `product_catalog`, `resource_guide` / `buyer_resources`, `commercial_landing` / `manufacturing_services`, and `trust_page` / `trust`. Confirmed `generate_lead` events also include those fields plus the site's `traffic_channel` and `traffic_source` classification.

## GA4 admin configuration queue

After an authorized user opens the GA4 property, complete and verify these property-level settings:

1. Mark the recommended `generate_lead` event as a key event. Keep `lead_submit_success` available for diagnostic comparison; do not mark clicks or form starts as completed leads.
2. Register event-scoped custom dimensions for `page_type`, `content_group`, `traffic_channel`, `traffic_source`, `form_location`, `product_interest`, and `resource_name`.
3. Use Realtime or DebugView after granting analytics consent on a controlled test visit. Submit through the configured server receiver and verify exactly one `lead_submit_success` and one `generate_lead` after confirmed receipt.
4. Download one checklist and verify `resource_download`, `resource_name`, `file_name`, `page_type`, and `content_group` without personal data.
5. Link the Search Console domain property to GA4 under the company-owned accounts when access is available.

Custom-dimension registration and key-event status live in GA4, not this repository. They remain pending until the authenticated property is opened and verified.

Contact names, email addresses, phone numbers, free-text messages, and uploaded documents are not added to Analytics event parameters. The site's vendor-neutral event objects remain available separately in `window.siteDataLayer`; Google commands use `window.dataLayer` through `gtag()` so the same event is not emitted twice.

## Visitor controls

The first visit displays an analytics permission panel with Allow and Decline actions. Every page footer receives an `Analytics Choices` control, and the privacy page provides the same control so a visitor can change or revoke the stored choice.

## Verification boundary

Repository and production checks can verify the Measurement ID, consent defaults, conditional Google tag loader, event calls, updated privacy disclosure, syntax, and deployed assets. Realtime user activity and DebugView must still be confirmed inside the authenticated GA4 property after accepting analytics on a test visit; the numeric property ID or public website cannot prove that GA4 processed the event.

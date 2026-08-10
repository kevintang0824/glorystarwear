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

Contact names, email addresses, phone numbers, free-text messages, and uploaded documents are not added to Analytics event parameters. The site's vendor-neutral event objects remain available separately in `window.siteDataLayer`; Google commands use `window.dataLayer` through `gtag()` so the same event is not emitted twice.

## Visitor controls

The first visit displays an analytics permission panel with Allow and Decline actions. Every page footer receives an `Analytics Choices` control, and the privacy page provides the same control so a visitor can change or revoke the stored choice.

## Verification boundary

Repository and production checks can verify the Measurement ID, consent defaults, conditional Google tag loader, event calls, updated privacy disclosure, syntax, and deployed assets. Realtime user activity and DebugView must still be confirmed inside the authenticated GA4 property after accepting analytics on a test visit; the numeric property ID or public website cannot prove that GA4 processed the event.

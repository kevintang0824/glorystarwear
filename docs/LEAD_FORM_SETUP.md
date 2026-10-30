# GloryStarWear Server Lead Form Setup

Updated: 2026-10-30

## Current behavior

- The Contact page starts with five essentials: name, email, product interest, a short project description, and inquiry consent. Buyer type, development route, order details, reference materials, and contact preferences are optional.
- The secure server submit button is displayed only when the Vercel endpoint reports that the receiving webhook and Cloudflare Turnstile are configured and the verification widget initializes.
- Secure submission requires a valid Turnstile token. Vercel checks the allowed origin, required fields, consent, token verification, and the verification hostname before forwarding the inquiry.
- The authenticated Worker stores the inquiry in D1 before returning success. Its email-hash rate limit allows at most five attempts per 15-minute bucket, and stored inquiries expire after 365 days.
- `lead_submit_success` is recorded after a confirmed server response; GA4 receives `generate_lead` only with analytics consent. The Thank You page needs a short-lived receipt from that response. If browser storage is unavailable, confirmation is shown on the form instead.
- WhatsApp and email remain alternative send routes. Email opens the visitor's local email application. Opening either application or copying a brief is contact intent, not proof of a received lead.

## Required Vercel environment variables

Configure these for Production, Preview, and Development as appropriate:

- `LEAD_WEBHOOK_URL`: required HTTPS URL of the owned receiving Worker.
- `LEAD_WEBHOOK_SECRET`: required bearer token sent to the Worker; it must match the Worker's secret of the same name.
- `TURNSTILE_SECRET_KEY`: required server-side Cloudflare verification secret.
- `TURNSTILE_SITE_KEY`: public widget key returned by the endpoint when all required settings exist.

Keep secrets in deployment configuration, never in HTML, source control, logs, or a public response. The receiver returns HTTP 2xx only after D1 accepts the inquiry or confirms the same lead ID was already stored. This is persistence confirmation; no sales-notification or CRM integration is implied.

## Request contract and limits

The browser sends `payloadVersion: 2`. In addition to `name`, a valid `email`, `product`, composed `message`, and `consent: true`, v2 requires nonempty `projectDetails`. `buyerType` may be blank or absent. Legacy v1 requests remain supported; unknown versions are rejected.

`projectDetails` is limited to 3,000 characters. The composed `message` carries the project description plus buyer type, development route, reference links, selected filenames, and other supplied context. Both Vercel and the Worker retain up to 12,000 characters of that message. The Worker enforces a 128 KiB actual-body limit while streaming, before JSON parsing, including when `Content-Length` is missing or inaccurate.

The Worker stores buyer type, development route, and reference details inside the composed message. It does not currently persist `projectDetails` or `briefReadiness` as separate database fields. Do not interpret forwarded readiness metadata as a stored lead score.

## Webhook payload

```json
{
  "event": "lead.created",
  "source": "glorystarwears.com",
  "lead": {
    "payloadVersion": 2,
    "leadId": "generated UUID",
    "receivedAt": "ISO timestamp",
    "name": "Buyer name",
    "email": "buyer@example.com",
    "phone": "Optional phone",
    "buyerType": "Optional buyer type",
    "developmentRoute": "Optional development route",
    "product": "Product category",
    "quantity": "Optional quantity",
    "market": "Optional market",
    "timeline": "Optional timeline",
    "projectDetails": "The buyer's short project description",
    "message": "Project description and composed supporting context",
    "sourcePage": "Page where the inquiry started",
    "landingPage": "First landing URL",
    "referrer": "First referrer",
    "trafficChannel": "ai_assistant",
    "trafficSource": "chatgpt",
    "campaign": {
      "utm_source": "example"
    }
  }
}
```

## Activation checks

1. Add the environment variables without committing secrets to Git.
2. Redeploy the Vercel project.
3. Request `GET /api/lead` and confirm `configured: true` with a public `turnstileSiteKey`; never expect a secret in this response.
4. Run `node scripts/test_lead_flow.mjs`, `node scripts/test_lead_receiver.mjs`, and the frontend tests before deployment. These checks use synthetic data and do not deliver a real inquiry.
5. For an intentional end-to-end check, use a controlled email address and a clearly labeled test brief, complete Turnstile, and verify the record in the receiver.
6. Confirm the browser reached `/thank-you.html`, or shows the on-form receipt when session storage is unavailable.
7. With analytics consent, use GA4 DebugView to verify one success event and one `generate_lead` event without personal information. A configured endpoint alone does not prove GA4 reporting or sales follow-up works.
8. Test failure paths locally and confirm the site does not show success or open the Thank You page when the receiver fails.
9. Deploy Worker changes separately from the Vercel website. The 12,000-character persistence fix requires a Worker deployment, but no database migration.

## Source classification

The browser derives a non-personal source classification from the first referrer and campaign tags. The same values are added to vendor-neutral data-layer events and to a prepared inquiry:

- `organic_search`: Google, Bing, Yahoo, DuckDuckGo, Yandex, or Baidu.
- `ai_assistant`: ChatGPT, Perplexity, Gemini, Copilot, Claude, or You.com.
- `organic_social`: LinkedIn, YouTube, Facebook, Instagram, Pinterest, Reddit, X, or TikTok.
- `paid_search`, `email`, `partner`, `campaign`, `referral`, or `direct`.

Treat this as attribution evidence, not proof that a particular answer or recommendation mentioned the brand. Referrer suppression, in-app browsers, redirects, and privacy controls can cause visits to be classified as direct or referral traffic.

Google AI Overviews and AI Mode can arrive with a normal Google Search referrer and are therefore classified as `organic_search` here. Use the Search Console reports actually available in the account, including a dedicated generative-AI report where offered. Record its date range and metric name; AI-feature impressions are not recommendation, click, or inquiry counts. Browser referral events and ordinary Web search totals do not isolate these impressions.

## Reference files and links

The secure form accepts a view-only reference link and records selected local filenames inside the message. It does not upload the files. The local chooser allows up to five files and 20 MB total; supported devices can pass the selected files through the system share menu. Otherwise the buyer must attach them separately in email or WhatsApp. Keep this distinction visible before sending.

Direct uploads need a separately configured owned storage destination and appropriate file validation, access, retention, and deletion behavior. No upload storage is configured by the current form.

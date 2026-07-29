# GloryStarWear Server Lead Form Setup

Updated: 2026-07-28

## Current behavior

- The website uses WhatsApp as the primary working inquiry route.
- Email opens the visitor's local email application and is not counted as a received lead.
- The secure server submit button is displayed only when the Vercel endpoint reports that a receiving webhook is configured.
- `lead_submit_success` is pushed only after the webhook returns a successful response.
- The Thank You page is opened only after that confirmed response.

## Required Vercel environment variables

Configure these for Production, Preview, and Development as appropriate:

- `LEAD_WEBHOOK_URL`: required HTTPS endpoint for a CRM, automation platform, server inbox, or owned lead receiver.
- `LEAD_WEBHOOK_SECRET`: optional bearer token sent to the receiving endpoint.

The receiver must return an HTTP 2xx response only after it has durably accepted the lead.

## Webhook payload

```json
{
  "event": "lead.created",
  "source": "glorystarwears.com",
  "lead": {
    "leadId": "generated UUID",
    "receivedAt": "ISO timestamp",
    "name": "Buyer name",
    "email": "buyer@example.com",
    "phone": "Optional phone",
    "product": "Product category",
    "quantity": "Optional quantity",
    "market": "Optional market",
    "timeline": "Optional timeline",
    "message": "Project details",
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
3. Request `GET /api/lead` from an allowed site origin and confirm `{ "configured": true }`.
4. Submit a test lead with a controlled email address.
5. Verify the receiver stored or delivered the lead before it returned 2xx.
6. Confirm the browser reached `/thank-you.html`.
7. Confirm `lead_submit_success` appears once and contains no personal information.
8. Test a receiver failure and confirm the site does not show success or open the Thank You page.
9. Add rate limiting and spam review in the receiving service before advertising the form widely.

## Source classification

The browser derives a non-personal source classification from the first referrer and campaign tags. The same values are added to vendor-neutral data-layer events and to a prepared inquiry:

- `organic_search`: Google, Bing, Yahoo, DuckDuckGo, Yandex, or Baidu.
- `ai_assistant`: ChatGPT, Perplexity, Gemini, Copilot, Claude, or You.com.
- `organic_social`: LinkedIn, YouTube, Facebook, Instagram, Pinterest, Reddit, X, or TikTok.
- `paid_search`, `email`, `partner`, `campaign`, `referral`, or `direct`.

Treat this as attribution evidence, not proof that a particular answer or recommendation mentioned the brand. Referrer suppression, in-app browsers, redirects, and privacy controls can cause visits to be classified as direct or referral traffic.

Google AI Overviews and AI Mode can arrive with a normal Google Search referrer and are therefore classified as `organic_search` here. Use Search Console's available generative-AI reporting for Google-specific visibility rather than trying to infer it from the browser referrer.

## File uploads

Do not add uploads until an owned storage provider, malware scanning, file-type limits, size limits, retention rules, deletion procedures, and updated privacy notice are configured.

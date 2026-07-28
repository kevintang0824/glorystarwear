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

## File uploads

Do not add uploads until an owned storage provider, malware scanning, file-type limits, size limits, retention rules, deletion procedures, and updated privacy notice are configured.

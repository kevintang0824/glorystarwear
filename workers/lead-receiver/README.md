# GloryStarWear lead receiver

This Worker is the private persistence layer for the public Vercel `/api/lead` function. It accepts only authenticated `lead.created` events, validates and bounds every field, rate-limits repeated submissions by a one-way email hash, and stores accepted inquiries in the dedicated `glorystarwear-leads` D1 database.

The `lead_id` primary key makes delivery idempotent. Accepted inquiry records are deleted after 365 days by the daily scheduled handler. Cloudflare Workers logs contain the random lead ID and result only; they do not log contact details or message content.

## Operations

```bash
npm install
npm run types
npm run check
npm run migrate:local
npm run migrate:remote
npm run deploy
```

Set `LEAD_WEBHOOK_SECRET` with `wrangler secret put`; never place it in this directory or in Git. The public Worker exposes only `/health` and authenticated `POST /leads`.

Review a metadata-only inbox view without printing message contents:

```bash
npx wrangler d1 execute glorystarwear-leads --remote --command "SELECT lead_id, received_at, product, market, status FROM leads ORDER BY received_at DESC LIMIT 25"
```

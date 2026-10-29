# GloryStarWear lead receiver

This Worker is the private persistence layer for the public Vercel `/api/lead` function. It accepts only authenticated `lead.created` events, validates and bounds every field, rate-limits repeated submissions by a one-way email hash, and stores accepted inquiries in the dedicated `glorystarwear-leads` D1 database.

The `lead_id` primary key makes delivery idempotent. Accepted inquiry records are deleted after 365 days by the daily scheduled handler. Cloudflare Workers logs contain the random lead ID and result only; they do not log contact details or message content.

The composed message uses the same 12,000-character limit as the public API, so reference links, selected filenames, and the buyer's project text are not cut off at the former 4,000-character boundary. Selected filenames are metadata, not uploaded files. Requests are limited to 128 KiB of actual body bytes while streaming, before JSON parsing; oversized bodies are rejected even when `Content-Length` is absent or inaccurate. This accommodates UTF-8 text and JSON escaping while retaining a bounded request size.

Run the local receiver regression checks from the repository root with Node.js 22.13 or newer:

```bash
node scripts/test_lead_receiver.mjs
```

These tests execute the Worker with a simulated database. They do not submit a live inquiry or contact a buyer. No database migration is needed for the message-bound fix; deploy the Worker after its checks pass.

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

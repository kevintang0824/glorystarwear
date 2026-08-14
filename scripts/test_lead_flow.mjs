import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const leadHandler = require("../api/lead.js");

class MockResponse {
  constructor() {
    this.headers = new Map();
    this.statusCode = 200;
    this.body = null;
  }

  setHeader(name, value) {
    this.headers.set(name.toLowerCase(), value);
    return this;
  }

  status(value) {
    this.statusCode = value;
    return this;
  }

  json(value) {
    this.body = value;
    return this;
  }

  end() {
    return this;
  }
}

const request = (method, body = {}, origin = "https://glorystarwears.com") => ({
  method,
  body,
  headers: { origin },
});

const validLead = {
  submissionId: "d5163dbe-7f62-4abf-9a31-2e7be64f4c35",
  turnstileToken: "synthetic-turnstile-token",
  name: "Flow Test",
  email: "flow-test@example.com",
  phone: "",
  product: "Tech pack review and development",
  quantity: "100 pcs",
  market: "USA",
  timeline: "Sample first",
  message: "Synthetic CI request. Do not contact.",
  companyWebsite: "",
  consent: true,
  sourcePage: "Flow test (/resources/custom-sportswear-tech-pack.html)",
  landingPage: "/resources/custom-sportswear-tech-pack.html",
  referrer: "https://www.google.com/",
  trafficChannel: "Organic Search",
  trafficSource: "google",
  campaign: {},
};

const originalFetch = globalThis.fetch;
const previousUrl = process.env.LEAD_WEBHOOK_URL;
const previousSecret = process.env.LEAD_WEBHOOK_SECRET;
const previousTurnstileSecret = process.env.TURNSTILE_SECRET_KEY;
const previousTurnstileSiteKey = process.env.TURNSTILE_SITE_KEY;

process.env.LEAD_WEBHOOK_URL = "https://receiver.example/leads";
process.env.LEAD_WEBHOOK_SECRET = "ci-only-webhook-secret";
process.env.TURNSTILE_SECRET_KEY = "ci-only-turnstile-secret";
process.env.TURNSTILE_SITE_KEY = "0x4AAAAAAACIOnlySiteKey";

try {
  const statusResponse = new MockResponse();
  await leadHandler(request("GET"), statusResponse);
  assert.equal(statusResponse.statusCode, 200);
  assert.deepEqual(statusResponse.body, {
    configured: true,
    turnstileSiteKey: process.env.TURNSTILE_SITE_KEY,
  });

  const deliveryCalls = [];
  globalThis.fetch = async (url, options) => {
    if (String(url).includes("/turnstile/v0/siteverify")) {
      return {
        ok: true,
        status: 200,
        json: async () => ({ success: true, hostname: "glorystarwears.com" }),
      };
    }
    deliveryCalls.push({ url: String(url), options });
    return { ok: true, status: 201 };
  };

  const successResponse = new MockResponse();
  await leadHandler(request("POST", validLead), successResponse);
  assert.equal(successResponse.statusCode, 201);
  assert.equal(successResponse.body.ok, true);
  assert.equal(successResponse.body.leadId, validLead.submissionId);
  assert.equal(deliveryCalls.length, 1);
  assert.equal(deliveryCalls[0].url, process.env.LEAD_WEBHOOK_URL);
  assert.equal(deliveryCalls[0].options.headers.Authorization, `Bearer ${process.env.LEAD_WEBHOOK_SECRET}`);
  const deliveredEvent = JSON.parse(deliveryCalls[0].options.body);
  assert.equal(deliveredEvent.event, "lead.created");
  assert.equal(deliveredEvent.lead.leadId, validLead.submissionId);

  let retryCount = 0;
  globalThis.fetch = async (url) => {
    if (String(url).includes("/turnstile/v0/siteverify")) {
      return {
        ok: true,
        status: 200,
        json: async () => ({ success: true, hostname: "glorystarwears.com" }),
      };
    }
    retryCount += 1;
    return retryCount === 1 ? { ok: false, status: 503 } : { ok: true, status: 201 };
  };
  const retryResponse = new MockResponse();
  await leadHandler(request("POST", validLead), retryResponse);
  assert.equal(retryResponse.statusCode, 201);
  assert.equal(retryCount, 2);

  const invalidOriginResponse = new MockResponse();
  await leadHandler(request("POST", validLead, "https://attacker.example"), invalidOriginResponse);
  assert.equal(invalidOriginResponse.statusCode, 403);

  const invalidLeadResponse = new MockResponse();
  await leadHandler(request("POST", { ...validLead, consent: false }), invalidLeadResponse);
  assert.equal(invalidLeadResponse.statusCode, 400);

  console.log("Lead flow contract tests passed.");
} finally {
  globalThis.fetch = originalFetch;
  if (previousUrl === undefined) delete process.env.LEAD_WEBHOOK_URL;
  else process.env.LEAD_WEBHOOK_URL = previousUrl;
  if (previousSecret === undefined) delete process.env.LEAD_WEBHOOK_SECRET;
  else process.env.LEAD_WEBHOOK_SECRET = previousSecret;
  if (previousTurnstileSecret === undefined) delete process.env.TURNSTILE_SECRET_KEY;
  else process.env.TURNSTILE_SECRET_KEY = previousTurnstileSecret;
  if (previousTurnstileSiteKey === undefined) delete process.env.TURNSTILE_SITE_KEY;
  else process.env.TURNSTILE_SITE_KEY = previousTurnstileSiteKey;
}

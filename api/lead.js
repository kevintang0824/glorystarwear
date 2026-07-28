const { randomUUID } = require("node:crypto");

const allowedOrigins = new Set([
  "https://glorystarwears.com",
  "https://www.glorystarwears.com",
  "https://glorystarwear.vercel.app",
  "https://glorystarwear-glorystarpack-s-projects.vercel.app",
]);

const isAllowedOrigin = (origin) => {
  if (!origin) return false;
  if (allowedOrigins.has(origin)) return true;

  return /^https:\/\/glorystarwear-[a-z0-9-]+-glorystarpack-s-projects\.vercel\.app$/.test(origin);
};

const readBody = (request) => {
  if (request.body && typeof request.body === "object") return request.body;
  if (typeof request.body !== "string") return {};

  try {
    return JSON.parse(request.body);
  } catch {
    return {};
  }
};

const cleanText = (value, maximumLength) => String(value || "").trim().slice(0, maximumLength);

const cleanCampaign = (campaign) => {
  if (!campaign || typeof campaign !== "object" || Array.isArray(campaign)) return {};

  return Object.fromEntries(
    Object.entries(campaign)
      .slice(0, 8)
      .map(([key, value]) => [cleanText(key, 40), cleanText(value, 160)])
      .filter(([key, value]) => key && value),
  );
};

module.exports = async function leadHandler(request, response) {
  const origin = cleanText(request.headers.origin, 240);
  const originAllowed = isAllowedOrigin(origin);
  const webhookUrl = process.env.LEAD_WEBHOOK_URL || "";

  response.setHeader("Cache-Control", "no-store");
  response.setHeader("Vary", "Origin");

  if (originAllowed) {
    response.setHeader("Access-Control-Allow-Origin", origin);
    response.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    response.setHeader("Access-Control-Allow-Headers", "Content-Type");
  }

  if (request.method === "OPTIONS") {
    return response.status(originAllowed ? 204 : 403).end();
  }

  if (request.method === "GET") {
    return response.status(200).json({ configured: Boolean(webhookUrl) });
  }

  if (request.method !== "POST") {
    response.setHeader("Allow", "GET, POST, OPTIONS");
    return response.status(405).json({ ok: false, error: "method_not_allowed" });
  }

  if (!originAllowed) {
    return response.status(403).json({ ok: false, error: "origin_not_allowed" });
  }

  if (!webhookUrl) {
    return response.status(503).json({ ok: false, error: "lead_service_unconfigured" });
  }

  let parsedWebhookUrl;
  try {
    parsedWebhookUrl = new URL(webhookUrl);
  } catch {
    return response.status(503).json({ ok: false, error: "lead_service_invalid" });
  }

  if (parsedWebhookUrl.protocol !== "https:") {
    return response.status(503).json({ ok: false, error: "lead_service_invalid" });
  }

  const body = readBody(request);
  if (cleanText(body.companyWebsite, 200)) {
    return response.status(202).json({ ok: true });
  }

  const lead = {
    leadId: randomUUID(),
    receivedAt: new Date().toISOString(),
    name: cleanText(body.name, 120),
    email: cleanText(body.email, 180).toLowerCase(),
    phone: cleanText(body.phone, 80),
    product: cleanText(body.product, 120),
    quantity: cleanText(body.quantity, 120),
    market: cleanText(body.market, 120),
    timeline: cleanText(body.timeline, 160),
    message: cleanText(body.message, 4000),
    sourcePage: cleanText(body.sourcePage, 500),
    landingPage: cleanText(body.landingPage, 500),
    referrer: cleanText(body.referrer, 500),
    campaign: cleanCampaign(body.campaign),
  };

  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email);
  if (!lead.name || !validEmail || !lead.product || !lead.message || body.consent !== true) {
    return response.status(400).json({ ok: false, error: "invalid_lead" });
  }

  const webhookHeaders = { "Content-Type": "application/json" };
  if (process.env.LEAD_WEBHOOK_SECRET) {
    webhookHeaders.Authorization = `Bearer ${process.env.LEAD_WEBHOOK_SECRET}`;
  }

  try {
    const webhookResponse = await fetch(parsedWebhookUrl, {
      method: "POST",
      headers: webhookHeaders,
      body: JSON.stringify({
        event: "lead.created",
        source: "glorystarwears.com",
        lead,
      }),
      signal: AbortSignal.timeout(8000),
    });

    if (!webhookResponse.ok) {
      return response.status(502).json({ ok: false, error: "lead_delivery_failed" });
    }
  } catch {
    return response.status(502).json({ ok: false, error: "lead_delivery_failed" });
  }

  return response.status(201).json({ ok: true, leadId: lead.leadId });
};

const { randomUUID } = require("node:crypto");

const allowedOrigins = new Set([
  "https://glorystarwears.com",
  "https://www.glorystarwears.com",
  "https://glorystarwear.vercel.app",
  "https://glorystarwear-glorystarpack-s-projects.vercel.app",
]);

const allowedTurnstileHostnames = new Set([
  "glorystarwears.com",
  "www.glorystarwears.com",
  "glorystarwear.vercel.app",
  "glorystarwear-glorystarpack-s-projects.vercel.app",
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

const isAllowedTurnstileHostname = (hostname) => {
  if (allowedTurnstileHostnames.has(hostname)) return true;
  return /^glorystarwear-[a-z0-9-]+-glorystarpack-s-projects\.vercel\.app$/.test(hostname);
};

const verifyTurnstile = async ({ token, secret, remoteIp, idempotencyKey }) => {
  const formData = new URLSearchParams({
    secret,
    response: token,
    idempotency_key: idempotencyKey,
  });
  if (remoteIp) formData.set("remoteip", remoteIp);

  const verificationResponse = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
    signal: AbortSignal.timeout(5000),
  });
  if (!verificationResponse.ok) return false;

  const verification = await verificationResponse.json().catch(() => ({}));
  return verification.success === true && isAllowedTurnstileHostname(cleanText(verification.hostname, 240));
};

module.exports = async function leadHandler(request, response) {
  const origin = cleanText(request.headers.origin, 240);
  const originAllowed = isAllowedOrigin(origin);
  const webhookUrl = process.env.LEAD_WEBHOOK_URL || "";
  const webhookSecret = process.env.LEAD_WEBHOOK_SECRET || "";
  const turnstileSecret = process.env.TURNSTILE_SECRET_KEY || "";
  const turnstileSiteKey = process.env.TURNSTILE_SITE_KEY || "";
  const receiverConfigured = Boolean(webhookUrl && webhookSecret && turnstileSecret && turnstileSiteKey);

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
    return response.status(200).json({
      configured: receiverConfigured,
      turnstileSiteKey: receiverConfigured ? turnstileSiteKey : "",
    });
  }

  if (request.method !== "POST") {
    response.setHeader("Allow", "GET, POST, OPTIONS");
    return response.status(405).json({ ok: false, error: "method_not_allowed" });
  }

  if (!originAllowed) {
    return response.status(403).json({ ok: false, error: "origin_not_allowed" });
  }

  if (!receiverConfigured) {
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
    leadId: /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(cleanText(body.submissionId, 80))
      ? cleanText(body.submissionId, 80)
      : randomUUID(),
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
    trafficChannel: cleanText(body.trafficChannel, 80),
    trafficSource: cleanText(body.trafficSource, 120),
    campaign: cleanCampaign(body.campaign),
  };

  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email);
  if (!lead.name || !validEmail || !lead.product || !lead.message || body.consent !== true) {
    return response.status(400).json({ ok: false, error: "invalid_lead" });
  }

  const turnstileToken = cleanText(body.turnstileToken, 2400);
  if (!turnstileToken) {
    return response.status(400).json({ ok: false, error: "human_verification_required" });
  }
  const remoteIp = cleanText(request.headers["x-forwarded-for"], 240).split(",")[0].trim();
  try {
    const humanVerified = await verifyTurnstile({
      token: turnstileToken,
      secret: turnstileSecret,
      remoteIp,
      idempotencyKey: lead.leadId,
    });
    if (!humanVerified) {
      return response.status(400).json({ ok: false, error: "human_verification_failed" });
    }
  } catch {
    return response.status(502).json({ ok: false, error: "human_verification_unavailable" });
  }

  const webhookHeaders = { "Content-Type": "application/json" };
  webhookHeaders.Authorization = `Bearer ${webhookSecret}`;

  try {
    const webhookBody = JSON.stringify({
      event: "lead.created",
      source: "glorystarwears.com",
      lead,
    });
    let deliveryConfirmed = false;

    for (let attempt = 0; attempt < 2 && !deliveryConfirmed; attempt += 1) {
      try {
        const webhookResponse = await fetch(parsedWebhookUrl, {
          method: "POST",
          headers: webhookHeaders,
          body: webhookBody,
          signal: AbortSignal.timeout(3500),
        });
        deliveryConfirmed = webhookResponse.ok;
        if (!deliveryConfirmed && webhookResponse.status < 500) break;
      } catch {
        // Retry one transient network failure with the same idempotent lead ID.
      }
    }

    if (!deliveryConfirmed) return response.status(502).json({ ok: false, error: "lead_delivery_failed" });
  } catch {
    return response.status(502).json({ ok: false, error: "lead_delivery_failed" });
  }

  return response.status(201).json({ ok: true, leadId: lead.leadId });
};

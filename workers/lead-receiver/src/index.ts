type Lead = {
  leadId: string;
  receivedAt: string;
  name: string;
  email: string;
  phone: string;
  product: string;
  quantity: string;
  market: string;
  timeline: string;
  message: string;
  sourcePage: string;
  landingPage: string;
  referrer: string;
  trafficChannel: string;
  trafficSource: string;
  campaign: Record<string, string>;
};

type LeadEvent = {
  event: "lead.created";
  source: "glorystarwears.com";
  lead: Lead;
};

const json = (body: Record<string, unknown>, status = 200) => Response.json(body, {
  status,
  headers: {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
  },
});

const sha256Hex = async (value: string) => {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
};

const secretsMatch = async (provided: string, expected: string) => {
  const encoder = new TextEncoder();
  const [providedHash, expectedHash] = await Promise.all([
    crypto.subtle.digest("SHA-256", encoder.encode(provided)),
    crypto.subtle.digest("SHA-256", encoder.encode(expected)),
  ]);
  return crypto.subtle.timingSafeEqual(providedHash, expectedHash);
};

const cleanText = (value: unknown, maximumLength: number) => String(value || "").trim().slice(0, maximumLength);

const cleanCampaign = (value: unknown) => {
  if (!value || typeof value !== "object" || Array.isArray(value)) return {};

  return Object.fromEntries(
    Object.entries(value)
      .slice(0, 8)
      .map(([key, entry]) => [cleanText(key, 40), cleanText(entry, 160)])
      .filter(([key, entry]) => key && entry),
  );
};

const readLeadEvent = (value: unknown): LeadEvent | null => {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;
  const payload = value as Record<string, unknown>;
  if (payload.event !== "lead.created" || payload.source !== "glorystarwears.com") return null;
  if (!payload.lead || typeof payload.lead !== "object" || Array.isArray(payload.lead)) return null;

  const input = payload.lead as Record<string, unknown>;
  const lead: Lead = {
    leadId: cleanText(input.leadId, 80),
    receivedAt: cleanText(input.receivedAt, 40),
    name: cleanText(input.name, 120),
    email: cleanText(input.email, 180).toLowerCase(),
    phone: cleanText(input.phone, 80),
    product: cleanText(input.product, 120),
    quantity: cleanText(input.quantity, 120),
    market: cleanText(input.market, 120),
    timeline: cleanText(input.timeline, 160),
    message: cleanText(input.message, 4000),
    sourcePage: cleanText(input.sourcePage, 500),
    landingPage: cleanText(input.landingPage, 500),
    referrer: cleanText(input.referrer, 500),
    trafficChannel: cleanText(input.trafficChannel, 80),
    trafficSource: cleanText(input.trafficSource, 120),
    campaign: cleanCampaign(input.campaign),
  };

  const validLeadId = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(lead.leadId);
  const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email);
  const validReceivedAt = Number.isFinite(Date.parse(lead.receivedAt));
  if (!validLeadId || !validEmail || !validReceivedAt || !lead.name || !lead.product || !lead.message) return null;

  return { event: "lead.created", source: "glorystarwears.com", lead };
};

const checkRateLimit = async (env: Env, email: string) => {
  const bucketStart = Math.floor(Date.now() / 900_000);
  const bucketKey = await sha256Hex(email);
  const results = await env.DB.batch<{ request_count: number }>([
    env.DB.prepare(
      `INSERT INTO lead_rate_limits (bucket_key, bucket_start, request_count)
       VALUES (?, ?, 1)
       ON CONFLICT(bucket_key, bucket_start)
       DO UPDATE SET request_count = request_count + 1`,
    ).bind(bucketKey, bucketStart),
    env.DB.prepare(
      "SELECT request_count FROM lead_rate_limits WHERE bucket_key = ? AND bucket_start = ?",
    ).bind(bucketKey, bucketStart),
  ]);

  const count = Number(results[1]?.results?.[0]?.request_count || 0);
  return count <= 5;
};

const saveLead = async (env: Env, lead: Lead) => env.DB.prepare(
  `INSERT OR IGNORE INTO leads (
    lead_id, received_at, retention_until, name, email, phone, product, quantity, market,
    timeline, message, source_page, landing_page, referrer, traffic_channel, traffic_source,
    campaign_json
  ) VALUES (?, ?, datetime(?, '+365 days'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
).bind(
  lead.leadId,
  lead.receivedAt,
  lead.receivedAt,
  lead.name,
  lead.email,
  lead.phone,
  lead.product,
  lead.quantity,
  lead.market,
  lead.timeline,
  lead.message,
  lead.sourcePage,
  lead.landingPage,
  lead.referrer,
  lead.trafficChannel,
  lead.trafficSource,
  JSON.stringify(lead.campaign),
).run();

const handleRequest = async (request: Request, env: Env) => {
  const url = new URL(request.url);

  if (request.method === "GET" && url.pathname === "/health") {
    await env.DB.prepare("SELECT 1 AS healthy").first();
    return json({ ok: true, service: "glorystarwear-lead-receiver", storage: "d1" });
  }

  if (request.method !== "POST" || url.pathname !== "/leads") {
    return json({ ok: false, error: "not_found" }, 404);
  }

  const providedSecret = request.headers.get("Authorization")?.replace(/^Bearer\s+/i, "") || "";
  if (!providedSecret || !env.LEAD_WEBHOOK_SECRET || !(await secretsMatch(providedSecret, env.LEAD_WEBHOOK_SECRET))) {
    return json({ ok: false, error: "unauthorized" }, 401);
  }

  const contentLength = Number(request.headers.get("Content-Length") || 0);
  if (contentLength > 32_768 || !request.headers.get("Content-Type")?.toLowerCase().startsWith("application/json")) {
    return json({ ok: false, error: "invalid_request" }, 400);
  }

  let input: unknown;
  try {
    input = await request.json();
  } catch {
    return json({ ok: false, error: "invalid_json" }, 400);
  }

  const event = readLeadEvent(input);
  if (!event) return json({ ok: false, error: "invalid_lead" }, 400);

  if (!(await checkRateLimit(env, event.lead.email))) {
    return json({ ok: false, error: "rate_limited" }, 429);
  }

  const result = await saveLead(env, event.lead);
  const duplicate = Number(result.meta.changes || 0) === 0;
  console.log(JSON.stringify({ message: "lead stored", leadId: event.lead.leadId, duplicate }));
  return json({ ok: true, leadId: event.lead.leadId, duplicate }, duplicate ? 200 : 201);
};

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    try {
      return await handleRequest(request, env);
    } catch (error) {
      console.error(JSON.stringify({
        message: "lead receiver request failed",
        error: error instanceof Error ? error.message : "unknown_error",
        path: new URL(request.url).pathname,
      }));
      return json({ ok: false, error: "internal_error" }, 500);
    }
  },

  async scheduled(_controller: ScheduledController, env: Env): Promise<void> {
    const results = await env.DB.batch([
      env.DB.prepare("DELETE FROM leads WHERE retention_until <= datetime('now')"),
      env.DB.prepare("DELETE FROM lead_rate_limits WHERE bucket_start < ?").bind(Math.floor(Date.now() / 900_000) - 96),
    ]);
    console.log(JSON.stringify({
      message: "lead retention cleanup complete",
      deletedLeads: Number(results[0]?.meta.changes || 0),
      deletedRateLimitBuckets: Number(results[1]?.meta.changes || 0),
    }));
  },
} satisfies ExportedHandler<Env>;

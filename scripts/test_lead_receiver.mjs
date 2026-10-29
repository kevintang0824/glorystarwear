import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { stripTypeScriptTypes } from "node:module";
import { timingSafeEqual, webcrypto } from "node:crypto";

// Run the actual Worker with an in-memory D1 boundary. No request is sent to
// Cloudflare, the production database, or a real buyer.
const source = await readFile(new URL("../workers/lead-receiver/src/index.ts", import.meta.url), "utf8");
const javascript = stripTypeScriptTypes(source);
const { default: worker } = await import(`data:text/javascript;base64,${Buffer.from(javascript).toString("base64")}`);
const cryptoDescriptor = Object.getOwnPropertyDescriptor(globalThis, "crypto");
const originalLog = console.log;
const originalError = console.error;
const workerLogs = [];
Object.defineProperty(globalThis, "crypto", {
  configurable: true,
  value: {
    subtle: {
      digest: (...args) => webcrypto.subtle.digest(...args),
      timingSafeEqual: (left, right) => timingSafeEqual(Buffer.from(left), Buffer.from(right)),
    },
  },
});
console.log = (...args) => workerLogs.push(args.join(" "));
console.error = (...args) => workerLogs.push(args.join(" "));

const webhookSecret = "local-test-secret-not-a-production-credential";
const event = (message) => ({
  event: "lead.created",
  source: "glorystarwears.com",
  lead: {
    leadId: "d5163dbe-7f62-4abf-9a31-2e7be64f4c35",
    receivedAt: "2026-10-29T12:00:00.000Z",
    name: "Synthetic Local Test",
    email: "test@example.com",
    product: "Custom teamwear program",
    message,
    sourcePage: "/contact.html",
    campaign: {},
  },
});

function environment({ rateCount = 1 } = {}) {
  const stored = [];
  let databaseCalls = 0;
  return {
    stored,
    get databaseCalls() { return databaseCalls; },
    LEAD_WEBHOOK_SECRET: webhookSecret,
    DB: {
      prepare(sql) {
        databaseCalls += 1;
        const statement = {
          values: [],
          bind(...values) { this.values = values; return this; },
          async run() {
            assert.ok(sql.startsWith("INSERT OR IGNORE INTO leads"));
            stored.push(this.values);
            return { meta: { changes: 1 } };
          },
        };
        return statement;
      },
      async batch() {
        return [{ results: [] }, { results: [{ request_count: rateCount }] }];
      },
    },
  };
}

function request(body, headers = {}) {
  return new Request("https://receiver.example/leads", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${webhookSecret}`, ...headers },
    body: typeof body === "string" || body instanceof Uint8Array || body instanceof ReadableStream ? body : JSON.stringify(body),
    duplex: "half",
  });
}

async function rejected(body, status, error, headers = {}) {
  const env = environment();
  const response = await worker.fetch(request(body, headers), env);
  assert.equal(response.status, status);
  assert.equal((await response.json()).error, error);
  assert.equal(env.databaseCalls, 0, "Rejected requests must not reach the database");
}

try {
  const referenceLink = "https://files.example/authorized-reference";
  const projectTail = "PROJECT-END: deliver the blue uniforms separately.";
  const composed = [
    "Buyer Type: Not provided",
    `Reference File Link: ${referenceLink}`,
    "Reference Files Selected: roster.csv, logo.pdf",
    "Context ".repeat(200),
    "Project Details:",
    "Uniform specification. ".repeat(130),
    projectTail,
  ].join("\n");
  assert.ok(composed.length > 4000 && composed.length < 12000);
  const longEnv = environment();
  const longResponse = await worker.fetch(request(event(composed)), longEnv);
  assert.equal(longResponse.status, 201);
  assert.equal(longEnv.stored[0][10], composed, "Persist the whole composed message, including its project tail");
  assert.ok(longEnv.stored[0][10].includes(referenceLink));
  assert.ok(longEnv.stored[0][10].endsWith(projectTail));

  // This valid message fits the API's string bound but exceeds the former
  // 32 KiB request limit once serialized as UTF-8.
  const unicodeMessage = "球队服装需求".repeat(1900) + "\n项目结束：保留此说明。";
  assert.ok(unicodeMessage.length < 12000);
  const unicodeBody = JSON.stringify(event(unicodeMessage));
  assert.ok(Buffer.byteLength(unicodeBody) > 32768);
  const unicodeEnv = environment();
  const unicodeResponse = await worker.fetch(request(unicodeBody, { "Content-Length": String(Buffer.byteLength(unicodeBody)) }), unicodeEnv);
  assert.equal(unicodeResponse.status, 201);
  assert.equal(unicodeEnv.stored[0][10], unicodeMessage);

  const boundedEnv = environment();
  const boundedResponse = await worker.fetch(request(event("x".repeat(12001))), boundedEnv);
  assert.equal(boundedResponse.status, 201);
  assert.equal(boundedEnv.stored[0][10].length, 12000, "Match the public API's message bound");

  await rejected("{}", 413, "request_too_large", { "Content-Length": String(128 * 1024 + 1) });
  const oversized = JSON.stringify(event("x".repeat(128 * 1024)));
  await rejected(oversized, 413, "request_too_large");
  await rejected(oversized, 413, "request_too_large", { "Content-Length": "2" });

  // Byte counting must also work when chunks split a multibyte character.
  const chunkBody = Buffer.from(JSON.stringify(event("颜色与尺寸确认")));
  const chunkStream = new ReadableStream({
    start(controller) {
      for (let offset = 0; offset < chunkBody.length; offset += 7) controller.enqueue(chunkBody.subarray(offset, offset + 7));
      controller.close();
    },
  });
  const chunkEnv = environment();
  assert.equal((await worker.fetch(request(chunkStream), chunkEnv)).status, 201);
  assert.equal(chunkEnv.stored[0][10], "颜色与尺寸确认");

  await rejected("{", 400, "invalid_json");
  await rejected(new Uint8Array([0xff]), 400, "invalid_json");
  await rejected(event("Hello"), 400, "invalid_request", { "Content-Type": "text/plain" });
  await rejected(event("Hello"), 401, "unauthorized", { Authorization: "Bearer wrong-secret" });
  await rejected({ ...event("Hello"), event: "another.event" }, 400, "invalid_lead");
  await rejected(event(" "), 400, "invalid_lead");
  await rejected({ ...event("Hello"), lead: { ...event("Hello").lead, email: "invalid-email" } }, 400, "invalid_lead");

  const limitedEnv = environment({ rateCount: 6 });
  const limitedResponse = await worker.fetch(request(event("Hello")), limitedEnv);
  assert.equal(limitedResponse.status, 429);
  assert.equal(limitedEnv.stored.length, 0, "Rate limiting must still prevent persistence");
  assert.ok(workerLogs.every((line) => !line.includes(referenceLink) && !line.includes(projectTail) && !line.includes("test@example.com")));
} finally {
  if (cryptoDescriptor) Object.defineProperty(globalThis, "crypto", cryptoDescriptor);
  else delete globalThis.crypto;
  console.log = originalLog;
  console.error = originalError;
}

console.log("Lead receiver persistence, Unicode, request-bound and validation checks passed.");

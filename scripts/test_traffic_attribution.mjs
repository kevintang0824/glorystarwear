import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

// Exercise the actual consent/attribution code without loading Analytics or
// sending a real inquiry. Page changes reuse the same browser storage.
const script = await readFile(new URL("../script.js", import.meta.url), "utf8");
const trackingSource = script.slice(0, script.indexOf("\nif (isThankYouPage)"));
assert.ok(trackingSource.includes("trackSessionLanding();"));
const storage = () => {
  const values = new Map();
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
  };
};

function visit({ path = "/", referrer = "", local = storage(), session = storage() } = {}) {
  const window = { location: new URL(path, "https://glorystarwears.com") };
  const loadedScripts = [];
  const document = {
    referrer,
    querySelector: () => null,
    querySelectorAll: () => [],
    getElementById: () => null,
    createElement: () => ({ dataset: {} }),
    head: { append: (element) => loadedScripts.push(element) },
  };
  const context = vm.createContext({ window, document, localStorage: local, sessionStorage: session, URL, URLSearchParams });
  vm.runInContext(`${trackingSource}\nglobalThis.tracking = { saveAnalyticsConsent, trackEvent, pageAttribution, pageTrafficAttribution, getPageContext };`, context);
  const events = (name) => window.dataLayer.filter((entry) => entry[0] === "event" && entry[1] === name);
  return { ...context.tracking, events, loadedScripts, window, local, session };
}

const ai = visit({ path: "/private-label-activewear-manufacturer.html", referrer: "https://chatgpt.com/" });
assert.equal(ai.loadedScripts.length, 0, "Analytics must not load before consent");
assert.equal(ai.events("session_landing").length, 0);
ai.saveAnalyticsConsent("granted");
assert.equal(ai.loadedScripts.length, 1);
assert.equal(ai.events("session_landing").length, 1);
assert.equal(ai.events("ai_assistant_landing").length, 1);
assert.equal(ai.events("ai_assistant_landing")[0][2].ai_source, "chatgpt");
ai.saveAnalyticsConsent("granted");
assert.equal(ai.events("ai_assistant_landing").length, 1, "Repeated consent must not duplicate a landing");

const contact = visit({ path: "/contact.html", referrer: "https://glorystarwears.com/private-label-activewear-manufacturer.html", local: ai.local, session: ai.session });
assert.equal(contact.events("session_landing").length, 0, "Navigation must not duplicate a landing");
contact.trackEvent("lead_submit_success", { product_interest: "private_label" });
assert.equal(contact.events("generate_lead")[0][2].traffic_source, "chatgpt");
assert.equal(contact.events("generate_lead")[0][2].traffic_channel, "ai_assistant");

const pending = visit({ path: "/fr/custom-teamwear-uniforms.html", referrer: "https://www.perplexity.ai/" });
pending.saveAnalyticsConsent("denied");
assert.equal(pending.loadedScripts.length, 0);
assert.equal(pending.events("session_landing").length, 0);
const later = visit({ path: "/fr/contact.html", referrer: "https://glorystarwears.com/fr/custom-teamwear-uniforms.html", local: pending.local, session: pending.session });
later.saveAnalyticsConsent("granted");
const deferred = later.events("ai_assistant_landing");
assert.equal(deferred.length, 1);
assert.equal(deferred[0][2].page_path, "/fr/custom-teamwear-uniforms.html");
assert.equal(deferred[0][2].page_type, "commercial_landing");
assert.equal(deferred[0][2].ai_source, "perplexity");
later.saveAnalyticsConsent("denied");
later.trackEvent("contact_click");
assert.equal(later.events("contact_click").length, 0, "Revoking consent must stop event sends");

const direct = visit();
const internal = visit({ path: "/contact.html?utm_source=internal_banner&utm_medium=referral", referrer: "https://glorystarwears.com/", session: direct.session });
assert.equal(internal.pageAttribution.referrer, "", "An empty first referrer is a valid direct visit");
assert.equal(internal.pageTrafficAttribution.channel, "direct");
assert.equal(Object.keys(internal.pageAttribution.campaign).length, 0, "Later UTMs must not overwrite first touch");

const campaign = visit({ path: "/?utm_source=chatgpt.com&utm_medium=referral" });
const changedCampaign = visit({ path: "/contact.html?utm_source=google&utm_medium=cpc", session: campaign.session });
assert.equal(changedCampaign.pageTrafficAttribution.source, "chatgpt");
assert.equal(changedCampaign.pageAttribution.campaign.utm_source, "chatgpt.com");
assert.equal(changedCampaign.getPageContext("/zh-cn/").pageType, "home");
assert.equal(changedCampaign.getPageContext("/es/products/").pageType, "product_hub");
assert.equal(changedCampaign.getPageContext("/ru/resources/").pageType, "resource_hub");

console.log("Traffic attribution and consent regression checks passed.");

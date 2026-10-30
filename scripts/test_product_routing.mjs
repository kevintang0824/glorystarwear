import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

const source = await readFile(new URL("../script.js", import.meta.url), "utf8");
const contact = await readFile(new URL("../contact.html", import.meta.url), "utf8");
const productSelect = contact.match(/<select name="product"[^>]*>([\s\S]*?)<\/select>/)?.[1] || "";
const productOptions = [...productSelect.matchAll(/<option value="([^"]*)"/g)].map((match) => ({ value: match[1] }));
const definitions = source.slice(source.indexOf("const inquiryPrefillOptions ="), source.indexOf("const inquiryPrefill ="));
const routes = source.slice(source.indexOf("const getProductInterestForPath ="), source.indexOf("const inquiryContext ="));
const applyPrefill = source.slice(source.indexOf("const applyInquiryPrefill ="), source.indexOf("quoteForms.forEach(applyInquiryPrefill)"));

function routing(search = "", initial = {}) {
  const values = new Map(Object.entries(initial));
  const context = vm.createContext({
    URLSearchParams,
    isContactPage: true,
    window: { location: { search } },
    buyerPathStorageKey: "buyer",
    productDirectionStorageKey: "direction",
    productShortlistStorageKey: "shortlist",
    fabricShortlistStorageKey: "fabric",
    sessionStorage: {
      getItem: (key) => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, value),
      removeItem: (key) => values.delete(key),
    },
  });
  vm.runInContext(`${definitions}\nconst inquiryPrefill = readInquiryPrefill();\n${routes}\n${applyPrefill}\nglobalThis.result = { inquiryPrefill, applyInquiryPrefill, getProductQuoteHref, getProductInterestForPath, readStoredProductDirection, readStoredProductShortlist, parseProductPagePath };`, context);
  return context.result;
}

const productCases = [
  ["private-label-gym-clothing", "gym_clothing", "Private label gym clothing"],
  ["custom-sublimated-teamwear", "sublimated_teamwear", "Custom sublimated teamwear"],
];
for (const locale of ["", "fr", "es", "pt", "ru", "zh-cn"]) {
  for (const [slug, token, label] of productCases) {
    const prefix = locale ? `/${locale}` : "";
    const path = `${prefix}/products/${slug}.html`;
    const helpers = routing();
    assert.equal(helpers.getProductInterestForPath(path), label);
    const href = helpers.getProductQuoteHref(path);
    assert.equal(href, `${prefix}/contact.html?product=${token}#quote-form`);
    const query = new URL(href, "https://glorystarwears.com").search;
    const destination = routing(query);
    assert.equal(destination.inquiryPrefill.values.product, label);
    assert.equal(destination.inquiryPrefill.source, "product_quote_link");
    assert.ok(productOptions.some((option) => option.value === label), "Contact must expose a stable product option value");
    const product = { value: "", dataset: {}, options: productOptions };
    destination.applyInquiryPrefill({ elements: { namedItem: (name) => name === "product" ? product : null } });
    assert.equal(product.value, label, "The route must fill the real product value");
    product.value = "Other custom sportswear";
    destination.applyInquiryPrefill({ elements: { namedItem: () => product } });
    assert.equal(product.value, "Other custom sportswear", "A buyer's existing selection must be preserved");

    const stored = routing("", {
      direction: JSON.stringify({ label: "Requested garment direction", sourcePath: path, savedAt: Date.now() }),
      shortlist: JSON.stringify({ items: [{ slug, label, path }], savedAt: Date.now() }),
    });
    assert.equal(stored.readStoredProductDirection()?.sourcePath, path);
    assert.equal(stored.readStoredProductShortlist()[0]?.path, path, "Keep the actual language page for provenance");
    const buyerHref = helpers.getProductQuoteHref(path, "club_school_team");
    const buyerPrefill = routing(new URL(buyerHref, "https://glorystarwears.com").search).inquiryPrefill;
    assert.equal(buyerPrefill.values.product, label);
    assert.equal(buyerPrefill.values.buyer, "Club, school, or team");
  }
}

for (const path of [
  "https://example.com/products/private-label-gym-clothing.html",
  "//example.com/products/private-label-gym-clothing.html",
  "/fr/products/../private-label-gym-clothing.html",
  "/xx/products/private-label-gym-clothing.html",
  "/fr/products/private-label-gym-clothing.html?next=https://example.com",
  "/fr/products/%2e%2e.html",
]) {
  const stored = routing("", {
    direction: JSON.stringify({ label: "Invalid source", sourcePath: path, savedAt: Date.now() }),
    shortlist: JSON.stringify({ items: [{ slug: "private-label-gym-clothing", label: "Invalid source", path }], savedAt: Date.now() }),
  });
  assert.equal(stored.parseProductPagePath(path), null);
  assert.equal(stored.readStoredProductDirection(), null);
  assert.equal(stored.readStoredProductShortlist().length, 0);
  assert.equal(stored.getProductQuoteHref(path), "/contact.html#quote-form");
}

assert.equal(routing("?development=oem").inquiryPrefill.source, "development_quote_link");
assert.equal(routing("?product=not_a_product").inquiryPrefill.hasValues, false);
assert.equal(routing("?buyer=not_a_buyer&product=gym_clothing").inquiryPrefill.source, "product_quote_link");
const expired = routing("", { direction: JSON.stringify({ label: "Old direction", sourcePath: "/fr/products/private-label-gym-clothing.html", savedAt: Date.now() - 3 * 60 * 60 * 1000 }) });
assert.equal(expired.readStoredProductDirection(), null);

// Follow each static product CTA's actual query through the same prefill logic.
for (const [slug, token, label] of productCases) {
  const page = await readFile(new URL(`../products/${slug}.html`, import.meta.url), "utf8");
  const main = page.split("<main>")[1].split("</main>")[0];
  const links = [...main.matchAll(/href="([^\"]*contact\.html[^\"]*)"/g)].map((match) => match[1]);
  assert.ok(links.length >= 2);
  for (const link of links) {
    const url = new URL(link, `https://glorystarwears.com/products/${slug}.html`);
    assert.equal(url.searchParams.get("product"), token);
    assert.equal(routing(url.search).inquiryPrefill.values.product, label);
  }
}

// A guide's real link must land in the same language and select a supported
// category. Compose generated markup with the production prefill parser.
for (const locale of ["", "fr/", "es/", "pt/", "ru/", "zh-cn/"]) {
  for (const [file, expectedTokens] of [
    ["resources/custom-sportswear-cost-lead-time.html", ["private_label", "teamwear"]],
    ["low-moq-sportswear-manufacturer.html", ["low_moq"]],
    ["resources/private-label-activewear-moq.html", ["private_label"]],
  ]) {
    const page = await readFile(new URL(`../${locale}${file}`, import.meta.url), "utf8");
    const main = page.match(/<main\b[^>]*>([\s\S]*?)<\/main>/)[1];
    const seen = new Set();
    for (const match of main.matchAll(/href="([^"]*contact\.html\?[^"]*)"/g)) {
      const url = new URL(match[1].replaceAll("&amp;", "&"), `https://glorystarwears.com/${locale}${file}`);
      assert.equal(url.pathname, `/${locale}contact.html`);
      assert.equal(url.hash, "#quote-form");
      const prefill = routing(url.search).inquiryPrefill;
      assert.ok(productOptions.some((option) => option.value === prefill.values.product));
      assert.equal(prefill.source, "product_quote_link");
      seen.add(url.searchParams.get("product"));
    }
    assert.deepEqual([...seen].sort(), [...expectedTokens].sort(), `${locale}${file}`);
  }
}

for (const locale of ["", "fr/", "es/", "pt/", "ru/", "zh-cn/"]) {
  const file = "resources/custom-sportswear-tech-pack.html";
  const page = await readFile(new URL(`../${locale}${file}`, import.meta.url), "utf8");
  const main = page.match(/<main\b[^>]*>([\s\S]*?)<\/main>/)[1];
  const combinations = new Set();
  for (const match of main.matchAll(/href="([^"]*contact\.html\?[^"]*)"/g)) {
    const url = new URL(match[1].replaceAll("&amp;", "&"), `https://glorystarwears.com/${locale}${file}`);
    const product = url.searchParams.get("product");
    const development = url.searchParams.get("development");
    const prefill = routing(url.search).inquiryPrefill;
    assert.equal(url.pathname, `/${locale}contact.html`);
    assert.equal(url.hash, "#quote-form");
    assert.ok(productOptions.some((option) => option.value === prefill.values.product));
    assert.equal(prefill.values.development, development === "oem"
      ? "OEM from our tech pack" : "ODM from references and requirements");
    assert.equal(prefill.values.buyer, undefined);
    combinations.add(`${product}:${development}`);
  }
  assert.deepEqual([...combinations].sort(), ["private_label:odm", "private_label:oem", "teamwear:odm", "teamwear:oem"]);
}

// Compose the native guide form's real options with the contact prefill parser.
for (const locale of ["", "fr/", "es/", "pt/", "ru/", "zh-cn/"]) {
  const file = "resources/oem-vs-odm-sportswear.html";
  const page = await readFile(new URL(`../${locale}${file}`, import.meta.url), "utf8");
  const form = page.match(/<form\b([^>]*data-inquiry-route-form[^>]*)>([\s\S]*?)<\/form>/);
  assert.ok(form, `${locale}${file}`);
  assert.match(form[1], /method="get"/);
  const action = form[1].match(/action="([^"]+)"/)[1];
  const destination = new URL(action, `https://glorystarwears.com/${locale}${file}`);
  assert.equal(destination.pathname, `/${locale}contact.html`);
  assert.equal(destination.hash, "#quote-form");
  const options = (name) => [...form[2].match(new RegExp(`<select name="${name}"[^>]*>([\\s\\S]*?)<\\/select>`))[1].matchAll(/value="([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(options("product"), ["private_label", "teamwear"]);
  assert.deepEqual(options("development"), ["oem", "odm", "light_custom"]);
  for (const product of options("product")) {
    for (const development of options("development")) {
      const prefill = routing(`?${new URLSearchParams({ product, development })}`).inquiryPrefill;
      assert.ok(productOptions.some((option) => option.value === prefill.values.product));
      assert.ok(prefill.values.development);
    }
  }
}

const setupStart = source.indexOf("const setupInquiryRouteForms =");
const setupEnd = source.indexOf("setupInquiryRouteForms();", setupStart) + "setupInquiryRouteForms();".length;
const setupSource = source.slice(setupStart, setupEnd);
function routeSubmit({ product = "private_label", development = "odm", blocked = false } = {}) {
  let submit;
  const values = new Map([["direction", "Previous product direction"], ["attribution", "original campaign"]]);
  const events = [];
  const context = vm.createContext({
    window: { location: { pathname: "/fr/resources/oem-vs-odm-sportswear.html" } },
    document: { title: "OEM / ODM guide", querySelectorAll: () => [{
      elements: { namedItem: (name) => ({ value: name === "product" ? product : development }) },
      addEventListener: (name, handler) => { assert.equal(name, "submit"); submit = handler; },
    }] },
    sessionStorage: {
      removeItem: (key) => { if (blocked) throw Error("Storage unavailable"); values.delete(key); },
      setItem: (key, value) => { if (blocked) throw Error("Storage unavailable"); values.set(key, value); },
    },
    inquirySourceKey: "source", productDirectionStorageKey: "direction", URLSearchParams,
    trackEvent: (name, payload) => events.push({ name, payload }),
  });
  vm.runInContext(`${definitions}\n${setupSource}`, context);
  submit();
  return { values, events };
}
const selected = routeSubmit();
assert.equal(JSON.parse(selected.values.get("source")).path, "/fr/resources/oem-vs-odm-sportswear.html");
assert.equal(selected.values.has("direction"), false);
assert.equal(selected.values.get("attribution"), "original campaign");
assert.equal(selected.events[0].name, "inquiry_route_selected");
assert.equal(selected.events[0].payload.product_interest, "Private label activewear program");
assert.equal(routeSubmit({ blocked: true }).events.length, 1, "Native navigation must survive blocked storage");
assert.equal(routeSubmit({ product: "invalid" }).events.length, 0, "Ignore unrecognized telemetry values");
assert.equal(routeSubmit({ product: "constructor" }).events.length, 0);

console.log("Product and guide routing, including tech-pack readiness, passed for all six language paths.");

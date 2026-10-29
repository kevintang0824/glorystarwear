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

console.log("Product routing checks passed for both product lines and all six language paths.");

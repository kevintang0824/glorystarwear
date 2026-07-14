import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteOrigin = "https://glorystarwears.com";
const keyFileName = "8022fa20d2ef4befc52093d274ae7687.txt";
const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const keyFilePath = resolve(scriptDirectory, "..", keyFileName);
const endpoint = process.env.INDEXNOW_ENDPOINT || "https://api.indexnow.org/indexnow";

const printHelp = () => {
  console.log(`Submit changed GloryStarWear URLs to IndexNow after they are live.

Usage:
  node scripts/submit-indexnow.mjs <url> [url...]

Example:
  node scripts/submit-indexnow.mjs \\
    https://glorystarwears.com/resources/oem-vs-odm-sportswear.html \\
    https://glorystarwears.com/resources/private-label-activewear-moq.html

Only canonical URLs on glorystarwears.com are accepted.`);
};

const argumentsList = process.argv.slice(2);

if (argumentsList.includes("--help") || argumentsList.includes("-h")) {
  printHelp();
  process.exit(0);
}

if (argumentsList.length === 0) {
  printHelp();
  process.exitCode = 1;
} else {
  const urls = [...new Set(argumentsList)].map((value) => {
    const url = new URL(value);
    if (url.origin !== siteOrigin) {
      throw new Error(`URL must use ${siteOrigin}: ${value}`);
    }
    url.hash = "";
    return url.href;
  });

  const key = (process.env.INDEXNOW_KEY || (await readFile(keyFilePath, "utf8"))).trim();
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      host: new URL(siteOrigin).host,
      key,
      keyLocation: `${siteOrigin}/${keyFileName}`,
      urlList: urls,
    }),
  });

  if (!response.ok) {
    const responseBody = await response.text();
    throw new Error(`IndexNow returned ${response.status}: ${responseBody || response.statusText}`);
  }

  console.log(`Submitted ${urls.length} URL${urls.length === 1 ? "" : "s"} to IndexNow.`);
}

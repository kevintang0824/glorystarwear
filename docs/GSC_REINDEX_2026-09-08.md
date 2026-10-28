# GloryStarWear Search Console re-crawl checklist

Updated: 2026-09-08

## Access status

The current Google account can open Search Console, but it is not verified for `sc-domain:glorystarwears.com`. Search Console showed “You do not have access to this resource” for the domain property. Do not submit a sitemap or request indexing from another property.

## After access is granted

1. Open the `sc-domain:glorystarwears.com` property.
2. Submit or refresh `https://glorystarwears.com/sitemap.xml`.
3. Inspect each URL below and confirm the user-declared and Google-selected canonicals.
4. Request indexing once for each URL after the production deployment is visible.

Priority URLs:

- `https://glorystarwears.com/`
- `https://glorystarwears.com/sportswear-manufacturer.html`
- `https://glorystarwears.com/private-label-activewear-manufacturer.html`
- `https://glorystarwears.com/low-moq-sportswear-manufacturer.html`
- `https://glorystarwears.com/products/private-label-gym-clothing.html`
- `https://glorystarwears.com/resources/custom-sportswear-tech-pack.html`
- `https://glorystarwears.com/process.html`

Record for each URL: inspection date, indexed status, last crawl, canonical selection, mobile result, enhancement errors, and the next review date.

## Production deployment verified

- Production alias: `https://glorystarwears.com`
- Script version: `20260907-1`
- Sitemap URL count: 142
- Live status: priority pages returned HTTP 200 on 2026-09-08
- AI attribution event: `ai_assistant_landing`

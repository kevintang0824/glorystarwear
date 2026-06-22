# GloryStarWear Website

Static multi-page website for GloryStarWear, a custom sportswear OEM/ODM supplier covering yoga wear, athleisure, training wear, basketball uniforms, football kits, racket sports apparel, rugby teamwear, youth sportswear, dancewear, accessories, packaging, and expanded sports categories.

## Project Type

- Pure static website: HTML, CSS, JavaScript, SVG, JPG images.
- No build step required.
- Can be deployed directly to GitHub Pages, Netlify, Vercel, Cloudflare Pages, or any standard web host.

## Required Files

Keep these files and folders together in the GitHub repository:

```text
.
├── index.html
├── customization.html
├── fabrics.html
├── one-stop-service.html
├── quality.html
├── process.html
├── faq.html
├── contact.html
├── products/
├── assets/
├── styles.css
├── script.js
├── robots.txt
├── sitemap.xml
├── 404.html
├── CNAME
├── .nojekyll
└── docs/
```

## Page Map

- `index.html`: homepage with product range, customization, fabric, packaging, quality, FAQ, and inquiry sections.
- `products/index.html`: product category overview.
- `products/yoga-wear.html`: yoga wear, leggings, sports bras, matching sets.
- `products/athleisure.html`: hoodies, joggers, tracksuits, lifestyle apparel.
- `products/training-wear.html`: gym tops, shorts, pants, compression layers, warm-up layers.
- `products/basketball-wear.html`: basketball uniforms, shorts, warm-up, fan products.
- `products/football-kits.html`: football match kits, goalkeeper kits, training gear.
- `products/accessories.html`: socks, caps, bags, packaging, labels, carton systems.
- `products/more-sports.html`: running, tennis, pickleball, padel, cycling, volleyball, compression, outdoor, golf, baseball, rugby, field hockey, youth sportswear, dancewear, cheer apparel, swimwear, combat sports.
- `customization.html`: OEM, ODM, logo, labels, trims, and packaging options.
- `fabrics.html`: performance fabric and decoration information.
- `one-stop-service.html`: packaging, labels, retail preparation, shipment.
- `quality.html`: QC process and inspection checkpoints.
- `process.html`: production process.
- `faq.html`: buyer FAQ for SEO/AEO.
- `contact.html`: inquiry and contact page.
- `404.html`: GitHub Pages fallback page for broken or moved URLs.

## Brand and Contact Settings

Current public-facing settings used across the site:

- Brand name: `GloryStarWear`
- Website domain: `https://glorystarwears.com/`
- GitHub Pages custom domain file: `CNAME`
- Email: `kevin@glorystarwears.com`
- Phone / WhatsApp: `+86 18020755949`
- Logo files:
  - `assets/logo-mark.svg`
  - `assets/logo-glorystarwear.svg`

If the domain, phone, email, or brand spelling changes, update all HTML files, `robots.txt`, `sitemap.xml`, and JSON-LD blocks.

## Local Preview

From the project root:

```bash
python3 -m http.server 4174
```

Then open:

```text
http://localhost:4174/
```

You can also open `index.html` directly in a browser, but using a local server is closer to real hosting.

## Deployment

### GitHub Pages

1. Create a new GitHub repository.
2. Upload all files in this folder.
3. In GitHub: `Settings` -> `Pages`.
4. Select the branch and root folder.
5. After publishing, test homepage, product pages, sitemap, and contact links.

### Netlify / Vercel / Cloudflare Pages

- Build command: leave empty.
- Publish directory: project root, usually `.`.
- Framework preset: static / no framework.

## SEO and AEO Materials

The site already includes:

- Unique page titles and meta descriptions.
- Canonical URLs.
- Open Graph and Twitter image metadata.
- JSON-LD structured data.
- Image alt text.
- FAQ / answer-style content for AEO.
- `robots.txt`.
- `sitemap.xml` with image sitemap entries.

Before going live, verify that `https://glorystarwears.com/` is the final domain. If not, replace it everywhere.

## Maintenance Notes

- Add new product images to `assets/images/`.
- Use descriptive lowercase filenames with hyphens.
- Keep image references relative in HTML, such as `../assets/images/example.jpg`.
- Keep all important product images listed in `sitemap.xml`.
- When adding a new page, add it to navigation, mobile navigation, footer links if needed, `sitemap.xml`, and related JSON-LD.

See also:

- `docs/GITHUB_UPLOAD_CHECKLIST.md`
- `docs/ASSET_MANIFEST.md`
- `docs/SEO_AEO_REVIEW.md`

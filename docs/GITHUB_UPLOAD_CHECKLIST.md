# GitHub Upload Checklist

Use this checklist before pushing the website to a GitHub repository.

## 1. Files To Include

Include:

- All `.html` files in the root.
- Entire `products/` folder.
- Entire `assets/` folder.
- `styles.css`.
- `script.js`.
- `robots.txt`.
- `sitemap.xml`.
- `404.html`.
- `CNAME`.
- `.nojekyll`.
- `README.md`.
- `docs/`.
- `.gitignore`.

Do not include:

- `.DS_Store`.
- Temporary screenshots.
- Generated image source folders outside this project.
- Browser cache files.
- Local `.env` files.
- `node_modules/`.

## 2. Domain Settings

Current production domain used inside SEO tags:

```text
https://glorystarwears.com/
```

Before publishing, confirm this is the final domain. If the final domain is different, update:

- Canonical URLs in all HTML pages.
- Open Graph URLs.
- JSON-LD URLs.
- `robots.txt`.
- `sitemap.xml`.
- `CNAME`.

## 3. Contact Settings

Current contact information:

```text
Email: kevin@glorystarwears.com
Phone / WhatsApp: +86 18020755949
```

Confirm this is correct before publishing.

## 4. Required Manual Tests

After uploading, open these pages:

- `/`
- `/products/`
- `/products/yoga-wear.html`
- `/products/training-wear.html`
- `/products/more-sports.html`
- `/customization.html`
- `/contact.html`
- `/sitemap.xml`
- `/robots.txt`
- a fake URL to confirm `404.html` works on GitHub Pages

Check:

- Header logo loads.
- Product images load.
- Product cards do not repeat obvious images in the same section.
- Mobile menu opens.
- WhatsApp and email links work.
- No horizontal scrolling on mobile.
- Product pages show images and text below the header.

## 5. SEO Checks

Run these after deployment:

- Submit `sitemap.xml` in Google Search Console.
- Test pages with Google Rich Results Test.
- Check image indexing after Google crawls the site.
- Confirm all canonical URLs use the live domain.
- Confirm the site is served over HTTPS.

## 6. Suggested Git Commit Order

Recommended first commit:

```bash
git add .
git commit -m "Initial GloryStarWear website"
```

Recommended later commits:

```bash
git commit -m "Add new product category images"
git commit -m "Update SEO sitemap and product catalog"
git commit -m "Refine mobile layout"
```

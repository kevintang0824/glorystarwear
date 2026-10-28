#!/usr/bin/env python3

"""Strengthen the English pages in the Search Console discovered-not-indexed set.

This is a narrowly scoped content and discovery pass. It updates only the URLs
recorded in the 2026-09-09 Search Console export, adds a buyer-intent bridge to
legacy product pages, exposes the product set from the catalog hub and llms.txt,
and keeps structured dates aligned with sitemap lastmod values.

The copy deliberately describes planning inputs and verification boundaries. It
does not create factory, certification, capacity, customer, price or lead-time
claims that are not supported by source evidence.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://glorystarwears.com"
TODAY = "2026-09-09"

TARGET_PRODUCT_SLUGS = (
    "accessories",
    "athleisure",
    "badminton-uniforms",
    "baseball-uniforms",
    "basketball-jerseys",
    "club-fan-merchandise",
    "club-hoodies-varsity-jackets",
    "cricket-uniforms",
    "custom-beach-volleyball-uniforms",
    "custom-bowling-shirts",
    "custom-boxing-apparel",
    "custom-darts-shirts",
    "custom-fishing-apparel",
    "custom-futsal-uniforms",
    "custom-handball-uniforms",
    "custom-padel-apparel",
    "custom-referee-uniforms",
    "custom-rowing-uniforms",
    "custom-running-shorts",
    "custom-sports-socks",
    "custom-table-tennis-uniforms",
    "custom-team-polo-shirts",
    "custom-ultimate-jerseys",
    "dancewear-cheer",
    "esports-jerseys",
    "field-hockey-uniforms",
    "flag-football-uniforms",
    "football-jerseys",
    "football-kits",
    "golf-apparel",
    "gym-tshirts-tank-tops",
    "gymnastics-leotards",
    "hoodies-sweatshirts",
    "ice-hockey-jerseys",
    "joggers-tracksuits",
    "lacrosse-uniforms",
    "marathon-event-apparel",
    "mma-rash-guards-fight-shorts",
    "pilates-activewear",
    "plus-size-activewear",
    "private-label-gym-leggings",
    "racket-sports-apparel",
    "rugby-uniforms",
    "running-wear",
    "soccer-uniforms",
    "softball-uniforms",
    "swimwear-water-sports",
    "team-warm-up-jackets",
    "tennis-pickleball-apparel",
    "track-field-uniforms",
    "trail-hiking-apparel",
    "training-shorts-joggers",
    "training-wear",
    "triathlon-endurance-apparel",
    "wrestling-singlets",
    "yoga-leggings",
)
TARGET_OTHER_PATHS = (
    "contact.html",
    "customization.html",
    "quality.html",
    "resources/index.html",
)

GROUPS = (
    (
        "Activewear and studio",
        "Private-label activewear, gym, studio, size-range, and layering pages.",
        {
            "athleisure",
            "gym-tshirts-tank-tops",
            "gymnastics-leotards",
            "hoodies-sweatshirts",
            "joggers-tracksuits",
            "pilates-activewear",
            "plus-size-activewear",
            "private-label-gym-leggings",
            "training-shorts-joggers",
            "training-wear",
            "yoga-leggings",
        },
    ),
    (
        "Teamwear and club orders",
        "Team, league, club, school, tournament, roster, and fan-merchandise pages.",
        {
            "badminton-uniforms",
            "baseball-uniforms",
            "basketball-jerseys",
            "club-fan-merchandise",
            "club-hoodies-varsity-jackets",
            "cricket-uniforms",
            "custom-beach-volleyball-uniforms",
            "custom-bowling-shirts",
            "custom-darts-shirts",
            "custom-futsal-uniforms",
            "custom-handball-uniforms",
            "custom-referee-uniforms",
            "custom-table-tennis-uniforms",
            "custom-team-polo-shirts",
            "custom-ultimate-jerseys",
            "dancewear-cheer",
            "esports-jerseys",
            "field-hockey-uniforms",
            "flag-football-uniforms",
            "football-jerseys",
            "football-kits",
            "ice-hockey-jerseys",
            "lacrosse-uniforms",
            "rugby-uniforms",
            "soccer-uniforms",
            "softball-uniforms",
            "team-warm-up-jackets",
            "track-field-uniforms",
            "wrestling-singlets",
        },
    ),
    (
        "Endurance, outdoor, and water sports",
        "Running, event, cycling-adjacent, outdoor, water, golf, and endurance pages.",
        {
            "custom-fishing-apparel",
            "custom-rowing-uniforms",
            "custom-running-shorts",
            "golf-apparel",
            "marathon-event-apparel",
            "running-wear",
            "swimwear-water-sports",
            "tennis-pickleball-apparel",
            "trail-hiking-apparel",
            "triathlon-endurance-apparel",
        },
    ),
    (
        "Court, combat, accessories, and specialty",
        "Court, combat, accessories, packaging, and specialist product pages.",
        {
            "accessories",
            "custom-boxing-apparel",
            "custom-padel-apparel",
            "custom-sports-socks",
            "mma-rash-guards-fight-shorts",
            "racket-sports-apparel",
        },
    ),
)


def text_from_tag(source: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>([\s\S]*?)</{tag}>", source, re.IGNORECASE)
    if not match:
        return ""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()


def meta_description(source: str) -> str:
    match = re.search(
        r'<meta\s+name="description"\s+content="([^"]+)"',
        source,
        re.IGNORECASE,
    )
    return html.unescape(match.group(1)).strip() if match else ""


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def parent_href(source: str) -> str:
    match = re.search(
        r'<div class="breadcrumb"[\s\S]*?<a href="\./">Products</a>'
        r'<span>/</span><a href="(\./[^"]+\.html)"',
        source,
        re.IGNORECASE,
    )
    return match.group(1) if match else "./"


def brief_name(h1: str) -> str:
    name = re.sub(r"\b(manufacturer|supplier|program)\b", "", h1, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name).strip(" -")
    return name or "custom sportswear product"


def buyer_route(slug: str) -> str:
    for name, _description, slugs in GROUPS:
        if slug in slugs:
            return name.lower()
    return "specialist sportswear"


def product_bridge(source: str, slug: str) -> str:
    h1 = text_from_tag(source, "h1") or slug.replace("-", " ").title()
    product = brief_name(h1)
    description = meta_description(source)
    if len(description) > 210:
        description = description[:207].rsplit(" ", 1)[0] + "..."
    parent = parent_href(source)
    parent_label = "Compare the parent product range" if parent != "./" else "Browse the full product catalog"
    heading_id = f"{slug}-buyer-brief"
    return f'''      <!-- GSC_DISCOVERED_BRIEF_START -->
      <section class="section keyword-section gsc-discovered-brief" aria-labelledby="{escape(heading_id)}">
        <div class="section-heading"><p class="eyebrow">Commercial buyer brief</p><h2 id="{escape(heading_id)}">What to define before requesting a {escape(product)} quote</h2><p>{escape(description)} A comparable {escape(buyer_route(slug))} brief should connect the exact product, intended wearer or use, size and quantity plan, decoration, packing, and approval record.</p></div>
        <div class="keyword-grid">
          <article><span>Product and quantity scope</span><p>State the style, wearer, fit block, size range, colors, quantity by size, and whether the order is for retail, a team, an event, or a club program.</p><a href="{escape(parent)}">{escape(parent_label)}</a></article>
          <article><span>Quote and sample inputs</span><p>Attach references, logo or artwork files, fabric direction, target market, delivery country, and target date. MOQ, sample rounds, lead time, price, and feasibility remain project-specific.</p><a href="../quote-checklist.html">Use the quote checklist</a></article>
          <article><span>Approval and quality controls</span><p>Link the approved sample, measurements, decoration version, material notes, inspection checks, labels, packing list, and release decision before bulk production.</p><a href="../quality.html">Review quality controls</a></article>
          <article><span>Next operational step</span><p>Use the process page to keep revisions, approvals, and handoffs traceable, then send one consolidated brief so the supplier response is easier to compare.</p><a href="../process.html">Review the development process</a> <a href="../faq.html">Read buyer FAQs</a></article>
        </div>
      </section>
      <!-- GSC_DISCOVERED_BRIEF_END -->
'''


def route_bridge(path: Path, kind: str) -> str:
    if kind == "contact":
        return '''      <!-- GSC_DISCOVERED_BRIEF_START -->
      <section class="section keyword-section gsc-discovered-brief" aria-labelledby="inquiry-buyer-brief">
        <div class="section-heading"><p class="eyebrow">Commercial inquiry route</p><h2 id="inquiry-buyer-brief">Send the details that make a custom sportswear quote useful</h2><p>Start with the product or program you are sourcing, then connect quantities, sizes, fabrics, artwork, packaging, delivery country, and target date in one reviewable brief.</p></div>
        <div class="keyword-grid"><article><span>Choose a product route</span><p>Open the closest product page first so the garment scope and sport-specific decisions are clear.</p><a href="./products/">Browse product categories</a></article><article><span>Prepare the inputs</span><p>Use the quote checklist for references, size splits, quantities, artwork, packing, and delivery information.</p><a href="./quote-checklist.html">Open the quote checklist</a></article><article><span>Understand the handoff</span><p>Review how briefs, samples, revisions, quality checks, and release decisions should connect.</p><a href="./process.html">Review the development process</a></article><article><span>Ask a focused question</span><p>Unknown details can remain open; marking them clearly makes the first supplier response more useful.</p><a href="./faq.html">Read the buyer FAQ</a></article></div>
      </section>
      <!-- GSC_DISCOVERED_BRIEF_END -->
'''
    if kind == "customization":
        return '''      <!-- GSC_DISCOVERED_BRIEF_START -->
      <section class="section keyword-section gsc-discovered-brief" aria-labelledby="customization-buyer-brief">
        <div class="section-heading"><p class="eyebrow">Commercial customization brief</p><h2 id="customization-buyer-brief">Choose decoration, materials, labels, and packaging before sampling</h2><p>Custom sportswear customization is easier to quote when the product role, artwork files, fabric direction, quantity, size range, and approval basis are named together.</p></div>
        <div class="keyword-grid"><article><span>Decoration route</span><p>State whether the brief needs sublimation, transfer, embroidery, patches, woven labels, or a combination on named garment panels.</p><a href="./fabrics.html">Review fabrics and colors</a></article><article><span>Brand system</span><p>Prepare logo files, placement dimensions, color references, labels, hangtags, barcode requirements, and packaging units.</p><a href="./resources/sportswear-logo-artwork-preparation-guide.html">Prepare artwork files</a></article><article><span>Approval route</span><p>Keep the artwork revision, identified sample, measurements, decoration check, and release decision connected before bulk production.</p><a href="./process.html">Review the development process</a></article><article><span>Quote next step</span><p>Send product references, quantities, sizes, destination, and target date in one brief so MOQ and feasibility can be confirmed for the project.</p><a href="./quote-checklist.html">Use the quote checklist</a></article></div>
      </section>
      <!-- GSC_DISCOVERED_BRIEF_END -->
'''
    if kind == "quality":
        return '''      <!-- GSC_DISCOVERED_BRIEF_START -->
      <section class="section keyword-section gsc-discovered-brief" aria-labelledby="quality-buyer-brief">
        <div class="section-heading"><p class="eyebrow">Commercial quality route</p><h2 id="quality-buyer-brief">Define the quality evidence before comparing sportswear suppliers</h2><p>A useful custom sportswear quality brief connects the product, approved reference, measurements, artwork, labels, packing rules, inspection scope, exceptions, and release authority. The actual inspection result remains specific to the named product or lot.</p></div>
        <div class="keyword-grid"><article><span>Reference control</span><p>Identify the current tech pack, signed sample, size chart, material codes, artwork revision, label file, and packing specification that control production.</p><a href="./process.html">Map the approval process</a></article><article><span>Product checks</span><p>Set the relevant checks for fabric, color, fit, measurements, stitching, decoration, labels, packaging, count, and carton marks.</p><a href="./resources/sportswear-aql-inspection-checklist.html">Review an AQL inspection route</a></article><article><span>Evidence and exceptions</span><p>Retain measurement sheets, inspection scope, defect records, corrective action, recheck results, packing reconciliation, and authorized release decisions.</p><a href="./certificates.html">Map compliance evidence</a></article><article><span>Quote-ready handoff</span><p>Send the product category, order quantity, size range, market, inspection expectations, delivery country, and open questions in one reviewable brief.</p><a href="./quote-checklist.html">Prepare the quote checklist</a> <a href="./contact.html#quote-form">Discuss a project</a></article></div>
      </section>
      <!-- GSC_DISCOVERED_BRIEF_END -->
'''
    if kind == "resources":
        return '''      <!-- GSC_DISCOVERED_BRIEF_START -->
      <section class="section keyword-section gsc-discovered-brief" aria-labelledby="resources-buyer-brief">
        <div class="section-heading"><p class="eyebrow">Commercial resource routes</p><h2 id="resources-buyer-brief">Choose the buyer guide that moves your sourcing decision forward</h2><p>Use these routes to connect a product search with the next commercial question: development model, MOQ, specification, artwork, packaging, supplier evidence, quality, and quote preparation.</p></div>
        <div class="keyword-grid"><article><span>Find the product route</span><p>Start from the closest activewear, teamwear, endurance, court, combat, or specialist product page to define the garment and order context.</p><a href="../products/">Browse product categories</a></article><article><span>Define the specification</span><p>Use tech-pack, fabric, size-grading, artwork, and packaging guides to convert a product idea into reviewable inputs.</p><a href="./custom-sportswear-tech-pack.html">Build a product specification</a></article><article><span>Verify and control</span><p>Compare supplier evidence, sample approvals, inspection checkpoints, compliance records, and the boundaries of any planning example.</p><a href="../quality.html">Review quality controls</a> <a href="../about-factory.html">Review supplier evidence</a></article><article><span>Prepare the inquiry</span><p>Consolidate quantities, sizes, artwork, packaging, destination, target date, and open questions before asking for MOQ, feasibility, price, or timing.</p><a href="../quote-checklist.html">Open the quote checklist</a> <a href="../contact.html#quote-form">Start a project brief</a></article></div>
      </section>
      <!-- GSC_DISCOVERED_BRIEF_END -->
'''
    return ""


def insert_before_anchor(source: str, block: str, anchor: str) -> str:
    if anchor not in source:
        raise ValueError(f"anchor not found: {anchor}")
    return source.replace(anchor, block + anchor, 1)


def update_target_page(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    original = source
    if '"dateModified"' in source:
        source = re.sub(
            r'("dateModified"\s*:\s*")\d{4}-\d{2}-\d{2}(")',
            rf"\g<1>{TODAY}\g<2>",
            source,
        )

    if path.as_posix().endswith("/products/index.html"):
        return source != original

    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("products/") and "gsc-discovered-brief" not in source:
        slug = path.stem
        if "GENERATED_PRODUCT_PAGE" not in source:
            source = insert_before_anchor(source, product_bridge(source, slug), '      <section class="product-cta">')
    elif relative == "contact.html" and "gsc-discovered-brief" not in source:
        source = insert_before_anchor(source, route_bridge(path, "contact"), '      <section class="contact-section">')
    elif relative == "customization.html" and "gsc-discovered-brief" not in source:
        source = insert_before_anchor(source, route_bridge(path, "customization"), '      <section class="product-cta">')
    elif relative == "quality.html" and "gsc-discovered-brief" not in source:
        source = insert_before_anchor(source, route_bridge(path, "quality"), '      <section class="product-cta">')
    elif relative == "resources/index.html" and "gsc-discovered-brief" not in source:
        source = insert_before_anchor(source, route_bridge(path, "resources"), '      <section class="product-cta">')

    if source != original:
        path.write_text(source, encoding="utf-8")
    return source != original


def update_product_hub() -> None:
    path = ROOT / "products" / "index.html"
    source = path.read_text(encoding="utf-8")
    source = re.sub(r"Showing \d+ categories", "Showing 87 categories", source, count=1)
    marker_start = "      <!-- GSC_DISCOVERY_HUB_START -->"
    marker_end = "      <!-- GSC_DISCOVERY_HUB_END -->"
    grouped = {name: [] for name, _description, _slugs in GROUPS}
    assigned = set()

    for slug in TARGET_PRODUCT_SLUGS:
        product_path = ROOT / "products" / f"{slug}.html"
        product_source = product_path.read_text(encoding="utf-8")
        h1 = text_from_tag(product_source, "h1") or slug.replace("-", " ").title()
        label = brief_name(h1)
        group_name = next(name for name, _description, slugs in GROUPS if slug in slugs)
        grouped[group_name].append((slug, label))
        assigned.add(slug)

    expected = set(TARGET_PRODUCT_SLUGS)
    if assigned != expected:
        raise ValueError(f"Unassigned GSC target product slugs: {sorted(expected - assigned)}")

    cards = []
    for group_name, description, _slugs in GROUPS:
        links = "".join(
            f'<li><a href="./{escape(slug)}.html">{escape(label)} planning and quote inputs</a></li>'
            for slug, label in grouped[group_name]
        )
        cards.append(
            f'<article><span>{escape(group_name)}</span><p>{escape(description)}</p><ul class="gsc-discovery-links">{links}</ul></article>'
        )
    block = f'''{marker_start}
      <section class="section keyword-section gsc-discovery-hub" aria-labelledby="gsc-discovery-heading">
        <div class="section-heading"><p class="eyebrow">Priority crawl paths</p><h2 id="gsc-discovery-heading">Browse product pages by buying intent</h2><p>These focused pages connect sport, product type, collection route, and quote preparation. Open the closest page before requesting a project review.</p></div>
        <div class="keyword-grid gsc-discovery-grid">{"".join(cards)}</div>
      </section>
{marker_end}
'''
    pattern = re.compile(re.escape(marker_start) + r"[\s\S]*?" + re.escape(marker_end))
    if pattern.search(source):
        source = pattern.sub(block.rstrip(), source, count=1)
    else:
        anchor = '      <section class="section product-listing">'
        if anchor not in source:
            raise ValueError("product hub listing anchor not found")
        source = source.replace(anchor, block + anchor, 1)
    path.write_text(source, encoding="utf-8")


HOME_ROUTE_GROUPS = (
    (
        "Private-label activewear",
        "Gym, studio, layering, size-range, and private-label collection routes.",
        (
            "private-label-gym-leggings",
            "athleisure",
            "training-wear",
            "yoga-leggings",
        ),
    ),
    (
        "Teamwear and club programs",
        "Football, soccer, basketball, esports, roster, and club-order routes.",
        (
            "football-kits",
            "soccer-uniforms",
            "basketball-jerseys",
            "esports-jerseys",
        ),
    ),
    (
        "Endurance and event apparel",
        "Running, marathon, triathlon, swimwear, and event merchandise routes.",
        (
            "marathon-event-apparel",
            "running-wear",
            "triathlon-endurance-apparel",
            "swimwear-water-sports",
        ),
    ),
    (
        "Specialist sportswear",
        "Combat, racket, golf, accessories, and specialist product routes.",
        (
            "custom-boxing-apparel",
            "racket-sports-apparel",
            "golf-apparel",
            "accessories",
        ),
    ),
)


def update_homepage() -> None:
    path = ROOT / "index.html"
    source = path.read_text(encoding="utf-8")
    marker_start = "      <!-- GSC_HOME_ROUTES_START -->"
    marker_end = "      <!-- GSC_HOME_ROUTES_END -->"
    cards = []
    for group_name, description, slugs in HOME_ROUTE_GROUPS:
        links = "".join(
            f'<li><a href="./products/{escape(slug)}.html">{escape(brief_name(text_from_tag((ROOT / "products" / f"{slug}.html").read_text(encoding="utf-8"), "h1") or slug.replace("-", " ").title()))}</a></li>'
            for slug in slugs
        )
        cards.append(
            f'<article><span>{escape(group_name)}</span><p>{escape(description)}</p><ul class="gsc-discovery-links">{links}</ul></article>'
        )
    block = f'''{marker_start}
      <section class="section keyword-section gsc-home-routes" aria-labelledby="gsc-home-routes-heading">
        <div class="section-heading"><p class="eyebrow">Commercial search routes</p><h2 id="gsc-home-routes-heading">Start with the sportswear program you need to source</h2><p>Choose a focused product path for private-label activewear, teamwear, endurance, or specialist sportswear. Each route connects product decisions with sampling, quality, packaging, and quote preparation.</p></div>
        <div class="keyword-grid gsc-home-route-grid">{"".join(cards)}</div>
      </section>
{marker_end}
'''
    pattern = re.compile(re.escape(marker_start) + r"[\s\S]*?" + re.escape(marker_end))
    if pattern.search(source):
        source = pattern.sub(block.rstrip(), source, count=1)
    else:
        anchor = '      <section class="section featured-products" id="products">'
        if anchor not in source:
            raise ValueError("homepage featured product anchor not found")
        source = source.replace(anchor, block + anchor, 1)
    path.write_text(source, encoding="utf-8")


def update_llms() -> None:
    path = ROOT / "llms.txt"
    source = path.read_text(encoding="utf-8")
    marker_start = "<!-- GSC_DISCOVERY_PRODUCT_INDEX_START -->"
    marker_end = "<!-- GSC_DISCOVERY_PRODUCT_INDEX_END -->"
    sections = []
    for group_name, description, _slugs in GROUPS:
        lines = [f"### {group_name}", "", description, ""]
        for slug in TARGET_PRODUCT_SLUGS:
            if slug not in next(group_slugs for name, _d, group_slugs in GROUPS if name == group_name):
                continue
            product_source = (ROOT / "products" / f"{slug}.html").read_text(encoding="utf-8")
            h1 = text_from_tag(product_source, "h1") or slug.replace("-", " ").title()
            lines.append(f"- [{brief_name(h1)}]({ORIGIN}/products/{slug}.html)")
        sections.append("\n".join(lines))
    sections_text = "\n\n".join(sections)
    block = f'''{marker_start}
## Priority Product Page Index

These pages target product-specific commercial searches. They describe planning inputs and verification questions; exact MOQ, price, lead time, capacity, certification, stock, and feasibility require a project-specific response.

{sections_text}
{marker_end}'''
    pattern = re.compile(re.escape(marker_start) + r"[\s\S]*?" + re.escape(marker_end))
    if pattern.search(source):
        source = pattern.sub(block, source, count=1)
    else:
        anchor = "## Sportswear Manufacturing Blog"
        if anchor not in source:
            raise ValueError("llms.txt blog anchor not found")
        source = source.replace(anchor, block + "\n\n" + anchor, 1)
    source = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {TODAY}", source, count=1)
    path.write_text(source, encoding="utf-8")


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    target_paths = [f"products/{slug}.html" for slug in TARGET_PRODUCT_SLUGS] + list(TARGET_OTHER_PATHS)
    for relative in target_paths:
        page_path = ROOT / relative
        page_source = page_path.read_text(encoding="utf-8")
        canonical_match = re.search(r'<link rel="canonical" href="([^"]+)"', page_source, re.IGNORECASE)
        if not canonical_match:
            raise ValueError(f"canonical missing: {relative}")
        canonical = html.unescape(canonical_match.group(1))
        block_pattern = re.compile(rf"(<url>[\s\S]*?<loc>{re.escape(canonical)}</loc>[\s\S]*?<lastmod>)([^<]+)(</lastmod>[\s\S]*?</url>)")
        source, replacements = block_pattern.subn(rf"\g<1>{TODAY}\g<3>", source, count=1)
        if replacements != 1:
            raise ValueError(f"sitemap entry missing: {canonical}")
    path.write_text(source, encoding="utf-8")


def main() -> None:
    if len(TARGET_PRODUCT_SLUGS) != 56 or len(set(TARGET_PRODUCT_SLUGS)) != 56:
        raise ValueError("Expected 56 unique target product pages")
    for slug in TARGET_PRODUCT_SLUGS:
        path = ROOT / "products" / f"{slug}.html"
        if not path.exists():
            raise FileNotFoundError(path)
        update_target_page(path)
    for relative in TARGET_OTHER_PATHS:
        path = ROOT / relative
        if not path.exists():
            raise FileNotFoundError(path)
        update_target_page(path)
    update_homepage()
    update_product_hub()
    update_llms()
    update_sitemap()
    legacy_count = sum(
        1
        for slug in TARGET_PRODUCT_SLUGS
        if "GENERATED_PRODUCT_PAGE" not in (ROOT / "products" / f"{slug}.html").read_text(encoding="utf-8")
    )
    print(f"Optimized {len(TARGET_PRODUCT_SLUGS) + len(TARGET_OTHER_PATHS)} GSC target pages; added buyer bridges to {legacy_count} legacy product pages.")


if __name__ == "__main__":
    main()

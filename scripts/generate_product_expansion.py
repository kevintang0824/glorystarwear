#!/usr/bin/env python3

"""Generate the researched product-detail expansion and its internal links.

The source data intentionally describes planning scope rather than verified
stock, pricing, capacity, or production evidence. Generated pages therefore
use CollectionPage and ItemList markup, never Product or Offer markup.
"""

from __future__ import annotations

import html
import json
import re
import struct
from pathlib import Path

from site_chrome import site_footer_markup, site_header_markup


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "scripts" / "product_expansion_catalog.json"
TODAY = "2026-08-28"
ORIGIN = "https://glorystarwears.com"
SCRIPT_VERSION = "20260828-6"
STYLE_VERSION = "20260828-6"
PRODUCT_HUB_FILENAMES = {"index.html", "lookbook.html", "more-sports.html", "new-products.html"}
GENERATED_PRODUCT_MARKER = "GENERATED_PRODUCT_PAGE"
UPDATED_EXISTING_PRODUCT_SLUGS = {
    "more-sports",
    "new-products",
    "outdoor-training-outerwear",
    "triathlon-endurance-apparel",
    "yoga-wear",
    "american-football-uniforms",
    "baseball-softball-teamwear",
    "rugby-hockey-teamwear",
    "dancewear-cheer",
    "running-wear",
    "training-shorts-joggers",
    "racket-sports-apparel",
    "tennis-pickleball-apparel",
    "private-label-gym-clothing",
    "combat-sports-apparel",
    "wrestling-singlets",
    "custom-sublimated-teamwear",
    "yoga-leggings",
    "athleisure",
    "soccer-uniforms",
    "seamless-activewear",
    "club-fan-merchandise",
    "cycling-wear",
    "volleyball-teamwear",
}
LLMS_GROUP_SLUGS = {
    "Activewear and Studio": {
        "yoga-wear", "yoga-leggings", "sports-bras", "seamless-activewear",
        "plus-size-activewear", "athleisure", "hoodies-sweatshirts",
        "joggers-tracksuits", "training-wear", "gym-tshirts-tank-tops",
        "training-shorts-joggers", "private-label-gym-clothing",
        "compression-base-layers", "pilates-activewear",
        "private-label-gym-leggings",
    },
    "Team Uniforms and Club Programs": {
        "basketball-wear", "basketball-jerseys", "football-kits",
        "football-jerseys", "custom-sublimated-teamwear",
        "volleyball-teamwear", "volleyball-uniforms", "team-warm-up-jackets",
        "baseball-softball-teamwear", "rugby-hockey-teamwear",
        "youth-sportswear", "club-fan-merchandise",
        "club-hoodies-varsity-jackets", "soccer-uniforms", "esports-jerseys",
        "cheerleading-uniforms", "track-field-uniforms", "lacrosse-uniforms",
        "wrestling-singlets", "gymnastics-leotards", "cricket-uniforms",
        "american-football-uniforms", "netball-uniforms",
        "ice-hockey-jerseys", "flag-football-uniforms", "baseball-uniforms",
        "softball-uniforms", "rugby-uniforms", "field-hockey-uniforms",
        "custom-handball-uniforms", "custom-futsal-uniforms",
        "custom-bowling-shirts", "custom-darts-shirts",
        "custom-ultimate-jerseys", "custom-team-polo-shirts",
        "custom-beach-volleyball-uniforms", "custom-referee-uniforms",
    },
    "Endurance, Outdoor, and Water Sports": {
        "running-wear", "running-singlets-shirts", "cycling-wear",
        "cycling-jerseys-bib-shorts", "outdoor-training-outerwear",
        "golf-apparel", "golf-polo-shirts-skorts", "swimwear-water-sports",
        "rash-guards-board-shorts", "trail-hiking-apparel",
        "winter-sports-apparel", "triathlon-endurance-apparel",
        "marathon-event-apparel", "custom-fishing-apparel",
        "custom-rowing-uniforms",
        "custom-running-shorts", "custom-cycling-skinsuits",
        "custom-triathlon-suits", "custom-motocross-jerseys",
    },
    "Court, Combat, and Specialty Sports": {
        "tennis-pickleball-apparel", "racket-sports-apparel",
        "combat-sports-apparel", "mma-rash-guards-fight-shorts",
        "dancewear-cheer",
        "badminton-uniforms", "custom-padel-apparel", "custom-boxing-apparel",
        "custom-table-tennis-uniforms", "custom-weightlifting-singlets",
    },
    "Accessories and Packaging": {
        "accessories", "custom-sports-socks", "custom-sports-caps-bags",
        "private-label-sportswear-packaging",
    },
}


def escaped(value: str) -> str:
    return html.escape(value, quote=True)


def sentence(value: str) -> str:
    """Return source copy with a sentence-case first character."""
    value = value.strip()
    return value[:1].upper() + value[1:] if value else value


def contextual_name(value: str) -> str:
    """Lowercase category names while preserving proper-name capitalization."""
    lowered = value.lower()
    return re.sub(r"\bpilates\b", "Pilates", lowered)


def jpeg_size(path: Path) -> tuple[int, int]:
    """Read JPEG dimensions without adding a build dependency."""
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            raise ValueError(f"Not a JPEG: {path}")
        while True:
            marker_start = handle.read(1)
            if not marker_start:
                break
            if marker_start != b"\xff":
                continue
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if marker in {bytes([value]) for value in range(0xC0, 0xC4)} | {
                bytes([value]) for value in range(0xC5, 0xC8)
            } | {bytes([value]) for value in range(0xC9, 0xCC)} | {
                bytes([value]) for value in range(0xCD, 0xD0)
            }:
                length = struct.unpack(">H", handle.read(2))[0]
                payload = handle.read(length - 2)
                height, width = struct.unpack(">HH", payload[1:5])
                return width, height
            if marker in {b"\xd8", b"\xd9"}:
                continue
            length_bytes = handle.read(2)
            if len(length_bytes) != 2:
                break
            length = struct.unpack(">H", length_bytes)[0]
            handle.seek(length - 2, 1)
    raise ValueError(f"Could not read JPEG dimensions: {path}")


def responsive_sources(image_name: str, extension: str) -> list[tuple[str, int]]:
    base = ROOT / "assets" / "images" / f"{image_name}.{extension}"
    if not base.exists():
        return []
    width, _ = jpeg_size(base) if extension == "jpg" else jpeg_size(
        ROOT / "assets" / "images" / f"{image_name}.jpg"
    )
    candidates = []
    for candidate_width in (480, 900, 1200):
        candidate = ROOT / "assets" / "images" / f"{image_name}-{candidate_width}.{extension}"
        if candidate.exists():
            candidates.append((f"../assets/images/{candidate.name}", candidate_width))
    candidates.append((f"../assets/images/{base.name}", width))
    return candidates


def source_set(image_name: str, extension: str) -> str:
    return ", ".join(
        f"{path} {width}w" for path, width in responsive_sources(image_name, extension)
    )


def picture_markup(
    image_name: str,
    alt: str,
    *,
    sizes: str,
    priority: bool = False,
) -> str:
    jpg_path = ROOT / "assets" / "images" / f"{image_name}.jpg"
    avif_path = ROOT / "assets" / "images" / f"{image_name}.avif"
    if not jpg_path.exists() or not avif_path.exists():
        raise FileNotFoundError(f"Missing AVIF/JPEG pair for {image_name}")
    width, height = jpeg_size(jpg_path)
    loading = "" if priority else ' loading="lazy"'
    fetch_priority = ' fetchpriority="high"' if priority else ""
    return (
        '<picture data-evidence-status="illustrative">'
        f'<source type="image/avif" srcset="{escaped(source_set(image_name, "avif"))}" sizes="{escaped(sizes)}" />'
        f'<img src="../assets/images/{escaped(image_name)}.jpg" '
        f'srcset="{escaped(source_set(image_name, "jpg"))}" sizes="{escaped(sizes)}" '
        f'alt="{escaped(alt)}" width="{width}" height="{height}"{loading}{fetch_priority} decoding="async" '
        'data-evidence-status="illustrative" data-media-kind="product-planning-reference" />'
        "</picture>"
    )


def preload_markup(image_name: str) -> str:
    avif_path = ROOT / "assets" / "images" / f"{image_name}.avif"
    if not avif_path.exists():
        raise FileNotFoundError(avif_path)
    return (
        '<link rel="preload" as="image" type="image/avif" fetchpriority="high" '
        f'href="../assets/images/{escaped(image_name)}.avif" '
        f'imagesrcset="{escaped(source_set(image_name, "avif"))}" imagesizes="100vw" />'
    )


def navigation(current_slug: str) -> str:
    del current_slug
    return "\n" + site_header_markup()


def footer_markup() -> str:
    return site_footer_markup()


def schema_for(item: dict) -> dict:
    page_url = f"{ORIGIN}/products/{item['slug']}.html"
    image_url = f"{ORIGIN}/assets/images/{item['hero_image']}.jpg"
    parent_url = f"{ORIGIN}/products/{item['parent_slug']}.html"
    answers = item_answers(item)
    faq_nodes = [
        {
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        }
        for question, answer in answers
    ]
    about_nodes = [
        {"@type": "Thing", "name": item["short_name"]},
        {"@type": "Thing", "name": "Custom sportswear sourcing"},
        {"@type": "Thing", "name": "OEM and ODM project planning"},
    ]
    for keyword in item.get("keywords", [])[:5]:
        if keyword.lower() not in {node["name"].lower() for node in about_nodes}:
            about_nodes.append({"@type": "Thing", "name": keyword})

    page_node = {
        "@type": "CollectionPage",
        "@id": f"{page_url}#webpage",
        "name": item["h1"],
        "url": page_url,
        "description": item["meta_description"],
        "dateModified": TODAY,
        "inLanguage": "en",
        "isPartOf": {"@id": f"{ORIGIN}/#website"},
        "publisher": {"@id": f"{ORIGIN}/#organization"},
        "image": {
            "@type": "ImageObject",
            "url": image_url,
            "caption": "Illustrative product-planning reference; not a photographed stock item, customer order, current production run, or approved specification.",
        },
        "about": about_nodes,
        "audience": {"@type": "Audience", "audienceType": item["buyers"]},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": 3,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": direction["title"],
                }
                for index, direction in enumerate(item_directions(item), start=1)
            ],
        },
    }
    if item.get("keywords"):
        page_node["keywords"] = item["keywords"]
    if item.get("official_sources"):
        page_node["citation"] = [source["url"] for source in item["official_sources"]]
        page_node["mentions"] = [
            {"@type": "Thing", "name": source["name"], "url": source["url"]}
            for source in item["official_sources"]
        ]

    return {
        "@context": "https://schema.org",
        "@graph": [
            page_node,
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{ORIGIN}/"},
                    {"@type": "ListItem", "position": 2, "name": "Products", "item": f"{ORIGIN}/products/"},
                    {"@type": "ListItem", "position": 3, "name": item["parent_name"], "item": parent_url},
                    {"@type": "ListItem", "position": 4, "name": item["short_name"], "item": page_url},
                ],
            },
            {"@type": "FAQPage", "mainEntity": faq_nodes},
        ],
    }


def item_directions(item: dict) -> list[dict]:
    direction_content = [
        (
            "Range and silhouette planning",
            [sentence(item["range"]), item["fit"], f"Buyer and use context: {item['buyers']}."],
        ),
        (
            "Material and construction review",
            [item["fabric"], item["construction"], item["movement"]],
        ),
        (
            "Branding, order, and approval control",
            [item["branding"], sentence(item["order"]), item["evidence"]],
        ),
    ]
    return [
        {
            "title": title,
            "image": media["image"],
            "alt": media["alt"],
            "bullets": bullets,
        }
        for (title, bullets), media in zip(direction_content, item["direction_images"])
    ]


def item_specifications(item: dict) -> list[tuple[str, str]]:
    return [
        ("Range and intended use", f"{sentence(item['range'])} Define the buyer and use case: {item['buyers']}."),
        ("Movement and wear conditions", item["movement"]),
        ("Fit and size system", item["fit"]),
        ("Material target", item["fabric"]),
        ("Construction and reinforcement", item["construction"]),
        ("Branding, order, and approval", f"{item['branding']} {sentence(item['order'])} {item['evidence']}"),
    ]


def item_answers(item: dict) -> list[tuple[str, str]]:
    name = contextual_name(item["short_name"])
    return [
        (
            f"Can the {name} project be quoted from a reference image alone?",
            f"No. A reference image can identify a {name} direction, but a useful review also needs the requested garments, intended use, buyer market, quantity and size split, material and branding goals, packing, delivery country, and target date. Feasibility is confirmed only after the submitted project brief is reviewed.",
        ),
        (
            "How are fit, material, and construction routes approved?",
            "Convert the intended movement and fit into measurable requirements, approve coded material swatches, and review the proposed construction on an identified project sample. The suggestions on this page are planning inputs, not approved specifications or universal performance claims.",
        ),
        (
            "How are MOQ, samples, and lead time confirmed?",
            f"MOQ, sample cost, sample rounds, and lead time are confirmed after reviewing {item['order']} No universal figure on this page is a quotation or production commitment.",
        ),
        (
            "What evidence should be checked before bulk release?",
            f"Bulk-release evidence: {item['evidence']} Branding handoff: {item['branding']}",
        ),
    ]


def render_page(item: dict) -> str:
    title = item["title"]
    description = item["meta_description"]
    if not 30 <= len(title) <= 65:
        raise ValueError(f"Title length for {item['slug']}: {len(title)}")
    if not 100 <= len(description) <= 170:
        raise ValueError(f"Description length for {item['slug']}: {len(description)}")

    hero_alt = f"Illustrative product-planning reference: {item['hero_alt']}"
    hero_picture = picture_markup(item["hero_image"], hero_alt, sizes="100vw", priority=True)
    directions = item_directions(item)
    specifications = item_specifications(item)
    answers = item_answers(item)
    direction_cards = []
    for direction in directions:
        direction_picture = picture_markup(
            direction["image"],
            f"Illustrative product-planning reference: {direction['alt']}",
            sizes="(max-width: 720px) calc(100vw - 40px), (max-width: 1040px) 50vw, 33vw",
        )
        bullets = "".join(f"<li>{escaped(bullet)}</li>" for bullet in direction["bullets"])
        direction_cards.append(
            f'<article class="sku-card">{direction_picture}<div><h3>{escaped(direction["title"])}</h3><ul>{bullets}</ul></div></article>'
        )

    spec_cards = "".join(
        f'<article><span>{str(index).zfill(2)}</span><h3>{escaped(label)}</h3><p>{escaped(text)}</p></article>'
        for index, (label, text) in enumerate(specifications, start=1)
    )
    answer_cards = "".join(
        f'<article data-direct-answer><h3 data-direct-answer-question>{escaped(question)}</h3><p data-direct-answer-text>{escaped(answer)}</p></article>'
        for question, answer in answers
    )
    related_cards = "".join(
        f'<article><span>{escaped(link["label"])}</span><p>{escaped(link["description"])}</p><a href="{escaped(link["href"])}">{escaped(link["cta"])}</a></article>'
        for link in item["related"]
    )
    focus_cards = "".join(
        f'<article><span>{str(index).zfill(2)}</span><h3>{escaped(focus["title"])}</h3><p>{escaped(focus["body"])}</p></article>'
        for index, focus in enumerate(item["decision_focus"], start=1)
    )
    source_cards = "".join(
        f'<article><span>Official reference</span><h3>{escaped(source["name"])}</h3><p>{escaped(source["scope"])}</p><a href="{escaped(source["url"])}" target="_blank" rel="noreferrer">Open the current source</a></article>'
        for source in item.get("official_sources", [])
    )
    source_section = f"""      <section class="section keyword-section official-source-section" aria-labelledby="{escaped(item['slug'])}-official-sources">
        <div class="section-heading"><p class="eyebrow">Rules and verification</p><h2 id="{escaped(item['slug'])}-official-sources">Official rules and buyer verification</h2><p>These sources help identify questions for the brief; they do not prove that a proposed garment complies. The buyer must name the competition, market, season, and current rule set, then approve the final artwork, sample, and evidence.</p></div>
        <div class="keyword-grid">{source_cards}</div>
      </section>

""" if source_cards else ""
    schema = json.dumps(schema_for(item), ensure_ascii=False, indent=2)
    page_url = f"{ORIGIN}/products/{item['slug']}.html"
    image_url = f"{ORIGIN}/assets/images/{item['hero_image']}.jpg"

    return f"""<!doctype html>
<!-- {GENERATED_PRODUCT_MARKER}:{escaped(item['slug'])} -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{escaped(description)}" />
    <meta name="robots" content="index, follow, max-image-preview:large" />
    <link rel="canonical" href="{page_url}" />
    <meta property="og:title" content="{escaped(title)}" />
    <meta property="og:description" content="{escaped(item['og_description'])}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{page_url}" />
    <meta property="og:image" content="{image_url}" />
    <meta property="og:image:alt" content="{escaped(hero_alt)}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escaped(title)}" />
    <meta name="twitter:description" content="{escaped(item['og_description'])}" />
    <meta name="twitter:image" content="{image_url}" />
    <meta name="twitter:image:alt" content="{escaped(hero_alt)}" />
    <link rel="icon" type="image/svg+xml" href="../assets/logo-mark.svg" />
    <title>{escaped(title)}</title>
    {preload_markup(item['hero_image'])}
    <link rel="stylesheet" href="../styles.css?v={STYLE_VERSION}" />
    <script src="../assets/vendor/lucide.min.js?v=20260722-1" defer></script>
    <script src="../script.js?v={SCRIPT_VERSION}" defer></script>
  </head>
  <body class="product-page">
{navigation(item['slug'])}
    <main>
      <section class="product-hero">
        {hero_picture}
        <div class="product-hero-content">
          <div class="breadcrumb"><a href="../">Home</a><span>/</span><a href="./">Products</a><span>/</span><a href="./{escaped(item['parent_slug'])}.html">{escaped(item['parent_name'])}</a><span>/</span><span>{escaped(item['short_name'])}</span></div>
          <p class="eyebrow">{escaped(item['eyebrow'])}</p>
          <h1>{escaped(item['h1'])}</h1>
          <p>{escaped(item['summary'])}</p>
          <p class="product-detail-disclosure"><strong>Image and page scope:</strong> every image on this page is an illustrative planning reference, not a photograph of available stock, current production, a customer order, or an approved specification. Product feasibility and commercial terms are confirmed against the submitted brief.</p>
          <div class="product-cta-actions"><a class="button primary" href="../contact.html#quote-form"><i data-lucide="send"></i>Start This Product Brief</a><a class="button secondary" href="./{escaped(item['parent_slug'])}.html"><i data-lucide="layers"></i>View Parent Category</a></div>
          <small>Content reviewed <time datetime="{TODAY}">{TODAY}</time> · Buyer-facing planning scope, not a fixed quotation.</small>
        </div>
      </section>

      <section class="section product-listing" aria-labelledby="{escaped(item['slug'])}-directions">
        <div class="section-heading"><p class="eyebrow">Product directions</p><h2 id="{escaped(item['slug'])}-directions">Define the exact {escaped(contextual_name(item['short_name']))} range before sampling</h2><p>{escaped(item['scope'])}</p></div>
        <div class="sku-grid">{''.join(direction_cards)}</div>
      </section>

      <section class="section product-system" aria-labelledby="{escaped(item['slug'])}-specification">
        <div class="section-heading"><p class="eyebrow">Specification framework</p><h2 id="{escaped(item['slug'])}-specification">Six decisions that make the quotation and sample review more reliable</h2><p>Use these fields to turn a visual reference into a controlled product brief. Values remain proposed until the exact material, pattern, artwork, sample, and order route are approved.</p></div>
        <div class="product-system-grid">{spec_cards}</div>
      </section>

      <section class="section product-system" aria-labelledby="{escaped(item['slug'])}-decision-map">
        <div class="section-heading"><p class="eyebrow">Sport-specific decision map</p><h2 id="{escaped(item['slug'])}-decision-map">{escaped(item['focus_heading'])}</h2><p>{escaped(item['focus_intro'])}</p></div>
        <div class="product-system-grid">{focus_cards}</div>
      </section>

      <section class="section aeo-section" aria-labelledby="{escaped(item['slug'])}-answers">
        <div class="section-heading"><p class="eyebrow">Direct buyer answers</p><h2 id="{escaped(item['slug'])}-answers">{escaped(item['short_name'])} sourcing questions, answered clearly</h2><p>These short answers define what can be reviewed now, what the buyer should provide, and which terms still require project confirmation.</p></div>
        <div class="answer-grid" data-direct-answer-list>{answer_cards}</div>
      </section>

{source_section}      <section class="section keyword-section" aria-labelledby="{escaped(item['slug'])}-related">
        <div class="section-heading"><p class="eyebrow">Decision support</p><h2 id="{escaped(item['slug'])}-related">Continue from product idea to a controlled manufacturing brief</h2><p>Compare the parent collection, material and quality requirements, then send one consolidated brief rather than separate untracked messages.</p></div>
        <div class="keyword-grid">{related_cards}</div>
      </section>

      <section class="product-cta"><div><h2>Request a scoped {escaped(contextual_name(item['short_name']))} review</h2><p>{escaped(item['cta_summary'])}</p></div><div class="product-cta-actions"><a class="button primary" href="../contact.html#quote-form"><i data-lucide="send"></i>Request Details &amp; Quote</a><a class="button whatsapp" href="https://wa.me/8618020755949" target="_blank" rel="noreferrer"><i data-lucide="message-circle"></i>WhatsApp</a></div></section>
    </main>
{footer_markup()}
    <script type="application/ld+json">{schema}</script>
  </body>
</html>
"""


def replace_or_insert_block(path: Path, start: str, end: str, content: str, anchor: str) -> None:
    source = path.read_text(encoding="utf-8")
    block = f"{start}\n{content.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
    if pattern.search(source):
        source = pattern.sub(lambda _match: block, source, count=1)
    elif anchor in source:
        source = source.replace(anchor, f"{block}\n{anchor}", 1)
    else:
        raise ValueError(f"Anchor not found in {path}: {anchor}")
    path.write_text(source, encoding="utf-8")


def render_catalog_card(item: dict) -> str:
    image = picture_markup(
        item["hero_image"],
        f"Illustrative product-planning reference: {item['hero_alt']}",
        sizes="(max-width: 720px) calc(100vw - 40px), (max-width: 1040px) 50vw, 33vw",
    )
    return f"""          <article class="product-card">
            <a class="product-card-link" href="./{escaped(item['slug'])}.html" aria-label="Open {escaped(item['short_name'])} planning page"><span class="sr-only">Open {escaped(item['short_name'])} planning page</span></a>
            {image}
            <div><h3>{escaped(item['short_name'])}</h3><p>{escaped(item['catalog_summary'])}</p><span>{escaped(item['catalog_detail'])}</span></div>
          </article>"""


def update_product_index(items: list[dict]) -> None:
    path = ROOT / "products" / "index.html"
    cards = "\n".join(render_catalog_card(item) for item in items)
    replace_or_insert_block(
        path,
        "          <!-- PRODUCT_EXPANSION_START -->",
        "          <!-- PRODUCT_EXPANSION_END -->",
        cards,
        "        </div>\n      </section>\n\n      <section class=\"section keyword-section\">",
    )
    source = path.read_text(encoding="utf-8")
    source_without_expansion = re.sub(
        r"<!-- PRODUCT_EXPANSION_START -->[\s\S]*?<!-- PRODUCT_EXPANSION_END -->",
        "",
        source,
        count=1,
    )
    base_card_count = len(re.findall(r'class="product-card"', source_without_expansion))
    source = re.sub(
        r"Showing \d+ categories",
        f"Showing {base_card_count + len(items)} categories",
        source,
        count=1,
    )

    script_pattern = re.compile(
        r'<script type="application/ld\+json">\s*(\{[\s\S]*?"name"\s*:\s*"Custom Sportswear Product Categories"[\s\S]*?\})\s*</script>'
    )
    match = script_pattern.search(source)
    if not match:
        raise ValueError("Product-index CollectionPage JSON-LD not found")
    structured = json.loads(match.group(1))
    item_list = structured["mainEntity"]["itemListElement"]
    expansion_slugs = {item["slug"] for item in items}
    item_list = [
        entry
        for entry in item_list
        if entry.get("url", "").rsplit("/", 1)[-1].replace(".html", "") not in expansion_slugs
    ]
    for item in items:
        item_list.append(
            {
                "@type": "ListItem",
                "position": len(item_list) + 1,
                "name": item["short_name"],
                "url": f"{ORIGIN}/products/{item['slug']}.html",
            }
        )
    structured["mainEntity"]["itemListElement"] = item_list
    structured["mainEntity"]["numberOfItems"] = len(item_list)
    structured["dateModified"] = TODAY
    rendered = json.dumps(structured, ensure_ascii=False, indent=8)
    source = script_pattern.sub(f'<script type="application/ld+json">\n{rendered}\n    </script>', source, count=1)
    path.write_text(source, encoding="utf-8")


def update_parent_clusters(items: list[dict]) -> None:
    grouped: dict[str, list[dict]] = {}
    for item in items:
        if item["parent_slug"] in {"more-sports", "new-products"}:
            continue
        grouped.setdefault(item["parent_slug"], []).append(item)
    for parent_slug, children in grouped.items():
        path = ROOT / "products" / f"{parent_slug}.html"
        links = "".join(
            f'<article><span>{escaped(item["short_name"])}</span><p>{escaped(item["catalog_summary"])}</p><a href="./{escaped(item["slug"])}.html">Open the dedicated specification page</a></article>'
            for item in children
        )
        content = f"""      <section class="section keyword-section" aria-labelledby="{escaped(parent_slug)}-expanded-product-pages">
        <div class="section-heading"><p class="eyebrow">Expanded product coverage</p><h2 id="{escaped(parent_slug)}-expanded-product-pages">Dedicated pages for more precise product briefs</h2><p>Use these focused pages when the product needs its own fit, movement, construction, artwork, roster, or packaging decisions rather than a broad category overview.</p></div>
        <div class="keyword-grid">{links}</div>
      </section>"""
        replace_or_insert_block(
            path,
            f"      <!-- PRODUCT_CLUSTER_{parent_slug.upper().replace('-', '_')}_START -->",
            f"      <!-- PRODUCT_CLUSTER_{parent_slug.upper().replace('-', '_')}_END -->",
            content,
            "      <section class=\"product-cta\">",
        )
    update_parent_cluster_schema(grouped, items)


def update_parent_cluster_schema(
    grouped: dict[str, list[dict]], items: list[dict]
) -> None:
    """Keep visible parent-child links and CollectionPage ItemLists aligned."""
    generated_urls = {f"{ORIGIN}/products/{item['slug']}.html" for item in items}
    script_pattern = re.compile(
        r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)'
    )

    for parent_slug, children in grouped.items():
        path = ROOT / "products" / f"{parent_slug}.html"
        source = path.read_text(encoding="utf-8")
        schema_updated = False

        def replace_schema(match: re.Match[str]) -> str:
            nonlocal schema_updated
            try:
                structured = json.loads(match.group(2))
            except json.JSONDecodeError:
                return match.group(0)
            nodes = structured.get("@graph", []) if isinstance(structured, dict) else []
            if isinstance(structured, dict) and structured.get("@type") == "CollectionPage":
                nodes = [structured]
            page_node = next(
                (node for node in nodes if isinstance(node, dict) and node.get("@type") == "CollectionPage"),
                None,
            )
            if page_node is None:
                return match.group(0)

            current = page_node.get("mainEntity", {})
            existing_entries = [
                entry
                for entry in current.get("itemListElement", [])
                if entry.get("url") not in generated_urls
            ] if isinstance(current, dict) else []
            child_entries = [
                {
                    "@type": "ListItem",
                    "position": len(existing_entries) + index,
                    "name": child["short_name"],
                    "url": f"{ORIGIN}/products/{child['slug']}.html",
                }
                for index, child in enumerate(children, start=1)
            ]
            item_list = existing_entries + child_entries
            for position, entry in enumerate(item_list, start=1):
                entry["position"] = position
            page_node["mainEntity"] = {
                "@type": "ItemList",
                "numberOfItems": len(item_list),
                "itemListElement": item_list,
            }
            schema_updated = True
            rendered = json.dumps(structured, ensure_ascii=False, separators=(",", ":"))
            return f"{match.group(1)}{rendered}{match.group(3)}"

        source = script_pattern.sub(replace_schema, source)
        if not schema_updated:
            raise ValueError(f"CollectionPage JSON-LD not found in parent: {path}")
        path.write_text(source, encoding="utf-8")


def update_discovery_hubs(items: list[dict]) -> None:
    configurations = [
        {
            "slug": "more-sports",
            "start": "      <!-- EXPANDED_SPORT_DISCOVERY_START -->",
            "end": "      <!-- EXPANDED_SPORT_DISCOVERY_END -->",
            "eyebrow": "Expanded sport coverage",
            "heading": "Open sport-specific product and specification pages",
            "intro": "These focused pages separate movement, fit, material, construction, artwork, roster, packing, and approval decisions that cannot be resolved on a broad sports directory alone.",
            "cta": "Open the product specification",
            "description_key": "catalog_summary",
        },
        {
            "slug": "new-products",
            "start": "      <!-- RECENT_PRODUCT_BRIEFS_START -->",
            "end": "      <!-- RECENT_PRODUCT_BRIEFS_END -->",
            "eyebrow": "Recently added planning pages",
            "heading": f"Start with a deeper brief for {len(items)} product directions",
            "intro": "Use these new planning pages to structure a buyer inquiry. They are not stock listings or confirmed production commitments; exact feasibility follows review of the submitted project.",
            "cta": "Review the buyer brief",
            "description_key": "catalog_detail",
        },
    ]
    for configuration in configurations:
        cards = "".join(
            f'<article><span>{escaped(item["short_name"])}</span><p>{escaped(item[configuration["description_key"]])}</p><a href="./{escaped(item["slug"])}.html">{escaped(configuration["cta"])}</a></article>'
            for item in items
        )
        content = f"""      <section class="section keyword-section" aria-labelledby="{configuration['slug']}-expanded-product-briefs">
        <div class="section-heading"><p class="eyebrow">{escaped(configuration['eyebrow'])}</p><h2 id="{configuration['slug']}-expanded-product-briefs">{escaped(configuration['heading'])}</h2><p>{escaped(configuration['intro'])}</p></div>
        <div class="keyword-grid">{cards}</div>
      </section>"""
        replace_or_insert_block(
            ROOT / "products" / f"{configuration['slug']}.html",
            configuration["start"],
            configuration["end"],
            content,
            "      <section class=\"product-cta\">",
        )
    update_discovery_hub_schema(items)


def update_discovery_hub_schema(items: list[dict]) -> None:
    generated_urls = {f"{ORIGIN}/products/{item['slug']}.html" for item in items}
    script_pattern = re.compile(
        r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)'
    )

    for hub_slug in ("more-sports", "new-products"):
        path = ROOT / "products" / f"{hub_slug}.html"
        source = path.read_text(encoding="utf-8")
        schema_updated = False

        def replace_schema(match: re.Match[str]) -> str:
            nonlocal schema_updated
            try:
                structured = json.loads(match.group(2))
            except json.JSONDecodeError:
                return match.group(0)
            graph = structured.get("@graph", []) if isinstance(structured, dict) else []
            page_node = next(
                (node for node in graph if isinstance(node, dict) and node.get("@type") == "CollectionPage"),
                None,
            )
            if page_node is None:
                return match.group(0)

            existing_entries = []
            if hub_slug == "more-sports":
                main_entity = page_node.get("mainEntity", {})
                existing_entries = [
                    entry for entry in main_entity.get("itemListElement", [])
                    if entry.get("url") not in generated_urls
                ]
            expansion_entries = [
                {
                    "@type": "ListItem",
                    "position": len(existing_entries) + index,
                    "name": item["short_name"],
                    "url": f"{ORIGIN}/products/{item['slug']}.html",
                }
                for index, item in enumerate(items, start=1)
            ]
            item_list = existing_entries + expansion_entries
            for position, entry in enumerate(item_list, start=1):
                entry["position"] = position
            page_node["mainEntity"] = {
                "@type": "ItemList",
                "numberOfItems": len(item_list),
                "itemListElement": item_list,
            }
            schema_updated = True
            rendered = json.dumps(structured, ensure_ascii=False, separators=(",", ":"))
            return f"{match.group(1)}{rendered}{match.group(3)}"

        source = script_pattern.sub(replace_schema, source)
        if not schema_updated:
            raise ValueError(f"CollectionPage JSON-LD not found in discovery hub: {path}")
        path.write_text(source, encoding="utf-8")


def update_collection_dates() -> None:
    paths = [ROOT / "products" / "index.html"] + [
        ROOT / "products" / f"{slug}.html"
        for slug in sorted(UPDATED_EXISTING_PRODUCT_SLUGS)
    ]
    script_pattern = re.compile(
        r'(<script type="application/ld\+json">)([\s\S]*?)(</script>)'
    )

    for path in paths:
        source = path.read_text(encoding="utf-8")
        collection_found = False

        def replace_script(match: re.Match[str]) -> str:
            nonlocal collection_found
            try:
                structured = json.loads(match.group(2))
            except json.JSONDecodeError:
                return match.group(0)

            nodes = structured.get("@graph", []) if isinstance(structured, dict) else []
            if isinstance(structured, dict) and structured.get("@type") == "CollectionPage":
                nodes = [structured]
            updated = False
            for node in nodes:
                if isinstance(node, dict) and node.get("@type") == "CollectionPage":
                    node["dateModified"] = TODAY
                    updated = True
            if not updated:
                return match.group(0)
            collection_found = True
            rendered = json.dumps(structured, ensure_ascii=False, separators=(",", ":"))
            return f"{match.group(1)}{rendered}{match.group(3)}"

        source = script_pattern.sub(replace_script, source)
        if not collection_found:
            raise ValueError(f"CollectionPage JSON-LD not found in {path}")
        path.write_text(source, encoding="utf-8")


def update_llms(items: list[dict]) -> None:
    index_source = (ROOT / "products" / "index.html").read_text(encoding="utf-8")
    script_pattern = re.compile(
        r'<script type="application/ld\+json">\s*(\{[\s\S]*?"name"\s*:\s*"Custom Sportswear Product Categories"[\s\S]*?\})\s*</script>'
    )
    match = script_pattern.search(index_source)
    if not match:
        raise ValueError("Product-index JSON-LD missing while building llms.txt")
    entries = json.loads(match.group(1))["mainEntity"]["itemListElement"]
    grouped: dict[str, list[dict]] = {name: [] for name in LLMS_GROUP_SLUGS}
    ungrouped = []
    for entry in entries:
        slug = entry["url"].rsplit("/", 1)[-1].replace(".html", "")
        group_name = next(
            (name for name, slugs in LLMS_GROUP_SLUGS.items() if slug in slugs),
            "",
        )
        if group_name:
            grouped[group_name].append(entry)
        else:
            ungrouped.append(entry)
    if ungrouped:
        raise ValueError(f"Ungrouped llms.txt product pages: {ungrouped}")
    group_sections = []
    for group_name, group_entries in grouped.items():
        links = "\n".join(
            f"- [{entry['name']}]({entry['url']})" for entry in group_entries
        )
        group_sections.append(f"### {group_name}\n\n{links}")
    content = f"""## Complete Product Page Index

The following canonical pages cover every product direction in the public catalogue. Product pages describe planning and quotation inputs. Their images are illustrative references, and no fixed MOQ, price, lead time, factory route, stock status, certification, or project feasibility should be inferred.

{chr(10).join(chr(10) + section for section in group_sections).strip()}
"""
    path = ROOT / "llms.txt"
    replace_or_insert_block(
        path,
        "<!-- PRODUCT_EXPANSION_START -->",
        "<!-- PRODUCT_EXPANSION_END -->",
        content,
        "## Sourcing Notes",
    )
    source = path.read_text(encoding="utf-8")
    source = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {TODAY}", source, count=1)
    path.write_text(source, encoding="utf-8")


def update_sitemap(items: list[dict]) -> None:
    entries = []
    for item in items:
        entries.append(
            f"""  <url>
    <loc>{ORIGIN}/products/{escaped(item['slug'])}.html</loc>
    <image:image>
      <image:loc>{ORIGIN}/assets/images/{escaped(item['hero_image'])}.jpg</image:loc>
      <image:title>Illustrative {escaped(item['short_name'].lower())} product planning reference</image:title>
    </image:image>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.72</priority>
  </url>"""
        )
    replace_or_insert_block(
        ROOT / "sitemap.xml",
        "  <!-- PRODUCT_EXPANSION_START -->",
        "  <!-- PRODUCT_EXPANSION_END -->",
        "\n".join(entries),
        "</urlset>",
    )
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    updated_paths = ["products/"] + [
        f"products/{slug}.html" for slug in sorted(UPDATED_EXISTING_PRODUCT_SLUGS)
    ]
    for relative_url in updated_paths:
        page_url = f"{ORIGIN}/{relative_url}"
        pattern = re.compile(
            rf"(<loc>{re.escape(page_url)}</loc>[\s\S]*?<lastmod>)[^<]+(</lastmod>)"
        )
        source, replacements = pattern.subn(rf"\g<1>{TODAY}\g<2>", source, count=1)
        if replacements != 1:
            raise ValueError(f"Sitemap entry not found for current lastmod: {page_url}")
    path.write_text(source, encoding="utf-8")


def insert_tag_attributes(tag: str, attributes: str) -> str:
    """Add attributes before an HTML tag's closing bracket."""
    if tag.endswith("/>"):
        return f"{tag[:-2].rstrip()} {attributes} />"
    return f"{tag[:-1].rstrip()} {attributes}>"


def mark_product_media(source: str, product_name: str) -> str:
    """Make illustrative product-media status visible without JavaScript."""

    def mark_picture(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "data-evidence-status=" in tag:
            return tag
        return insert_tag_attributes(tag, 'data-evidence-status="illustrative"')

    def mark_image(match: re.Match[str]) -> str:
        tag = match.group(0)
        alt_match = re.search(r'alt="([^"]*)"', tag)
        if alt_match and not alt_match.group(1).lower().startswith(
            "illustrative product-planning reference"
        ):
            prefixed_alt = f"Illustrative product-planning reference: {alt_match.group(1)}"
            tag = tag[: alt_match.start(1)] + prefixed_alt + tag[alt_match.end(1) :]
        elif not alt_match:
            tag = insert_tag_attributes(
                tag,
                f'alt="Illustrative product-planning reference for {escaped(product_name)}"',
            )
        missing_attributes = []
        if "data-evidence-status=" not in tag:
            missing_attributes.append('data-evidence-status="illustrative"')
        if "data-media-kind=" not in tag:
            missing_attributes.append('data-media-kind="product-planning-reference"')
        if missing_attributes:
            tag = insert_tag_attributes(tag, " ".join(missing_attributes))
        return tag

    source = re.sub(r"<picture\b[^>]*>", mark_picture, source)
    source = re.sub(r"<img\b[^>]*>", mark_image, source)
    return source


def add_static_product_evidence() -> None:
    """Expose image and capability boundaries to HTML-only crawlers."""
    disclosure = (
        '<p class="product-detail-disclosure"><strong>Image and page scope:</strong> '
        "images are illustrative product-planning references, not photographs of available "
        "stock, current production, customer orders, or approved specifications. Exact product "
        "scope, materials, construction, decoration, MOQ, sampling, lead time, packing, and "
        "reorder conditions require project-specific confirmation.</p>"
    )
    for path in sorted((ROOT / "products").glob("*.html")):
        if path.name in PRODUCT_HUB_FILENAMES:
            continue
        source = path.read_text(encoding="utf-8")
        heading_match = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", source)
        if not heading_match:
            raise ValueError(f"Product page has no h1: {path}")
        product_name = html.unescape(re.sub(r"<[^>]+>", "", heading_match.group(1))).strip()
        source = mark_product_media(source, product_name)
        if "product-detail-disclosure" not in source:
            hero_summary = re.compile(
                r'(<section class="product-hero"[\s\S]*?<h1[^>]*>[\s\S]*?</h1>\s*<p(?:\s[^>]*)?>[\s\S]*?</p>)'
            )
            source, replacements = hero_summary.subn(rf"\1{disclosure}", source, count=1)
            if replacements != 1:
                raise ValueError(f"Could not insert static product disclosure: {path}")
        social_alt = f"Illustrative product-planning reference for {product_name}"
        if 'property="og:image:alt"' not in source:
            source, replacements = re.subn(
                r'(<meta property="og:image"[^>]*>)',
                rf'\1\n    <meta property="og:image:alt" content="{escaped(social_alt)}" />',
                source,
                count=1,
            )
            if replacements != 1:
                raise ValueError(f"Could not insert Open Graph image alt: {path}")
        if 'name="twitter:image:alt"' not in source:
            source, replacements = re.subn(
                r'(<meta name="twitter:image"[^>]*>)',
                rf'\1\n    <meta name="twitter:image:alt" content="{escaped(social_alt)}" />',
                source,
                count=1,
            )
            if replacements != 1:
                raise ValueError(f"Could not insert X image alt: {path}")
        path.write_text(source, encoding="utf-8")


def main() -> None:
    items = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    slugs = [item["slug"] for item in items]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Duplicate product-expansion slug")
    rendered_pages: dict[str, str] = {}
    for item in items:
        if item.get("category") not in {"activewear", "teamwear", "specialty"}:
            raise ValueError(f"Unsupported product category for {item['slug']}")
        memberships = [
            group_name
            for group_name, group_slugs in LLMS_GROUP_SLUGS.items()
            if item["slug"] in group_slugs
        ]
        if len(memberships) != 1:
            raise ValueError(
                f"{item['slug']} must belong to exactly one llms.txt group; found {memberships}"
            )
        parent_path = ROOT / "products" / f"{item['parent_slug']}.html"
        if not parent_path.exists():
            raise FileNotFoundError(f"Missing parent page for {item['slug']}: {parent_path}")
        target_path = ROOT / "products" / f"{item['slug']}.html"
        expected_marker = f"<!-- {GENERATED_PRODUCT_MARKER}:{item['slug']} -->"
        if target_path.exists():
            existing_source = target_path.read_text(encoding="utf-8")
            is_legacy_generated = "Buyer-facing planning scope, not a fixed quotation." in existing_source
            if expected_marker not in existing_source and not is_legacy_generated:
                raise ValueError(f"Refusing to overwrite non-generated product page: {target_path}")
        if len(item["direction_images"]) != 3:
            raise ValueError(f"{item['slug']} must define exactly three direction images")
        if len(item["decision_focus"]) != 4:
            raise ValueError(f"{item['slug']} must define exactly four decision-focus cards")
        rendered_pages[item["slug"]] = render_page(item)
    for slug, rendered in rendered_pages.items():
        (ROOT / "products" / f"{slug}.html").write_text(rendered, encoding="utf-8")
    add_static_product_evidence()
    update_product_index(items)
    update_parent_clusters(items)
    update_discovery_hubs(items)
    update_collection_dates()
    update_llms(items)
    update_sitemap(items)
    print(f"Generated {len(items)} product pages and integrated their discovery paths.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import deque
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse


ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_ORIGIN = "https://glorystarwears.com"
EXPECTED_SCRIPT_VERSION = "20260729-2"
EXPECTED_FORM_STYLE_VERSION = "20260728-1"
PRIORITY_LCP_PAGES = {
    "index.html",
    "sportswear-manufacturer.html",
    "low-moq-sportswear-manufacturer.html",
    "private-label-activewear-manufacturer.html",
    "custom-teamwear-uniforms.html",
    "one-stop-service.html",
    "process.html",
    "products/yoga-wear.html",
    "products/new-products.html",
    "products/training-wear.html",
    "products/compression-base-layers.html",
    "products/private-label-gym-clothing.html",
    "products/private-label-sportswear-packaging.html",
    "products/basketball-wear.html",
    "products/basketball-jerseys.html",
    "products/football-kits.html",
    "resources/index.html",
    "resources/sportswear-manufacturer-due-diligence-checklist.html",
    "resources/private-label-activewear-moq.html",
    "resources/custom-sportswear-tech-pack.html",
    "resources/sportswear-logo-artwork-preparation-guide.html",
    "resources/sportswear-packaging-label-handoff-checklist.html",
    "resources/sportswear-aql-inspection-checklist.html",
    "resources/teamwear-roster-packing-guide.html",
}
TITLE_LENGTH_RANGE = (30, 65)
DESCRIPTION_LENGTH_RANGE = (100, 170)
IMAGE_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
NON_VISIBLE_RE = re.compile(
    r"<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>",
    re.IGNORECASE,
)
TAG_RE = re.compile(r"<[^>]+>")
IGNORED_PATH_PARTS = {
    ".git",
    ".local-backups",
    ".vercel",
    ".wrangler",
    "build",
    "dist",
    "node_modules",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.h1_count = 0
        self.description = ""
        self.robots = ""
        self.canonical = ""
        self.ids = []
        self.links = []
        self.assets = []
        self.image_assets = []
        self.image_preloads = []
        self.json_ld_blocks = []
        self.current_json_ld = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            meta_name = attributes.get("name", "").lower()
            if meta_name == "description":
                self.description = attributes.get("content", "").strip()
            elif meta_name == "robots":
                self.robots = attributes.get("content", "").strip()
        elif tag == "link":
            relationships = set(attributes.get("rel", "").lower().split())
            href = attributes.get("href", "")
            if "canonical" in relationships:
                self.canonical = href
            if relationships.intersection({"stylesheet", "icon"}) and href:
                self.assets.append(href)
            if "preload" in relationships and attributes.get("as", "").lower() == "image":
                self.image_preloads.append(attributes)
                if href:
                    self.assets.append(href)
                    self.image_assets.append(href)
                for candidate in attributes.get("imagesrcset", "").split(","):
                    source = candidate.strip().split(" ", 1)[0]
                    if source:
                        self.assets.append(source)
                        self.image_assets.append(source)
        elif tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        elif tag in {"img", "source"}:
            if tag == "img" and attributes.get("src"):
                self.assets.append(attributes["src"])
                self.image_assets.append(attributes["src"])
            for candidate in attributes.get("srcset", "").split(","):
                source = candidate.strip().split(" ", 1)[0]
                if source:
                    self.assets.append(source)
                    self.image_assets.append(source)
        elif tag == "script":
            if attributes.get("src"):
                self.assets.append(attributes["src"])
            if attributes.get("type", "").lower() == "application/ld+json":
                self.current_json_ld = []

        if attributes.get("id"):
            self.ids.append(attributes["id"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.current_json_ld is not None:
            self.json_ld_blocks.append("".join(self.current_json_ld).strip())
            self.current_json_ld = None

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.current_json_ld is not None:
            self.current_json_ld.append(data)

    @property
    def title(self):
        return "".join(self.title_parts).strip()


def site_file_for_url(url):
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and parsed.netloc != "glorystarwears.com":
        return None

    path = unquote(parsed.path)
    if path == "/":
        return ROOT / "index.html"
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    return ROOT / path.lstrip("/")


def duplicate_values(values):
    seen = set()
    duplicates = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def normalized_text(value):
    return re.sub(r"\s+", " ", unescape(value)).strip()


def structured_nodes(value):
    if not isinstance(value, (dict, list)):
        return
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from structured_nodes(child)
    else:
        for child in value:
            yield from structured_nodes(child)


def main():
    errors = []
    pages = {}
    page_internal_links = {}
    canonical_owners = {}
    title_owners = {}
    description_owners = {}
    internal_targets = set()
    local_assets = set()
    json_ld_count = 0
    image_count = 0
    avif_image_count = 0

    script_source = (ROOT / "script.js").read_text(encoding="utf-8")
    required_attribution_markers = {
        '"ai_assistant"': "AI-assistant traffic classification",
        "traffic_channel": "traffic channel event field",
        "traffic_source": "traffic source event field",
        "referrer_host": "referrer host event field",
    }
    for marker, label in required_attribution_markers.items():
        if marker not in script_source:
            errors.append(f"script.js: missing {label}")

    vercel_config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    www_redirect_present = any(
        redirect.get("destination") == "https://glorystarwears.com/$1"
        and redirect.get("permanent") is True
        and any(
            condition.get("type") == "host"
            and condition.get("value") == "www.glorystarwears.com"
            for condition in redirect.get("has", [])
        )
        for redirect in vercel_config.get("redirects", [])
    )
    if not www_redirect_present:
        errors.append("vercel.json: missing permanent www-to-apex host redirect")

    node_binary = shutil.which("node")
    if node_binary:
        syntax_check = subprocess.run(
            [node_binary, "--check", str(ROOT / "script.js")],
            capture_output=True,
            text=True,
            check=False,
        )
        if syntax_check.returncode:
            details = (syntax_check.stderr or syntax_check.stdout).strip()
            errors.append(f"script.js: JavaScript syntax check failed: {details}")

    html_files = sorted(
        path
        for path in ROOT.rglob("*.html")
        if not IGNORED_PATH_PARTS.intersection(path.relative_to(ROOT).parts)
    )
    for html_file in html_files:
        parser = PageParser()
        source = html_file.read_text(encoding="utf-8")
        parser.feed(source)
        visible_text = normalized_text(
            TAG_RE.sub(" ", NON_VISIBLE_RE.sub(" ", source))
        )
        relative_name = html_file.relative_to(ROOT).as_posix()
        pages[html_file.resolve()] = parser

        if not parser.title:
            errors.append(f"{relative_name}: missing title")
        elif not TITLE_LENGTH_RANGE[0] <= len(parser.title) <= TITLE_LENGTH_RANGE[1]:
            errors.append(
                f"{relative_name}: title length {len(parser.title)} is outside "
                f"{TITLE_LENGTH_RANGE[0]}-{TITLE_LENGTH_RANGE[1]} characters"
            )
        if not parser.description:
            errors.append(f"{relative_name}: missing meta description")
        elif not DESCRIPTION_LENGTH_RANGE[0] <= len(parser.description) <= DESCRIPTION_LENGTH_RANGE[1]:
            errors.append(
                f"{relative_name}: meta description length {len(parser.description)} is outside "
                f"{DESCRIPTION_LENGTH_RANGE[0]}-{DESCRIPTION_LENGTH_RANGE[1]} characters"
            )
        if not parser.canonical:
            errors.append(f"{relative_name}: missing canonical")
        if parser.h1_count != 1:
            errors.append(f"{relative_name}: expected one H1, found {parser.h1_count}")

        if relative_name == "process.html":
            required_process_markers = {
                "sportswear-sampling-production-approval-register.csv": "sampling approval register link",
                'data-resource-download="sampling-production-approval-register"': "sampling approval download tracking",
                '"@type": "DigitalDocument"': "sampling approval document schema",
                '"dateModified": "2026-08-01"': "current process modification date",
            }
            for marker, label in required_process_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "private-label-activewear-manufacturer.html":
            required_activewear_markers = {
                "private-label-activewear-collection-planner.csv": "activewear collection planner link",
                'data-resource-download="private-label-activewear-collection-planner"': "activewear planner download tracking",
                '"@type": "DigitalDocument"': "activewear planner document schema",
                '"dateModified": "2026-08-01"': "current activewear page modification date",
            }
            for marker, label in required_activewear_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "resources/custom-sportswear-tech-pack.html":
            required_tech_pack_markers = {
                "sportswear-tech-pack-intake-template.csv": "tech pack template link",
                'data-resource-download="sportswear-tech-pack-intake-template"': "tech pack download tracking",
                '"@type":"DigitalDocument"': "tech pack document schema",
                '"isAccessibleForFree":true': "free template disclosure in schema",
                '"dateModified":"2026-08-01"': "current tech pack modification date",
                "What it is not:": "visible template scope disclosure",
            }
            for marker, label in required_tech_pack_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "resources/sportswear-logo-artwork-preparation-guide.html":
            required_artwork_markers = {
                "sportswear-artwork-approval-register.csv": "artwork approval register link",
                'data-resource-download="sportswear-artwork-approval-register"': "artwork download tracking",
                '"@type":"DigitalDocument"': "artwork document schema",
                '"isAccessibleForFree":true': "free artwork register disclosure in schema",
                '"dateModified":"2026-08-01"': "current artwork guide modification date",
                "rights confirmation": "artwork rights field disclosure",
                "adobe.com/creativecloud/file-types/image/comparison/raster-vs-vector.html": "authoritative vector and raster reference",
            }
            for marker, label in required_artwork_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "resources/sportswear-packaging-label-handoff-checklist.html":
            required_packaging_markers = {
                "sportswear-packaging-handoff-register.csv": "packaging handoff register link",
                'data-resource-download="sportswear-packaging-handoff-register"': "packaging download tracking",
                '"@type":"DigitalDocument"': "packaging document schema",
                '"isAccessibleForFree":true': "free packaging register disclosure in schema",
                '"dateModified":"2026-08-02"': "current packaging guide modification date",
                "gs1.org/standards/barcodes": "authoritative barcode reference",
                "ftc.gov/business-guidance/industry/clothing-and-textiles": "authoritative clothing labeling reference",
            }
            for marker, label in required_packaging_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        duplicate_ids = duplicate_values(parser.ids)
        if duplicate_ids:
            errors.append(f"{relative_name}: duplicate IDs: {', '.join(duplicate_ids)}")

        if parser.canonical:
            previous_owner = canonical_owners.get(parser.canonical)
            if previous_owner:
                errors.append(
                    f"{relative_name}: canonical duplicates {previous_owner}: {parser.canonical}"
                )
            canonical_owners[parser.canonical] = relative_name

        for value, owners, label in (
            (parser.title, title_owners, "title"),
            (parser.description, description_owners, "meta description"),
        ):
            if not value:
                continue
            previous_owner = owners.get(value)
            if previous_owner:
                errors.append(
                    f"{relative_name}: duplicate {label} also used by {previous_owner}"
                )
            owners[value] = relative_name

        structured_types = set()
        for block in parser.json_ld_blocks:
            json_ld_count += 1
            try:
                structured_data = json.loads(block)
            except json.JSONDecodeError as error:
                errors.append(f"{relative_name}: invalid JSON-LD: {error}")
                continue

            for node in structured_nodes(structured_data):
                node_type = node.get("@type")
                if isinstance(node_type, str):
                    structured_types.add(node_type)
                elif isinstance(node_type, list):
                    structured_types.update(
                        value for value in node_type if isinstance(value, str)
                    )

                if node_type != "FAQPage":
                    continue
                for question in node.get("mainEntity", []):
                    question_text = normalized_text(question.get("name", ""))
                    answer_text = normalized_text(
                        question.get("acceptedAnswer", {}).get("text", "")
                    )
                    if question_text and question_text not in visible_text:
                        errors.append(
                            f"{relative_name}: FAQ question is not visible: "
                            f"{question_text}"
                        )
                    if answer_text and answer_text not in visible_text:
                        errors.append(
                            f"{relative_name}: FAQ answer is not visible for: "
                            f"{question_text}"
                        )

        if 'class="breadcrumb"' in source and "BreadcrumbList" not in structured_types:
            errors.append(
                f"{relative_name}: visible breadcrumb is missing BreadcrumbList JSON-LD"
            )

        if "script.js" in source and f"script.js?v={EXPECTED_SCRIPT_VERSION}" not in source:
            errors.append(
                f"{relative_name}: expected script version {EXPECTED_SCRIPT_VERSION}"
            )

        if "data-quote-form" in source:
            required_form_markers = {
                'name="consent" type="checkbox" required': "required privacy consent",
                "data-server-submit": "server submit control",
                "data-whatsapp-inquiry": "WhatsApp fallback",
                "data-email-inquiry": "email fallback",
                "data-copy-inquiry": "copy fallback",
                'href="./privacy.html"': "privacy notice link",
            }
            for marker, label in required_form_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: quote form is missing {label}")
            if f"styles.css?v={EXPECTED_FORM_STYLE_VERSION}" not in source:
                errors.append(
                    f"{relative_name}: expected form style version "
                    f"{EXPECTED_FORM_STYLE_VERSION}"
                )

        for preload in parser.image_preloads:
            if preload.get("type", "").lower() != "image/avif":
                errors.append(f"{relative_name}: image preload is not AVIF")
            if preload.get("fetchpriority", "").lower() != "high":
                errors.append(
                    f"{relative_name}: image preload is missing fetchpriority=high"
                )

        for image_match in IMAGE_RE.finditer(source):
            image_count += 1
            picture_start = source.rfind("<picture", 0, image_match.start())
            picture_end = source.rfind("</picture>", 0, image_match.start())
            if picture_start <= picture_end:
                errors.append(
                    f"{relative_name}: image is missing an AVIF picture source"
                )
                continue
            picture_close = source.find("</picture>", image_match.end())
            picture_markup = source[picture_start:picture_close]
            if 'type="image/avif"' not in picture_markup:
                errors.append(
                    f"{relative_name}: image picture is missing image/avif"
                )
                continue
            avif_image_count += 1

        base_url = parser.canonical or urljoin(f"{PRODUCTION_ORIGIN}/", relative_name)
        page_internal_links[html_file.resolve()] = set()
        for href in parser.links:
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            target_url = urljoin(base_url, href)
            target_file = site_file_for_url(target_url)
            if target_file is not None:
                resolved_target = target_file.resolve()
                internal_targets.add(resolved_target)
                page_internal_links[html_file.resolve()].add(resolved_target)

        for asset in parser.assets:
            if asset.startswith("data:"):
                continue
            asset_url = urljoin(base_url, asset)
            asset_file = site_file_for_url(asset_url)
            if asset_file is not None:
                local_assets.add(asset_file.resolve())

    for target in sorted(internal_targets):
        if not target.exists():
            errors.append(f"broken internal target: {target.relative_to(ROOT)}")

    for asset in sorted(local_assets):
        if not asset.exists():
            errors.append(f"missing local asset: {asset.relative_to(ROOT)}")

    sitemap_tree = ET.parse(ROOT / "sitemap.xml")
    sitemap_root = sitemap_tree.getroot()
    namespace = {
        "s": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "image": "http://www.google.com/schemas/sitemap-image/1.1",
    }
    sitemap_entries = []
    for url_node in sitemap_root.findall("s:url", namespace):
        location_node = url_node.find("s:loc", namespace)
        if location_node is None or not location_node.text:
            continue
        sitemap_entries.append(
            {
                "url": location_node.text.strip(),
                "images": [
                    node.text.strip()
                    for node in url_node.findall("image:image/image:loc", namespace)
                    if node.text
                ],
            }
        )
    sitemap_urls = [entry["url"] for entry in sitemap_entries]

    for duplicate in duplicate_values(sitemap_urls):
        errors.append(f"duplicate sitemap URL: {duplicate}")

    sitemap_url_set = set(sitemap_urls)

    indexable_files = {
        html_file
        for html_file, page in pages.items()
        if page.canonical in sitemap_url_set and "noindex" not in page.robots.lower()
    }
    start_file = (ROOT / "index.html").resolve()
    click_depth = {start_file: 0}
    queue = deque([start_file])
    while queue:
        source_file = queue.popleft()
        next_depth = click_depth[source_file] + 1
        for target_file in page_internal_links.get(source_file, set()):
            if target_file not in indexable_files or target_file in click_depth:
                continue
            click_depth[target_file] = next_depth
            queue.append(target_file)

    unreachable_indexable = sorted(indexable_files - set(click_depth))
    for html_file in unreachable_indexable:
        errors.append(
            f"{html_file.relative_to(ROOT)}: indexable page is unreachable from homepage"
        )

    deep_indexable = sorted(
        (depth, html_file)
        for html_file, depth in click_depth.items()
        if html_file in indexable_files and depth > 3
    )
    for depth, html_file in deep_indexable:
        errors.append(
            f"{html_file.relative_to(ROOT)}: click depth {depth} exceeds 3"
        )

    for relative_name in sorted(PRIORITY_LCP_PAGES):
        html_file = (ROOT / relative_name).resolve()
        page = pages.get(html_file)
        if page is None:
            errors.append(f"{relative_name}: priority LCP page is missing")
        elif not page.image_preloads:
            errors.append(f"{relative_name}: priority LCP page is missing an image preload")

    for html_file, page in pages.items():
        if not page.canonical:
            continue
        relative_name = html_file.relative_to(ROOT).as_posix()
        is_noindex = "noindex" in page.robots.lower()
        if is_noindex and page.canonical in sitemap_url_set:
            errors.append(f"noindex page appears in sitemap: {relative_name}")
        elif not is_noindex and page.canonical not in sitemap_url_set:
            errors.append(f"indexable page missing from sitemap: {relative_name}")

    for entry in sitemap_entries:
        url = entry["url"]
        target_file = site_file_for_url(url)
        if target_file is None or not target_file.exists():
            errors.append(f"sitemap URL has no local file: {url}")
            continue
        page = pages.get(target_file.resolve())
        if page is None:
            errors.append(f"sitemap target was not parsed: {url}")
        elif page.canonical != url:
            errors.append(f"sitemap/canonical mismatch: {url} != {page.canonical}")

        duplicate_images = duplicate_values(entry["images"])
        if duplicate_images:
            errors.append(
                f"sitemap URL has duplicate images: {url}: "
                f"{', '.join(duplicate_images)}"
            )

        if page is None:
            continue
        page_image_urls = {
            urljoin(page.canonical or url, asset)
            for asset in page.image_assets
        }
        for image_url in entry["images"]:
            image_file = site_file_for_url(image_url)
            if image_file is None or not image_file.exists():
                errors.append(f"sitemap image has no local file: {url}: {image_url}")
            if image_url not in page_image_urls:
                errors.append(
                    f"sitemap image is not referenced by page: {url}: {image_url}"
                )

    summary = {
        "html_files": len(html_files),
        "sitemap_urls": len(sitemap_urls),
        "sitemap_images": sum(len(entry["images"]) for entry in sitemap_entries),
        "unique_canonicals": len(canonical_owners),
        "unique_titles": len(title_owners),
        "unique_descriptions": len(description_owners),
        "json_ld_blocks": json_ld_count,
        "images": image_count,
        "avif_images": avif_image_count,
        "internal_targets": len(internal_targets),
        "local_assets": len(local_assets),
        "max_click_depth": max(click_depth.values(), default=0),
        "unreachable_indexable": len(unreachable_indexable),
        "errors": errors,
    }
    print(json.dumps(summary, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

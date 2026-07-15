#!/usr/bin/env python3

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse


ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_ORIGIN = "https://glorystarwears.com"
EXPECTED_ASSET_VERSION = "20260715-6"
TITLE_LENGTH_RANGE = (30, 65)
DESCRIPTION_LENGTH_RANGE = (100, 170)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.h1_count = 0
        self.description = ""
        self.canonical = ""
        self.ids = []
        self.links = []
        self.assets = []
        self.json_ld_blocks = []
        self.current_json_ld = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and attributes.get("name", "").lower() == "description":
            self.description = attributes.get("content", "").strip()
        elif tag == "link":
            relationships = set(attributes.get("rel", "").lower().split())
            href = attributes.get("href", "")
            if "canonical" in relationships:
                self.canonical = href
            if relationships.intersection({"stylesheet", "icon"}) and href:
                self.assets.append(href)
        elif tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        elif tag in {"img", "source"}:
            if tag == "img" and attributes.get("src"):
                self.assets.append(attributes["src"])
            for candidate in attributes.get("srcset", "").split(","):
                source = candidate.strip().split(" ", 1)[0]
                if source:
                    self.assets.append(source)
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


def main():
    errors = []
    pages = {}
    canonical_owners = {}
    title_owners = {}
    description_owners = {}
    internal_targets = set()
    local_assets = set()
    json_ld_count = 0

    html_files = sorted(ROOT.rglob("*.html"))
    for html_file in html_files:
        parser = PageParser()
        source = html_file.read_text(encoding="utf-8")
        parser.feed(source)
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

        for block in parser.json_ld_blocks:
            json_ld_count += 1
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                errors.append(f"{relative_name}: invalid JSON-LD: {error}")

        if "styles.css" in source or "script.js" in source:
            if f"v={EXPECTED_ASSET_VERSION}" not in source:
                errors.append(
                    f"{relative_name}: expected asset version {EXPECTED_ASSET_VERSION}"
                )

        base_url = parser.canonical or urljoin(f"{PRODUCTION_ORIGIN}/", relative_name)
        for href in parser.links:
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            target_url = urljoin(base_url, href)
            target_file = site_file_for_url(target_url)
            if target_file is not None:
                internal_targets.add(target_file.resolve())

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
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = [
        node.text.strip()
        for node in sitemap_root.findall("s:url/s:loc", namespace)
        if node.text
    ]

    for duplicate in duplicate_values(sitemap_urls):
        errors.append(f"duplicate sitemap URL: {duplicate}")

    for url in sitemap_urls:
        target_file = site_file_for_url(url)
        if target_file is None or not target_file.exists():
            errors.append(f"sitemap URL has no local file: {url}")
            continue
        page = pages.get(target_file.resolve())
        if page is None:
            errors.append(f"sitemap target was not parsed: {url}")
        elif page.canonical != url:
            errors.append(f"sitemap/canonical mismatch: {url} != {page.canonical}")

    summary = {
        "html_files": len(html_files),
        "sitemap_urls": len(sitemap_urls),
        "unique_canonicals": len(canonical_owners),
        "unique_titles": len(title_owners),
        "unique_descriptions": len(description_owners),
        "json_ld_blocks": json_ld_count,
        "internal_targets": len(internal_targets),
        "local_assets": len(local_assets),
        "errors": errors,
    }
    print(json.dumps(summary, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

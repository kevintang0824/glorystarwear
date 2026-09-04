#!/usr/bin/env python3
"""Audit complete static locale editions against the English source DOM."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://glorystarwears.com"
LOCALES = {"fr": "fr", "es": "es", "pt": "pt", "ru": "ru", "zh-cn": "zh-CN"}


def table(name):
    result = {}
    for line in (ROOT / "scripts/locales" / name).read_text().splitlines():
        if line.strip():
            key, *values = line.split("|")
            result[key] = values
    return result


PAGES = table("pages.tsv")


def route(key):
    return "/" + (key[:-5] if key.endswith("index") else key + ".html")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = ""; self.title = ""; self.description = ""; self.canonical = ""; self.alternates = []
        self.main = False; self.skip = 0; self.tags = []; self.text = []; self.images = 0; self.forms = 0; self.controls = 0; self.links = []; self.scripts = []; self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html": self.lang = attrs.get("lang", "")
        if tag == "title": self.in_title = True
        if tag == "meta" and attrs.get("name") == "description": self.description = attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical": self.canonical = attrs.get("href", "")
        if tag == "link" and attrs.get("rel") == "alternate" and attrs.get("hreflang"): self.alternates.append((attrs.get("hreflang", ""), attrs.get("href", "")))
        if tag == "main": self.main = True
        if self.main:
            self.tags.append(tag)
            if tag == "img": self.images += 1
            if tag == "form": self.forms += 1
            if tag in ("input", "select", "textarea", "button"): self.controls += 1
            if tag == "a" and attrs.get("href"): self.links.append(attrs["href"])
        if tag == "script" and attrs.get("src"): self.scripts.append(attrs["src"])
        if tag in ("script", "style", "svg"): self.skip += 1

    def handle_endtag(self, tag):
        if self.main: self.tags.append("/" + tag)
        if tag == "main": self.main = False
        if tag == "title": self.in_title = False
        if tag in ("script", "style", "svg") and self.skip: self.skip -= 1

    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.main and not self.skip and data.strip(): self.text.append(" ".join(data.split()))


def local_file(current_key, href):
    parsed = urlsplit(urljoin(ORIGIN + route(current_key), href))
    if parsed.netloc and parsed.netloc != "glorystarwears.com": return None
    path = parsed.path
    if path.endswith("/"): path += "index.html"
    target = ROOT / path.lstrip("/")
    return target if target.exists() else None


errors = []
source_pages = {}
for key in PAGES:
    path = ROOT / (key + ".html")
    page = Page(); page.feed(path.read_text()); source_pages[key] = page

for locale, language in LOCALES.items():
    for key, values in PAGES.items():
        path = ROOT / locale / (key + ".html")
        if not path.exists(): errors.append(f"{path}: missing"); continue
        source = source_pages[key]; page = Page(); page.feed(path.read_text())
        expected_title = values[list(LOCALES).index(locale) + 1] + " | GloryStarWear"
        expected_alt = [("en", ORIGIN + route(key))] + [(lang, ORIGIN + f"/{loc}{route(key)}") for loc, lang in LOCALES.items()] + [("x-default", ORIGIN + route(key))]
        if page.lang != language: errors.append(f"{path}: lang mismatch")
        if page.title.strip() != expected_title: errors.append(f"{path}: title mismatch")
        if len(page.description.strip()) < 25 and key != "404": errors.append(f"{path}: short description")
        if page.canonical != ORIGIN + f"/{locale}{route(key)}": errors.append(f"{path}: canonical mismatch")
        if page.alternates != expected_alt: errors.append(f"{path}: hreflang mismatch")
        if page.tags != source.tags: errors.append(f"{path}: main DOM structure differs from English")
        if len(page.text) != len(source.text): errors.append(f"{path}: visible content nodes differ from English")
        if (page.images, page.forms, page.controls, len(page.links)) != (source.images, source.forms, source.controls, len(source.links)): errors.append(f"{path}: controls or links differ from English")
        source_html = path.read_text()
        menu = re.findall(r'<a href="([^"]+)" data-site-language="([^"]+)"', source_html)
        expected_menu = [(route(key), "en")] + [(f"/{loc}{route(key)}", lang) for loc, lang in LOCALES.items()]
        if menu != expected_menu: errors.append(f"{path}: language menu mismatch")
        current = re.findall(r'<a href="[^"]+" data-site-language="([^"]+)"[^>]*aria-current="true"', source_html)
        if current != [language]: errors.append(f"{path}: current language mismatch")
        if not any("/script.js" in src for src in page.scripts): errors.append(f"{path}: shared runtime missing")
        if not any("/assets/language.js" in src for src in page.scripts): errors.append(f"{path}: language runtime missing")
        for href in page.links:
            if href.startswith(("mailto:", "tel:", "https://", "http://", "#", "?")): continue
            if local_file(key, href) is None and not (href.startswith("/") and (ROOT / href.lstrip("/")).exists()): errors.append(f"{path}: missing target {href}")
        body = " ".join(page.text)
        if locale == "zh-cn" and len(re.findall(r"[\u4e00-\u9fff]", body)) < 80 and key != "404": errors.append(f"{path}: insufficient Chinese content")
        if locale == "ru" and len(re.findall(r"[А-Яа-яЁё]", body)) < 150: errors.append(f"{path}: insufficient Russian content")
        if locale in ("fr", "es", "pt") and len(body) < 500 and key != "404": errors.append(f"{path}: insufficient localized content")
        for marker in ("translate.google", "gtranslate", "goog-te-combo", "gloryStarTranslateInit"):
            if marker.lower() in source_html.lower(): errors.append(f"{path}: translator marker {marker}")

for key in PAGES:
    path = ROOT / (key + ".html"); page = Page(); page.feed(path.read_text())
    expected_alt = [("en", ORIGIN + route(key))] + [(lang, ORIGIN + f"/{loc}{route(key)}") for loc, lang in LOCALES.items()] + [("x-default", ORIGIN + route(key))]
    if page.alternates != expected_alt: errors.append(f"{path}: English hreflang mismatch")

try:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}; urls = [node.text for node in ET.parse(ROOT / "sitemap-languages.xml").getroot().findall("s:url/s:loc", ns)]
except Exception as exc:
    urls = []; errors.append(f"sitemap-languages.xml: {exc}")
expected_urls = [ORIGIN + f"/{locale}{route(key)}" for locale in LOCALES for key in PAGES if "noindex" not in (ROOT / (key + ".html")).read_text().split("</head>", 1)[0]]
if sorted(urls) != sorted(expected_urls): errors.append("sitemap-languages.xml: URL set mismatch")

summary = {"languages": len(LOCALES), "source_routes": len(PAGES), "localized_pages": len(PAGES) * len(LOCALES), "localized_sitemap_urls": len(urls), "errors": errors}
print(json.dumps(summary, ensure_ascii=False, indent=2)); raise SystemExit(bool(errors))

#!/usr/bin/env python3
"""Regression checks for localized page identity and visible FAQ markup."""
import json
import re
import unittest
from collections import Counter

import build_full_locales as locales


def schema_blocks(markup):
    return [json.loads(raw) for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>',
        markup, flags=re.I,
    )]


def nodes(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from nodes(item)


def strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, str):
        yield value


class LocaleSchemaTests(unittest.TestCase):
    def test_localized_company_name_keeps_the_public_brand(self):
        for locale in locales.LOCALE_ORDER:
            content = locales.load_content(locale)
            self.assertFalse(any(re.search(r"\bGloryStarWar\b", text) for text in content.values()))
            for key in ("index", "about-factory"):
                rendered = locales.replace_html(locales.source_for(key).read_text(), key, locale, content)
                with self.subTest(locale=locale, page=key):
                    self.assertIn("© 2026 GloryStarWear", rendered)
                    self.assertIn(content["GloryStarWear home"], rendered)

    def test_company_identity_and_program_routes_stay_connected(self):
        origin = locales.ORIGIN
        definitions = []
        for page in ("index", "about-factory"):
            markup = locales.source_for(page).read_text()
            company = next(n for b in schema_blocks(markup) for n in nodes(b)
                           if n.get("@type") == "Organization")
            definitions.append(company)
            self.assertIn(company["legalName"], markup)
            self.assertIn(company["email"], markup)
            self.assertIn(company["address"]["addressLocality"], markup)
        self.assertEqual(definitions[0], definitions[1])
        references = definitions[0]["hasOfferCatalog"]["itemListElement"]
        self.assertEqual(len(references), 2)
        for offer in references:
            service_id = offer["itemOffered"]["@id"]
            page = service_id.removeprefix(origin + "/").split(".html#")[0]
            markup = locales.source_for(page).read_text()
            service = next(n for b in schema_blocks(markup) for n in nodes(b)
                           if n.get("@id") == service_id and n.get("@type") == "Service")
            self.assertEqual(service["provider"]["@id"], definitions[0]["@id"])
            channel = service["availableChannel"]["serviceUrl"]
            self.assertIn(channel.removeprefix(origin + "/"), markup)

    def test_public_legal_name_is_not_replaced_by_a_translation(self):
        for locale in locales.LOCALE_ORDER:
            source = locales.source_for("about-factory").read_text()
            rendered = locales.replace_html(source, "about-factory", locale, locales.load_content(locale))
            with self.subTest(locale=locale):
                self.assertIn("<p>Xiamen Glorystar Import and Export Co., Ltd.</p>", rendered)

    def test_known_page_routes_only(self):
        origin = locales.ORIGIN
        examples = {
            origin + "/private-label-activewear-manufacturer.html#service": origin + "/fr/private-label-activewear-manufacturer.html#service",
            origin + "/products/?filter=activewear#range": origin + "/fr/products/?filter=activewear#range",
            origin + "/#organization": origin + "/#organization",
            origin + "/#website": origin + "/#website",
            origin + "/assets/images/hero-brand-campaign.jpg": origin + "/assets/images/hero-brand-campaign.jpg",
            origin + "/assets/downloads/private-label-activewear-collection-planner.csv": origin + "/assets/downloads/private-label-activewear-collection-planner.csv",
            "https://example.com/source.html": "https://example.com/source.html",
            "mailto:kevin@glorystarwears.com": "mailto:kevin@glorystarwears.com",
            "tel:+8618020755949": "tel:+8618020755949",
        }
        for source, expected in examples.items():
            with self.subTest(url=source):
                self.assertEqual(locales.localized_schema_url(source, "index", "fr"), expected)

    def test_real_pages_match_localized_content(self):
        keys = [
            "index", "about-factory", "faq", "private-label-activewear-manufacturer",
            "custom-teamwear-uniforms", "products/private-label-gym-clothing",
            "products/american-football-uniforms", "resources/custom-sportswear-tech-pack",
            "blog/clothing-sample-rounds-before-bulk-production",
        ]
        for locale in locales.LOCALE_ORDER:
            content = locales.load_content(locale)
            for key in keys:
                with self.subTest(locale=locale, page=key):
                    source = locales.source_for(key).read_text()
                    rendered = locales.replace_html(source, key, locale, content)
                    originals = schema_blocks(source)
                    translated = schema_blocks(rendered)
                    self.assertEqual(len(originals), len(translated))
                    canonical = locales.ORIGIN + locales.locale_route(key, locale)
                    self.assertIn(f'rel="canonical" href="{canonical}"', rendered)

                    visible_faq = locales.FaqText()
                    visible_faq.feed(rendered)
                    visible_pairs = dict(visible_faq.pairs)
                    for block in translated:
                        for node in nodes(block):
                            kind = node.get("@type")
                            if kind in locales.SCHEMA_PAGE_TYPES:
                                self.assertEqual(node.get("inLanguage"), locales.LOCALES[locale][0])
                                if node.get("url"):
                                    self.assertTrue(node["url"].startswith(locales.ORIGIN + f"/{locale}/"))
                            if kind == "Question":
                                self.assertIn(node["name"], visible_pairs)
                                self.assertEqual(node["acceptedAnswer"]["text"], visible_pairs[node["name"]])

                    # A locale must not invent a new organization/site entity or
                    # move media, English downloads, or external source links.
                    for original, localized in zip(originals, translated):
                        shared_before = [n for n in nodes(original) if n.get("@type") in ("Organization", "WebSite")]
                        shared_after = [n for n in nodes(localized) if n.get("@type") in ("Organization", "WebSite")]
                        self.assertEqual(shared_before, shared_after)
                        def fixed_urls(value):
                            return Counter(s for s in strings(value) if s in locales.SHARED_SCHEMA_IDS or "/assets/" in s or s.startswith("http") and not s.startswith(locales.ORIGIN + "/"))
                        self.assertEqual(fixed_urls(original), fixed_urls(localized))


if __name__ == "__main__":
    unittest.main()

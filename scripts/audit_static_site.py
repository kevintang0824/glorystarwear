#!/usr/bin/env python3

import csv
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, deque
from html import unescape
from html.parser import HTMLParser
from math import log, sqrt
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

from site_chrome import site_footer_markup, site_header_markup


ROOT = Path(__file__).resolve().parent.parent
PRODUCTION_ORIGIN = "https://glorystarwears.com"
EXPECTED_SCRIPT_VERSION = "20260828-8"
EXPECTED_FORM_STYLE_VERSION = "20260828-8"
CATALOG_PATH = ROOT / "scripts" / "product_expansion_catalog.json"
CATALOG_ITEMS = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
CATALOG_SLUG_LIST = [item["slug"] for item in CATALOG_ITEMS]
EXPANDED_PRODUCT_SLUGS = frozenset(CATALOG_SLUG_LIST)
RULE_SOURCE_PRODUCT_SLUGS = frozenset(
    item["slug"] for item in CATALOG_ITEMS if item.get("official_sources")
)
NON_CONCRETE_PRODUCT_SLUGS = {"index", "lookbook", "new-products", "more-sports"}
BASE_CONCRETE_PRODUCT_COUNT = 59
EXPECTED_CONCRETE_PRODUCT_COUNT = BASE_CONCRETE_PRODUCT_COUNT + len(EXPANDED_PRODUCT_SLUGS)
BASE_QUOTE_PRODUCT_OPTION_COUNT = 31
EXPECTED_QUOTE_PRODUCT_OPTION_COUNT = BASE_QUOTE_PRODUCT_OPTION_COUNT + len(EXPANDED_PRODUCT_SLUGS)
GENERATED_PRODUCT_MARKER_RE = re.compile(
    r"<!-- GENERATED_PRODUCT_PAGE:([a-z0-9]+(?:-[a-z0-9]+)*) -->"
)
PRIORITY_LCP_PAGES = {
    "index.html",
    "sportswear-manufacturer.html",
    "low-moq-sportswear-manufacturer.html",
    "private-label-activewear-manufacturer.html",
    "custom-teamwear-uniforms.html",
    "one-stop-service.html",
    "process.html",
    "certificates.html",
    "case-studies.html",
    "contact.html",
    "products/yoga-wear.html",
    "products/new-products.html",
    "products/lookbook.html",
    "products/training-wear.html",
    "products/compression-base-layers.html",
    "products/private-label-gym-clothing.html",
    "products/private-label-sportswear-packaging.html",
    "products/sports-bras.html",
    "products/plus-size-activewear.html",
    "products/cycling-wear.html",
    "products/cycling-jerseys-bib-shorts.html",
    "products/golf-apparel.html",
    "products/golf-polo-shirts-skorts.html",
    "products/racket-sports-apparel.html",
    "products/tennis-pickleball-apparel.html",
    "products/youth-sportswear.html",
    "products/basketball-wear.html",
    "products/basketball-jerseys.html",
    "products/football-kits.html",
    "products/volleyball-teamwear.html",
    "products/volleyball-uniforms.html",
    *{f"products/{slug}.html" for slug in EXPANDED_PRODUCT_SLUGS},
    "resources/index.html",
    "resources/sportswear-manufacturer-due-diligence-checklist.html",
    "resources/private-label-activewear-moq.html",
    "resources/custom-sportswear-cost-lead-time.html",
    "resources/custom-sportswear-tech-pack.html",
    "resources/sportswear-logo-artwork-preparation-guide.html",
    "resources/sportswear-packaging-label-handoff-checklist.html",
    "resources/sportswear-aql-inspection-checklist.html",
    "resources/teamwear-roster-packing-guide.html",
    "blog/index.html",
    "blog/activewear-odor-resistance-antibacterial-test.html",
    "blog/moisture-wicking-quick-dry-activewear-test.html",
    "blog/apparel-print-wash-test-logo-durability.html",
    "blog/apparel-incoterms-exw-fob-ddp-landed-cost.html",
    "blog/sportswear-sublimation-color-matching-guide.html",
    "blog/volleyball-uniform-rules-checklist.html",
    "blog/us-clothing-label-requirements-private-label.html",
    "blog/clothing-sample-to-bulk-quality-control.html",
    "blog/clothing-sample-rounds-before-bulk-production.html",
    "blog/activewear-leggings-quality-testing.html",
    "blog/running-shorts-chafing-ride-up-test.html",
    "blog/verify-ai-generated-tech-pack.html",
    "blog/sports-bra-fit-support-wear-test.html",
    "blog/activewear-inclusive-sizing-fit-test.html",
    "blog/youth-team-uniform-sizing-order-checklist.html",
    "blog/custom-apparel-packaging-moq-inventory-planning.html",
    "editorial-policy.html",
}
REQUIRED_MAIN_LINKS = {
    "blog/clothing-sample-to-bulk-quality-control.html": {
        "process.html",
        "sportswear-manufacturer.html",
    },
    "blog/volleyball-uniform-rules-checklist.html": {
        "custom-teamwear-uniforms.html",
    },
    "blog/youth-team-uniform-sizing-order-checklist.html": {
        "custom-teamwear-uniforms.html",
    },
    "products/yoga-leggings.html": {
        "blog/activewear-leggings-quality-testing.html",
        "products/private-label-gym-leggings.html",
        "resources/activewear-fabric-selection-guide.html",
        "resources/activewear-size-grading-guide.html",
    },
    "products/training-shorts-joggers.html": {
        "products/custom-running-shorts.html",
    },
    "blog/running-shorts-chafing-ride-up-test.html": {
        "products/custom-running-shorts.html",
    },
    "products/tennis-pickleball-apparel.html": {
        "products/badminton-uniforms.html",
        "products/custom-padel-apparel.html",
    },
    "products/mma-rash-guards-fight-shorts.html": {
        "products/custom-boxing-apparel.html",
    },
    "custom-teamwear-uniforms.html": {
        "products/badminton-uniforms.html",
        "products/custom-handball-uniforms.html",
    },
    "products/football-kits.html": {
        "products/custom-futsal-uniforms.html",
    },
    "products/racket-sports-apparel.html": {
        "products/custom-table-tennis-uniforms.html",
    },
    "products/custom-sublimated-teamwear.html": {
        "products/custom-bowling-shirts.html",
        "products/custom-darts-shirts.html",
        "products/custom-ultimate-jerseys.html",
    },
    "products/wrestling-singlets.html": {
        "products/custom-weightlifting-singlets.html",
    },
    "resources/custom-sportswear-cost-lead-time.html": {
        "low-moq-sportswear-manufacturer.html",
        "process.html",
        "sportswear-manufacturer.html",
    },
}
TITLE_LENGTH_RANGE = (30, 65)
DESCRIPTION_LENGTH_RANGE = (100, 170)
IMAGE_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
NON_VISIBLE_RE = re.compile(
    r"<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>",
    re.IGNORECASE,
)
TAG_RE = re.compile(r"<[^>]+>")
MAIN_TEXT_TOKEN_RE = re.compile(r"[a-z0-9]+")
MAIN_TEXT_STOPWORDS = set(
    """
    a about above after again against all am an and any are arent as at be because
    been before being below between both but by can cannot could couldnt did didnt
    do does doesnt doing dont down during each few for from further had hadnt has
    hasnt have havent having he hed hell hes her here heres hers herself him himself
    his how hows i id ill im ive if in into is isnt it its itself lets me more most
    mustnt my myself no nor not of off on once only or other ought our ours ourselves
    out over own same shant she shed shell shes should shouldnt so some such than that
    thats the their theirs them themselves then there theres these they theyd theyll
    theyre theyve this those through to too under until up very was wasnt we wed well
    were weve werent what whats when whens where wheres which while who whos whom why
    whys with wont would wouldnt you youd youll youre youve your yours yourself
    yourselves
    """.split()
)
IGNORED_PATH_PARTS = {
    ".git",
    ".local-backups",
    ".vercel",
    ".wrangler",
    "build",
    "docs",
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
        self.og_title = ""
        self.og_description = ""
        self.og_type = ""
        self.og_url = ""
        self.og_image = ""
        self.og_image_alt = ""
        self.twitter_card = ""
        self.twitter_image = ""
        self.twitter_image_alt = ""
        self.ids = []
        self.links = []
        self.current_link_href = None
        self.current_link_text = []
        self.case_study_link_texts = []
        self.main_depth = 0
        self.main_links = []
        self.primary_main_contact_links = []
        self.assets = []
        self.image_assets = []
        self.images = []
        self.image_preloads = []
        self.json_ld_blocks = []
        self.current_json_ld = None
        self.faq_list_depth = 0
        self.in_faq_summary = False
        self.current_faq_summary = []
        self.visible_faq_questions = []
        self.direct_answers = []
        self.direct_answer_depth = 0
        self.direct_answer_capture = ""
        self.direct_answer_capture_tag = ""
        self.direct_question_parts = []
        self.direct_answer_parts = []
        self.structured_modified_dates = set()
        self.article_meta_depth = 0
        self.visible_article_dates = set()
        self.visible_article_links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if self.direct_answer_depth:
            self.direct_answer_depth += 1
        elif tag == "article" and "data-direct-answer" in attributes:
            self.direct_answer_depth = 1
            self.direct_question_parts = []
            self.direct_answer_parts = []
        if self.direct_answer_depth and "data-direct-answer-question" in attributes:
            self.direct_answer_capture = "question"
            self.direct_answer_capture_tag = tag
        elif self.direct_answer_depth and "data-direct-answer-text" in attributes:
            self.direct_answer_capture = "answer"
            self.direct_answer_capture_tag = tag

        if tag == "main":
            self.main_depth += 1

        if tag == "div":
            class_names = set(attributes.get("class", "").split())
            if self.faq_list_depth:
                self.faq_list_depth += 1
            elif "faq-list" in class_names:
                self.faq_list_depth = 1
            if self.article_meta_depth:
                self.article_meta_depth += 1
            elif "article-meta" in class_names:
                self.article_meta_depth = 1

        if tag == "time" and self.article_meta_depth:
            visible_date = attributes.get("datetime", "")
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", visible_date):
                self.visible_article_dates.add(visible_date)

        if tag == "summary" and self.faq_list_depth:
            self.in_faq_summary = True
            self.current_faq_summary = []

        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            meta_name = attributes.get("name", "").lower()
            meta_property = attributes.get("property", "").lower()
            if meta_name == "description":
                self.description = attributes.get("content", "").strip()
            elif meta_name == "robots":
                self.robots = attributes.get("content", "").strip()
            elif meta_name == "twitter:card":
                self.twitter_card = attributes.get("content", "").strip()
            elif meta_name == "twitter:image":
                self.twitter_image = attributes.get("content", "").strip()
            elif meta_name == "twitter:image:alt":
                self.twitter_image_alt = attributes.get("content", "").strip()
            if meta_property == "og:title":
                self.og_title = attributes.get("content", "").strip()
            elif meta_property == "og:description":
                self.og_description = attributes.get("content", "").strip()
            elif meta_property == "og:type":
                self.og_type = attributes.get("content", "").strip()
            elif meta_property == "og:url":
                self.og_url = attributes.get("content", "").strip()
            elif meta_property == "og:image":
                self.og_image = attributes.get("content", "").strip()
            elif meta_property == "og:image:alt":
                self.og_image_alt = attributes.get("content", "").strip()
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
            href = attributes["href"]
            self.links.append(href)
            self.current_link_href = href
            self.current_link_text = []
            if self.main_depth:
                self.main_links.append(href)
                class_names = set(attributes.get("class", "").split())
                if {"button", "primary"}.issubset(class_names):
                    self.primary_main_contact_links.append(href)
            if self.article_meta_depth:
                self.visible_article_links.append(href)
        elif tag in {"img", "source"}:
            if tag == "img" and attributes.get("src"):
                self.assets.append(attributes["src"])
                self.image_assets.append(attributes["src"])
                self.images.append(attributes)
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
        if self.direct_answer_capture_tag == tag:
            self.direct_answer_capture = ""
            self.direct_answer_capture_tag = ""
        if self.direct_answer_depth:
            if self.direct_answer_depth == 1 and tag == "article":
                question = normalized_text("".join(self.direct_question_parts))
                answer = normalized_text("".join(self.direct_answer_parts))
                if question or answer:
                    self.direct_answers.append((question, answer))
                self.direct_answer_depth = 0
            else:
                self.direct_answer_depth -= 1

        if tag == "title":
            self.in_title = False
        elif tag == "summary" and self.in_faq_summary:
            question = normalized_text("".join(self.current_faq_summary))
            if question:
                self.visible_faq_questions.append(question)
            self.in_faq_summary = False
            self.current_faq_summary = []
        elif tag == "script" and self.current_json_ld is not None:
            self.json_ld_blocks.append("".join(self.current_json_ld).strip())
            self.current_json_ld = None
        elif tag == "a" and self.current_link_href is not None:
            link_path = urlparse(self.current_link_href).path
            if link_path == "case-studies.html" or link_path.endswith(
                "/case-studies.html"
            ):
                self.case_study_link_texts.append(
                    normalized_text(" ".join(self.current_link_text))
                )
            self.current_link_href = None
            self.current_link_text = []

        if tag == "div" and self.faq_list_depth:
            self.faq_list_depth -= 1
        if tag == "div" and self.article_meta_depth:
            self.article_meta_depth -= 1
        if tag == "main" and self.main_depth:
            self.main_depth -= 1

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.in_faq_summary:
            self.current_faq_summary.append(data)
        if self.current_link_href is not None:
            self.current_link_text.append(data)
        if self.current_json_ld is not None:
            self.current_json_ld.append(data)
        if self.direct_answer_capture == "question":
            self.direct_question_parts.append(data)
        elif self.direct_answer_capture == "answer":
            self.direct_answer_parts.append(data)

    @property
    def title(self):
        return "".join(self.title_parts).strip()


class MainTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main_depth = 0
        self.skip_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.main_depth += 1
        if self.main_depth and tag in {"script", "style", "svg", "noscript"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if (
            self.main_depth
            and tag in {"script", "style", "svg", "noscript"}
            and self.skip_depth
        ):
            self.skip_depth -= 1
        if tag == "main" and self.main_depth:
            self.main_depth -= 1

    def handle_data(self, data):
        if self.main_depth and not self.skip_depth:
            self.parts.append(data)


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


def extract_marked_block(source, start, end):
    match = re.search(re.escape(start) + r"([\s\S]*?)" + re.escape(end), source)
    return match.group(1) if match else ""


def product_select_options(source):
    select_match = re.search(
        r'<select\s+name="product"[^>]*>([\s\S]*?)</select>', source
    )
    if not select_match:
        return []
    options = []
    for match in re.finditer(
        r"<option(?P<attributes>[^>]*)>(?P<text>[\s\S]*?)</option>",
        select_match.group(1),
    ):
        value_match = re.search(r'value="([^"]*)"', match.group("attributes"))
        text = normalized_text(TAG_RE.sub(" ", match.group("text")))
        options.append(unescape(value_match.group(1)) if value_match else text)
    return options


def main_text_vector(path):
    parser = MainTextParser()
    parser.feed(path.read_text(encoding="utf-8"))
    tokens = MAIN_TEXT_TOKEN_RE.findall(" ".join(parser.parts).lower())
    return Counter(
        token
        for token in tokens
        if len(token) > 1 and token not in MAIN_TEXT_STOPWORDS
    )


def cosine_similarity(left, right):
    denominator = sqrt(
        sum(value * value for value in left.values())
        * sum(value * value for value in right.values())
    )
    if not denominator:
        return 0.0
    numerator = sum(left[token] * right[token] for token in left.keys() & right.keys())
    return numerator / denominator


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
    duplicate_catalog_slugs = duplicate_values(CATALOG_SLUG_LIST)
    if duplicate_catalog_slugs:
        errors.append(
            "product catalog contains duplicate slugs: "
            + ", ".join(duplicate_catalog_slugs)
        )
    pages = {}
    page_internal_links = {}
    main_internal_links = {}
    canonical_owners = {}
    title_owners = {}
    description_owners = {}
    internal_targets = set()
    local_assets = set()
    json_ld_count = 0
    image_count = 0
    avif_image_count = 0
    visible_faq_pages = 0
    faq_schema_pages = 0
    article_schema_pages = 0
    preferred_image_pages = 0
    primary_ctas_bypassing_form_anchor = 0
    factory_media_register_fields = 0
    undisclosed_factory_media_visuals = 0
    unqualified_factory_video_availability_answers = 0
    case_studies_target_links = 0
    misleading_case_claim_anchors = 0
    undisclosed_case_planning_visuals = 0
    ambiguous_case_scenario_phrases = 0
    homepage_manufacturer_main_text_cosine_similarity = 0.0
    expanded_product_max_cosine_similarity = 0.0
    expanded_product_most_similar_pair = []
    expanded_product_contextual_inlinks = {}

    llms_source = (ROOT / "llms.txt").read_text(encoding="utf-8")
    concrete_product_files = sorted(
        path
        for path in (ROOT / "products").glob("*.html")
        if path.stem not in NON_CONCRETE_PRODUCT_SLUGS
    )
    concrete_product_urls = {
        f"{PRODUCTION_ORIGIN}/products/{path.name}"
        for path in concrete_product_files
    }
    disk_generated_slugs = set()
    for path in concrete_product_files:
        source = path.read_text(encoding="utf-8")
        marker = GENERATED_PRODUCT_MARKER_RE.search(source)
        if not marker:
            continue
        marker_slug = marker.group(1)
        disk_generated_slugs.add(marker_slug)
        if marker_slug != path.stem:
            errors.append(
                f"products/{path.name}: generated marker slug {marker_slug} "
                "does not match the filename"
            )
    for slug in sorted(EXPANDED_PRODUCT_SLUGS - disk_generated_slugs):
        errors.append(f"products/{slug}.html: missing generated-page identity marker")
    for slug in sorted(disk_generated_slugs - EXPANDED_PRODUCT_SLUGS):
        errors.append(f"products/{slug}.html: stale generated page is absent from catalog")

    llms_complete_index = extract_marked_block(
        llms_source,
        "<!-- PRODUCT_EXPANSION_START -->",
        "<!-- PRODUCT_EXPANSION_END -->",
    )
    if not llms_complete_index:
        errors.append("llms.txt: missing complete product index marker block")
    llms_product_url_list = re.findall(
        rf"{re.escape(PRODUCTION_ORIGIN)}/products/[a-z0-9-]+\.html",
        llms_complete_index,
    )
    llms_product_url_counts = Counter(llms_product_url_list)
    llms_product_urls = set(llms_product_url_counts)
    for url, count in sorted(llms_product_url_counts.items()):
        if count != 1:
            errors.append(
                f"llms.txt: complete product index contains {url} {count} times"
            )
    for extra_url in sorted(llms_product_urls - concrete_product_urls):
        errors.append(f"llms.txt: complete product index has extra product URL: {extra_url}")
    for missing_url in sorted(concrete_product_urls - llms_product_urls):
        errors.append(f"llms.txt: missing concrete product URL: {missing_url}")
    all_llms_product_urls = set(
        re.findall(
            rf"{re.escape(PRODUCTION_ORIGIN)}/products/[a-z0-9-]+\.html",
            llms_source,
        )
    )
    if len(concrete_product_files) != EXPECTED_CONCRETE_PRODUCT_COUNT:
        errors.append(
            "products: expected "
            f"{EXPECTED_CONCRETE_PRODUCT_COUNT} concrete pages, found "
            f"{len(concrete_product_files)}"
        )
    if not concrete_product_urls.issubset(all_llms_product_urls):
        errors.append("llms.txt: product URLs escaped the complete product index")
    if "Last updated: 2026-08-28" not in llms_source:
        errors.append("llms.txt: missing current update date")
    for required_url in (
        f"{PRODUCTION_ORIGIN}/low-moq-sportswear-manufacturer.html",
        f"{PRODUCTION_ORIGIN}/faq.html",
    ):
        if required_url not in llms_source:
            errors.append(f"llms.txt: missing GEO discovery URL: {required_url}")
    if re.search(
        r"\[[^\]]*case studies[^\]]*\]\(https://glorystarwears\.com/case-studies\.html\)",
        llms_source,
        re.IGNORECASE,
    ):
        ambiguous_case_scenario_phrases += 1
        errors.append(
            "llms.txt: case-studies URL is mislabeled as completed case studies"
        )

    script_source = (ROOT / "script.js").read_text(encoding="utf-8")
    for slug in sorted(EXPANDED_PRODUCT_SLUGS):
        if f'"{slug}"' not in script_source:
            errors.append(f"script.js: missing expanded product catalog entry: {slug}")
    required_attribution_markers = {
        '"ai_assistant"': "AI-assistant traffic classification",
        "traffic_channel": "traffic channel event field",
        "traffic_source": "traffic source event field",
        "referrer_host": "referrer host event field",
        'googleAnalyticsMeasurementId = "G-3QHK9TGCHQ"': "GA4 measurement ID",
        'analytics_storage: "denied"': "default denied analytics storage",
        'ad_user_data: "denied"': "denied advertising user data",
        'ad_personalization: "denied"': "denied advertising personalization",
        "loadGoogleAnalytics": "consent-controlled Google tag loader",
        'window.gtag("event", "generate_lead"': "recommended GA4 lead event",
        "page_type": "GA4 page-type context",
        "content_group": "GA4 content-group context",
        'data-manage-analytics-consent': "analytics preference control",
        "window.siteDataLayer.push(eventDetails)": "separate vendor-neutral event layer",
        'const banner = document.createElement("div")': "valid non-modal consent dialog element",
        "quoteSubmissionIds": "idempotent quote submission identifier",
        '"Tech pack review and development"': "tech-pack inquiry prefill route",
        '"Quality and inspection planning"': "quality inquiry prefill route",
        "setupTurnstile": "Turnstile form protection",
        "turnstileToken": "Turnstile response delivery",
        'new URL("/contact.html#quote-form"': "direct quote-form route",
        "buyerPathStorageKey": "buyer-path session handoff",
        'trackEvent("buyer_quote_prefill"': "buyer-path quote prefill analytics",
        'trackEvent("quote_progress"': "quote completion milestone analytics",
        'trackEvent("quote_validation_error"': "quote validation analytics",
        "initializeSecureSubmission": "near-viewport secure form initialization",
        'skipLink.textContent = "Skip to main content"': "site-wide skip link",
        "setupProductDetailExplorer": "product detail explorer",
        "productDirectionStorageKey": "product-direction inquiry handoff",
        'trackEvent("product_detail_view"': "product-detail view analytics",
        'trackEvent("product_detail_image_select"': "product-detail image analytics",
        'trackEvent("product_direction_quote_select"': "product-direction quote analytics",
        'image.dataset.evidenceStatus = "illustrative"': "illustrative product-media status",
        "Real style-specific image not yet provided": "honest five-view evidence placeholders",
        'bar.setAttribute("aria-label", "Quick product actions")': "accessible mobile product actions",
        "fabricShortlistStorageKey": "fabric-shortlist session handoff",
        'trackEvent("fabric_shortlist_quote"': "fabric-shortlist quote analytics",
        'trackEvent("quote_reference_link_added"': "reference-link analytics",
        'mobileQuoteBar.classList.toggle("is-suppressed"': "mobile quote-bar form suppression",
        'mobileQuoteBar.toggleAttribute("inert"': "mobile quote-bar focus suppression",
        '"Custom fishing apparel"': "fishing product inquiry mapping",
        '"Custom rowing uniforms"': "rowing product inquiry mapping",
        '"Pilates activewear"': "Pilates product inquiry mapping",
        '"Flag football uniforms"': "flag-football product inquiry mapping",
        '"Baseball uniforms"': "baseball product inquiry mapping",
        '"Softball uniforms"': "softball product inquiry mapping",
        '"Rugby uniforms"': "rugby product inquiry mapping",
        '"Field hockey uniforms"': "field-hockey product inquiry mapping",
        '"Custom running shorts"': "running-shorts product inquiry mapping",
        '"Badminton uniforms"': "badminton product inquiry mapping",
        '"Private label gym leggings"': "gym-leggings product inquiry mapping",
        '"Custom boxing apparel"': "boxing product inquiry mapping",
        '"Custom handball uniforms"': "handball product inquiry mapping",
        '"Custom padel apparel"': "padel product inquiry mapping",
        '"Custom futsal uniforms"': "futsal product inquiry mapping",
        '"Custom table tennis uniforms"': "table-tennis product inquiry mapping",
        '"Custom bowling shirts"': "bowling product inquiry mapping",
        '"Custom darts shirts"': "darts product inquiry mapping",
        '"Custom ultimate jerseys"': "ultimate product inquiry mapping",
        '"Custom weightlifting singlets"': "weightlifting product inquiry mapping",
        '"Custom team polo shirts"': "team-polo product inquiry mapping",
        '"Custom cycling skinsuits"': "cycling-skinsuit product inquiry mapping",
        '"Custom triathlon suits"': "triathlon-suit product inquiry mapping",
        '"Custom beach volleyball uniforms"': "beach-volleyball product inquiry mapping",
        '"Custom motocross jerseys"': "motocross product inquiry mapping",
        '"Custom referee uniforms"': "referee product inquiry mapping",
        '"Yoga leggings"': "yoga-leggings product inquiry mapping",
        '"Seamless activewear"': "seamless-activewear product inquiry mapping",
        '"Soccer uniforms"': "soccer-uniform product inquiry mapping",
        "data-product-buyer-route": "product-detail buyer routing",
        'trackEvent("product_buyer_route_select"': "product buyer-route analytics",
        "sportswear-collection-development-brief.csv": "product-level planning resource",
        "data-fabric-shortlist-remove": "shortlist item removal control",
        "is-section-current": "site-wide current-section navigation state",
        'trackEvent("navigation_select"': "desktop and mobile navigation analytics",
        "setDesktopNavDropdown": "accessible desktop navigation dropdown state",
    }
    for marker, label in required_attribution_markers.items():
        if marker not in script_source:
            errors.append(f"script.js: missing {label}")

    lead_api_source = (ROOT / "api" / "lead.js").read_text(encoding="utf-8")
    required_lead_api_markers = {
        "TURNSTILE_SECRET_KEY": "Turnstile server secret",
        "TURNSTILE_SITE_KEY": "Turnstile public site key status",
        "human_verification_required": "missing-verification rejection",
        "https://challenges.cloudflare.com/turnstile/v0/siteverify": "Turnstile Siteverify request",
        "LEAD_WEBHOOK_SECRET": "authenticated downstream delivery",
        "for (let attempt = 0; attempt < 2": "idempotent transient delivery retry",
        "body.submissionId": "client submission idempotency key",
        "cleanText(body.message, 12000)": "non-truncating structured inquiry allowance",
    }
    for marker, label in required_lead_api_markers.items():
        if marker not in lead_api_source:
            errors.append(f"api/lead.js: missing {label}")

    lead_worker_source = (ROOT / "workers" / "lead-receiver" / "src" / "index.ts").read_text(encoding="utf-8")
    required_lead_worker_markers = {
        "crypto.subtle.timingSafeEqual": "constant-time webhook secret comparison",
        "INSERT OR IGNORE INTO leads": "idempotent D1 insert",
        "lead_rate_limits": "persistent lead rate limit",
        "retention_until <= datetime('now')": "scheduled retention deletion",
        "satisfies ExportedHandler<Env>": "generated Worker binding type check",
    }
    for marker, label in required_lead_worker_markers.items():
        if marker not in lead_worker_source:
            errors.append(f"workers/lead-receiver/src/index.ts: missing {label}")

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
    expected_directory_redirects = {
        "/products": "/products/",
        "/resources": "/resources/",
        "/blog": "/blog/",
    }
    configured_redirects = {
        redirect.get("source"): redirect.get("destination")
        for redirect in vercel_config.get("redirects", [])
        if redirect.get("permanent") is True
    }
    for source_path, destination_path in expected_directory_redirects.items():
        if configured_redirects.get(source_path) != destination_path:
            errors.append(
                f"vercel.json: missing canonical directory redirect "
                f"{source_path} -> {destination_path}"
            )

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
    quote_product_options = {
        filename: product_select_options((ROOT / filename).read_text(encoding="utf-8"))
        for filename in ("index.html", "contact.html")
    }
    if Counter(quote_product_options["index.html"]) != Counter(
        quote_product_options["contact.html"]
    ):
        errors.append("homepage and contact product option sets differ")
    def inquiry_label_key(value):
        return re.sub(r"^custom\s+", "", normalized_text(value).lower())

    expanded_inquiry_labels = {
        inquiry_label_key(item["short_name"]): item["short_name"]
        for item in CATALOG_ITEMS
    }
    for filename, options in quote_product_options.items():
        if len(options) != EXPECTED_QUOTE_PRODUCT_OPTION_COUNT:
            errors.append(
                f"{filename}: expected {EXPECTED_QUOTE_PRODUCT_OPTION_COUNT} product options, "
                f"found {len(options)}"
            )
        duplicates = duplicate_values(options)
        if duplicates:
            errors.append(
                f"{filename}: duplicate product options: {', '.join(duplicates)}"
            )
        option_keys = {inquiry_label_key(option) for option in options}
        missing_labels = sorted(
            label
            for key, label in expanded_inquiry_labels.items()
            if key not in option_keys
        )
        if missing_labels:
            errors.append(
                f"{filename}: missing catalog inquiry options: {', '.join(missing_labels)}"
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

        if site_header_markup() not in source:
            errors.append(f"{relative_name}: site header differs from shared chrome")
        if site_footer_markup() not in source:
            errors.append(f"{relative_name}: site footer differs from shared chrome")
        if source.count("data-site-chrome") != 3:
            errors.append(
                f"{relative_name}: expected shared desktop, mobile, and footer chrome markers"
            )

        is_concrete_product_page = (
            html_file.parent == ROOT / "products"
            and html_file.stem not in NON_CONCRETE_PRODUCT_SLUGS
        )
        if is_concrete_product_page:
            if "product-detail-disclosure" not in source:
                errors.append(
                    f"{relative_name}: missing static product image and capability disclosure"
                )
            for picture_tag in re.findall(r"<picture\b[^>]*>", source):
                if 'data-evidence-status="illustrative"' not in picture_tag:
                    errors.append(
                        f"{relative_name}: picture is missing static illustrative status"
                    )
            for image in parser.images:
                if image.get("data-evidence-status") != "illustrative":
                    errors.append(
                        f"{relative_name}: image is missing static illustrative status"
                    )
                if image.get("data-media-kind") != "product-planning-reference":
                    errors.append(
                        f"{relative_name}: image is missing product-planning media kind"
                    )
                if not image.get("alt", "").lower().startswith(
                    "illustrative product-planning reference"
                ):
                    errors.append(
                        f"{relative_name}: image alt does not disclose illustrative scope"
                    )
            if not parser.og_image_alt.lower().startswith("illustrative"):
                errors.append(
                    f"{relative_name}: Open Graph image alt does not disclose illustrative scope"
                )
            if not parser.twitter_image_alt.lower().startswith("illustrative"):
                errors.append(
                    f"{relative_name}: X image alt does not disclose illustrative scope"
                )

        if re.search(r'"@type"\s*:\s*"Product"', source):
            errors.append(
                f"{relative_name}: unsupported Product structured data; "
                "use CollectionPage/ItemList until a verifiable SKU exists"
            )

        if relative_name == "index.html":
            homepage_category_markers = {
                '"@type": "ItemList"': "product category ItemList",
                '"@id": "https://glorystarwears.com/#product-category-list"': "category-list entity ID",
                '"numberOfItems": 8': "category-list item count",
            }
            for marker, label in homepage_category_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name in {"index.html", "contact.html"}:
            quote_form_markers = {
                'name="referenceLink"': "buyer-authorized reference-link field",
                'name="message" rows="5" maxlength="3000"': "bounded project-details field",
                "quote-order-grid": "visible quantity, market, and timing fields",
                "quote-next-step": "post-inquiry expectation setting",
                "Custom fishing apparel": "fishing inquiry option",
                "Custom rowing uniforms": "rowing inquiry option",
                "Pilates activewear": "Pilates inquiry option",
                "Flag football uniforms": "flag-football inquiry option",
                "Baseball uniforms": "baseball inquiry option",
                "Softball uniforms": "softball inquiry option",
                "Rugby uniforms": "rugby inquiry option",
                "Field hockey uniforms": "field-hockey inquiry option",
                "Custom running shorts": "running-shorts inquiry option",
                "Badminton uniforms": "badminton inquiry option",
                "Private label gym leggings": "gym-leggings inquiry option",
                "Custom boxing apparel": "boxing inquiry option",
                "Custom handball uniforms": "handball inquiry option",
                "Custom padel apparel": "padel inquiry option",
                "Custom futsal uniforms": "futsal inquiry option",
                "Custom table tennis uniforms": "table-tennis inquiry option",
                "Custom bowling shirts": "bowling inquiry option",
                "Custom darts shirts": "darts inquiry option",
                "Custom ultimate jerseys": "ultimate inquiry option",
                "Custom weightlifting singlets": "weightlifting inquiry option",
                "Custom team polo shirts": "team-polo inquiry option",
                "Custom cycling skinsuits": "cycling-skinsuit inquiry option",
                "Custom triathlon suits": "triathlon-suit inquiry option",
                "Custom beach volleyball uniforms": "beach-volleyball inquiry option",
                "Custom motocross jerseys": "motocross inquiry option",
                "Custom referee uniforms": "referee inquiry option",
                "Yoga leggings": "yoga-leggings inquiry option",
                "Seamless activewear": "seamless-activewear inquiry option",
                "Soccer uniforms": "soccer-uniform inquiry option",
            }
            for marker, label in quote_form_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "fabrics.html":
            fabric_library_markers = {
                "Compare 16 material directions": "expanded fabric library heading",
                "data-fabric-search": "fabric search input",
                "data-fabric-structure": "construction filter",
                "data-fabric-decoration": "decoration filter",
                "data-fabric-shortlist-panel": "fabric shortlist builder",
                "data-fabric-shortlist-copy": "fabric shortlist copy action",
                'href="./contact.html?product=fabric#quote-form"': "fabric quote prefill route",
                "Sportswear color library workflow": "color-control workflow",
                "Does this page show currently stocked fabrics or colors?": "fabric-stock boundary answer",
                '"@type": "FAQPage"': "fabric and color FAQ schema",
            }
            for marker, label in fabric_library_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")
            fabric_direction_count = len(
                re.findall(r'<article\s+data-fabric-id="FB-\d{2}"', source)
            )
            if fabric_direction_count != 16:
                errors.append(
                    f"{relative_name}: expected 16 fabric planning directions, "
                    f"found {fabric_direction_count}"
                )

        if relative_name.startswith("products/") and html_file.stem in EXPANDED_PRODUCT_SLUGS:
            expanded_page_markers = {
                "Image and page scope:": "visible illustrative-media scope",
                "Specification framework": "static specification framework",
                "Sport-specific decision map": "sport-specific decision section",
                "Direct buyer answers": "static direct-answer section",
                "Feasibility is confirmed only after the submitted project brief is reviewed.": "project feasibility boundary",
                "No universal figure on this page is a quotation or production commitment.": "commercial boundary",
                '"@type": "CollectionPage"': "CollectionPage schema",
                '"@type": "ItemList"': "ItemList schema",
                '"@type": "FAQPage"': "FAQPage schema",
            }
            for marker, label in expanded_page_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")
            if html_file.stem in RULE_SOURCE_PRODUCT_SLUGS:
                rule_source_markers = {
                    "Official rules and buyer verification": "visible official-source section",
                    "These sources help identify questions for the brief": "source-scope boundary",
                    '"citation"': "citation property in CollectionPage schema",
                    '"mentions"': "referenced-entity property in CollectionPage schema",
                }
                for marker, label in rule_source_markers.items():
                    if marker not in source:
                        errors.append(f"{relative_name}: missing {label}")
            if len(parser.main_links) < 7:
                errors.append(
                    f"{relative_name}: expanded page has too few contextual main links"
                )
            for image in parser.images:
                if image.get("data-evidence-status", "").lower() != "illustrative":
                    errors.append(
                        f"{relative_name}: expanded-page image is not marked illustrative"
                    )

        if relative_name in {
            "products/baseball-softball-teamwear.html",
            "products/rugby-hockey-teamwear.html",
        }:
            hub_markers = {
                "Image and capability scope:": "visible hub evidence boundary",
                '"@type":"ImageObject"': "illustrative hub ImageObject schema",
                "not current stock, a customer order, or production evidence": "schema image-evidence boundary",
                "manufactured or coordinated": "manufacturing-route boundary",
            }
            for marker, label in hub_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")
            if "illustrative" not in parser.og_image_alt.lower():
                errors.append(
                    f"{relative_name}: Open Graph image alt lacks illustrative status"
                )
            if "illustrative" not in parser.twitter_image_alt.lower():
                errors.append(
                    f"{relative_name}: social image alt lacks illustrative status"
                )
            for image in parser.images:
                if image.get("data-evidence-status", "").lower() != "illustrative":
                    errors.append(
                        f"{relative_name}: hub image is not marked illustrative"
                    )
                if "illustrative" not in image.get("alt", "").lower():
                    errors.append(
                        f"{relative_name}: hub image alt lacks illustrative status"
                    )

        if relative_name == "products/baseball-softball-teamwear.html":
            for forbidden in (
                "Yes. We can produce",
                "What to customize for baseball uniforms",
            ):
                if forbidden in source:
                    errors.append(
                        f"{relative_name}: parent hub retains child-product claim: {forbidden}"
                    )

        if relative_name == "products/rugby-hockey-teamwear.html":
            for forbidden in (
                "lacrosse",
                "Rugby Hockey",
                "rugby or hockey",
                "OEM and ODM support",
            ):
                if forbidden.lower() in source.lower():
                    errors.append(
                        f"{relative_name}: parent hub retains conflicting intent: {forbidden}"
                    )

        if relative_name == "products/american-football-uniforms.html":
            child_start = "<!-- PRODUCT_CLUSTER_AMERICAN_FOOTBALL_UNIFORMS_START -->"
            child_end = "<!-- PRODUCT_CLUSTER_AMERICAN_FOOTBALL_UNIFORMS_END -->"
            child_pattern = re.compile(
                re.escape(child_start) + r"[\s\S]*?" + re.escape(child_end),
                re.IGNORECASE,
            )
            child_match = child_pattern.search(source)
            if not child_match:
                errors.append(
                    f"{relative_name}: missing dedicated flag-football child route"
                )
            source_without_child_route = child_pattern.sub("", source, count=1)
            source_without_child_route = NON_VISIBLE_RE.sub(
                " ", source_without_child_route
            )
            if re.search(
                r"\b(?:flag football|7v7|7-on-7)\b",
                source_without_child_route,
                re.IGNORECASE,
            ):
                errors.append(
                    f"{relative_name}: flag/7v7 intent appears outside the child route"
                )
            if "padded-gridiron" not in source.lower():
                errors.append(
                    f"{relative_name}: missing padded-gridiron intent boundary"
                )

        for anchor_text in parser.case_study_link_texts:
            case_studies_target_links += 1
            label = normalized_text(anchor_text).lower()
            forbidden_label = any(
                phrase in label
                for phrase in (
                    "case studies",
                    "customer case",
                    "client case",
                    "completed case",
                    "delivered result",
                    "project evidence",
                    "comparable case",
                )
            )
            compatible_label = not forbidden_label and (
                label in {"planning", "planning examples"}
                or "planning example" in label
                or "hypothetical" in label
                or "project brief" in label
                or "evidence format" in label
                or "evidence boundar" in label
            )
            if not compatible_label:
                misleading_case_claim_anchors += 1
                errors.append(
                    f"{relative_name}: misleading case-studies anchor: "
                    f"{anchor_text or '[empty]'}"
                )

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

        is_noindex = "noindex" in parser.robots.lower()
        if not is_noindex:
            preferred_image_fields = {
                "Open Graph title": parser.og_title,
                "Open Graph description": parser.og_description,
                "Open Graph type": parser.og_type,
                "Open Graph URL": parser.og_url,
                "Open Graph image": parser.og_image,
                "social card type": parser.twitter_card,
                "social card image": parser.twitter_image,
            }
            for label, value in preferred_image_fields.items():
                if not value:
                    errors.append(f"{relative_name}: missing {label}")

            if parser.og_url and parser.canonical and parser.og_url != parser.canonical:
                errors.append(
                    f"{relative_name}: Open Graph URL does not match canonical: "
                    f"{parser.og_url} != {parser.canonical}"
                )
            if (
                parser.og_image
                and parser.twitter_image
                and parser.og_image != parser.twitter_image
            ):
                errors.append(
                    f"{relative_name}: preferred image metadata does not match: "
                    f"{parser.og_image} != {parser.twitter_image}"
                )
            if parser.og_image:
                preferred_image_pages += 1
                preferred_image_file = site_file_for_url(parser.og_image)
                if preferred_image_file is None or not preferred_image_file.exists():
                    errors.append(
                        f"{relative_name}: preferred image has no local file: "
                        f"{parser.og_image}"
                    )

        if relative_name == "process.html":
            required_process_markers = {
                "sportswear-sampling-production-approval-register.csv": "sampling approval register link",
                'data-resource-download="sampling-production-approval-register"': "sampling approval download tracking",
                '"@type": "DigitalDocument"': "sampling approval document schema",
                '"dateModified": "2026-08-28"': "current process modification date",
                "Coordinate the wider product-to-shipment workflow": "one-stop workflow handoff",
            }
            for marker, label in required_process_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "private-label-activewear-manufacturer.html":
            required_activewear_markers = {
                "private-label-activewear-collection-planner.csv": "activewear collection planner link",
                'data-resource-download="private-label-activewear-collection-planner"': "activewear planner download tracking",
                '"@type": "DigitalDocument"': "activewear planner document schema",
                '"dateModified": "2026-08-27"': "current activewear page modification date",
                "us-clothing-label-requirements-private-label.html": "U.S. clothing-label article link",
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
                '"dateModified":"2026-08-25"': "current tech pack modification date",
                "us-clothing-label-requirements-private-label.html": "U.S. clothing-label article link",
                "What it is not:": "visible template scope disclosure",
                "Send Tech Pack for Review": "tech-pack conversion bridge",
            }
            for marker, label in required_tech_pack_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/index.html":
            required_blog_markers = {
                "activewear-odor-resistance-antibacterial-test.html": "odor-control claim-test article link",
                "moisture-wicking-quick-dry-activewear-test.html": "moisture-management article link",
                "clothing-sample-rounds-before-bulk-production.html": "sample-round article link",
                "activewear-leggings-quality-testing.html": "leggings-test article link",
                "running-shorts-chafing-ride-up-test.html": "running-shorts article link",
                "verify-ai-generated-tech-pack.html": "AI tech-pack article link",
                "sports-bra-fit-support-wear-test.html": "sports-bra article link",
                "activewear-inclusive-sizing-fit-test.html": "inclusive-fit article link",
                "youth-team-uniform-sizing-order-checklist.html": "youth-uniform article link",
                "custom-apparel-packaging-moq-inventory-planning.html": "packaging-MOQ article link",
                "clothing-sample-to-bulk-quality-control.html": "sample-to-bulk article link",
                "volleyball-uniform-rules-checklist.html": "volleyball-rules article link",
                "us-clothing-label-requirements-private-label.html": "U.S. clothing-label article link",
                "sportswear-sublimation-color-matching-guide.html": "sublimation-color article link",
                "apparel-print-wash-test-logo-durability.html": "decoration wash-test article link",
                "feed.xml": "RSS feed discovery link",
                "editorial-policy.html": "editorial policy link",
                '"@type":"Blog"': "blog structured data",
                '"dateModified":"2026-08-13"': "current blog modification date",
            }
            for marker, label in required_blog_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/activewear-odor-resistance-antibacterial-test.html":
            required_odor_markers = {
                "activewear-odor-control-claim-test-register.csv": "odor-control claim register link",
                'data-resource-download="activewear-odor-control-claim-test-register"': "odor register download tracking",
                '"@type":"BlogPosting"': "odor article BlogPosting schema",
                '"@type":"DigitalDocument"': "odor register document schema",
                '"isAccessibleForFree":true': "free odor register disclosure",
                '"dateModified":"2026-08-13"': "current odor article modification date",
                "An antibacterial result does not automatically prove": "visible claim-mechanism limitation",
                "Reddit identifies odor-return language; standards and regulators define evidence limits": "source-method disclosure",
                "members.aatcc.org/store/tm211": "AATCC bacterial-odor source",
                "members.aatcc.org/store/tm216": "AATCC odor-adsorbency source",
                "epa.gov/pesticide-registration/prn-2000-1": "EPA treated-article source",
                "epa.gov/safepestcontrol/consumer-products-treated-pesticides": "EPA consumer treated-product source",
                "ftc.gov/business-guidance/resources/advertising-faqs": "FTC claim-substantiation source",
            }
            for marker, label in required_odor_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/moisture-wicking-quick-dry-activewear-test.html":
            required_moisture_markers = {
                "activewear-moisture-management-test-register.csv": "moisture-management register link",
                'data-resource-download="activewear-moisture-management-test-register"': "moisture register download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "moisture register document schema",
                '"isAccessibleForFree":true': "free moisture register disclosure",
                '"dateModified":"2026-08-13"': "current moisture article modification date",
                "No single moisture test proves": "visible universal performance limitation",
                "Reddit identifies the wearer problem; textile methods define measurable properties": "source-method disclosure",
                "aatcc.org/testing/standards": "AATCC method directory source",
                "members.aatcc.org/store/tm195": "AATCC liquid moisture source",
                "aatcc-2022-mid-year-standards-supplement": "AATCC vertical wicking source",
                "members.aatcc.org/store/tm199": "AATCC drying time source",
                "members.aatcc.org/store/tm200": "AATCC drying rate source",
                "store.astm.org/d1776_d1776m-20r24.html": "ASTM conditioning source",
                "ftc.gov/business-guidance/resources/advertising-faqs": "FTC claim substantiation source",
            }
            for marker, label in required_moisture_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/sportswear-sublimation-color-matching-guide.html":
            required_sublimation_color_markers = {
                "sublimation-color-approval-register.csv": "sublimation color register link",
                'data-resource-download="sublimation-color-approval-register"': "sublimation color download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "sublimation color document schema",
                '"isAccessibleForFree":true': "free sublimation register disclosure",
                "A HEX, RGB, CMYK, named color code": "visible exact-match limitation",
                "Reddit identifies the recurring problem; color standards shape the control method": "source-method disclosure",
                "color.org/profile.xalter": "ICC profile source",
                "color.org/creatingprofiles.xalter": "ICC profiling source",
                "helpx.adobe.com/photoshop/using/proofing-colors.html": "Adobe soft-proof source",
                "iso.org/standard/51385.html": "ISO color-difference source",
                "There is no responsible universal value": "visible tolerance limitation",
            }
            for marker, label in required_sublimation_color_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/apparel-print-wash-test-logo-durability.html":
            required_print_wash_markers = {
                "apparel-print-wash-test-register.csv": "print wash-test register link",
                'data-resource-download="apparel-print-wash-test-register"': "print wash-test download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "print wash-test document schema",
                '"isAccessibleForFree":true': "free print wash-test register disclosure",
                '"dateModified":"2026-08-13"': "current print wash-test modification date",
                "There is no responsible universal promise": "visible universal wash-count limitation",
                "Reddit identifies the durability question; standards define repeatable evidence": "source-method disclosure",
                "iso.org/standard/75934.html": "ISO domestic washing and drying source",
                "iso.org/standard/67602.html": "ISO apparel appearance source",
                "store.astm.org/d3938-18r23.html": "ASTM care instruction source",
                "aatcc.org/testing/standards": "AATCC method directory source",
                "ftc.gov/business-guidance/resources/clothes-captioning": "FTC care-label evidence source",
            }
            for marker, label in required_print_wash_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/us-clothing-label-requirements-private-label.html":
            required_us_label_markers = {
                "us-clothing-label-handoff-checklist.csv": "U.S. clothing-label checklist link",
                'data-resource-download="us-clothing-label-handoff-checklist"': "U.S. label checklist download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "U.S. label checklist document schema",
                '"isAccessibleForFree":true': "free U.S. label checklist disclosure",
                "Reddit identifies the uncertainty; FTC guidance controls the factual answer": "source-method disclosure",
                "ftc.gov/business-guidance/resources/threading-your-way-through": "FTC textile-label source",
                "ftc.gov/business-guidance/resources/clothes-captioning": "FTC care-label source",
                "ftc.gov/business-guidance/industry/registered-identification-number-database": "FTC RN source",
                "not legal advice, compliance certification": "visible legal and certification limitation",
            }
            for marker, label in required_us_label_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/clothing-sample-rounds-before-bulk-production.html":
            required_sample_round_markers = {
                "sportswear-sampling-production-approval-register.csv": "sample approval register link",
                'data-resource-download="sampling-production-approval-register"': "sample register download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"dateModified":"2026-08-09"': "current article modification date",
                "There is no responsible fixed number": "visible direct-answer limitation",
            }
            for marker, label in required_sample_round_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/activewear-leggings-quality-testing.html":
            required_leggings_test_markers = {
                "activewear-leggings-quality-test-checklist.csv": "leggings test checklist link",
                'data-resource-download="activewear-leggings-quality-test-checklist"': "leggings checklist download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"dateModified":"2026-08-09"': "current article modification date",
                "one black base-size sample cannot prove": "visible test-scope limitation",
            }
            for marker, label in required_leggings_test_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/running-shorts-chafing-ride-up-test.html":
            required_running_shorts_markers = {
                "running-shorts-wear-test-checklist.csv": "running-shorts checklist link",
                'data-resource-download="running-shorts-wear-test-checklist"': "running-shorts download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"dateModified":"2026-08-09"': "current article modification date",
                "No liner type or inseam can guarantee": "visible wear-test limitation",
            }
            for marker, label in required_running_shorts_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/verify-ai-generated-tech-pack.html":
            required_ai_tech_pack_markers = {
                "ai-tech-pack-verification-checklist.csv": "AI tech-pack checklist link",
                'data-resource-download="ai-tech-pack-verification-checklist"': "AI checklist download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"dateModified":"2026-08-09"': "current article modification date",
                "Treat every AI-generated tech pack as an unverified draft": "visible verification limitation",
            }
            for marker, label in required_ai_tech_pack_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/sports-bra-fit-support-wear-test.html":
            required_sports_bra_markers = {
                "sports-bra-fit-wear-test-checklist.csv": "sports-bra checklist link",
                'data-resource-download="sports-bra-fit-wear-test-checklist"': "sports-bra download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"dateModified":"2026-08-09"': "current article modification date",
                "No size architecture or fabric can guarantee": "visible support limitation",
                "editorial-policy.html": "author methodology link",
                "feed.xml": "RSS feed discovery",
            }
            for marker, label in required_sports_bra_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/activewear-inclusive-sizing-fit-test.html":
            required_inclusive_fit_markers = {
                "activewear-fit-range-validation-checklist.csv": "fit-range checklist link",
                'data-resource-download="activewear-fit-range-validation-checklist"': "fit-range download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"dateModified":"2026-08-10"': "current article modification date",
                "One base-size wearer cannot prove the full range": "visible fit-scope limitation",
                "iso.org/standard/61686.html": "current anthropometric definition reference",
                "editorial-policy.html": "author methodology link",
                "feed.xml": "RSS feed discovery",
            }
            for marker, label in required_inclusive_fit_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/youth-team-uniform-sizing-order-checklist.html":
            required_youth_order_markers = {
                "youth-team-uniform-order-validation-checklist.csv": "youth order checklist link",
                'data-resource-download="youth-team-uniform-order-validation-checklist"': "youth checklist download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "youth checklist document schema",
                '"isAccessibleForFree":true': "free youth checklist disclosure",
                "one child, one sample, or one age label cannot prove fit": "visible fit-scope limitation",
                "iso.org/standard/61686.html": "anthropometric terminology reference",
                "editorial-policy.html": "author methodology link",
                "feed.xml": "RSS feed discovery",
            }
            for marker, label in required_youth_order_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/custom-apparel-packaging-moq-inventory-planning.html":
            required_packaging_moq_markers = {
                "apparel-packaging-moq-inventory-planner.csv": "packaging inventory planner link",
                'data-resource-download="apparel-packaging-moq-inventory-planner"': "packaging planner download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "packaging planner document schema",
                '"isAccessibleForFree":true': "free packaging planner disclosure",
                '"dateModified":"2026-08-10"': "current article modification date",
                "there is no responsible universal packaging MOQ": "visible universal-MOQ limitation",
                "gs1.org/standards/barcodes": "authoritative barcode reference",
                "ftc.gov/business-guidance/industry/clothing-and-textiles": "authoritative apparel label reference",
                "editorial-policy.html": "author methodology link",
                "feed.xml": "RSS feed discovery",
            }
            for marker, label in required_packaging_moq_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/clothing-sample-to-bulk-quality-control.html":
            required_sample_to_bulk_markers = {
                "sample-to-bulk-quality-control-checklist.csv": "sample-to-bulk checklist link",
                'data-resource-download="sample-to-bulk-quality-control-checklist"': "sample-to-bulk download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "sample-to-bulk checklist document schema",
                '"isAccessibleForFree":true': "free sample-to-bulk checklist disclosure",
                "No sealed sample, photograph, video call, or single inspection can guarantee": "visible production-control limitation",
                "iso.org/standard/85464.html": "current ISO 2859-1 reference",
                "iso.org/standard/57309.html": "dimensional-change preparation reference",
                "iso.org/standard/41877.html": "dimensional-change method reference",
                "ftc.gov/business-guidance/industry/clothing-and-textiles": "authoritative U.S. apparel label reference",
                "editorial-policy.html": "author methodology link",
                "feed.xml": "RSS feed discovery",
            }
            for marker, label in required_sample_to_bulk_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/volleyball-uniform-rules-checklist.html":
            required_volleyball_rules_markers = {
                "volleyball-uniform-ruleset-approval-checklist.csv": "volleyball ruleset checklist link",
                'data-resource-download="volleyball-uniform-ruleset-approval-checklist"': "volleyball checklist download tracking",
                '"@type":"BlogPosting"': "blog posting structured data",
                '"@type":"DigitalDocument"': "volleyball checklist document schema",
                '"isAccessibleForFree":true': "free volleyball checklist disclosure",
                "there is no universal volleyball uniform design": "visible universal-design limitation",
                "usavolleyball.org/resources-for-officials/rulebooks-and-interpretations/": "current USA Volleyball rules source",
                "nfhs.org/sports/volleyball/rules": "current NFHS volleyball rules source",
                "ncaa.org/championships/playing-rules/womens-volleyball-playing-rules/": "current NCAA volleyball rules source",
                "editorial-policy.html": "author methodology link",
                "feed.xml": "RSS feed discovery",
            }
            for marker, label in required_volleyball_rules_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/volleyball-teamwear.html":
            required_volleyball_program_markers = {
                "volleyball-uniform-rules-checklist.html": "volleyball rules article link",
                "Seven program roles": "program-role separation",
                "Eight planning gates": "season planning workflow",
                '"dateModified":"2026-08-28"': "current page modification date",
            }
            for marker, label in required_volleyball_program_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/volleyball-uniforms.html":
            required_volleyball_uniform_markers = {
                "volleyball-uniform-rules-checklist.html": "volleyball rules article link",
                "volleyball-uniform-ruleset-approval-checklist.csv": "volleyball ruleset checklist link",
                'data-resource-download="volleyball-uniform-ruleset-approval-checklist"': "volleyball checklist download tracking",
                "Eight sample checks": "physical uniform approval workflow",
                '"@type":"DigitalDocument"': "volleyball checklist document schema",
                '"dateModified":"2026-08-10"': "current page modification date",
            }
            for marker, label in required_volleyball_uniform_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "editorial-policy.html":
            required_editorial_markers = {
                "Who, how, and why": "visible Who How Why explanation",
                "AI may assist the workflow": "AI-assistance disclosure",
                "Planning visuals and sample rows are illustrative": "image and example disclosure",
                "Report an error or unsupported statement": "correction process",
                '"@id":"https://glorystarwears.com/#editorial-team"': "editorial team entity",
                "feed.xml": "RSS feed link",
            }
            for marker, label in required_editorial_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/sports-bras.html":
            required_sports_bra_product_markers = {
                "sports-bra-fit-support-wear-test.html": "sports-bra validation guide link",
                "sports-bra-fit-wear-test-checklist.csv": "sports-bra checklist link",
            }
            for marker, label in required_sports_bra_product_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/plus-size-activewear.html":
            required_inclusive_product_markers = {
                "activewear-inclusive-sizing-fit-test.html": "inclusive fit validation guide link",
                "activewear-fit-range-validation-checklist.csv": "fit-range checklist link",
            }
            for marker, label in required_inclusive_product_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/youth-sportswear.html":
            required_youth_product_markers = {
                "Plan youth sportswear by program role": "program-level direct answer",
                "Program architecture": "program route comparison",
                "Six planning gates": "program planning workflow",
                "youth-team-uniform-sizing-order-checklist.html": "youth order validation article link",
                "youth-team-uniform-order-validation-checklist.csv": "youth order checklist link",
            }
            for marker, label in required_youth_product_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/private-label-sportswear-packaging.html":
            required_packaging_product_markers = {
                "Quote every packaging component at its own quantity": "component-level direct answer",
                "Customization routes": "packaging route comparison",
                "custom-apparel-packaging-moq-inventory-planning.html": "packaging-MOQ article link",
                "apparel-packaging-moq-inventory-planner.csv": "packaging planner link",
                "sportswear-packaging-label-handoff-checklist.html": "packaging handoff link",
                "us-clothing-label-requirements-private-label.html": "U.S. clothing-label article link",
                '"dateModified":"2026-08-12"': "current product page modification date",
            }
            for marker, label in required_packaging_product_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/racket-sports-apparel.html":
            required_racket_program_markers = {
                "Build the racket-sports collection around the program": "program-level direct answer",
                "Program architecture": "program route comparison",
                "Six planning gates": "collection planning workflow",
                "tennis-pickleball-apparel.html": "specific garment page link",
            }
            for marker, label in required_racket_program_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/tennis-pickleball-apparel.html":
            required_court_garment_markers = {
                "tennis-pickleball-apparel-sample-checklist.csv": "court apparel sample checklist link",
                'data-resource-download="tennis-pickleball-apparel-sample-checklist"': "court checklist download tracking",
                '"@type":"DigitalDocument"': "court checklist document schema",
                '"isAccessibleForFree":true': "free court checklist disclosure",
                "Approve court apparel with the intended ball load": "garment-level direct answer",
                "no pocket depth, liner length, gripper, fabric, or inseam can guarantee": "visible universal-performance limitation",
                "racket-sports-apparel.html": "program-level racket page link",
            }
            for marker, label in required_court_garment_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/cycling-wear.html":
            required_cycling_program_markers = {
                "Build the cycling collection around the rider program": "collection-level direct answer",
                "Program architecture": "program route comparison",
                "Six planning gates": "collection planning workflow",
                "cycling-jerseys-bib-shorts.html": "specific jersey and bib page link",
            }
            for marker, label in required_cycling_program_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/cycling-jerseys-bib-shorts.html":
            required_cycling_detail_markers = {
                "cycling-jersey-bib-sample-checklist.csv": "cycling sample checklist link",
                'data-resource-download="cycling-jersey-bib-sample-checklist"': "cycling checklist download tracking",
                '"@type":"DigitalDocument"': "cycling checklist document schema",
                '"isAccessibleForFree":true': "free cycling checklist disclosure",
                "Approve cycling jerseys and bib shorts in riding posture": "garment-level direct answer",
                "no chamois shape, thickness, gripper width": "visible universal-comfort limitation",
            }
            for marker, label in required_cycling_detail_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/golf-apparel.html":
            required_golf_program_markers = {
                "Plan the golf program around the venue": "collection-level direct answer",
                "Program routes": "program route comparison",
                "Six planning gates": "collection planning workflow",
                "golf-polo-shirts-skorts.html": "specific polo and skort page link",
            }
            for marker, label in required_golf_program_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/golf-polo-shirts-skorts.html":
            required_golf_detail_markers = {
                "golf-polo-skort-sample-checklist.csv": "golf sample checklist link",
                'data-resource-download="golf-polo-skort-sample-checklist"': "golf checklist download tracking",
                '"@type":"DigitalDocument"': "golf checklist document schema",
                '"isAccessibleForFree":true': "free golf checklist disclosure",
                "Approve golf polos and skorts through swing": "garment-level direct answer",
                "no fabric name, cooling or UV label": "visible performance-claim limitation",
            }
            for marker, label in required_golf_detail_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "resources/sportswear-logo-artwork-preparation-guide.html":
            required_artwork_markers = {
                "sportswear-artwork-approval-register.csv": "artwork approval register link",
                'data-resource-download="sportswear-artwork-approval-register"': "artwork download tracking",
                '"@type":"DigitalDocument"': "artwork document schema",
                '"isAccessibleForFree":true': "free artwork register disclosure in schema",
                '"dateModified":"2026-08-13"': "current artwork guide modification date",
                "sportswear-sublimation-color-matching-guide.html": "sublimation-color article link",
                "apparel-print-wash-test-logo-durability.html": "decoration wash-test article link",
                "rights confirmation": "artwork rights field disclosure",
                "adobe.com/creativecloud/file-types/image/comparison/raster-vs-vector.html": "authoritative vector and raster reference",
            }
            for marker, label in required_artwork_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "sportswear-manufacturer.html":
            required_manufacturer_route_markers = {
                'id="production-route-heading"': "route-selection section",
                "proposed inquiry scopes, not pre-confirmed manufacturing routes": "project-specific route boundary",
                'href="./resources/oem-vs-odm-sportswear.html"': "generic OEM-versus-ODM method handoff",
                'id="supplier-evidence-heading"': "supplier-evidence section",
                'href="#supplier-evidence-heading"': "hero supplier-evidence route",
                "the hero image is an illustrative planning visual": "visible hero-image disclosure",
                "not proof of factory identity, ownership, capacity": "visible supplier-claim boundary",
                "illustrative planning visuals, not documentary evidence": "visible image disclosure",
            }
            for marker, label in required_manufacturer_route_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

            for image_tag in IMAGE_RE.findall(source):
                alt_match = re.search(r'\balt="([^"]*)"', image_tag, re.IGNORECASE)
                alt_text = alt_match.group(1).strip() if alt_match else ""
                status_match = re.search(
                    r'\bdata-evidence-status="([^"]*)"',
                    image_tag,
                    re.IGNORECASE,
                )
                evidence_status = (
                    status_match.group(1).strip().lower() if status_match else ""
                )
                if evidence_status not in {"illustrative", "verified"}:
                    errors.append(
                        f"{relative_name}: image is missing a valid evidence status"
                    )
                elif (
                    evidence_status == "illustrative"
                    and "illustrative" not in alt_text.lower()
                ):
                    errors.append(
                        f"{relative_name}: illustrative image alt does not disclose status"
                    )
                elif evidence_status == "verified" and not re.search(
                    r'\bdata-evidence-source="[^"]+"', image_tag, re.IGNORECASE
                ):
                    errors.append(
                        f"{relative_name}: verified image is missing its evidence source"
                    )

        if relative_name == "case-studies.html":
            required_planning_markers = {
                "every buyer type, product mix, action, visual, and proposed outcome on this page is hypothetical": "complete hypothetical-content disclosure",
                "contains no actual buyer, order, production, delivery, reorder, testimonial, or outcome fact": "scenario fact boundary",
                "What a verified public project story would require": "verified-story evidence requirements",
                "The planning briefs above do not satisfy these requirements": "planning-versus-evidence boundary",
            }
            for marker, label in required_planning_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

            if not re.search(
                r'"dateModified"\s*:\s*"\d{4}-\d{2}-\d{2}"', source
            ):
                errors.append(
                    f"{relative_name}: CollectionPage is missing dateModified"
                )

            h1_match = re.search(
                r"<h1\b[^>]*>(.*?)</h1>", source, re.IGNORECASE | re.DOTALL
            )
            h1_text = normalized_text(
                TAG_RE.sub(" ", h1_match.group(1)) if h1_match else ""
            )
            for label, value in (
                ("title", parser.title),
                ("H1", h1_text),
                ("meta description", parser.description),
                ("Open Graph title", parser.og_title),
            ):
                if "planning" not in value.lower() or "case stud" in value.lower():
                    errors.append(
                        f"{relative_name}: {label} does not preserve planning-example intent"
                    )

            if not all(
                term in parser.og_description.lower()
                for term in ("illustrative", "planning")
            ):
                errors.append(
                    f"{relative_name}: Open Graph description does not preserve "
                    "the illustrative planning boundary"
                )

            collection_nodes = []
            for block in parser.json_ld_blocks:
                try:
                    structured_data = json.loads(block)
                except json.JSONDecodeError:
                    continue
                collection_nodes.extend(
                    node
                    for node in structured_nodes(structured_data)
                    if node.get("@type") == "CollectionPage"
                )
            collection_descriptions = [
                normalized_text(node.get("description", "")).lower()
                for node in collection_nodes
            ]
            if not any(
                "hypothetical" in description
                and "not completed" in description
                and "delivered results" in description
                for description in collection_descriptions
            ):
                errors.append(
                    f"{relative_name}: CollectionPage description does not preserve "
                    "the hypothetical-content boundary"
                )

            for label, value in (
                ("Open Graph image alt", parser.og_image_alt),
                ("social image alt", parser.twitter_image_alt),
            ):
                if "illustrative" not in value.lower():
                    errors.append(
                        f"{relative_name}: {label} does not disclose illustrative status"
                    )

            for image in parser.images:
                evidence_status = image.get("data-evidence-status", "").lower()
                alt_text = image.get("alt", "").strip()
                image_has_issue = False
                if evidence_status not in {"illustrative", "verified"}:
                    image_has_issue = True
                    errors.append(
                        f"{relative_name}: image is missing a valid evidence status"
                    )
                elif (
                    evidence_status == "illustrative"
                    and "illustrative" not in alt_text.lower()
                ):
                    image_has_issue = True
                    errors.append(
                        f"{relative_name}: illustrative image alt does not disclose status"
                    )
                elif evidence_status == "verified" and not image.get(
                    "data-evidence-source", ""
                ).strip():
                    image_has_issue = True
                    errors.append(
                        f"{relative_name}: verified image is missing its evidence source"
                    )
                if image_has_issue:
                    undisclosed_case_planning_visuals += 1

            ambiguous_phrases = (
                "a boutique activewear buyer planned",
                "a fitness brand needed",
                "a teamwear buyer requested",
                "an ecommerce seller improved",
            )
            phrase_count = sum(
                source.lower().count(phrase) for phrase in ambiguous_phrases
            )
            ambiguous_case_scenario_phrases += phrase_count
            if phrase_count:
                errors.append(
                    f"{relative_name}: contains {phrase_count} ambiguous "
                    "past-tense buyer scenario phrases"
                )

        if relative_name == "about-factory.html":
            phrase_count = source.lower().count("anonymized buyer scenarios")
            ambiguous_case_scenario_phrases += phrase_count
            if phrase_count:
                errors.append(
                    f"{relative_name}: hypothetical briefs are described as anonymized buyers"
                )

        if relative_name == "resources/index.html" and "case-studies.html" in source:
            phrase_count = sum(
                source.lower().count(phrase)
                for phrase in ("project evidence", "use comparable cases")
            )
            ambiguous_case_scenario_phrases += phrase_count
            if phrase_count:
                errors.append(
                    f"{relative_name}: planning examples are described as project evidence"
                )

        if relative_name == "custom-teamwear-uniforms.html":
            required_teamwear_program_markers = {
                "multi-sport programs, roster sizing, decoration choices": "broad teamwear program description",
                "Full-Color Sublimation Route": "sublimation-route label",
                "Review sublimation artwork and color controls": "descriptive narrow-route link",
            }
            for marker, label in required_teamwear_program_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/custom-sublimated-teamwear.html":
            required_sublimated_teamwear_markers = {
                "sportswear-sublimation-color-matching-guide.html": "sublimation-color article link",
                "color code or screen mockup is an input": "visible physical color approval boundary",
                "Use this page for full-color sublimation controls": "sublimation-only decision boundary",
                "Compare All Teamwear Routes": "broad teamwear route link",
                "production-fabric color approval": "fabric-specific approval scope",
            }
            for marker, label in required_sublimated_teamwear_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "customization.html":
            required_customization_markers = {
                "sportswear-sublimation-color-matching-guide.html": "sublimation-color article link",
                '"dateModified": "2026-08-13"': "current customization modification date",
                "Sublimation Color Approval": "sublimation color workflow card",
                "Decoration Wash Testing": "decoration wash-test workflow card",
                "apparel-print-wash-test-logo-durability.html": "decoration wash-test article link",
            }
            for marker, label in required_customization_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "resources/sportswear-packaging-label-handoff-checklist.html":
            required_packaging_markers = {
                "sportswear-packaging-handoff-register.csv": "packaging handoff register link",
                'data-resource-download="sportswear-packaging-handoff-register"': "packaging download tracking",
                '"@type":"DigitalDocument"': "packaging document schema",
                '"isAccessibleForFree":true': "free packaging register disclosure in schema",
                '"dateModified":"2026-08-12"': "current packaging guide modification date",
                "us-clothing-label-requirements-private-label.html": "U.S. clothing-label article link",
                "custom-apparel-packaging-moq-inventory-planning.html": "packaging-MOQ article link",
                "gs1.org/standards/barcodes": "authoritative barcode reference",
                "ftc.gov/business-guidance/industry/clothing-and-textiles": "authoritative clothing labeling reference",
            }
            for marker, label in required_packaging_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "factory-video.html":
            required_factory_media_markers = {
                "sportswear-factory-media-verification-register.csv": "factory media verification register link",
                'data-resource-download="sportswear-factory-media-verification-register"': "factory media download tracking",
                '"@type":"DigitalDocument"': "factory media document schema",
                '"isAccessibleForFree":true': "free factory media register disclosure",
                "No source-verified GloryStarWear factory footage is currently published": "current factory footage disclosure",
                "Media verifies only the scene, time, and scope captured": "visible media evidence limitation",
                "does not confirm or guarantee a live call": "conditional live-call availability boundary",
                "about-factory.html": "supplier verification overview link",
                "sportswear-manufacturer-due-diligence-checklist.html": "full due-diligence method link",
            }
            for marker, label in required_factory_media_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

            factory_image_alts = []
            for image_tag in IMAGE_RE.findall(source):
                alt_match = re.search(r'\balt="([^"]*)"', image_tag, re.IGNORECASE)
                factory_image_alts.append(alt_match.group(1).strip() if alt_match else "")
            undisclosed_factory_media_visuals = sum(
                not alt.startswith("Illustrative ") for alt in factory_image_alts
            )
            if len(factory_image_alts) != 4:
                errors.append(
                    f"{relative_name}: expected 4 illustrative content images, "
                    f"found {len(factory_image_alts)}"
                )
            if undisclosed_factory_media_visuals:
                errors.append(
                    f"{relative_name}: {undisclosed_factory_media_visuals} image alt values "
                    "do not disclose illustrative status"
                )

            unqualified_factory_video_availability_answers = source.count(
                "Yes. A video call"
            )
            if unqualified_factory_video_availability_answers:
                errors.append(
                    f"{relative_name}: contains "
                    f"{unqualified_factory_video_availability_answers} unqualified "
                    "video-call availability answers"
                )

            factory_register_path = (
                ROOT
                / "assets"
                / "downloads"
                / "sportswear-factory-media-verification-register.csv"
            )
            if not factory_register_path.exists():
                errors.append(f"{relative_name}: missing factory media verification CSV")
            else:
                with factory_register_path.open(
                    newline="", encoding="utf-8-sig"
                ) as factory_register_file:
                    factory_register_rows = list(csv.reader(factory_register_file))
                if not factory_register_rows:
                    errors.append(f"{relative_name}: factory media verification CSV is empty")
                else:
                    factory_register_header = factory_register_rows[0]
                    factory_media_register_fields = len(factory_register_header)
                    if factory_media_register_fields != 47:
                        errors.append(
                            f"{relative_name}: factory media verification CSV has "
                            f"{factory_media_register_fields} fields instead of 47"
                        )
                    if len(set(factory_register_header)) != factory_media_register_fields:
                        errors.append(
                            f"{relative_name}: factory media verification CSV has "
                            "duplicate headers"
                        )
                    malformed_factory_rows = [
                        row_number
                        for row_number, row in enumerate(factory_register_rows, start=1)
                        if len(row) != factory_media_register_fields
                    ]
                    if malformed_factory_rows:
                        errors.append(
                            f"{relative_name}: factory media verification CSV has "
                            f"malformed rows {malformed_factory_rows}"
                        )
                    required_factory_register_fields = {
                        "contracting_entity",
                        "facility_name",
                        "facility_location_claim",
                        "actual_capture_date",
                        "continuous_or_edited_status",
                        "observed_fact",
                        "not_shown_or_not_verified",
                        "confidentiality_or_redaction",
                        "publication_permission",
                        "decision_gate",
                        "limitation_note",
                    }
                    missing_factory_register_fields = sorted(
                        required_factory_register_fields - set(factory_register_header)
                    )
                    if missing_factory_register_fields:
                        errors.append(
                            f"{relative_name}: factory media verification CSV is missing "
                            f"fields {', '.join(missing_factory_register_fields)}"
                        )

        if relative_name == "about-factory.html":
            required_supplier_verification_markers = {
                "Request and verify factory media": "descriptive factory media route link",
                "confirm current media and call availability separately": "conditional media availability boundary",
                'property="og:image:alt"': "Open Graph illustrative image disclosure",
                'name="twitter:image:alt"': "Twitter illustrative image disclosure",
            }
            for marker, label in required_supplier_verification_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "certificates.html":
            required_compliance_markers = {
                "sportswear-compliance-evidence-register.csv": "compliance evidence register link",
                'data-resource-download="sportswear-compliance-evidence-register"': "compliance download tracking",
                '"@type":"DigitalDocument"': "compliance document schema",
                '"isAccessibleForFree":true': "free compliance register disclosure in schema",
                '"dateModified":"2026-08-27"': "current compliance checklist modification date",
                "us-clothing-label-requirements-private-label.html": "U.S. clothing-label article link",
                "nist.gov/publications/guide-united-states-apparel": "authoritative U.S. apparel overview",
                "ftc.gov/business-guidance/industry/clothing-and-textiles": "authoritative U.S. label reference",
                "cpsc.gov/FAQ/Clothing": "authoritative U.S. product-safety reference",
                "europa.eu/youreurope/business/product-rules-compliance": "authoritative EU textile-label reference",
                "commission.europa.eu/business-economy-euro/doing-business-eu": "authoritative EU product-safety reference",
            }
            for marker, label in required_compliance_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/lookbook.html":
            required_gallery_markers = {
                "sportswear-product-gallery-shortlist.csv": "product gallery shortlist link",
                'data-resource-download="sportswear-product-gallery-shortlist"': "gallery shortlist download tracking",
                '"@type": "DigitalDocument"': "gallery shortlist document schema",
                '"isAccessibleForFree": true': "free gallery shortlist disclosure in schema",
                '"dateModified": "2026-08-27"': "current product gallery modification date",
                "A visual reference is not a production specification": "visible visual-reference scope disclosure",
            }
            for marker, label in required_gallery_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "resources/custom-sportswear-cost-lead-time.html":
            required_quote_comparison_markers = {
                "sportswear-supplier-quote-comparison.csv": "supplier quote comparison link",
                'data-resource-download="sportswear-supplier-quote-comparison"': "quote comparison download tracking",
                '"@type":"DigitalDocument"': "quote comparison document schema",
                '"isAccessibleForFree":true': "free quote comparison disclosure in schema",
                "This worksheet does not calculate or guarantee price": "visible quote worksheet scope disclosure",
                "Ask on WhatsApp": "direct WhatsApp inquiry route",
                "apparel-incoterms-exw-fob-ddp-landed-cost.html": "apparel delivery-term comparison handoff",
            }
            for marker, label in required_quote_comparison_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "blog/apparel-incoterms-exw-fob-ddp-landed-cost.html":
            required_incoterm_markers = {
                "apparel-incoterm-landed-cost-register.csv": "apparel Incoterm register link",
                'data-resource-download="apparel-incoterm-landed-cost-register"': "Incoterm register download tracking",
                '"@type":"DigitalDocument"': "Incoterm register document schema",
                '"isAccessibleForFree":true': "free Incoterm register disclosure in schema",
                '"dateModified":"2026-08-12"': "current apparel Incoterms modification date",
                "This register does not select a rule": "visible Incoterm worksheet limitation",
                "academy.iccwbo.org/incoterms/article/incoterms-2020-exw-or-ddp": "ICC EXW and DDP source",
                "academy.iccwbo.org/incoterms/article/incoterms-2020-fca-or-fob": "ICC FCA and FOB source",
                "academy.iccwbo.org/incoterms/article/incoterms-2020-dap-or-ddp": "ICC DAP and DDP source",
                "www.help.cbp.gov/s/article/Article-1066": "authoritative U.S. importer reference",
                "Reddit exposes recurring buyer confusion": "visible Reddit evidence boundary",
            }
            for marker, label in required_incoterm_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "contact.html":
            required_contact_markers = {
                'data-lead-endpoint="/api/lead"': "same-origin lead endpoint",
                "Complete once, then send by WhatsApp or email": "working inquiry-route explanation",
                "Cost and lead-time review": "commercial planning inquiry option",
                "sportswear-supplier-quote-comparison.csv": "supplier comparison handoff",
                "Tech pack review and development": "tech-pack inquiry option",
                "Artwork and decoration review": "artwork inquiry option",
                "Fabric selection and performance testing": "fabric inquiry option",
                "Packaging and label handoff": "packaging inquiry option",
                "Quality and inspection planning": "quality inquiry option",
                '"@id": "https://glorystarwears.com/#organization"': "canonical organization entity reference",
            }
            for marker, label in required_contact_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "products/private-label-gym-clothing.html":
            required_gym_program_markers = {
                "What happens after you send the gym clothing brief?": "post-brief response scope",
                "Verify supplier scope and evidence": "supplier due-diligence handoff",
                "Review sample and bulk-release controls": "sample-control handoff",
                "Send Gym Clothing Brief": "gym inquiry CTA",
                '"@type":"Service"': "gym manufacturing Service schema",
                '"isAccessibleForFree":true': "free gym planner disclosure",
                '"dateModified":"2026-08-28"': "current gym program modification date",
            }
            for marker, label in required_gym_program_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if relative_name == "one-stop-service.html":
            required_one_stop_markers = {
                "Build a One-Stop Order Brief": "one-stop hero inquiry CTA",
                "Compare Cost &amp; Lead-Time Assumptions": "one-stop commercial handoff",
                "WhatsApp the Product List": "one-stop WhatsApp CTA",
                '"provider": { "@id": "https://glorystarwears.com/#organization" }': "organization reference in Service schema",
                '"dateModified": "2026-08-28"': "current one-stop modification date",
            }
            for marker, label in required_one_stop_markers.items():
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
        structured_faq_questions = set()
        structured_faq_pairs = []
        structured_article_author_urls = set()
        article_schema_nodes = 0
        for block in parser.json_ld_blocks:
            json_ld_count += 1
            try:
                structured_data = json.loads(block)
            except json.JSONDecodeError as error:
                errors.append(f"{relative_name}: invalid JSON-LD: {error}")
                continue

            for node in structured_nodes(structured_data):
                node_type = node.get("@type")
                modified_date = node.get("dateModified")
                if isinstance(modified_date, str) and re.fullmatch(
                    r"\d{4}-\d{2}-\d{2}", modified_date
                ):
                    parser.structured_modified_dates.add(modified_date)
                if isinstance(node_type, str):
                    structured_types.add(node_type)
                elif isinstance(node_type, list):
                    structured_types.update(
                        value for value in node_type if isinstance(value, str)
                    )

                node_types = (
                    {node_type}
                    if isinstance(node_type, str)
                    else {
                        value
                        for value in node_type
                        if isinstance(value, str)
                    }
                    if isinstance(node_type, list)
                    else set()
                )
                if node_types.intersection({"Article", "BlogPosting"}):
                    article_schema_nodes += 1
                    authors = node.get("author", [])
                    if isinstance(authors, dict):
                        authors = [authors]
                    valid_authors = [
                        author for author in authors if isinstance(author, dict)
                    ]
                    if not any(
                        normalized_text(author.get("name", ""))
                        for author in valid_authors
                    ):
                        errors.append(
                            f"{relative_name}: Article/BlogPosting author is missing a name"
                        )
                    author_urls = {
                        author.get("url", "").strip()
                        for author in valid_authors
                        if isinstance(author.get("url"), str)
                        and author.get("url", "").strip()
                    }
                    if not author_urls:
                        errors.append(
                            f"{relative_name}: Article/BlogPosting author is missing a URL"
                        )
                    structured_article_author_urls.update(author_urls)

                    publisher = node.get("publisher")
                    if not isinstance(publisher, dict) or not (
                        normalized_text(publisher.get("name", ""))
                        or normalized_text(publisher.get("@id", ""))
                    ):
                        errors.append(
                            f"{relative_name}: Article/BlogPosting is missing a publisher"
                        )

                if node_type != "FAQPage":
                    continue
                for question in node.get("mainEntity", []):
                    question_text = normalized_text(question.get("name", ""))
                    if question_text:
                        structured_faq_questions.add(question_text)
                    answer_text = normalized_text(
                        question.get("acceptedAnswer", {}).get("text", "")
                    )
                    if question_text or answer_text:
                        structured_faq_pairs.append((question_text, answer_text))
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

        visible_faq_questions = set(parser.visible_faq_questions)
        if visible_faq_questions or parser.direct_answers:
            visible_faq_pages += 1
        if "FAQPage" in structured_types:
            faq_schema_pages += 1
            for question_text in sorted(
                visible_faq_questions - structured_faq_questions
            ):
                errors.append(
                    f"{relative_name}: visible FAQ question is missing from JSON-LD: "
                    f"{question_text}"
                )
        if html_file.stem in EXPANDED_PRODUCT_SLUGS:
            visible_direct_answers = Counter(parser.direct_answers)
            schema_direct_answers = Counter(structured_faq_pairs)
            if sum(visible_direct_answers.values()) != 4:
                errors.append(
                    f"{relative_name}: expected exactly four visible direct-answer pairs"
                )
            if visible_direct_answers != schema_direct_answers:
                errors.append(
                    f"{relative_name}: visible direct answers and FAQ schema differ"
                )

        if structured_types.intersection({"Article", "BlogPosting"}):
            article_schema_pages += 1
            expected_visible_date = max(
                parser.structured_modified_dates,
                default="",
            )
            if (
                expected_visible_date
                and expected_visible_date not in parser.visible_article_dates
            ):
                errors.append(
                    f"{relative_name}: structured dateModified is not shown in "
                    f"article metadata: {expected_visible_date}"
                )

            visible_article_urls = {
                urljoin(parser.canonical, link)
                for link in parser.visible_article_links
            }
            for author_url in sorted(
                structured_article_author_urls - visible_article_urls
            ):
                errors.append(
                    f"{relative_name}: structured author URL is not linked in "
                    f"article metadata: {author_url}"
                )

            if article_schema_nodes != 1:
                errors.append(
                    f"{relative_name}: expected one Article/BlogPosting node, "
                    f"found {article_schema_nodes}"
                )

        if 'class="breadcrumb"' in source and "BreadcrumbList" not in structured_types:
            errors.append(
                f"{relative_name}: visible breadcrumb is missing BreadcrumbList JSON-LD"
            )

        if "script.js" in source and f"script.js?v={EXPECTED_SCRIPT_VERSION}" not in source:
            errors.append(
                f"{relative_name}: expected script version {EXPECTED_SCRIPT_VERSION}"
            )
        if "styles.css" in source and f"styles.css?v={EXPECTED_FORM_STYLE_VERSION}" not in source:
            errors.append(
                f"{relative_name}: expected style version {EXPECTED_FORM_STYLE_VERSION}"
            )

        if relative_name == "privacy.html":
            required_analytics_privacy_markers = {
                "Google Analytics 4 loads only after you allow analytics": "analytics consent disclosure",
                "glorystarwear-analytics-consent-v1": "analytics preference storage disclosure",
                "Advertising storage, advertising user data, and ad personalization remain denied": "advertising consent disclosure",
                "data-manage-analytics-consent": "analytics choice control",
                "dedicated Cloudflare D1 inquiry database": "secure lead storage disclosure",
                "365 days after receipt": "secure-form retention period",
                "Cloudflare Turnstile": "automated-spam protection disclosure",
            }
            for marker, label in required_analytics_privacy_markers.items():
                if marker not in source:
                    errors.append(f"{relative_name}: missing {label}")

        if "data-quote-form" in source:
            required_form_markers = {
                'name="consent" type="checkbox" required': "required privacy consent",
                "data-server-submit": "server submit control",
                "data-whatsapp-inquiry": "WhatsApp fallback",
                "data-email-inquiry": "email fallback",
                "data-copy-inquiry": "copy fallback",
                "data-turnstile-container": "human verification container",
                "data-quote-progress": "required-field completion progress",
                'aria-label="Custom sportswear quote form"': "accessible form name",
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

        if relative_name == "contact.html" and "quote-form" not in parser.ids:
            errors.append("contact.html: missing quote-form anchor")

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
        for href in parser.primary_main_contact_links:
            target = urlparse(urljoin(base_url, href))
            if target.path.endswith("/contact.html") and target.fragment != "quote-form":
                primary_ctas_bypassing_form_anchor += 1
                errors.append(
                    f"{relative_name}: primary contact CTA bypasses #quote-form: {href}"
                )
        page_internal_links[html_file.resolve()] = set()
        main_internal_links[html_file.resolve()] = set()
        for href in parser.links:
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            target_url = urljoin(base_url, href)
            target_file = site_file_for_url(target_url)
            if target_file is not None:
                resolved_target = target_file.resolve()
                internal_targets.add(resolved_target)
                page_internal_links[html_file.resolve()].add(resolved_target)

        for href in parser.main_links:
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            target_file = site_file_for_url(urljoin(base_url, href))
            if target_file is not None:
                main_internal_links[html_file.resolve()].add(target_file.resolve())

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
    for slug in sorted(EXPANDED_PRODUCT_SLUGS):
        target_file = (ROOT / "products" / f"{slug}.html").resolve()
        inlink_count = sum(
            target_file in target_links
            for target_links in main_internal_links.values()
        )
        expanded_product_contextual_inlinks[slug] = inlink_count
        if inlink_count < 4:
            errors.append(
                f"products/{slug}.html: expected at least 4 contextual HTML inlinks, "
                f"found {inlink_count}"
            )

    for asset in sorted(local_assets):
        if not asset.exists():
            errors.append(f"missing local asset: {asset.relative_to(ROOT)}")

    for source_name, target_names in sorted(REQUIRED_MAIN_LINKS.items()):
        source_file = (ROOT / source_name).resolve()
        if source_file not in pages:
            errors.append(f"required main-link source is missing: {source_name}")
            continue
        source_links = main_internal_links.get(source_file, set())
        for target_name in sorted(target_names):
            target_file = (ROOT / target_name).resolve()
            if target_file not in source_links:
                errors.append(
                    f"{source_name}: main content is missing link to {target_name}"
                )

    homepage_manufacturer_main_text_cosine_similarity = round(
        cosine_similarity(
            main_text_vector(ROOT / "index.html"),
            main_text_vector(ROOT / "sportswear-manufacturer.html"),
        ),
        4,
    )
    expanded_similarity_pairs = []
    expanded_vectors = {
        slug: main_text_vector(ROOT / "products" / f"{slug}.html")
        for slug in sorted(EXPANDED_PRODUCT_SLUGS)
    }
    document_frequency = Counter(
        token
        for vector in expanded_vectors.values()
        for token in vector
    )
    corpus_size = len(expanded_vectors)
    expanded_tfidf_vectors = {
        slug: {
            token: count * (log((1 + corpus_size) / (1 + document_frequency[token])) + 1)
            for token, count in vector.items()
        }
        for slug, vector in expanded_vectors.items()
    }
    for left_index, left_slug in enumerate(sorted(EXPANDED_PRODUCT_SLUGS)):
        for right_slug in sorted(EXPANDED_PRODUCT_SLUGS)[left_index + 1 :]:
            similarity = cosine_similarity(
                expanded_tfidf_vectors[left_slug],
                expanded_tfidf_vectors[right_slug],
            )
            expanded_similarity_pairs.append((similarity, left_slug, right_slug))
    if expanded_similarity_pairs:
        similarity, left_slug, right_slug = max(expanded_similarity_pairs)
        expanded_product_max_cosine_similarity = round(similarity, 4)
        expanded_product_most_similar_pair = [left_slug, right_slug]
        if similarity > 0.82:
            errors.append(
                "expanded product pages are too similar: "
                f"{left_slug} vs {right_slug} = {similarity:.4f}"
            )

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
                "lastmod": (
                    url_node.find("s:lastmod", namespace).text.strip()
                    if url_node.find("s:lastmod", namespace) is not None
                    and url_node.find("s:lastmod", namespace).text
                    else ""
                ),
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

    product_index_source = (ROOT / "products" / "index.html").read_text(
        encoding="utf-8"
    )
    product_card_count = len(
        re.findall(r'class="product-card"', product_index_source)
    )
    expected_catalog_card_count = EXPECTED_CONCRETE_PRODUCT_COUNT + 2
    if product_card_count != expected_catalog_card_count:
        errors.append(
            "products/index.html: expected "
            f"{expected_catalog_card_count} catalogue cards, found "
            f"{product_card_count}"
        )
    if f'"numberOfItems":{EXPECTED_CONCRETE_PRODUCT_COUNT}' not in re.sub(
        r"\s+", "", product_index_source
    ):
        errors.append(
            "products/index.html: product ItemList numberOfItems does not match "
            f"{EXPECTED_CONCRETE_PRODUCT_COUNT}"
        )
    for slug in sorted(EXPANDED_PRODUCT_SLUGS):
        product_url = f"{PRODUCTION_ORIGIN}/products/{slug}.html"
        if f'./{slug}.html' not in product_index_source:
            errors.append(
                f"products/index.html: missing expanded product link: {slug}"
            )
        if product_url not in sitemap_url_set:
            errors.append(f"sitemap.xml: missing expanded product URL: {product_url}")

    for hub_name in ("more-sports", "new-products"):
        hub_source = (ROOT / "products" / f"{hub_name}.html").read_text(
            encoding="utf-8"
        )
        for slug in sorted(EXPANDED_PRODUCT_SLUGS):
            product_url = f"{PRODUCTION_ORIGIN}/products/{slug}.html"
            if product_url not in hub_source:
                errors.append(
                    f"products/{hub_name}.html: schema is missing expanded product URL: {slug}"
                )

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

        if page is not None and page.structured_modified_dates:
            expected_lastmod = max(page.structured_modified_dates)
            if entry["lastmod"] != expected_lastmod:
                errors.append(
                    f"sitemap lastmod mismatch: {url}: "
                    f"{entry['lastmod'] or 'missing'} != {expected_lastmod}"
                )

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
        "concrete_product_pages": len(concrete_product_files),
        "catalog_product_cards": product_card_count,
        "llms_indexed_product_pages": len(
            concrete_product_urls.intersection(llms_product_urls)
        ),
        "expanded_product_pages": len(EXPANDED_PRODUCT_SLUGS),
        "expanded_product_max_cosine_similarity": expanded_product_max_cosine_similarity,
        "expanded_product_most_similar_pair": expanded_product_most_similar_pair,
        "expanded_product_contextual_inlinks": expanded_product_contextual_inlinks,
        "unique_canonicals": len(canonical_owners),
        "unique_titles": len(title_owners),
        "unique_descriptions": len(description_owners),
        "json_ld_blocks": json_ld_count,
        "images": image_count,
        "avif_images": avif_image_count,
        "visible_faq_pages": visible_faq_pages,
        "faq_schema_pages": faq_schema_pages,
        "article_schema_pages": article_schema_pages,
        "preferred_image_pages": preferred_image_pages,
        "primary_ctas_bypassing_form_anchor": primary_ctas_bypassing_form_anchor,
        "factory_media_register_fields": factory_media_register_fields,
        "undisclosed_factory_media_visuals": undisclosed_factory_media_visuals,
        "unqualified_factory_video_availability_answers": unqualified_factory_video_availability_answers,
        "case_studies_target_links": case_studies_target_links,
        "misleading_case_claim_anchors": misleading_case_claim_anchors,
        "undisclosed_case_planning_visuals": undisclosed_case_planning_visuals,
        "ambiguous_case_scenario_phrases": ambiguous_case_scenario_phrases,
        "homepage_manufacturer_main_text_cosine_similarity": homepage_manufacturer_main_text_cosine_similarity,
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

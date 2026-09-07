#!/usr/bin/env python3
"""Build complete static language editions from the English HTML source.

The source pages are copied byte-for-byte at the markup level. Only visible
text, selected accessibility attributes, metadata, internal routes, and the
locale chrome are changed. Translation data is read from the checked-in
static content maps, so the published site never calls a translation service.
"""
from __future__ import annotations

from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
import json
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "https://glorystarwears.com"
VERSION = "20260907-1"
LOCALES = {
    "fr": ("fr", "Français", "🇫🇷", "FR"),
    "es": ("es", "Español", "🇪🇸", "ES"),
    "pt": ("pt", "Português", "🇵🇹", "PT"),
    "ru": ("ru", "Русский", "🇷🇺", "RU"),
    "zh-cn": ("zh-CN", "简体中文", "🇨🇳", "中文"),
}
LOCALE_ORDER = list(LOCALES)

# Company identity and introduction copy are maintained here so the legal name
# stays exact across every static language edition, even when the offline
# content maps are refreshed from a changed English source page.
COMPANY_TEXT = {
    "fr": {
        "About": "À propos",
        "About GloryStarWear": "À propos de GloryStarWear",
        "Grow your business with a one-stop sportswear solution": "Développez votre activité avec une solution de vêtements de sport tout-en-un",
        "Xiamen Glorystar Import and Export Co., Ltd.": "Xiamen Glorystar Import and Export Co., Ltd.",
        "GloryStarWear is operated by Xiamen Glorystar Import and Export Co., Ltd., based in Xiamen, Fujian, China. We support private-label and custom activewear projects through OEM and ODM services.": "GloryStarWear est exploité par Xiamen Glorystar Import and Export Co., Ltd., basé à Xiamen, dans le Fujian, en Chine. Nous accompagnons les projets de vêtements de sport personnalisés et sous marque privée grâce à des services OEM et ODM.",
        "Our product scope includes": "Notre gamme comprend",
        "yoga wear": "vêtements de yoga",
        "gym wear": "vêtements de fitness",
        "sports bras": "soutiens-gorge de sport",
        "leggings": "leggings",
        ", and": " et",
        "coordinated sets": "ensembles coordonnés",
        ". Buyers can review our published manufacturing workflow, fabric options, and quality-control framework before discussing a project.": ". Les acheteurs peuvent consulter notre flux de fabrication publié, nos options de tissus et notre cadre de contrôle qualité avant de discuter d’un projet.",
        "Review supplier evidence": "Consulter les éléments de preuve fournisseur",
        "Discuss your activewear project": "Discuter de votre projet de vêtements actifs",
        "Illustrative GloryStarWear project-support team concept, not a staff photograph": "Concept illustratif de l’équipe de soutien aux projets GloryStarWear, et non une photo du personnel",
        "Illustrative project-support concept. Confirm current team, facility, capacity, and project responsibilities directly for each order.": "Concept illustratif de soutien au projet. Confirmez directement pour chaque commande l’équipe, le site, la capacité et les responsabilités actuelles.",
    },
    "es": {
        "About": "Acerca de",
        "About GloryStarWear": "Acerca de GloryStarWear",
        "Grow your business with a one-stop sportswear solution": "Haga crecer su negocio con una solución deportiva integral",
        "Xiamen Glorystar Import and Export Co., Ltd.": "Xiamen Glorystar Import and Export Co., Ltd.",
        "GloryStarWear is operated by Xiamen Glorystar Import and Export Co., Ltd., based in Xiamen, Fujian, China. We support private-label and custom activewear projects through OEM and ODM services.": "GloryStarWear está operado por Xiamen Glorystar Import and Export Co., Ltd., con sede en Xiamen, Fujian, China. Apoyamos proyectos de ropa deportiva personalizada y de marca privada mediante servicios OEM y ODM.",
        "Our product scope includes": "Nuestra gama de productos incluye",
        "yoga wear": "ropa de yoga",
        "gym wear": "ropa de gimnasio",
        "sports bras": "sujetadores deportivos",
        "leggings": "leggings",
        ", and": " y",
        "coordinated sets": "conjuntos coordinados",
        ". Buyers can review our published manufacturing workflow, fabric options, and quality-control framework before discussing a project.": ". Los compradores pueden consultar nuestro flujo de fabricación publicado, las opciones de tejido y el marco de control de calidad antes de hablar de un proyecto.",
        "Review supplier evidence": "Revisar las pruebas del proveedor",
        "Discuss your activewear project": "Hablar sobre su proyecto de ropa deportiva",
        "Illustrative GloryStarWear project-support team concept, not a staff photograph": "Concepto ilustrativo del equipo de apoyo a proyectos de GloryStarWear, no una fotografía del personal",
        "Illustrative project-support concept. Confirm current team, facility, capacity, and project responsibilities directly for each order.": "Concepto ilustrativo de apoyo al proyecto. Confirme directamente en cada pedido el equipo, las instalaciones, la capacidad y las responsabilidades actuales.",
    },
    "pt": {
        "About": "Sobre",
        "About GloryStarWear": "Sobre a GloryStarWear",
        "Grow your business with a one-stop sportswear solution": "Faça seu negócio crescer com uma solução esportiva completa",
        "Xiamen Glorystar Import and Export Co., Ltd.": "Xiamen Glorystar Import and Export Co., Ltd.",
        "GloryStarWear is operated by Xiamen Glorystar Import and Export Co., Ltd., based in Xiamen, Fujian, China. We support private-label and custom activewear projects through OEM and ODM services.": "A GloryStarWear é operada pela Xiamen Glorystar Import and Export Co., Ltd., sediada em Xiamen, Fujian, China. Apoiamos projetos de roupa desportiva personalizada e de marca própria através de serviços OEM e ODM.",
        "Our product scope includes": "A nossa gama de produtos inclui",
        "yoga wear": "roupa de ioga",
        "gym wear": "roupa de ginásio",
        "sports bras": "soutiens desportivos",
        "leggings": "leggings",
        ", and": " e",
        "coordinated sets": "conjuntos coordenados",
        ". Buyers can review our published manufacturing workflow, fabric options, and quality-control framework before discussing a project.": ". Os compradores podem consultar o nosso fluxo de fabrico publicado, as opções de tecido e o quadro de controlo de qualidade antes de discutir um projeto.",
        "Review supplier evidence": "Consultar as evidências do fornecedor",
        "Discuss your activewear project": "Falar sobre o seu projeto de roupa desportiva",
        "Illustrative GloryStarWear project-support team concept, not a staff photograph": "Conceito ilustrativo da equipa de apoio a projetos da GloryStarWear, não uma fotografia da equipa",
        "Illustrative project-support concept. Confirm current team, facility, capacity, and project responsibilities directly for each order.": "Conceito ilustrativo de apoio ao projeto. Confirme diretamente em cada encomenda a equipa, as instalações, a capacidade e as responsabilidades atuais.",
    },
    "ru": {
        "About": "О компании",
        "About GloryStarWear": "О GloryStarWear",
        "Grow your business with a one-stop sportswear solution": "Развивайте бизнес с универсальным решением для спортивной одежды",
        "Xiamen Glorystar Import and Export Co., Ltd.": "Xiamen Glorystar Import and Export Co., Ltd.",
        "GloryStarWear is operated by Xiamen Glorystar Import and Export Co., Ltd., based in Xiamen, Fujian, China. We support private-label and custom activewear projects through OEM and ODM services.": "GloryStarWear управляется компанией Xiamen Glorystar Import and Export Co., Ltd., расположенной в Сямыне, провинция Фуцзянь, Китай. Мы поддерживаем проекты по спортивной одежде под собственной маркой и на заказ с помощью услуг OEM и ODM.",
        "Our product scope includes": "В нашу линейку входят",
        "yoga wear": "одежда для йоги",
        "gym wear": "одежда для тренировок",
        "sports bras": "спортивные бюстгальтеры",
        "leggings": "леггинсы",
        ", and": " и",
        "coordinated sets": "согласованные комплекты",
        ". Buyers can review our published manufacturing workflow, fabric options, and quality-control framework before discussing a project.": ". Перед обсуждением проекта покупатели могут изучить опубликованный производственный процесс, варианты тканей и систему контроля качества.",
        "Review supplier evidence": "Изучить подтверждающие материалы поставщика",
        "Discuss your activewear project": "Обсудить проект спортивной одежды",
        "Illustrative GloryStarWear project-support team concept, not a staff photograph": "Иллюстративная концепция команды поддержки проектов GloryStarWear, а не фотография сотрудников",
        "Illustrative project-support concept. Confirm current team, facility, capacity, and project responsibilities directly for each order.": "Иллюстративная концепция поддержки проекта. Для каждого заказа напрямую подтвердите текущую команду, площадку, мощности и зоны ответственности.",
    },
    "zh-cn": {
        "About": "关于我们",
        "About GloryStarWear": "关于 GloryStarWear",
        "Grow your business with a one-stop sportswear solution": "用一站式运动服装解决方案助力业务增长",
        "Xiamen Glorystar Import and Export Co., Ltd.": "Xiamen Glorystar Import and Export Co., Ltd.",
        "GloryStarWear is operated by Xiamen Glorystar Import and Export Co., Ltd., based in Xiamen, Fujian, China. We support private-label and custom activewear projects through OEM and ODM services.": "GloryStarWear 由 Xiamen Glorystar Import and Export Co., Ltd. 运营，公司位于中国福建省厦门市。我们通过 OEM 和 ODM 服务支持自有品牌及定制运动服装项目。",
        "Our product scope includes": "我们的产品范围包括",
        "yoga wear": "瑜伽服",
        "gym wear": "健身服",
        "sports bras": "运动内衣",
        "leggings": "紧身裤",
        ", and": "和",
        "coordinated sets": "配套套装",
        ". Buyers can review our published manufacturing workflow, fabric options, and quality-control framework before discussing a project.": "。买家可以在洽谈项目之前查看我们公开的生产流程、面料选项和质量控制框架。",
        "Review supplier evidence": "查看供应商资料",
        "Discuss your activewear project": "洽谈您的运动服装项目",
        "Illustrative GloryStarWear project-support team concept, not a staff photograph": "GloryStarWear 项目支持团队示意图，并非员工照片",
        "Illustrative project-support concept. Confirm current team, facility, capacity, and project responsibilities directly for each order.": "项目支持示意图。每个订单的当前团队、场地、产能和项目职责请直接确认。",
    },
}

# Keep the homepage search and social metadata as deliberate native copy. The
# broader offline content maps cover every page, but a few long metadata
# strings contain awkward literal translations that can weaken click-through.
LOCALE_META = {
    "fr": {
        "description": "Fabricant OEM et ODM de vêtements de sport personnalisés pour marques privées, vêtements actifs, uniformes d’équipe, échantillons, emballages et contrôle qualité.",
        "og:title": "Fabricant de vêtements de sport personnalisés | GloryStarWear",
        "og:description": "Développez votre collection avec un partenaire OEM et ODM pour vêtements actifs, tenues d’équipe, échantillons, emballages et contrôle qualité.",
        "twitter:title": "Fabricant de vêtements de sport personnalisés | GloryStarWear",
        "twitter:description": "Vêtements actifs, tenues d’équipe, échantillons, emballages et contrôle qualité pour les marques qui se développent.",
    },
    "es": {
        "description": "Fabricante OEM y ODM de ropa deportiva personalizada para marcas privadas, ropa activa, uniformes de equipo, muestras, embalaje y control de calidad.",
        "og:title": "Fabricante de ropa deportiva personalizada | GloryStarWear",
        "og:description": "Desarrolle su colección con un socio OEM y ODM para ropa activa, uniformes de equipo, muestras, embalaje y control de calidad.",
        "twitter:title": "Fabricante de ropa deportiva personalizada | GloryStarWear",
        "twitter:description": "Ropa activa, uniformes de equipo, muestras, embalaje y control de calidad para marcas en crecimiento.",
    },
    "pt": {
        "description": "Fabricante OEM e ODM de roupa desportiva personalizada para marcas próprias, activewear, equipamentos de equipa, amostras, embalagem e controlo de qualidade.",
        "og:title": "Fabricante de roupa desportiva personalizada | GloryStarWear",
        "og:description": "Desenvolva a sua coleção com um parceiro OEM e ODM para activewear, equipamentos de equipa, amostras, embalagem e controlo de qualidade.",
        "twitter:title": "Fabricante de roupa desportiva personalizada | GloryStarWear",
        "twitter:description": "Activewear, equipamentos de equipa, amostras, embalagem e controlo de qualidade para marcas em crescimento.",
    },
    "ru": {
        "description": "Производитель спортивной одежды OEM и ODM на заказ для собственных брендов: activewear, командная форма, образцы, упаковка и контроль качества.",
        "og:title": "Производитель спортивной одежды на заказ | GloryStarWear",
        "og:description": "Разрабатывайте коллекции с OEM- и ODM-партнёром по activewear, командной форме, образцам, упаковке и контролю качества.",
        "twitter:title": "Производитель спортивной одежды на заказ | GloryStarWear",
        "twitter:description": "Activewear, командная форма, образцы, упаковка и контроль качества для растущих брендов.",
    },
    "zh-cn": {
        "description": "OEM 和 ODM 定制运动服装制造商，支持自有品牌运动服、团队队服、打样、品牌包装和质量控制。",
        "og:title": "定制运动服装制造商 | GloryStarWear",
        "og:description": "为成长中的品牌提供运动服、团队队服、打样、品牌包装和质量控制服务。",
        "twitter:title": "定制运动服装制造商 | GloryStarWear",
        "twitter:description": "支持运动服、团队队服、打样、品牌包装和质量控制的 OEM 与 ODM 服务。",
    },
}


def load_table(name: str) -> dict[str, list[str]]:
    table: dict[str, list[str]] = {}
    for line in (ROOT / "scripts/locales" / name).read_text().splitlines():
        if not line.strip():
            continue
        key, *values = line.split("|")
        table[key] = values
    return table


PAGES = load_table("pages.tsv")
UI = load_table("ui.tsv")


def route_for(key: str) -> str:
    return "/" + (key[:-5] if key.endswith("index") else key + ".html")


def source_for(key: str) -> Path:
    return ROOT / (key + ".html")


def locale_route(key: str, locale: str) -> str:
    return f"/{locale}{route_for(key)}"


class SourceInfo(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.h1 = ""
        self.in_title = False
        self.in_h1 = False
        self.noindex = False
        self.images = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.in_h1 = True
        if tag == "meta" and attrs.get("name") == "robots":
            self.noindex = "noindex" in attrs.get("content", "")
        if tag == "img":
            self.images += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1 += data


SOURCES: dict[str, SourceInfo] = {}
for page_key in PAGES:
    parser = SourceInfo()
    parser.feed(source_for(page_key).read_text())
    SOURCES[page_key] = parser


def load_content(locale: str) -> dict[str, str]:
    path = ROOT / "scripts/locales" / f"content-{locale}.json"
    if not path.exists():
        raise SystemExit(f"Missing {path}. Run scripts/update_locale_content.py first.")
    return json.loads(path.read_text())


def old_h1(locale: str, key: str) -> str | None:
    """Keep the already-reviewed page heading translations when available."""
    path = ROOT / locale / f"{key}.html"
    if not path.exists():
        return None
    match = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", path.read_text())
    if not match:
        return None
    return re.sub(r"<[^>]+>", "", unescape(match.group(1))).strip() or None


def translatable(value: str) -> bool:
    value = unescape(value).strip()
    if len(value) < 2 or not re.search(r"[A-Za-z]", value):
        return False
    if re.fullmatch(r"[A-Z0-9_-]{1,8}", value):
        return False
    if value in {"GloryStarWear", "WhatsApp", "SKU", "MOQ", "OEM", "ODM", "AI", "PDF", "CSV", "SVG", "EPS", "EXW", "FOB", "DDP"}:
        return False
    if "@" in value or value.startswith(("http://", "https://", "mailto:", "tel:")):
        return False
    return True


def translate_text(value: str, content: dict[str, str]) -> str:
    leading = value[: len(value) - len(value.lstrip())]
    trailing = value[len(value.rstrip()) :]
    core = unescape(value.strip())
    translated = content.get(core, core)
    return leading + translated + trailing


def source_key_from_url(current_key: str, href: str) -> str | None:
    if not href or href.startswith(("#", "?", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlsplit(urljoin(ORIGIN + route_for(current_key), href))
    if parsed.netloc and parsed.netloc != "glorystarwears.com":
        return None
    path = parsed.path or "/"
    if path.endswith("/"):
        path += "index.html"
    if not path.endswith(".html"):
        return None
    key = path.lstrip("/")[:-5]
    return key if key in PAGES else None


def localized_href(current_key: str, href: str, locale: str) -> str:
    target = source_key_from_url(current_key, href)
    if target is None:
        return localized_asset_url(current_key, href)
    parsed = urlsplit(href)
    return locale_route(target, locale) + (f"?{parsed.query}" if parsed.query else "") + (f"#{parsed.fragment}" if parsed.fragment else "")


def localized_asset_url(current_key: str, value: str) -> str:
    """Resolve source-relative assets from the locale directory back to root."""
    if not value or value.startswith(("#", "?", "http://", "https://", "//", "data:", "mailto:", "tel:")):
        return value
    parsed = urlsplit(value)
    absolute = urlsplit(urljoin(ORIGIN + route_for(current_key), value))
    if absolute.netloc and absolute.netloc != "glorystarwears.com":
        return value
    path = absolute.path
    if path and (ROOT / path.lstrip("/")).exists():
        return path + (f"?{parsed.query}" if parsed.query else "") + (f"#{parsed.fragment}" if parsed.fragment else "")
    return value


def localized_srcset(current_key: str, value: str) -> str:
    parts = []
    for candidate in value.split(","):
        bits = candidate.strip().split(None, 1)
        if bits:
            bits[0] = localized_asset_url(current_key, bits[0])
        parts.append(" ".join(bits))
    return ", ".join(parts)


TOKEN_RE = re.compile(r"<!--[\s\S]*?-->|<![^>]*>|<script\b[\s\S]*?</script>|<style\b[\s\S]*?</style>|<svg\b[\s\S]*?</svg>|<[^>]+>|[^<]+", re.I)
ATTR_RE = re.compile(r"\b(alt|title|placeholder|aria-label|aria-description|content|src|srcset|imagesrcset|href)=(['\"])(.*?)\2", re.I | re.S)


def replace_tag(tag: str, current_key: str, locale: str, content: dict[str, str]) -> str:
    if tag.startswith("<!--") or tag.startswith("<!") or re.match(r"<\s*(style|svg)\b", tag, re.I):
        return tag
    if re.match(r"<\s*script\b", tag, re.I) and re.search(r"</script\s*>", tag, re.I):
        opening_end = tag.find(">")
        if opening_end > 0:
            return replace_tag(tag[: opening_end + 1], current_key, locale, content) + tag[opening_end + 1 :]
        return tag
    name_match = re.match(r"<\s*([A-Za-z0-9:-]+)", tag)
    name = name_match.group(1).lower() if name_match else ""

    def attr(match):
        attr_name, quote, value = match.groups()
        if attr_name.lower() == "content" and name == "meta":
            meta_key = re.search(r'\b(?:name|property)=["\']([^"\']+)', tag, re.I)
            meta_key = meta_key.group(1).lower() if meta_key else ""
            translatable_meta = {"description", "og:title", "og:description", "og:image:alt", "twitter:title", "twitter:description", "twitter:image:alt"}
            if meta_key not in translatable_meta:
                return match.group(0)
        if attr_name.lower() in ("src", "href"):
            value = localized_asset_url(current_key, value)
        elif attr_name.lower() in ("srcset", "imagesrcset"):
            value = localized_srcset(current_key, value)
        elif translatable(value):
            value = translate_text(value, content)
        return f"{attr_name}={quote}{escape(value, quote=True)}{quote}"

    tag = ATTR_RE.sub(attr, tag)
    if name == "a":
        tag = re.sub(
            r"(\bhref=)(['\"])(.*?)\2",
            lambda m: f"{m.group(1)}{m.group(2)}{localized_href(current_key, m.group(3), locale)}{m.group(2)}",
            tag,
            flags=re.I | re.S,
        )
    else:
        tag = re.sub(
            r"(\b(?:href|src)=)(['\"])(.*?)\2",
            lambda m: f"{m.group(1)}{m.group(2)}{localized_asset_url(current_key, m.group(3))}{m.group(2)}",
            tag,
            flags=re.I | re.S,
        )
    return tag


def localized_alternates(key: str) -> str:
    items = [("en", ORIGIN + route_for(key))]
    items.extend((data[0], ORIGIN + locale_route(key, locale)) for locale, data in LOCALES.items())
    items.append(("x-default", ORIGIN + route_for(key)))
    return "\n".join(f'    <link rel="alternate" hreflang="{lang}" href="{href}">' for lang, href in items)


def override_meta(markup: str, overrides: dict[str, str]) -> str:
    """Replace selected name/property meta content after locale rendering."""
    if not overrides:
        return markup

    def replace_tag(match: re.Match[str]) -> str:
        tag = match.group(0)
        key_match = re.search(r'\b(?:name|property)=["\']([^"\']+)["\']', tag, flags=re.I)
        if not key_match:
            return tag
        value = overrides.get(key_match.group(1).lower())
        if value is None:
            return tag
        return re.sub(
            r'(\bcontent=)(["\'])[^"\']*\2',
            lambda content_match: (
                f'{content_match.group(1)}{content_match.group(2)}'
                f'{escape(value, quote=True)}{content_match.group(2)}'
            ),
            tag,
            count=1,
            flags=re.I,
        )

    return re.sub(r'<meta\b[^>]*>', replace_tag, markup, flags=re.I)


def language_menu_block(locale: str, key: str, content: dict[str, str]) -> str:
    current_name = LOCALES[locale][1]
    current_flag = LOCALES[locale][2]
    current_code = LOCALES[locale][3]
    options = [('en', 'English', '🇺🇸', 'EN', route_for(key))]
    options.extend((data[0], data[1], data[2], data[3], locale_route(key, loc)) for loc, data in LOCALES.items())
    links = []
    for loc, name, flag, code, href in options:
        current = ' aria-current="true"' if loc == LOCALES[locale][0] else ''
        native_names = {"en": "English", "fr": "French", "es": "Spanish", "pt": "Portuguese", "ru": "Russian", "zh-CN": "Chinese (Simplified)"}
        links.append(f'<a href="{href}" data-site-language="{loc}" lang="{loc}"{current}><span aria-hidden="true">{flag}</span><span>{escape(name)}<small>{native_names.get(loc, name)}</small></span><span class="language-check" aria-hidden="true">✓</span></a>')
    label = content.get("Select website language", "Select website language")
    menu_title = "Language / 语言"
    return f'<details class="language-switcher" data-language-switcher><summary class="language-trigger" aria-label="{escape(label)}" aria-controls="site-language-menu"><span data-language-flag aria-hidden="true">{current_flag}</span><span class="language-current-name" data-language-name>{escape(current_name)}</span><span class="language-current-code" data-language-code aria-hidden="true">{LOCALES[locale][3]}</span><i data-lucide="chevron-down" aria-hidden="true"></i></summary><div class="language-menu" id="site-language-menu"><p class="language-menu-title">{escape(menu_title)}</p><div class="language-options">{"".join(links)}</div></div></details>'


def replace_html(source: str, key: str, locale: str, content: dict[str, str]) -> str:
    if "About" in COMPANY_TEXT.get(locale, {}):
        content = {**content, "About": COMPANY_TEXT[locale]["About"]}
    if key == "index":
        content = {**content, **COMPANY_TEXT.get(locale, {})}
    translated_h1 = old_h1(locale, key)
    text_nodes = 0

    def token(match):
        nonlocal text_nodes
        value = match.group(0)
        if value.startswith("<"):
            return replace_tag(value, key, locale, content)
        if not translatable(value):
            return value
        text_nodes += 1
        translated = translate_text(value, content)
        if translated_h1 and text_nodes == 1 and SOURCES[key].h1.strip():
            # The first text node in the page is normally the skip link. The
            # heading is replaced separately below, so do not use this branch.
            pass
        return translated

    rendered = TOKEN_RE.sub(token, source)
    rendered = re.sub(r"(<html\b[^>]*\blang=)(['\"])[^'\"]*\2", rf"\g<1>\g<2>{LOCALES[locale][0]}\g<2>", rendered, count=1, flags=re.I)
    rendered = re.sub(r"(<title>)[\s\S]*?(</title>)", rf"\g<1>{escape(PAGES[key][LOCALE_ORDER.index(locale) + 1])} | GloryStarWear\g<2>", rendered, count=1, flags=re.I)
    if translated_h1:
        rendered = re.sub(r"(<h1\b[^>]*>)[\s\S]*?(</h1>)", lambda m: m.group(1) + escape(translated_h1) + m.group(2), rendered, count=1, flags=re.I)
    canonical = ORIGIN + locale_route(key, locale)
    rendered = re.sub(
        r'(<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\'])[^"\']*(["\'])',
        rf'\g<1>{canonical}\g<2>',
        rendered,
        count=1,
        flags=re.I,
    )
    rendered = re.sub(r'\s*<!-- LOCALE_ALTERNATES_START -->[\s\S]*?<!-- LOCALE_ALTERNATES_END -->', '', rendered)
    rendered = re.sub(r'\s*</head>', f'\n{localized_alternates(key)}\n  </head>', rendered, count=1)
    rendered = re.sub(r'(<meta property="og:url" content=")[^"]+', rf'\g<1>{canonical}', rendered, count=1)
    rendered = re.sub(r'(<meta property="og:locale" content=")[^"]+', rf'\g<1>{LOCALES[locale][0].replace("-", "_")}', rendered, count=1)
    # Replace the English chrome with the same menu component used by the
    # existing site, while keeping the rest of the source DOM intact.
    old_menu = re.search(r'<details class="language-switcher"[\s\S]*?</details>', rendered)
    if old_menu:
        rendered = rendered[:old_menu.start()] + language_menu_block(locale, key, content) + rendered[old_menu.end():]
    ui_index = LOCALE_ORDER.index(locale)
    runtime = {name: values[ui_index] for name, values in UI.items() if len(values) > ui_index}
    runtime.update({"locale": locale, "lang": LOCALES[locale][0]})
    marker = f'<script type="application/json" id="locale-ui">{json.dumps(runtime, ensure_ascii=False)}</script>'
    rendered = re.sub(r'<script\b[^>]*id="locale-ui"[^>]*>[\s\S]*?</script>', marker, rendered, count=1, flags=re.I)
    if 'id="locale-ui"' not in rendered:
        rendered = rendered.replace("</head>", marker + "</head>", 1)
    if key == "index":
        rendered = override_meta(rendered, LOCALE_META.get(locale, {}))
    return rendered


def build() -> None:
    for locale in LOCALE_ORDER:
        content = load_content(locale)
        for key in PAGES:
            destination = ROOT / locale / f"{key}.html"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(replace_html(source_for(key).read_text(), key, locale, content))
    sitemap_root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for locale in LOCALE_ORDER:
        for key in PAGES:
            if SOURCES[key].noindex:
                continue
            node = ET.SubElement(sitemap_root, "url")
            ET.SubElement(node, "loc").text = ORIGIN + locale_route(key, locale)
    ET.indent(sitemap_root)
    ET.ElementTree(sitemap_root).write(ROOT / "sitemap-languages.xml", encoding="utf-8", xml_declaration=True)
    print(f"Built {len(PAGES) * len(LOCALE_ORDER)} complete static language pages.")


if __name__ == "__main__":
    build()

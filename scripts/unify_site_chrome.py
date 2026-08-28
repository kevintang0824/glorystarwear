#!/usr/bin/env python3

"""Replace historical page-specific chrome with the shared site shell."""

from __future__ import annotations

import re
from pathlib import Path

from site_chrome import site_footer_markup, site_header_markup


ROOT = Path(__file__).resolve().parent.parent
IGNORED_PARTS = {
    ".git",
    ".vercel",
    "build",
    "dist",
    "docs",
    "node_modules",
}
HEADER_RE = re.compile(
    r'\s*<header\b[^>]*class="[^"]*\bsite-header\b[^"]*"[\s\S]*?</header>'
    r'\s*<nav\b[^>]*class="[^"]*\bmobile-nav\b[^"]*"[\s\S]*?</nav>'
)
FOOTER_RE = re.compile(
    r'\s*<footer\b[^>]*class="[^"]*\bsite-footer\b[^"]*"[\s\S]*?</footer>'
)


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if IGNORED_PARTS.intersection(path.relative_to(ROOT).parts):
            continue
        source = path.read_text(encoding="utf-8")
        source, header_count = HEADER_RE.subn(
            "\n" + site_header_markup(), source, count=1
        )
        source, footer_count = FOOTER_RE.subn(
            "\n" + site_footer_markup(), source, count=1
        )
        if header_count != 1 or footer_count != 1:
            raise ValueError(
                f"Expected one header/mobile-nav/footer pair in {path}: "
                f"header={header_count}, footer={footer_count}"
            )
        path.write_text(source, encoding="utf-8")
        changed += 1
    print(f"Unified header and footer markup across {changed} HTML pages.")


if __name__ == "__main__":
    main()

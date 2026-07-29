#!/usr/bin/env python3
"""Turn a Google Search Console performance CSV into a concise SEO opportunity report."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ALIASES = {
    "query": {"query", "queries", "top queries", "search query"},
    "page": {"page", "pages", "top pages", "landing page", "url"},
    "clicks": {"clicks"},
    "impressions": {"impressions"},
    "ctr": {"ctr", "click through rate", "click-through rate"},
    "position": {"position", "average position", "avg position"},
}

BRAND_TERMS = ("glorystarwear", "glory star wear", "glory starwear", "glorystarwears")


@dataclass(frozen=True)
class SearchRow:
    query: str
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().replace("_", " "))


def resolve_columns(fieldnames: Iterable[str]) -> dict[str, str]:
    normalized = {normalize_header(name): name for name in fieldnames if name}
    resolved: dict[str, str] = {}
    for target, aliases in ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                resolved[target] = normalized[alias]
                break
    return resolved


def parse_integer(value: str) -> int:
    cleaned = re.sub(r"[^\d.-]", "", value or "")
    return int(round(float(cleaned))) if cleaned else 0


def parse_decimal(value: str) -> float:
    cleaned = re.sub(r"[^\d.-]", "", value or "")
    return float(cleaned) if cleaned else 0.0


def parse_ctr(value: str) -> float:
    raw = (value or "").strip()
    parsed = parse_decimal(raw)
    return parsed / 100 if "%" in raw or parsed > 1 else parsed


def load_rows(path: Path) -> tuple[list[SearchRow], dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        columns = resolve_columns(reader.fieldnames)
        missing = {"clicks", "impressions", "ctr", "position"} - columns.keys()
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        if "query" not in columns and "page" not in columns:
            raise ValueError("CSV must include a Query or Page column")

        rows = [
            SearchRow(
                query=(row.get(columns.get("query", ""), "") or "").strip(),
                page=(row.get(columns.get("page", ""), "") or "").strip(),
                clicks=parse_integer(row.get(columns["clicks"], "")),
                impressions=parse_integer(row.get(columns["impressions"], "")),
                ctr=parse_ctr(row.get(columns["ctr"], "")),
                position=parse_decimal(row.get(columns["position"], "")),
            )
            for row in reader
        ]
    return rows, columns


def is_brand_query(query: str) -> bool:
    normalized = re.sub(r"\s+", " ", query.lower())
    return any(term in normalized for term in BRAND_TERMS)


def expected_ctr(position: float) -> float:
    if position <= 1.5:
        return 0.20
    if position <= 3:
        return 0.10
    if position <= 5:
        return 0.06
    if position <= 10:
        return 0.025
    return 0.0


def display_key(row: SearchRow) -> str:
    if row.query and row.page:
        return f"{row.query} → {row.page}"
    return row.query or row.page


def markdown_table(rows: list[SearchRow], limit: int) -> list[str]:
    lines = [
        "| Query or page | Clicks | Impressions | CTR | Position |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows[:limit]:
        key = display_key(row).replace("|", "\\|")
        lines.append(
            f"| {key} | {row.clicks:,} | {row.impressions:,} | "
            f"{row.ctr:.1%} | {row.position:.1f} |"
        )
    if not rows:
        lines.append("| No matching rows | 0 | 0 | 0.0% | — |")
    return lines


def build_report(rows: list[SearchRow], source: Path, limit: int, minimum_impressions: int) -> str:
    total_clicks = sum(row.clicks for row in rows)
    total_impressions = sum(row.impressions for row in rows)
    weighted_position = (
        sum(row.position * row.impressions for row in rows) / total_impressions
        if total_impressions
        else 0
    )
    overall_ctr = total_clicks / total_impressions if total_impressions else 0

    non_brand = [row for row in rows if not row.query or not is_brand_query(row.query)]
    striking_distance = sorted(
        (
            row
            for row in non_brand
            if row.impressions >= minimum_impressions and 4 <= row.position <= 20
        ),
        key=lambda row: (row.impressions * max(1, 21 - row.position), row.clicks),
        reverse=True,
    )
    ctr_opportunities = sorted(
        (
            row
            for row in non_brand
            if row.impressions >= minimum_impressions
            and row.position <= 10
            and row.ctr < expected_ctr(row.position)
        ),
        key=lambda row: row.impressions * (expected_ctr(row.position) - row.ctr),
        reverse=True,
    )
    zero_click_visibility = sorted(
        (
            row
            for row in non_brand
            if row.impressions >= minimum_impressions and row.clicks == 0
        ),
        key=lambda row: (row.impressions, -row.position),
        reverse=True,
    )
    winners = sorted(
        non_brand,
        key=lambda row: (row.clicks, row.impressions),
        reverse=True,
    )

    report = [
        "# Search Console Opportunity Report",
        "",
        f"Source: `{source}`",
        "",
        "## Baseline",
        "",
        f"- Rows: {len(rows):,}",
        f"- Clicks: {total_clicks:,}",
        f"- Impressions: {total_impressions:,}",
        f"- CTR: {overall_ctr:.1%}",
        f"- Impression-weighted position: {weighted_position:.1f}",
        "",
        "## Striking-distance opportunities",
        "",
        "Prioritize relevant non-brand queries or pages already ranking between positions 4 and 20.",
        "",
        *markdown_table(striking_distance, limit),
        "",
        "## CTR opportunities",
        "",
        "Review title, snippet, intent match, and rich-result eligibility for these visible results.",
        "",
        *markdown_table(ctr_opportunities, limit),
        "",
        "## Visible but receiving no clicks",
        "",
        "Check whether the page answers the query directly or whether another URL should own the intent.",
        "",
        *markdown_table(zero_click_visibility, limit),
        "",
        "## Current non-brand winners",
        "",
        "Protect these pages, add relevant internal links, and use their winning topics to guide evidence-led content.",
        "",
        *markdown_table(winners, limit),
        "",
        "## Review sequence",
        "",
        "1. Confirm the query belongs to the page before editing.",
        "2. Improve the direct answer and evidence before adding more keyword variants.",
        "3. Improve the title or description when ranking is strong but CTR is weak.",
        "4. Link from a relevant winning page to a striking-distance commercial page.",
        "5. Compare the next 28 days with the previous 28 days; do not judge a change after a few days.",
        "",
    ]
    return "\n".join(report)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze a Google Search Console performance CSV."
    )
    parser.add_argument("csv_file", type=Path, help="CSV exported from Search Console")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown output path; otherwise print to standard output",
    )
    parser.add_argument("--limit", type=int, default=15, help="Rows per report section")
    parser.add_argument(
        "--minimum-impressions",
        type=int,
        default=25,
        help="Minimum impressions for opportunity sections",
    )
    args = parser.parse_args()

    if args.limit < 1 or args.minimum_impressions < 1:
        parser.error("--limit and --minimum-impressions must be positive")

    try:
        rows, _ = load_rows(args.csv_file)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    report = build_report(
        rows,
        source=args.csv_file,
        limit=args.limit,
        minimum_impressions=args.minimum_impressions,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

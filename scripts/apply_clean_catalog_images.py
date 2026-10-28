#!/usr/bin/env python3
"""Atomically point the catalog at a complete, verified set of cleaned images.

Results must contain one JSON object per cleanup-manifest object key with a
public ``url``.  The catalog remains untouched unless every supplied source
image has a successful public replacement, so visitors never see a mixture of
watermarked and clean detail photos.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "assets" / "catalog" / "catalog-data.json"
DEFAULT_MANIFEST = ROOT / ".cache" / "catalog-logo-removal" / "manifest.ndjson"
DEFAULT_RESULTS = ROOT / ".cache" / "catalog-logo-removal" / "results.ndjson"


def json_lines(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json_lines(args.manifest)
    results = json_lines(args.results)
    expected = {item["object_key"]: item for item in manifest}
    completed = {item.get("object_key"): item for item in results if item.get("status") == "uploaded"}

    if len(expected) != 38002:
        raise RuntimeError(f"Manifest must contain exactly 38,002 entries, got {len(expected):,}")
    missing = sorted(set(expected) - set(completed))
    invalid = [key for key, item in completed.items() if key in expected and not str(item.get("url", "")).startswith("https://")]
    unexpected = sorted(set(completed) - set(expected))
    if missing or invalid or unexpected:
        raise RuntimeError(
            f"Refusing partial catalog update: missing={len(missing)}, invalid={len(invalid)}, unexpected={len(unexpected)}"
        )

    catalog: dict[str, Any] = json.loads(args.data.read_text(encoding="utf-8"))
    products = {str(product["id"]): product for product in catalog["products"]}
    replacements: dict[tuple[str, str], str] = {}
    primary: dict[str, str] = {}
    for object_key, item in expected.items():
        url = completed[object_key]["url"]
        replacements[(item["product_id"], item["origin_url"])] = url
        if item["is_primary"]:
            primary[item["product_id"]] = url

    if len(primary) != len(products):
        raise RuntimeError(f"Expected a primary replacement for every product, got {len(primary)}")
    changed = 0
    for product_id, product in products.items():
        gallery = product.get("gallery", [])
        if not gallery:
            raise RuntimeError(f"Product has no gallery: {product_id}")
        for entry in gallery:
            key = (product_id, entry.get("src", ""))
            if key not in replacements:
                raise RuntimeError(f"Missing gallery replacement: {product_id} {entry.get('src')}")
            entry["src"] = replacements[key]
        product["cover"] = primary[product_id]
        product["coverRemote"] = ""
        changed += 1

    summary = {"products_updated": changed, "images_replaced": len(replacements), "data": str(args.data)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0
    temp = args.data.with_suffix(".clean.tmp")
    temp.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    temp.replace(args.data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Switch the supplier catalog to a complete local watermark-cleaned image set."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "assets" / "catalog" / "catalog-data.json"
DEFAULT_MANIFEST = ROOT / ".cache" / "catalog-logo-removal" / "manifest.ndjson"
DEFAULT_RESULTS = ROOT / ".cache" / "catalog-logo-removal" / "local-results-v2.ndjson"
DEFAULT_BACKUP = ROOT / ".cache" / "catalog-logo-removal" / "catalog-data.before-local-cleanup.json"


def read_json_lines(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--backup", type=Path, default=DEFAULT_BACKUP)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest = read_json_lines(args.manifest)
    results = read_json_lines(args.results)
    expected = {item["object_key"]: item for item in manifest}
    completed = {item.get("object_key"): item for item in results if item.get("status") == "complete"}
    if len(expected) != 38_002:
        raise RuntimeError(f"Expected 38,002 manifest entries; found {len(expected):,}")
    if len(completed) != 38_002 or set(expected) != set(completed):
        missing = len(set(expected) - set(completed))
        unexpected = len(set(completed) - set(expected))
        raise RuntimeError(f"Refusing partial update: missing={missing}, unexpected={unexpected}")

    catalog: dict[str, Any] = json.loads(args.data.read_text(encoding="utf-8"))
    products = {str(item["id"]): item for item in catalog.get("products", [])}
    replacement_by_source: dict[tuple[str, str], str] = {}
    primary_by_product: dict[str, str] = {}
    for object_key, item in expected.items():
        result = completed[object_key]
        local_src = str(result.get("local_src", ""))
        if not local_src.startswith("../assets/catalog/"):
            raise RuntimeError(f"Invalid local image path for {object_key}: {local_src}")
        local_path = ROOT / local_src.removeprefix("../")
        if not local_path.is_file():
            raise FileNotFoundError(local_path)
        product_id = str(item["product_id"])
        replacement_by_source[(product_id, str(item["origin_url"]))] = local_src
        if item.get("is_primary"):
            primary_by_product[product_id] = local_src

    if set(primary_by_product) != set(products):
        raise RuntimeError(f"Primary image coverage mismatch: {len(primary_by_product)} of {len(products)} products")

    images_updated = 0
    for product_id, product in products.items():
        gallery = product.get("gallery", [])
        if not gallery:
            raise RuntimeError(f"Product has no gallery: {product_id}")
        for entry in gallery:
            key = (product_id, str(entry.get("src", "")))
            if key not in replacement_by_source:
                raise RuntimeError(f"No local image result for {product_id}: {entry.get('src', '')}")
            entry["src"] = replacement_by_source[key]
            entry.pop("clean", None)
            images_updated += 1
        product["cover"] = primary_by_product[product_id]
        product["coverRemote"] = ""

    summary = {
        "products_updated": len(products),
        "images_updated": images_updated,
        "watermarks_removed": sum(bool(item.get("watermark_removed")) for item in completed.values()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.dry_run:
        return 0

    args.backup.parent.mkdir(parents=True, exist_ok=True)
    if not args.backup.exists():
        shutil.copy2(args.data, args.backup)
    temp = args.data.with_suffix(".local-clean.tmp")
    temp.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    temp.replace(args.data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

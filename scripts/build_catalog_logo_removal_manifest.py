#!/usr/bin/env python3
"""Build a deterministic per-image cleanup manifest from the supplied Yupoo export.

The manifest is intentionally written under ``.cache/``: it records every source
file and target key without adding a 38k-line operational file to version control.
It is safe to regenerate, and it does not extract the 37GB archive.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = Path(
    "/Users/kevintang/Documents/Codex/网站抓取任务/"
    "healongsportswear_catalog_2026-09-15_logo_removed.zip"
)
DEFAULT_DATA = ROOT / "assets" / "catalog" / "catalog-data.json"
DEFAULT_OUTPUT = ROOT / ".cache" / "catalog-logo-removal" / "manifest.ndjson"


def read_csv(archive: zipfile.ZipFile, suffix: str) -> list[dict[str, str]]:
    member = next(name for name in archive.namelist() if name.endswith(suffix))
    with archive.open(member) as stream:
        return list(csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline="")))


def numeric_name(value: str) -> int:
    match = re.match(r"\s*(\d+)", value or "")
    return int(match.group(1)) if match else sys.maxsize


def member_lookup(archive: zipfile.ZipFile) -> tuple[dict[str, str], dict[str, list[str]]]:
    by_path: dict[str, str] = {}
    by_name: dict[str, list[str]] = defaultdict(list)
    for member in archive.namelist():
        if "/images/" not in member or member.endswith("/"):
            continue
        # `local_file` is relative to the export root, even where the zip
        # metadata mangled non-ASCII directory characters.
        relative = member.split("/", 1)[1] if "/" in member else member
        by_path[relative] = member
        by_name[Path(member).name].append(member)
    return by_path, by_name


def resolve_member(row: dict[str, str], by_path: dict[str, str], by_name: dict[str, list[str]]) -> str:
    path = row["local_file"]
    if path in by_path:
        return by_path[path]
    candidates = by_name.get(Path(path).name, [])
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError(f"Cannot map export image to archive member: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--key-prefix",
        default="catalog-clean/v1",
        help="R2 object-key prefix only; no public hostname is embedded here.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.archive.is_file():
        raise FileNotFoundError(args.archive)
    catalog: dict[str, Any] = json.loads(args.data.read_text(encoding="utf-8"))
    products = {str(product["id"]): product for product in catalog["products"]}

    with zipfile.ZipFile(args.archive) as archive:
        rows = read_csv(archive, "/images.csv")
        by_path, by_name = member_lookup(archive)

    rows_by_product: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("download_status") != "downloaded":
            continue
        if row["album_id"] not in products:
            raise RuntimeError(f"Export image has no catalog product: {row['album_id']}")
        row["archive_member"] = resolve_member(row, by_path, by_name)
        rows_by_product[row["album_id"]].append(row)

    manifest: list[dict[str, Any]] = []
    for product_id, product in products.items():
        gallery_by_url = {entry.get("src"): entry for entry in product.get("gallery", [])}
        image_rows = sorted(
            rows_by_product.get(product_id, []),
            key=lambda row: (numeric_name(row.get("name", "")), int(row.get("index") or 0)),
        )
        if len(image_rows) != int(product.get("photoCount") or 0):
            raise RuntimeError(f"Unexpected image count for {product_id}: {len(image_rows)}")
        if len(gallery_by_url) != len(image_rows):
            raise RuntimeError(f"Gallery mismatch for {product_id}")

        primary_url = product.get("gallery", [{}])[0].get("src")
        for position, row in enumerate(image_rows, start=1):
            source_url = row["origin_url"]
            if source_url not in gallery_by_url:
                raise RuntimeError(f"Image URL not in catalog gallery: {product_id} {source_url}")
            source = gallery_by_url[source_url]
            suffix = Path(row["local_file"]).suffix.lower() or ".jpg"
            extension = ".webp" if suffix in {".jpg", ".jpeg", ".png", ".webp"} else suffix
            object_key = f"{args.key_prefix.strip('/')}/{product_id}/{position:03d}_{row['photo_id']}{extension}"
            manifest.append(
                {
                    "product_id": product_id,
                    "product_title": product["title"],
                    "gallery_index": source.get("index", position),
                    "is_primary": source_url == primary_url,
                    "archive_member": row["archive_member"],
                    "origin_url": source_url,
                    "width": int(row.get("width") or 0),
                    "height": int(row.get("height") or 0),
                    "object_key": object_key,
                }
            )

    if len(manifest) != 38002:
        raise RuntimeError(f"Expected 38,002 images, found {len(manifest):,}")
    primary_count = sum(item["is_primary"] for item in manifest)
    if primary_count != len(products):
        raise RuntimeError(f"Expected {len(products)} primary images, found {primary_count}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        for item in manifest:
            stream.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp.replace(args.output)
    print(
        json.dumps(
            {
                "manifest": str(args.output),
                "images": len(manifest),
                "products": len(products),
                "primary_images": primary_count,
                "key_prefix": args.key_prefix.strip("/"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

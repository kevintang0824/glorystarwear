#!/usr/bin/env python3
"""Restore Yupoo album cover order for the local supplier catalog.

The source export's gallery rows are presented in reverse upload order.  The
album-level ``cover_url`` identifies the visual selected for that album card;
for the supplied export it maps to the source image named ``1.jpg``.  This
script uses that source metadata to:

1. rebuild local card covers from the selected album cover; and
2. order gallery images by their original numeric filenames (1, 2, 3, ...).

It writes every rebuilt cover to a temporary staging directory before replacing
the current files, so a failed conversion does not leave a mixed cover set.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE = Path("/Users/kevintang/Documents/Codex/网站抓取任务/healongsportswear_catalog_2026-09-15_logo_removed.zip")
DATA_PATH = ROOT / "assets" / "catalog" / "catalog-data.json"
COVERS_DIR = ROOT / "assets" / "catalog" / "covers"


def parent_url(url: str) -> str:
    return url.rsplit("/", 1)[0] if url else ""


def source_name_order(row: dict[str, str]) -> tuple[int, str, int]:
    """Sort `1.jpg`, `2.jpg`, ... before non-numeric legacy names."""
    match = re.match(r"\s*(\d+)", row.get("name", ""))
    numeric = int(match.group(1)) if match else sys.maxsize
    return numeric, row.get("name", ""), int(row.get("index") or 0)


def csv_rows(archive: zipfile.ZipFile, suffix: str) -> list[dict[str, str]]:
    path = next(name for name in archive.namelist() if name.endswith(suffix))
    with archive.open(path) as stream:
        return list(csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline="")))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--covers", type=Path, default=COVERS_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-covers", action="store_true", help="Only update image order in the catalog data.")
    return parser.parse_args()


def convert_cover(archive_path: Path, member: str, output: Path) -> None:
    """Extract one image and produce a JPEG card cover with max edge 480px."""
    with tempfile.TemporaryDirectory(prefix="catalog-cover-source-") as source_dir:
        source = Path(source_dir) / Path(member).name
        with zipfile.ZipFile(archive_path) as archive, archive.open(member) as raw, source.open("wb") as target:
            shutil.copyfileobj(raw, target)
        completed = subprocess.run(
            [
                "sips",
                "--resampleHeightWidthMax",
                "480",
                "--setProperty",
                "format",
                "jpeg",
                str(source),
                "--out",
                str(output),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode:
            raise RuntimeError(f"sips failed for {member}: {completed.stderr.strip()}")


def main() -> int:
    args = parse_args()
    if not args.archive.is_file():
        raise FileNotFoundError(f"Archive not found: {args.archive}")
    if not args.data.is_file():
        raise FileNotFoundError(f"Catalog data not found: {args.data}")

    catalog: dict[str, Any] = json.loads(args.data.read_text(encoding="utf-8"))
    products = {str(product["id"]): product for product in catalog.get("products", [])}

    with zipfile.ZipFile(args.archive) as archive:
        product_rows = csv_rows(archive, "/products.csv")
        image_rows = csv_rows(archive, "/images.csv")
        archive_members = {
            name.split("/", 1)[1]: name
            for name in archive.namelist()
            if "/" in name
        }
        archive_members_by_basename: dict[str, list[str]] = defaultdict(list)
        for member in archive_members.values():
            archive_members_by_basename[Path(member).name].append(member)

    images_by_album: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in image_rows:
        member = archive_members.get(row.get("local_file", ""))
        if not member:
            basename_matches = archive_members_by_basename.get(Path(row.get("local_file", "")).name, [])
            member = basename_matches[0] if len(basename_matches) == 1 else None
        if row.get("download_status") == "downloaded" and member:
            row["_archive_member"] = member
            images_by_album[row["album_id"]].append(row)

    primary_rows: dict[str, dict[str, str]] = {}
    unmatched_primary: list[str] = []
    missing_gallery: list[str] = []
    changed_galleries = 0

    for product_row in product_rows:
        product_id = product_row["album_id"]
        product = products.get(product_id)
        rows = sorted(images_by_album.get(product_id, []), key=source_name_order)
        if not product or not rows:
            continue

        cover_directory = parent_url(product_row.get("cover_url", ""))
        matches = [row for row in rows if parent_url(row.get("origin_url", "")) == cover_directory]
        primary = matches[0] if len(matches) == 1 else None
        if primary:
            primary_rows[product_id] = primary
        else:
            unmatched_primary.append(product_id)

        # Keep the selected album cover first, then preserve the supplier's
        # original numeric sequence for all remaining detail images.
        ordered_rows = ([primary] if primary else []) + [row for row in rows if row is not primary]
        existing_by_source = {item.get("src"): item for item in product.get("gallery", [])}
        ordered_gallery = []
        for index, row in enumerate(ordered_rows, start=1):
            existing = existing_by_source.get(row["origin_url"])
            if not existing:
                missing_gallery.append(product_id)
                break
            ordered_gallery.append({**existing, "index": index})
        else:
            if [item.get("src") for item in product.get("gallery", [])] != [item.get("src") for item in ordered_gallery]:
                changed_galleries += 1
            product["gallery"] = ordered_gallery

    if missing_gallery:
        raise RuntimeError(f"Archive gallery rows missing from catalog data: {sorted(set(missing_gallery))[:10]}")

    current_cover_ids = {path.stem for path in args.covers.glob("*.jpg")}
    rebuild_ids = sorted(primary_rows)
    missing_cover_ids = sorted(product_id for product_id in primary_rows if product_id not in current_cover_ids)
    summary = {
        "catalog_products": len(products),
        "galleries_reordered": changed_galleries,
        "primary_covers_rebuilt": 0 if args.skip_covers else len(rebuild_ids),
        "primary_covers_skipped": len(rebuild_ids) if args.skip_covers else 0,
        "primary_cover_metadata_unmatched": unmatched_primary,
        "local_cover_missing_before_rebuild": missing_cover_ids,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return 0

    if not args.skip_covers:
        args.covers.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="catalog-front-covers-") as staging_dir:
            staging = Path(staging_dir)
            for position, product_id in enumerate(rebuild_ids, start=1):
                output = staging / f"{product_id}.jpg"
                convert_cover(args.archive, primary_rows[product_id]["_archive_member"], output)
                if position % 200 == 0 or position == len(rebuild_ids):
                    print(f"Prepared {position}/{len(rebuild_ids)} primary covers", flush=True)
            for product_id in rebuild_ids:
                (staging / f"{product_id}.jpg").replace(args.covers / f"{product_id}.jpg")

    args.data.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Rebuilt covers and wrote catalog data.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

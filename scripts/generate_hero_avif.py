#!/usr/bin/env python3

import argparse
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
IGNORED_PATH_PARTS = {
    ".git",
    ".local-backups",
    ".vercel",
    ".wrangler",
    "build",
    "dist",
    "node_modules",
}


class PageImageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        attributes = dict(attrs)
        self.images.append(attributes)


def jpeg_files(include_all_images):
    files = set()
    html_files = (
        path
        for path in ROOT.rglob("*.html")
        if not IGNORED_PATH_PARTS.intersection(path.relative_to(ROOT).parts)
    )
    for html_file in html_files:
        parser = PageImageParser()
        parser.feed(html_file.read_text(encoding="utf-8"))
        for image in parser.images:
            if not include_all_images and image.get("fetchpriority") != "high":
                continue
            references = [image.get("src", "")]
            references.extend(
                candidate.strip().split()[0]
                for candidate in image.get("srcset", "").split(",")
                if candidate.strip()
            )
            for reference in references:
                if reference.lower().endswith((".jpg", ".jpeg")):
                    files.add((html_file.parent / reference).resolve())
    return sorted(files)


def encode_avif(job, crf, preset):
    source, target = job
    command = [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-map_metadata",
        "-1",
        "-frames:v",
        "1",
        "-c:v",
        "libsvtav1",
        "-crf",
        str(crf),
        "-preset",
        str(preset),
        "-pix_fmt",
        "yuv420p10le",
        str(target),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        target.unlink(missing_ok=True)
        return source, target, result.stderr.strip()
    return source, target, ""


def main():
    argument_parser = argparse.ArgumentParser(
        description="Generate AVIF counterparts for JPEG images used by the website."
    )
    argument_parser.add_argument(
        "--all-images",
        action="store_true",
        help="Process every JPEG image instead of only high-priority hero images.",
    )
    argument_parser.add_argument("--force", action="store_true")
    argument_parser.add_argument("--dry-run", action="store_true")
    argument_parser.add_argument("--workers", type=int, default=2)
    argument_parser.add_argument("--crf", type=int, default=38)
    argument_parser.add_argument("--preset", type=int, default=8)
    arguments = argument_parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("ffmpeg is required to generate AVIF files", file=sys.stderr)
        return 1

    jobs = []
    for source in jpeg_files(arguments.all_images):
        if not source.exists():
            print(f"missing source image: {source.relative_to(ROOT)}", file=sys.stderr)
            return 1
        target = source.with_suffix(".avif")
        if arguments.force or not target.exists() or source.stat().st_mtime > target.stat().st_mtime:
            jobs.append((source, target))

    if arguments.dry_run:
        for source, target in jobs:
            print(f"{source.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
        print(f"pending={len(jobs)}")
        return 0

    failures = []
    generated = []
    with ThreadPoolExecutor(max_workers=max(1, arguments.workers)) as pool:
        futures = [
            pool.submit(encode_avif, job, arguments.crf, arguments.preset)
            for job in jobs
        ]
        for future in as_completed(futures):
            source, target, error = future.result()
            if error:
                failures.append((source, error))
            else:
                generated.append((source, target))

    for source, error in failures:
        print(f"failed {source.relative_to(ROOT)}: {error}", file=sys.stderr)

    source_bytes = sum(source.stat().st_size for source, target in generated)
    target_bytes = sum(target.stat().st_size for source, target in generated)
    print(
        f"generated={len(generated)} failed={len(failures)} "
        f"source_bytes={source_bytes} avif_bytes={target_bytes}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

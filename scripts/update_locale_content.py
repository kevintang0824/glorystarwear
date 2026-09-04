#!/usr/bin/env python3
"""Create checked-in static copy maps with an offline Argos model.

The model archives live outside the repository. This script is a maintainer
tool; the normal build only consumes the resulting JSON maps and makes no
network or model calls.
"""
from __future__ import annotations

from html import unescape
from pathlib import Path
import json
import re
import sys

import ctranslate2
import sentencepiece as spm

ROOT = Path(__file__).resolve().parent.parent
MODEL_ROOT = Path("/tmp/glorystar-argos-models/extracted")
MODEL_DIRS = {
    "fr": "translate-en_fr-1_9",
    "es": "en_es",
    "pt": "translate-en_pt-1_9",
    "ru": "translate-en_ru-1_9",
    "zh-cn": "translate-en_zh-1_9",
}
TOKEN_RE = re.compile(r"<!--[\s\S]*?-->|<![^>]*>|<script\b[\s\S]*?</script>|<style\b[\s\S]*?</style>|<svg\b[\s\S]*?</svg>|<[^>]+>|[^<]+", re.I)
ATTR_RE = re.compile(r"\b(alt|title|placeholder|aria-label|aria-description|content)=(['\"])(.*?)\2", re.I | re.S)


def translatable(value: str) -> bool:
    value = unescape(value).strip()
    if len(value) < 2 or not re.search(r"[A-Za-z]", value):
        return False
    if "@" in value or value.startswith(("http://", "https://", "mailto:", "tel:")):
        return False
    if re.fullmatch(r"[A-Z0-9_-]{1,8}", value):
        return False
    if value in {"GloryStarWear", "WhatsApp", "SKU", "MOQ", "OEM", "ODM", "AI", "PDF", "CSV", "SVG", "EPS", "EXW", "FOB", "DDP"}:
        return False
    return True


def collect() -> list[str]:
    values: set[str] = set()
    routes = [*ROOT.glob("*.html"), *ROOT.glob("products/*.html"), *ROOT.glob("resources/*.html"), *ROOT.glob("blog/*.html")]
    for path in routes:
        source = path.read_text()
        for token in TOKEN_RE.findall(source):
            if token.startswith("<"):
                if token.startswith(("<!--", "<!", "<script", "<style", "<svg")):
                    continue
                for match in ATTR_RE.finditer(token):
                    if translatable(match.group(3)):
                        values.add(unescape(match.group(3)).strip())
            elif translatable(token):
                values.add(unescape(token).strip())
    return sorted(values, key=lambda value: (len(value), value))


def chunks(text: str, limit: int = 260) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = re.split(r"(?<=[.!?])\s+", text)
    result: list[str] = []
    for part in parts:
        if len(part) <= limit:
            result.append(part)
            continue
        bits = re.split(r"(?<=[,;:])\s+", part)
        current = ""
        for bit in bits:
            if current and len(current) + 1 + len(bit) > limit:
                result.append(current)
                current = bit
            else:
                current = f"{current} {bit}".strip()
        if current:
            result.append(current)
    return result


def translate_values(values: list[str], model_dir: Path) -> dict[str, str]:
    processor = spm.SentencePieceProcessor(model_file=str(model_dir / "sentencepiece.model"))
    translator = ctranslate2.Translator(str(model_dir / "model"), device="cpu", inter_threads=8)
    result: dict[str, str] = {}
    tasks: list[tuple[str, list[str]]] = []
    for value in values:
        parts = chunks(value)
        tasks.extend((value, [part]) for part in parts)
    for start in range(0, len(tasks), 128):
        batch = tasks[start : start + 128]
        tokens = [processor.encode(parts[0], out_type=str) for _, parts in batch]
        outputs = translator.translate_batch(tokens, beam_size=1, replace_unknowns=True, max_batch_size=128)
        for (original, _), output in zip(batch, outputs):
            value = "".join(output.hypotheses[0]).replace("▁", " ").strip()
            result.setdefault(original, "")
            result[original] += (" " if result[original] else "") + value
    return result


def main() -> None:
    values = collect()
    print(f"Collected {len(values)} unique visible strings.")
    requested = sys.argv[1:] or list(MODEL_DIRS)
    for locale in requested:
        if locale not in MODEL_DIRS:
            raise SystemExit(f"Unknown locale {locale}; choose from {', '.join(MODEL_DIRS)}")
        directory = MODEL_DIRS[locale]
        path = MODEL_ROOT / directory
        if not path.exists():
            raise SystemExit(f"Missing model directory: {path}")
        destination = ROOT / "scripts/locales" / f"content-{locale}.json"
        existing = json.loads(destination.read_text()) if destination.exists() else {}
        missing = [value for value in values if value not in existing]
        print(f"{locale}: translating {len(missing)} newly discovered strings.")
        output = translate_values(missing, path)
        existing.update(output)
        destination.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n")
        print(f"Wrote {destination} ({len(existing)} strings).")


if __name__ == "__main__":
    main()

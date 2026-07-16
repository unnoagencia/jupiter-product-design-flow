#!/usr/bin/env python3
"""Validate persistent design-flow artifacts for one feature."""

from __future__ import annotations

import argparse
import json
import re
import zlib
from pathlib import Path
from typing import Optional, Tuple

REQUIRED_HEADINGS = {
    "DESIGN_BRIEF.md": [
        "## Problema", "## Usuário principal e JTBD", "## Resultado de sucesso",
        "## Escopo", "## Fora de escopo", "## Marca e direção visual", "## Restrições",
    ],
    "TASKS.md": ["## Implementação", "## QA"],
    "DESIGN_REVIEW.md": [
        "## Evidências", "## Síntese", "## Must fix", "## Should fix",
        "## Could improve", "## O que preservar",
    ],
    "INFORMATION_ARCHITECTURE.md": [
        "## Mapa de rotas e views", "## Modelo de navegação", "## Fluxos críticos",
    ],
}

PLACEHOLDER_RE = re.compile(
    r"TODO|\[(?:Feature|slug|Problema|Incluído|Excluído|nome|arquivo|nota|"
    r"Prioridade|Fluxo|condição|resultado|Hipótese|identificador|Data)\b[^\]]*\]",
    re.IGNORECASE,
)
KNOWN_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
PNG_ALLOWED_DEPTHS = {
    0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8},
    4: {8, 16}, 6: {8, 16},
}
MAX_FILE_BYTES = 25_000_000
MAX_CHUNK_BYTES = 25_000_000
MAX_PIXELS = 50_000_000
MAX_DECODED_BYTES = 128_000_000


def _has_heading(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def _read_markdown(path: Path, errors: list[str]) -> Optional[str]:
    if path.exists() and not path.is_file():
        errors.append(f"artifact path is not a file: {path.name}")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read {path.name}: {exc.__class__.__name__}")
        return None


def _validate_markdown(path: Path, errors: list[str]) -> None:
    text = _read_markdown(path, errors)
    if text is None:
        return
    if len(text.strip()) < 120:
        errors.append(f"artifact is suspiciously short: {path.name}")
    for heading in REQUIRED_HEADINGS.get(path.name, []):
        if not _has_heading(text, heading):
            errors.append(f"{path.name}: missing heading {heading!r}")
    if PLACEHOLDER_RE.search(text):
        errors.append(f"{path.name}: contains unfilled template placeholders or TODO markers")


def _valid_chunk_type(chunk_type: bytes) -> bool:
    return (
        len(chunk_type) == 4
        and all((65 <= byte <= 90) or (97 <= byte <= 122) for byte in chunk_type)
        and 65 <= chunk_type[2] <= 90  # PNG reserved bit must be zero (uppercase).
    )


def png_dimensions(path: Path) -> Optional[Tuple[int, int]]:
    """Return dimensions only after bounded validation of a non-interlaced PNG."""
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if not data.startswith(PNG_SIGNATURE):
        return None

    position = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = None
    compression = filtering = interlace = None
    idat = bytearray()
    has_palette = seen_ihdr = seen_idat = seen_iend = False
    idat_closed = False

    while position < len(data):
        if position + 12 > len(data):
            return None
        length = int.from_bytes(data[position:position + 4], "big")
        if length > MAX_CHUNK_BYTES:
            return None
        chunk_type = data[position + 4:position + 8]
        if not _valid_chunk_type(chunk_type):
            return None
        chunk_end = position + 12 + length
        if chunk_end > len(data):
            return None
        chunk_data = data[position + 8:position + 8 + length]
        expected_crc = int.from_bytes(data[position + 8 + length:chunk_end], "big")
        if (zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF) != expected_crc:
            return None

        is_critical = 65 <= chunk_type[0] <= 90
        if is_critical and chunk_type not in {b"IHDR", b"PLTE", b"IDAT", b"IEND"}:
            return None

        if chunk_type == b"IHDR":
            if seen_ihdr or position != len(PNG_SIGNATURE) or length != 13:
                return None
            seen_ihdr = True
            width = int.from_bytes(chunk_data[0:4], "big")
            height = int.from_bytes(chunk_data[4:8], "big")
            bit_depth, color_type, compression, filtering, interlace = chunk_data[8:13]
        elif not seen_ihdr:
            return None
        elif chunk_type == b"PLTE":
            if has_palette or seen_idat or color_type in {0, 4}:
                return None
            if length == 0 or length % 3 != 0 or length > 768:
                return None
            if color_type == 3 and length // 3 > (1 << bit_depth):
                return None
            has_palette = True
        elif chunk_type == b"IDAT":
            if idat_closed:
                return None
            if color_type == 3 and not has_palette:
                return None
            seen_idat = True
            if len(idat) + length > MAX_FILE_BYTES:
                return None
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            if length != 0 or not seen_idat:
                return None
            seen_iend = True
            position = chunk_end
            break
        elif seen_idat:
            idat_closed = True

        position = chunk_end

    if not seen_ihdr or not seen_idat or not seen_iend or position != len(data):
        return None
    if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
        return None
    if width * height > MAX_PIXELS:
        return None
    if color_type not in PNG_CHANNELS or bit_depth not in PNG_ALLOWED_DEPTHS[color_type]:
        return None
    if compression != 0 or filtering != 0 or interlace != 0:
        return None
    if color_type == 3 and not has_palette:
        return None
    if not idat:
        return None

    bits_per_pixel = PNG_CHANNELS[color_type] * bit_depth
    row_bytes = (width * bits_per_pixel + 7) // 8
    expected_size = height * (1 + row_bytes)
    if expected_size <= 0 or expected_size > MAX_DECODED_BYTES:
        return None

    try:
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(bytes(idat), expected_size + 1)
        if len(decoded) > expected_size or decoder.unconsumed_tail:
            return None
        decoded += decoder.flush(expected_size + 1 - len(decoded))
    except (zlib.error, ValueError):
        return None
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        return None
    if len(decoded) != expected_size:
        return None
    for row in range(height):
        if decoded[row * (row_bytes + 1)] not in {0, 1, 2, 3, 4}:
            return None

    return width, height


def _validate_screenshots(directory: Path, errors: list[str]) -> int:
    if directory.exists() and not directory.is_dir():
        errors.append("screenshots path exists but is not a directory")
        return 0
    if not directory.is_dir():
        return 0
    try:
        candidates = list(directory.iterdir())
    except OSError as exc:
        errors.append(f"cannot inspect screenshots directory: {exc.__class__.__name__}")
        return 0

    valid = 0
    for path in candidates:
        suffix = path.suffix.lower()
        if suffix not in KNOWN_IMAGE_SUFFIXES:
            continue
        if not path.is_file():
            errors.append(f"visual evidence is not a readable file: {path.name}")
            continue
        if suffix != ".png":
            errors.append(f"unsupported visual evidence format: {path.name}; use PNG")
            continue
        if not png_dimensions(path):
            errors.append(f"invalid, unsafe, or corrupt PNG visual evidence: {path.name}")
            continue
        valid += 1
    return valid


def validate(feature_dir: Path, require_review: bool) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not feature_dir.is_dir():
        return {"ok": False, "feature_dir": str(feature_dir), "errors": ["feature directory does not exist"], "warnings": []}

    required = ["DESIGN_BRIEF.md", "TASKS.md"] + (["DESIGN_REVIEW.md"] if require_review else [])
    for name in required:
        if not (feature_dir / name).exists():
            errors.append(f"missing required file: {name}")
    for name in REQUIRED_HEADINGS:
        path = feature_dir / name
        if path.exists():
            _validate_markdown(path, errors)

    review = feature_dir / "DESIGN_REVIEW.md"
    if review.exists() and _validate_screenshots(feature_dir / "screenshots", errors) == 0:
        errors.append("DESIGN_REVIEW.md exists but screenshots/ has no valid PNG visual evidence")

    return {"ok": not errors, "feature_dir": str(feature_dir), "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_dir", type=Path)
    parser.add_argument("--require-review", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(args.feature_dir, args.require_review)
    except Exception as exc:  # JSON mode must never leak a traceback.
        result = {"ok": False, "feature_dir": str(args.feature_dir), "errors": [f"unexpected validator error: {exc.__class__.__name__}"], "warnings": []}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if result["ok"] else "FAIL", result["feature_dir"])
        for item in result["errors"]:
            print("ERROR:", item)
        for item in result["warnings"]:
            print("WARN:", item)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

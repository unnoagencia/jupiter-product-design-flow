#!/usr/bin/env python3
"""Validate persistent design-flow artifacts for one feature."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_HEADINGS = {
    "DESIGN_BRIEF.md": [
        "## Problema",
        "## Usuário principal e JTBD",
        "## Resultado de sucesso",
        "## Escopo",
        "## Fora de escopo",
        "## Marca e direção visual",
        "## Restrições",
    ],
    "TASKS.md": ["## Implementação", "## QA"],
    "DESIGN_REVIEW.md": [
        "## Evidências",
        "## Síntese",
        "## Must fix",
        "## Should fix",
        "## Could improve",
        "## O que preservar",
    ],
}


def validate(feature_dir: Path, require_review: bool) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not feature_dir.is_dir():
        return {
            "ok": False,
            "feature_dir": str(feature_dir),
            "errors": ["feature directory does not exist"],
            "warnings": [],
        }

    files = ["DESIGN_BRIEF.md", "TASKS.md"]
    if require_review:
        files.append("DESIGN_REVIEW.md")

    for name in files:
        path = feature_dir / name
        if not path.is_file():
            errors.append(f"missing required file: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < 120:
            errors.append(f"artifact is suspiciously short: {name}")
        for heading in REQUIRED_HEADINGS.get(name, []):
            if heading not in text:
                errors.append(f"{name}: missing heading {heading!r}")
        if "TODO" in text or "[Feature]" in text or "[Problema" in text:
            warnings.append(f"{name}: contains template placeholders or TODO markers")

    ia = feature_dir / "INFORMATION_ARCHITECTURE.md"
    if ia.exists():
        text = ia.read_text(encoding="utf-8")
        for heading in ["## Mapa de rotas e views", "## Modelo de navegação", "## Fluxos críticos"]:
            if heading not in text:
                errors.append(f"INFORMATION_ARCHITECTURE.md: missing heading {heading!r}")

    review = feature_dir / "DESIGN_REVIEW.md"
    screenshots = feature_dir / "screenshots"
    if review.exists():
        image_count = 0
        if screenshots.is_dir():
            image_count = sum(1 for p in screenshots.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
        if image_count == 0:
            errors.append("DESIGN_REVIEW.md exists but screenshots/ has no visual evidence")

    return {
        "ok": not errors,
        "feature_dir": str(feature_dir),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("feature_dir", type=Path)
    parser.add_argument("--require-review", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = validate(args.feature_dir, args.require_review)
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

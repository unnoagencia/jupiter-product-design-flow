#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError as exc:  # pragma: no cover - runtime diagnostic
    raise SystemExit("Pillow is required: install it in an isolated environment before export") from exc

VIEWPORT = (1080, 1350)
REMOTE_RE = re.compile(r"^(?:https?:)?//", re.I)
ATTR_RE = re.compile(r"(?:src|href)\s*=\s*['\"]([^'\"]+)['\"]", re.I)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)


class SlideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slides: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        classes = values.get("class", "").split()
        slide_id = values.get("data-slide", "").strip()
        if tag in {"section", "article", "div"} and "slide" in classes and slide_id:
            self.slides.append(slide_id)


def discover_slides(html_path: Path) -> list[str]:
    parser = SlideParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    duplicates = sorted({item for item in parser.slides if parser.slides.count(item) > 1})
    if duplicates:
        raise ValueError(f"duplicate data-slide ids: {', '.join(duplicates)}")
    if not parser.slides:
        raise ValueError("no .slide elements with data-slide were found")
    return parser.slides


def collect_local_dependencies(html_path: Path, project_root: Path | None = None) -> list[Path]:
    text = html_path.read_text(encoding="utf-8")
    root = (project_root or html_path.parent).resolve()
    raw = ATTR_RE.findall(text) + CSS_URL_RE.findall(text)
    dependencies: list[Path] = []
    remote: list[str] = []
    for value in raw:
        value = value.strip()
        if not value or value.startswith(("#", "data:", "javascript:")):
            continue
        if REMOTE_RE.match(value):
            remote.append(value)
            continue
        clean = value.split("?", 1)[0].split("#", 1)[0]
        path = (html_path.parent / clean).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"HTML dependency escapes the project directory: {value}")
        if path not in dependencies:
            dependencies.append(path)
    if remote:
        raise ValueError("remote HTML dependencies are not allowed: " + ", ".join(remote))
    missing = [str(path) for path in dependencies if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing local HTML dependencies: " + ", ".join(missing))
    return dependencies


def render_slide(html_path: Path, slide_id: str, output: Path, wait_ms: int) -> None:
    query = urlencode({"export": "1", "slide": slide_id})
    url = f"{html_path.resolve().as_uri()}?{query}"
    command = [
        "npx",
        "playwright",
        "screenshot",
        "--browser",
        "chromium",
        "--viewport-size",
        f"{VIEWPORT[0]},{VIEWPORT[1]}",
        "--wait-for-timeout",
        str(wait_ms),
        url,
        str(output),
    ]
    subprocess.run(command, check=True)
    with Image.open(output) as image:
        if image.size != VIEWPORT:
            raise ValueError(f"wrong dimensions for {output.name}: {image.size}")
        if image.format != "PNG":
            raise ValueError(f"wrong format for {output.name}: {image.format}")


def make_contact_sheet(outputs: list[Path], output: Path) -> None:
    columns = 2
    thumb = (324, 405)
    gap = 24
    margin = 24
    rows = (len(outputs) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (margin * 2 + columns * thumb[0] + gap, margin * 2 + rows * thumb[1] + (rows - 1) * gap),
        "#D8D9DC",
    )
    draw = ImageDraw.Draw(canvas)
    for index, path in enumerate(outputs):
        row, column = divmod(index, columns)
        x = margin + column * (thumb[0] + gap)
        y = margin + row * (thumb[1] + gap)
        with Image.open(path) as source:
            preview = ImageOps.fit(source.convert("RGB"), thumb, method=Image.Resampling.LANCZOS)
        canvas.paste(preview, (x, y))
        draw.rectangle((x, y, x + thumb[0] - 1, y + thumb[1] - 1), outline="#B9BBC0", width=1)
    canvas.save(output, format="PNG", optimize=True)


def package_project(
    project: Path,
    html_path: Path,
    outputs: list[Path],
    preview: Path,
    zip_name: str,
    dependencies: list[Path] | None = None,
) -> Path:
    candidates = [html_path, project / "LEGENDA.txt", project / "README.md", preview, *outputs]
    candidates.extend(dependencies or [])
    assets = project / "assets"
    if assets.is_dir():
        candidates.extend(sorted(path for path in assets.rglob("*") if path.is_file()))
    export_script = project / "scripts" / "export.py"
    if export_script.is_file():
        candidates.append(export_script)

    unique: list[Path] = []
    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if path.is_file() and resolved not in seen:
            unique.append(path)
            seen.add(resolved)

    output = project / zip_name
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in unique:
            archive.write(path, path.resolve().relative_to(project.resolve()))

    with zipfile.ZipFile(output) as archive:
        broken = archive.testzip()
        if broken:
            raise ValueError(f"corrupt ZIP entry: {broken}")
        names = set(archive.namelist())
        required_paths = [html_path, preview, *outputs, *(dependencies or [])]
        required = {str(path.resolve().relative_to(project.resolve())) for path in required_paths}
        missing = sorted(required - names)
        if missing:
            raise ValueError("missing ZIP entries: " + ", ".join(missing))
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and package a local HTML carousel")
    parser.add_argument("project", type=Path, help="carousel project directory")
    parser.add_argument("--html", default="index.html", help="HTML file relative to project")
    parser.add_argument("--expected", type=int, default=8, help="expected slide count")
    parser.add_argument("--wait-ms", type=int, default=500, help="wait before each screenshot")
    parser.add_argument("--zip", dest="zip_name", default="carousel.zip", help="output ZIP filename")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.resolve()
    html_path = (project / args.html).resolve()
    if not html_path.is_file():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    if not html_path.is_relative_to(project):
        raise ValueError("--html must resolve inside the project directory")
    if args.expected < 1:
        raise ValueError("--expected must be positive")
    if args.wait_ms < 0:
        raise ValueError("--wait-ms cannot be negative")

    slides = discover_slides(html_path)
    if len(slides) != args.expected:
        raise ValueError(f"expected {args.expected} slides, found {len(slides)}")
    dependencies = collect_local_dependencies(html_path, project)

    output_dir = project / "slides"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, slide_id in enumerate(slides, start=1):
        output = output_dir / f"slide-{index:02d}.png"
        render_slide(html_path, slide_id, output, args.wait_ms)
        outputs.append(output)

    preview = project / "preview-contact-sheet.png"
    make_contact_sheet(outputs, preview)
    package = package_project(project, html_path, outputs, preview, args.zip_name, dependencies)

    print(f"slides={len(outputs)}")
    print(f"dependencies={len(dependencies)}")
    print(f"preview={preview}")
    print(f"zip={package}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

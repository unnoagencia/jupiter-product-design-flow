#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlencode, urlparse

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError as exc:  # pragma: no cover - runtime diagnostic
    raise SystemExit("Pillow is required: install it in an isolated environment before export") from exc

VIEWPORT = (1080, 1350)
REMOTE_RE = re.compile(r"^(?:https?:)?//", re.I)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\(\s*)?['\"]?([^'\"\s;)]+)", re.I)
JS_IMPORT_RE = re.compile(
    r"(?:\bimport\s*(?:[^'\"]*?\sfrom\s*)?|\bexport\s+[^'\"]*?\sfrom\s*)['\"]([^'\"]+)['\"]",
    re.I,
)
JS_DYNAMIC_IMPORT_RE = re.compile(r"\bimport\(\s*['\"]([^'\"]+)['\"]\s*\)", re.I)
JS_NEW_URL_RE = re.compile(r"\bnew\s+URL\(\s*['\"]([^'\"]+)['\"]\s*,\s*import\.meta\.url\s*\)", re.I)
READY_SELECTOR = '[data-carousel-ready="true"]'
READY_SCRIPT = """
<script data-carousel-readiness>
(() => {
  async function markReady() {
    try {
      await document.fonts.ready;
      await Promise.all(Array.from(document.fonts).map((font) => font.load()));
      const images = Array.from(document.images);
      await Promise.all(images.map((image) => image.decode()));
      if (images.some((image) => !image.complete || image.naturalWidth === 0)) {
        throw new Error('one or more images failed to load');
      }
      document.documentElement.dataset.carouselReady = 'true';
    } catch (error) {
      document.documentElement.dataset.carouselReady = 'error';
      document.documentElement.dataset.carouselError = String(error);
      console.error('carousel readiness failed', error);
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markReady, { once: true });
  } else {
    markReady();
  }
})();
</script>
""".strip()


class SlideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.slides: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        classes = values.get("class", "").split()
        slide_id = values.get("data-slide", "").strip()
        if tag in {"section", "article", "div"} and "slide" in classes and slide_id:
            self.slides.append(slide_id)


class DependencyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def add(self, value: str | None) -> None:
        if value and value.strip():
            self.references.append(value.strip())

    def add_srcset(self, value: str | None) -> None:
        if not value:
            return
        for candidate in value.split(","):
            url = candidate.strip().split()[0] if candidate.strip() else ""
            self.add(url)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        if tag in {"img", "script", "iframe", "embed", "input"}:
            self.add(values.get("src"))
        elif tag in {"video", "audio", "source", "track"}:
            self.add(values.get("src"))
            self.add(values.get("poster"))
        elif tag == "object":
            self.add(values.get("data"))
        elif tag == "link":
            rel = {item.lower() for item in values.get("rel", "").split()}
            if rel & {"stylesheet", "icon", "preload", "modulepreload", "manifest"}:
                self.add(values.get("href"))
        self.add_srcset(values.get("srcset"))


def discover_slides(html_path: Path) -> list[str]:
    parser = SlideParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    duplicates = sorted({item for item in parser.slides if parser.slides.count(item) > 1})
    if duplicates:
        raise ValueError(f"duplicate data-slide ids: {', '.join(duplicates)}")
    if not parser.slides:
        raise ValueError("no .slide elements with data-slide were found")
    return parser.slides


def is_ignorable_reference(value: str) -> bool:
    return not value or value.startswith(("#", "data:", "javascript:", "mailto:", "tel:", "blob:"))


def resolve_reference(value: str, source: Path, root: Path) -> Path | None:
    value = value.strip()
    if is_ignorable_reference(value):
        return None
    if REMOTE_RE.match(value):
        raise ValueError(f"remote dependency is not allowed: {value}")
    parsed = urlparse(value)
    if parsed.scheme and parsed.scheme != "file":
        raise ValueError(f"unsupported dependency scheme: {value}")
    clean = unquote(parsed.path).strip()
    path = Path(clean).resolve() if parsed.scheme == "file" else (source.parent / clean).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"dependency escapes the project directory: {value}")
    if not path.is_file():
        raise FileNotFoundError(f"missing local dependency: {path}")
    return path


def extract_references(path: Path) -> list[str]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix in {".html", ".htm"}:
        parser = DependencyParser()
        parser.feed(text)
        return parser.references + CSS_URL_RE.findall(text)
    if suffix == ".css":
        return CSS_IMPORT_RE.findall(text) + CSS_URL_RE.findall(text)
    if suffix in {".js", ".mjs", ".cjs"}:
        return JS_IMPORT_RE.findall(text) + JS_DYNAMIC_IMPORT_RE.findall(text) + JS_NEW_URL_RE.findall(text)
    return []


def collect_local_dependencies(html_path: Path, project_root: Path | None = None) -> list[Path]:
    root = (project_root or html_path.parent).resolve()
    html_path = html_path.resolve()
    if not html_path.is_relative_to(root):
        raise ValueError("HTML file must stay inside the project directory")
    queue: list[Path] = [html_path]
    visited: set[Path] = set()
    dependencies: list[Path] = []
    while queue:
        source = queue.pop(0)
        if source in visited:
            continue
        visited.add(source)
        for value in extract_references(source):
            dependency = resolve_reference(value, source, root)
            if dependency is None:
                continue
            if dependency != html_path and dependency not in dependencies:
                dependencies.append(dependency)
            if dependency.suffix.lower() in {".html", ".htm", ".css", ".js", ".mjs", ".cjs"}:
                queue.append(dependency)
    return dependencies


def make_ready_html(html_path: Path) -> Path:
    text = html_path.read_text(encoding="utf-8")
    if "data-carousel-readiness" in text:
        return html_path
    marker = "</body>"
    injected = text.replace(marker, READY_SCRIPT + "\n" + marker, 1) if marker in text else text + "\n" + READY_SCRIPT
    output = html_path.parent / ".carousel-export.html"
    output.write_text(injected, encoding="utf-8")
    return output


def dependencies_from_har(har_path: Path, project: Path) -> list[Path]:
    if not har_path.is_file():
        raise FileNotFoundError(f"Playwright did not create HAR evidence: {har_path}")
    payload = json.loads(har_path.read_text(encoding="utf-8"))
    dependencies: list[Path] = []
    for entry in payload.get("log", {}).get("entries", []):
        request_url = entry.get("request", {}).get("url", "")
        parsed = urlparse(request_url)
        if parsed.scheme in {"http", "https"}:
            raise ValueError(f"remote request detected during render: {request_url}")
        if parsed.scheme == "file":
            path = Path(unquote(parsed.path)).resolve()
            if not path.is_relative_to(project.resolve()):
                raise ValueError(f"runtime dependency escapes the project directory: {request_url}")
            if path.name == ".carousel-export.html":
                continue
            if not path.is_file():
                raise FileNotFoundError(f"runtime dependency is missing: {path}")
            if path not in dependencies:
                dependencies.append(path)
    return dependencies


def render_slide(html_path: Path, project: Path, slide_id: str, output: Path, wait_ms: int) -> list[Path]:
    query = urlencode({"export": "1", "slide": slide_id})
    url = f"{html_path.resolve().as_uri()}?{query}"
    har_path = output.with_suffix(".har")
    command = [
        "npx",
        "--no-install",
        "playwright",
        "screenshot",
        "--browser",
        "chromium",
        "--viewport-size",
        f"{VIEWPORT[0]},{VIEWPORT[1]}",
        "--wait-for-selector",
        READY_SELECTOR,
        "--timeout",
        "30000",
        "--save-har",
        str(har_path),
    ]
    if wait_ms:
        command.extend(["--wait-for-timeout", str(wait_ms)])
    command.extend([url, str(output)])
    try:
        subprocess.run(command, check=True)
        runtime_dependencies = dependencies_from_har(har_path, project)
    finally:
        har_path.unlink(missing_ok=True)
    with Image.open(output) as image:
        if image.size != VIEWPORT:
            raise ValueError(f"wrong dimensions for {output.name}: {image.size}")
        if image.format != "PNG":
            raise ValueError(f"wrong format for {output.name}: {image.format}")
    return runtime_dependencies


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


def validate_zip_name(zip_name: str) -> str:
    path = Path(zip_name)
    if path.is_absolute() or len(path.parts) != 1 or path.name != zip_name:
        raise ValueError("--zip must be a filename inside the project directory")
    if path.suffix.lower() != ".zip":
        raise ValueError("--zip must end with .zip")
    return path.name


def required_contract_files(project: Path) -> list[Path]:
    return [project / "README.md", project / "LEGENDA.txt", project / "assets" / "GEIST-LICENSE.txt"]


def package_project(
    project: Path,
    html_path: Path,
    outputs: list[Path],
    preview: Path,
    zip_name: str,
    dependencies: list[Path] | None = None,
    strict_contract: bool = True,
) -> Path:
    zip_name = validate_zip_name(zip_name)
    contract = required_contract_files(project)
    if strict_contract:
        missing_contract = [str(path.relative_to(project)) for path in contract if not path.is_file()]
        if missing_contract:
            raise FileNotFoundError("missing required carousel deliverables: " + ", ".join(missing_contract))

    candidates = [html_path, preview, *outputs, *(dependencies or [])]
    candidates.extend(path for path in contract if path.is_file())
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
        if not resolved.is_relative_to(project.resolve()):
            raise ValueError(f"package file escapes project directory: {path}")
        if path.is_file() and resolved not in seen:
            unique.append(path)
            seen.add(resolved)

    output = (project / zip_name).resolve()
    if not output.is_relative_to(project.resolve()):
        raise ValueError("ZIP output escapes project directory")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in unique:
            archive.write(path, path.resolve().relative_to(project.resolve()))

    with zipfile.ZipFile(output) as archive:
        broken = archive.testzip()
        if broken:
            raise ValueError(f"corrupt ZIP entry: {broken}")
        names = set(archive.namelist())
        required_paths = [html_path, preview, *outputs, *(dependencies or [])]
        if strict_contract:
            required_paths.extend(contract)
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
    parser.add_argument("--wait-ms", type=int, default=100, help="extra wait after fonts and images are ready")
    parser.add_argument("--zip", dest="zip_name", default="carousel.zip", help="output ZIP filename")
    parser.add_argument(
        "--relaxed-contract",
        action="store_true",
        help="allow packaging without README.md, LEGENDA.txt or assets/GEIST-LICENSE.txt",
    )
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
    validate_zip_name(args.zip_name)

    slides = discover_slides(html_path)
    if len(slides) != args.expected:
        raise ValueError(f"expected {args.expected} slides, found {len(slides)}")
    dependencies = collect_local_dependencies(html_path, project)
    ready_html = make_ready_html(html_path)

    output_dir = project / "slides"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    runtime_dependencies: list[Path] = []
    try:
        for index, slide_id in enumerate(slides, start=1):
            output = output_dir / f"slide-{index:02d}.png"
            discovered = render_slide(ready_html, project, slide_id, output, args.wait_ms)
            for path in discovered:
                if path != html_path and path not in runtime_dependencies:
                    runtime_dependencies.append(path)
            outputs.append(output)
    finally:
        if ready_html != html_path:
            ready_html.unlink(missing_ok=True)

    all_dependencies = list(dict.fromkeys([*dependencies, *runtime_dependencies]))
    preview = project / "preview-contact-sheet.png"
    make_contact_sheet(outputs, preview)
    package = package_project(
        project,
        html_path,
        outputs,
        preview,
        args.zip_name,
        all_dependencies,
        strict_contract=not args.relaxed_contract,
    )

    print(f"slides={len(outputs)}")
    print(f"dependencies={len(all_dependencies)}")
    print(f"preview={preview}")
    print(f"zip={package}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, UnicodeDecodeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_carousel.py"
SPEC = importlib.util.spec_from_file_location("export_carousel", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CarouselExporterTests(unittest.TestCase):
    def make_project(self, slide_count: int = 8) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "assets" / "photos").mkdir(parents=True)
        (root / "assets" / "font.woff2").write_bytes(b"font")
        (root / "assets" / "photos" / "scene.jpg").write_bytes(b"image")
        sections = "\n".join(
            f'<section class="slide" data-slide="slide-{index}">Slide {index}</section>'
            for index in range(1, slide_count + 1)
        )
        html = root / "index.html"
        html.write_text(
            "<style>@font-face{src:url('./assets/font.woff2')}</style>"
            '<img src="./assets/photos/scene.jpg">' + sections,
            encoding="utf-8",
        )
        (root / "README.md").write_text("credits", encoding="utf-8")
        (root / "LEGENDA.txt").write_text("caption", encoding="utf-8")
        return temp, root, html

    def test_discovers_eight_ordered_slides(self) -> None:
        temp, _, html = self.make_project()
        self.addCleanup(temp.cleanup)
        self.assertEqual(MODULE.discover_slides(html), [f"slide-{index}" for index in range(1, 9)])

    def test_duplicate_slide_id_is_rejected(self) -> None:
        temp, _, html = self.make_project(2)
        self.addCleanup(temp.cleanup)
        html.write_text(
            '<section class="slide" data-slide="same"></section>'
            '<section class="slide" data-slide="same"></section>',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.discover_slides(html)

    def test_remote_html_dependency_is_rejected(self) -> None:
        temp, _, html = self.make_project()
        self.addCleanup(temp.cleanup)
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<img src="https://example.com/remote.jpg">')
        with self.assertRaisesRegex(ValueError, "remote HTML dependencies"):
            MODULE.collect_local_dependencies(html)

    def test_missing_local_dependency_is_rejected(self) -> None:
        temp, _, html = self.make_project()
        self.addCleanup(temp.cleanup)
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<img src="./assets/missing.jpg">')
        with self.assertRaisesRegex(FileNotFoundError, "missing local HTML dependencies"):
            MODULE.collect_local_dependencies(html)

    def test_collects_font_and_nested_photo_dependencies(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        dependencies = MODULE.collect_local_dependencies(html)
        relative = {str(path.relative_to(root)) for path in dependencies}
        self.assertEqual(relative, {"assets/font.woff2", "assets/photos/scene.jpg"})

    def test_dependency_cannot_escape_project(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        outside = root.parent / f"{root.name}-outside.jpg"
        outside.write_bytes(b"outside")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        with html.open("a", encoding="utf-8") as handle:
            handle.write(f'<img src="../{outside.name}">')
        with self.assertRaisesRegex(ValueError, "escapes the project"):
            MODULE.collect_local_dependencies(html, root)

    def test_bundled_template_has_eight_unique_slides_and_brand_assets(self) -> None:
        template = Path(__file__).resolve().parents[1] / "templates" / "carousel-starter.html"
        text = template.read_text(encoding="utf-8")
        self.assertEqual(len(MODULE.discover_slides(template)), 8)
        self.assertIn("GeistMono-Medium.woff2", text)
        self.assertEqual(text.count("./assets/mark-white.svg"), 8)

    def test_package_recurses_nested_assets_and_is_integral(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        slides = root / "slides"
        slides.mkdir()
        outputs: list[Path] = []
        for index in range(1, 9):
            path = slides / f"slide-{index:02d}.png"
            Image.new("RGB", MODULE.VIEWPORT, "white").save(path, format="PNG")
            outputs.append(path)
        preview = root / "preview-contact-sheet.png"
        Image.new("RGB", (696, 1740), "white").save(preview, format="PNG")
        media = root / "media"
        media.mkdir()
        extra = media / "proof.jpg"
        extra.write_bytes(b"proof")
        package = MODULE.package_project(root, html, outputs, preview, "carousel.zip", [extra])
        with zipfile.ZipFile(package) as archive:
            names = set(archive.namelist())
            self.assertIsNone(archive.testzip())
        self.assertIn("assets/photos/scene.jpg", names)
        self.assertIn("assets/font.woff2", names)
        self.assertIn("media/proof.jpg", names)
        self.assertIn("slides/slide-08.png", names)
        self.assertIn("preview-contact-sheet.png", names)


if __name__ == "__main__":
    unittest.main()

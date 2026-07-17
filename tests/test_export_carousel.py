from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_carousel.py"
SPEC = importlib.util.spec_from_file_location("export_carousel", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CarouselExporterTests(unittest.TestCase):
    def make_project(self, slide_count: int = 8) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        temp = tempfile.TemporaryDirectory()
        # resolve() normalizes macOS' /var -> /private/var alias so production
        # paths and test assertions share the same canonical root.
        root = Path(temp.name).resolve()
        (root / "assets" / "photos").mkdir(parents=True)
        (root / "assets" / "font.woff2").write_bytes(b"font")
        (root / "assets" / "photos" / "scene.jpg").write_bytes(b"image")
        (root / "assets" / "GEIST-LICENSE.txt").write_text("license", encoding="utf-8")
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
        with self.assertRaisesRegex(ValueError, "remote dependency"):
            MODULE.collect_local_dependencies(html)

    def test_missing_local_dependency_is_rejected(self) -> None:
        temp, _, html = self.make_project()
        self.addCleanup(temp.cleanup)
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<img src="./assets/missing.jpg">')
        with self.assertRaisesRegex(FileNotFoundError, "missing local dependency"):
            MODULE.collect_local_dependencies(html)

    def test_collects_font_and_nested_photo_dependencies(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        dependencies = MODULE.collect_local_dependencies(html)
        relative = {str(path.relative_to(root)) for path in dependencies}
        self.assertEqual(relative, {"assets/font.woff2", "assets/photos/scene.jpg"})

    def test_anchor_href_is_not_treated_as_asset(self) -> None:
        temp, _, html = self.make_project()
        self.addCleanup(temp.cleanup)
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<a href="https://example.com/article">source</a>')
        MODULE.collect_local_dependencies(html)

    def test_srcset_dependencies_are_collected(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        second = root / "assets" / "photos" / "scene-2.jpg"
        second.write_bytes(b"image-2")
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<source srcset="./assets/photos/scene.jpg 1x, ./assets/photos/scene-2.jpg 2x">')
        relative = {str(path.relative_to(root)) for path in MODULE.collect_local_dependencies(html)}
        self.assertIn("assets/photos/scene-2.jpg", relative)

    def test_external_css_graph_is_collected_recursively(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        styles = root / "styles"
        media = root / "media"
        styles.mkdir()
        media.mkdir()
        (media / "background.png").write_bytes(b"png")
        (styles / "main.css").write_text(".hero{background:url('../media/background.png')}", encoding="utf-8")
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<link rel="stylesheet" href="./styles/main.css">')
        relative = {str(path.relative_to(root)) for path in MODULE.collect_local_dependencies(html)}
        self.assertIn("styles/main.css", relative)
        self.assertIn("media/background.png", relative)

    def test_remote_css_import_is_rejected(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        styles = root / "styles"
        styles.mkdir()
        (styles / "main.css").write_text('@import "https://example.com/remote.css";', encoding="utf-8")
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<link rel="stylesheet" href="./styles/main.css">')
        with self.assertRaisesRegex(ValueError, "remote dependency"):
            MODULE.collect_local_dependencies(html)

    def test_static_javascript_import_graph_is_collected(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        scripts = root / "scripts"
        media = root / "media"
        scripts.mkdir()
        media.mkdir()
        (media / "scene.jpg").write_bytes(b"scene")
        (scripts / "app.js").write_text("const scene = new URL('../media/scene.jpg', import.meta.url);", encoding="utf-8")
        with html.open("a", encoding="utf-8") as handle:
            handle.write('<script type="module" src="./scripts/app.js"></script>')
        relative = {str(path.relative_to(root)) for path in MODULE.collect_local_dependencies(html)}
        self.assertIn("scripts/app.js", relative)
        self.assertIn("media/scene.jpg", relative)

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

    def test_zip_name_cannot_escape_project(self) -> None:
        for value in ("../outside.zip", "/tmp/outside.zip", "nested/outside.zip", "carousel"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.validate_zip_name(value)

    def test_ready_html_uses_original_file_without_injection(self) -> None:
        temp, _, html = self.make_project()
        self.addCleanup(temp.cleanup)
        ready = MODULE.make_ready_html(html)
        self.assertEqual(ready, html)
        self.assertNotIn("data-carousel-readiness", ready.read_text(encoding="utf-8"))

    def test_ready_html_does_not_follow_fixed_name_symlink(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        outside = root.parent / f"{root.name}-outside.html"
        outside.write_text("do not overwrite", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        (root / ".carousel-export.html").symlink_to(outside)

        ready = MODULE.make_ready_html(html)
        self.addCleanup(lambda: ready.unlink(missing_ok=True))

        self.assertEqual(outside.read_text(encoding="utf-8"), "do not overwrite")
        self.assertEqual(ready, html)
        self.assertFalse(ready.is_symlink())

    def test_main_refuses_slides_directory_symlink_escape(self) -> None:
        temp, root, _ = self.make_project(slide_count=1)
        self.addCleanup(temp.cleanup)
        outside = root.parent / f"{root.name}-outside-slides"
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir())
        (root / "slides").symlink_to(outside, target_is_directory=True)

        argv = ["export_carousel.py", str(root), "--expected", "1", "--relaxed-contract"]
        with mock.patch.object(sys, "argv", argv), self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.main()
        self.assertEqual(list(outside.iterdir()), [])

    def test_main_refuses_slide_output_symlink_escape(self) -> None:
        temp, root, _ = self.make_project(slide_count=1)
        self.addCleanup(temp.cleanup)
        (root / "slides").mkdir()
        outside = root.parent / f"{root.name}-outside.png"
        outside.write_bytes(b"do not overwrite")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        (root / "slides" / "slide-01.png").symlink_to(outside)

        argv = ["export_carousel.py", str(root), "--expected", "1", "--relaxed-contract"]
        with mock.patch.object(sys, "argv", argv), self.assertRaisesRegex(ValueError, "symlink"):
            MODULE.main()
        self.assertEqual(outside.read_bytes(), b"do not overwrite")

    def test_bundled_template_has_eight_unique_slides_and_brand_assets(self) -> None:
        template = Path(__file__).resolve().parents[1] / "templates" / "carousel-starter.html"
        text = template.read_text(encoding="utf-8")
        self.assertEqual(len(MODULE.discover_slides(template)), 8)
        self.assertIn("GeistMono-Medium.woff2", text)
        self.assertEqual(text.count("./assets/mark-white.svg"), 8)

    def test_runtime_har_rejects_remote_requests(self) -> None:
        temp, root, _ = self.make_project()
        self.addCleanup(temp.cleanup)
        har = root / "runtime.har"
        har.write_text(
            '{"log":{"entries":[{"request":{"url":"https://example.com/tracker.js"}}]}}',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "remote request"):
            MODULE.dependencies_from_har(har, root)

    def test_package_requires_readme_caption_and_font_license(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        (root / "LEGENDA.txt").unlink()
        slide = root / "slide.png"
        preview = root / "preview.png"
        Image.new("RGB", MODULE.VIEWPORT, "white").save(slide, format="PNG")
        Image.new("RGB", (696, 1740), "white").save(preview, format="PNG")
        with self.assertRaisesRegex(FileNotFoundError, "LEGENDA.txt"):
            MODULE.package_project(root, html, [slide], preview, "carousel.zip")

    def test_relaxed_contract_is_explicit(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        for path in MODULE.required_contract_files(root):
            path.unlink(missing_ok=True)
        slide = root / "slide.png"
        preview = root / "preview.png"
        Image.new("RGB", MODULE.VIEWPORT, "white").save(slide, format="PNG")
        Image.new("RGB", (696, 1740), "white").save(preview, format="PNG")
        package = MODULE.package_project(
            root,
            html,
            [slide],
            preview,
            "carousel.zip",
            strict_contract=False,
        )
        self.assertTrue(package.is_file())

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

    def test_package_removes_temporary_zip_after_validation_failure(self) -> None:
        temp, root, html = self.make_project()
        self.addCleanup(temp.cleanup)
        slide = root / "slide.png"
        preview = root / "preview.png"
        Image.new("RGB", MODULE.VIEWPORT, "white").save(slide, format="PNG")
        Image.new("RGB", (696, 1740), "white").save(preview, format="PNG")

        with mock.patch.object(zipfile.ZipFile, "testzip", side_effect=RuntimeError("forced validation failure")):
            with self.assertRaisesRegex(RuntimeError, "forced validation failure"):
                MODULE.package_project(root, html, [slide], preview, "carousel.zip")

        self.assertFalse((root / "carousel.zip").exists())
        self.assertEqual(list(root.glob(".carousel.zip.*.zip")), [])


if __name__ == "__main__":
    unittest.main()

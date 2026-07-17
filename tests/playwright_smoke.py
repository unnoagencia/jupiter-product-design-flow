#!/usr/bin/env python3
"""Exercise the real Python -> Node -> Chromium carousel export path."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "scripts" / "export_carousel.py"
HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Smoke carousel</title></head>
<body>
  <main>
    <section class="slide" data-slide="smoke"
      style="width:1080px;height:1350px;background:#0a0a0b;color:#fafafa">
      <h1>Deterministic local render</h1>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary)
        (project / "index.html").write_text(HTML, encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(EXPORTER),
                str(project),
                "--expected",
                "1",
                "--wait-ms",
                "0",
                "--zip",
                "smoke.zip",
                "--relaxed-contract",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if completed.returncode != 0:
            diagnostic = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(f"carousel smoke export failed: {diagnostic}")

        slide = project / "slides" / "slide-01.png"
        preview = project / "preview-contact-sheet.png"
        package = project / "smoke.zip"
        with Image.open(slide) as image:
            assert image.size == (1080, 1350), image.size
            image.verify()
        with Image.open(preview) as image:
            image.verify()
        with zipfile.ZipFile(package) as archive:
            assert archive.testzip() is None
            names = set(archive.namelist())
            assert {"index.html", "slides/slide-01.png", "preview-contact-sheet.png"} <= names

    print("playwright carousel smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

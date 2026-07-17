from __future__ import annotations

import importlib.util
import os
import socketserver
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_carousel.py"
SPEC = importlib.util.spec_from_file_location("export_carousel_e2e", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@unittest.skipUnless(os.environ.get("RUN_PLAYWRIGHT_E2E") == "1", "set RUN_PLAYWRIGHT_E2E=1")
class PlaywrightExporterE2ETests(unittest.TestCase):
    def make_project(self, body: str) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name).resolve()
        html = root / "index.html"
        html.write_text(
            '<html data-carousel-ready="true"><head><meta data-carousel-readiness></head>'
            f'<body><section class="slide" data-slide="one">{body}</section></body></html>',
            encoding="utf-8",
        )
        return temp, root, html

    def test_real_chromium_render_retains_har(self) -> None:
        temp, root, html = self.make_project("secure render")
        self.addCleanup(temp.cleanup)
        slides = MODULE.ensure_output_directory(root / "slides", root)
        evidence = MODULE.ensure_output_directory(root / ".design" / "carousel-export" / "network", root)
        output = slides / "slide-01.png"
        har = evidence / "slide-01.har"

        dependencies = MODULE.render_slide(html, root, "one", output, 0, har)

        self.assertEqual(dependencies, [])
        self.assertTrue(output.is_file())
        self.assertTrue(har.is_file())

    def test_trusted_controller_selects_slide_and_applies_export_css(self) -> None:
        temp, root, html = self.make_project(
            "unused"
        )
        self.addCleanup(temp.cleanup)
        html.write_text(
            "<!doctype html><html><head><style>"
            "html,body{margin:0} .slide{width:1080px;height:1350px;background:#ff0000}"
            "body.export .slide[data-slide='second']{background:#00ff00}"
            "</style></head><body>"
            '<section class="slide" data-slide="first">first</section>'
            '<section class="slide" data-slide="second">second</section>'
            "</body></html>",
            encoding="utf-8",
        )
        slides = MODULE.ensure_output_directory(root / "slides", root)
        evidence = MODULE.ensure_output_directory(root / ".design" / "carousel-export" / "network", root)
        output = slides / "slide-02.png"
        har = evidence / "slide-02.har"

        MODULE.render_slide(html, root, "second", output, 0, har)

        with Image.open(output) as image:
            self.assertEqual(image.getpixel((540, 675))[:3], (0, 255, 0))

    def test_page_authored_http_cannot_leave_browser(self) -> None:
        hits = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
                hits.append(self.path)
                self.send_response(204)
                self.end_headers()

            def log_message(self, *_args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        temp, root, html = self.make_project(
            f'<script>fetch("http://127.0.0.1:{port}/must-not-leave")</script>blocked render'
        )
        self.addCleanup(temp.cleanup)
        slides = MODULE.ensure_output_directory(root / "slides", root)
        evidence = MODULE.ensure_output_directory(root / ".design" / "carousel-export" / "network", root)
        output = slides / "slide-01.png"
        har = evidence / "slide-01.har"

        dependencies = MODULE.render_slide(html, root, "one", output, 100, har)

        self.assertEqual(dependencies, [])
        self.assertEqual(hits, [])
        self.assertTrue(output.is_file())
        self.assertTrue(har.is_file())

    def test_automatic_image_http_is_blocked_before_listener(self) -> None:
        hits = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
                hits.append(self.path)
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()

            def log_message(self, *_args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        temp, root, html = self.make_project(
            f'<img src="http://127.0.0.1:{port}/must-not-load.png" alt="blocked">'
        )
        self.addCleanup(temp.cleanup)
        slides = MODULE.ensure_output_directory(root / "slides", root)
        evidence = MODULE.ensure_output_directory(root / ".design" / "carousel-export" / "network", root)
        output = slides / "slide-01.png"
        har = evidence / "slide-01.har"

        with self.assertRaisesRegex(ValueError, "remote request"):
            MODULE.render_slide(html, root, "one", output, 0, har)

        self.assertEqual(hits, [])
        self.assertFalse(output.exists())
        self.assertTrue(har.is_file())

    def test_page_authored_websocket_cannot_reach_server(self) -> None:
        connections = []

        class Handler(socketserver.BaseRequestHandler):
            def handle(self) -> None:
                connections.append(self.client_address)
                self.request.recv(4096)

        server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        temp, root, html = self.make_project(
            f'<script>new WebSocket("ws://127.0.0.1:{port}/must-not-connect")</script>blocked socket'
        )
        self.addCleanup(temp.cleanup)
        slides = MODULE.ensure_output_directory(root / "slides", root)
        evidence = MODULE.ensure_output_directory(root / ".design" / "carousel-export" / "network", root)
        output = slides / "slide-01.png"
        har = evidence / "slide-01.har"

        dependencies = MODULE.render_slide(html, root, "one", output, 100, har)

        self.assertEqual(dependencies, [])
        self.assertEqual(connections, [])
        self.assertTrue(output.is_file())
        self.assertTrue(har.is_file())

    def test_page_authored_webrtc_cannot_emit_stun_udp(self) -> None:
        datagrams = []

        class Handler(socketserver.BaseRequestHandler):
            def handle(self) -> None:
                datagrams.append(self.request[0])

        server = socketserver.ThreadingUDPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        port = server.server_address[1]
        temp, root, html = self.make_project(
            "<script>"
            f'const peer = new RTCPeerConnection({{iceServers:[{{urls:"stun:127.0.0.1:{port}"}}]}});'
            'peer.createDataChannel("blocked");'
            "peer.createOffer().then((offer) => peer.setLocalDescription(offer));"
            "</script>blocked WebRTC"
        )
        self.addCleanup(temp.cleanup)
        slides = MODULE.ensure_output_directory(root / "slides", root)
        evidence = MODULE.ensure_output_directory(root / ".design" / "carousel-export" / "network", root)
        output = slides / "slide-01.png"
        har = evidence / "slide-01.har"

        dependencies = MODULE.render_slide(html, root, "one", output, 500, har)

        self.assertEqual(dependencies, [])
        self.assertEqual(datagrams, [])
        self.assertTrue(output.is_file())
        self.assertTrue(har.is_file())


if __name__ == "__main__":
    unittest.main()

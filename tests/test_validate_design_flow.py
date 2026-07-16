from __future__ import annotations

import base64
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_design_flow.py"
SPEC = importlib.util.spec_from_file_location("validate_design_flow", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

VALID_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = (zlib.crc32(chunk_type + payload) & 0xFFFFFFFF).to_bytes(4, "big")
    return len(payload).to_bytes(4, "big") + chunk_type + payload + crc


def png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    chunks: list[tuple[bytes, bytes]] = []
    position = 8
    while position < len(data):
        length = int.from_bytes(data[position:position + 4], "big")
        chunk_type = data[position + 4:position + 8]
        payload = data[position + 8:position + 8 + length]
        chunks.append((chunk_type, payload))
        position += 12 + length
    return chunks


def build_png(chunks: list[tuple[bytes, bytes]]) -> bytes:
    return MODULE.PNG_SIGNATURE + b"".join(png_chunk(kind, payload) for kind, payload in chunks)


BRIEF = """# Design Brief: Fixture

## Problema
O usuário perde contexto durante uma tarefa operacional importante e precisa reconstruir informação.

## Usuário principal e JTBD
O operador precisa concluir uma ação sem alternar entre sistemas ou depender de memória.

## Resultado de sucesso
A ação principal é concluída com contexto, feedback e recuperação clara de erro.

## Escopo
Uma experiência funcional com conteúdo realista e estados essenciais.

## Fora de escopo
Administração avançada e integrações externas não aprovadas.

## Marca e direção visual
Reutilizar tokens, tipografia e componentes canônicos do projeto.

## Restrições
Mobile, navegação por teclado, contraste WCAG AA e ausência de dados sensíveis.
"""

TASKS = """# Build Tasks: Fixture

## Implementação
- [ ] Entregar uma fatia vertical com estrutura, estilo, comportamento, estados e conteúdo realista verificável.

## QA
- [ ] Capturar desktop e mobile, exercitar estados críticos e executar os testes relevantes antes de concluir.
"""

REVIEW = """# Design Review: Fixture

## Evidências
Foi capturada evidência visual válida para a view principal em viewport desktop.

## Síntese
A hierarquia principal funciona e a ação central permanece clara durante o fluxo.

## Must fix
Nenhum defeito crítico encontrado após a verificação registrada.

## Should fix
Nenhuma inconsistência relevante permaneceu na versão analisada.

## Could improve
A microcopy secundária pode ser refinada em uma iteração futura sem bloquear o uso.

## O que preservar
A clareza da ação principal, a densidade controlada e a aderência aos tokens canônicos.
"""

IA = """# Information Architecture: Fixture

## Mapa de rotas e views
- Principal `/`

## Modelo de navegação
Navegação direta, sem níveis secundários ou rotas paralelas.

## Fluxos críticos
O usuário entra na view, executa a ação principal e recebe confirmação explícita.
"""


class ValidatorTests(unittest.TestCase):
    def make_feature(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "DESIGN_BRIEF.md").write_text(BRIEF, encoding="utf-8")
        (root / "TASKS.md").write_text(TASKS, encoding="utf-8")
        return temp, root

    def add_review(self, root: Path, image: bytes = VALID_PNG) -> None:
        (root / "DESIGN_REVIEW.md").write_text(REVIEW, encoding="utf-8")
        shots = root / "screenshots"
        shots.mkdir()
        (shots / "desktop.png").write_bytes(image)

    def test_minimal_feature_passes_without_review(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        self.assertTrue(MODULE.validate(root, False)["ok"])

    def test_review_is_required_only_when_flagged(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        result = MODULE.validate(root, True)
        self.assertFalse(result["ok"])
        self.assertIn("missing required file: DESIGN_REVIEW.md", result["errors"])

    def test_existing_malformed_review_is_validated_without_flag(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        (root / "DESIGN_REVIEW.md").write_text("malformed review" * 20, encoding="utf-8")
        (root / "screenshots").mkdir()
        (root / "screenshots" / "desktop.png").write_bytes(VALID_PNG)
        result = MODULE.validate(root, False)
        self.assertFalse(result["ok"])
        self.assertTrue(any("missing heading" in error for error in result["errors"]))

    def test_fake_or_empty_image_is_rejected(self) -> None:
        for payload in (b"", b"not an image"):
            temp, root = self.make_feature()
            try:
                self.add_review(root, payload)
                result = MODULE.validate(root, True)
                self.assertFalse(result["ok"])
                self.assertTrue(any("PNG visual evidence" in error for error in result["errors"]))
            finally:
                temp.cleanup()

    def test_truncated_png_with_positive_header_dimensions_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        self.add_review(root, VALID_PNG[:24])
        result = MODULE.validate(root, True)
        self.assertFalse(result["ok"])
        self.assertTrue(any("PNG visual evidence" in error for error in result["errors"]))

    def test_png_with_invalid_crc_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        corrupted = bytearray(VALID_PNG)
        corrupted[20] ^= 0x01
        self.add_review(root, bytes(corrupted))
        result = MODULE.validate(root, True)
        self.assertFalse(result["ok"])
        self.assertTrue(any("PNG visual evidence" in error for error in result["errors"]))

    def test_png_with_zero_dimensions_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        zero_width = bytearray(VALID_PNG)
        zero_width[16:20] = b"\x00\x00\x00\x00"
        zero_width[29:33] = (zlib.crc32(bytes(zero_width[12:29])) & 0xFFFFFFFF).to_bytes(4, "big")
        self.add_review(root, bytes(zero_width))
        result = MODULE.validate(root, True)
        self.assertFalse(result["ok"])
        self.assertTrue(any("PNG visual evidence" in error for error in result["errors"]))

    def test_header_only_jpeg_and_malformed_webp_are_rejected(self) -> None:
        for filename, payload in (
            ("header.jpg", b"\xff\xd8\xff\xc0\x00\x11" + b"\x00" * 20),
            ("header.webp", b"RIFF" + (22).to_bytes(4, "little") + b"WEBPVP8X" + b"\x00" * 14),
        ):
            temp, root = self.make_feature()
            try:
                (root / "DESIGN_REVIEW.md").write_text(REVIEW, encoding="utf-8")
                shots = root / "screenshots"
                shots.mkdir()
                (shots / filename).write_bytes(payload)
                result = MODULE.validate(root, True)
                self.assertFalse(result["ok"])
                self.assertTrue(any("unsupported visual evidence format" in error for error in result["errors"]))
            finally:
                temp.cleanup()

    def test_unreadable_or_broken_image_path_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        (root / "DESIGN_REVIEW.md").write_text(REVIEW, encoding="utf-8")
        shots = root / "screenshots"
        shots.mkdir()
        (shots / "broken.png").symlink_to(shots / "missing-target.png")
        result = MODULE.validate(root, True)
        self.assertFalse(result["ok"])
        self.assertTrue(any("not a readable file" in error for error in result["errors"]))

    def test_unknown_critical_chunk_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        chunks.insert(-1, (b"ABCD", b""))
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_forbidden_palette_for_color_type_four_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        self.assertEqual(chunks[0][1][9], 4)
        idat_index = next(i for i, (kind, _) in enumerate(chunks) if kind == b"IDAT")
        chunks.insert(idat_index, (b"PLTE", b"\x00\x00\x00"))
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_non_consecutive_idat_chunks_are_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        rebuilt: list[tuple[bytes, bytes]] = []
        for kind, payload in png_chunks(VALID_PNG):
            if kind == b"IDAT":
                split = max(1, len(payload) // 2)
                rebuilt.extend([
                    (b"IDAT", payload[:split]),
                    (b"tEXt", b"note\x00between"),
                    (b"IDAT", payload[split:]),
                ])
            else:
                rebuilt.append((kind, payload))
        self.add_review(root, build_png(rebuilt))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_oversized_dimensions_are_rejected_before_decode(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        ihdr = bytearray(chunks[0][1])
        ihdr[0:4] = (100_000).to_bytes(4, "big")
        ihdr[4:8] = (100_000).to_bytes(4, "big")
        chunks[0] = (b"IHDR", bytes(ihdr))
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_oversized_sparse_png_file_is_rejected_before_read(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        (root / "DESIGN_REVIEW.md").write_text(REVIEW, encoding="utf-8")
        shots = root / "screenshots"
        shots.mkdir()
        path = shots / "oversized.png"
        with path.open("wb") as handle:
            handle.write(MODULE.PNG_SIGNATURE)
            handle.truncate(MODULE.MAX_FILE_BYTES + 1)
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_incomplete_zlib_stream_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        chunks = [(kind, payload[:-1] if kind == b"IDAT" else payload) for kind, payload in chunks]
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_incorrect_decoded_length_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        ihdr = bytearray(chunks[0][1])
        ihdr[4:8] = (2).to_bytes(4, "big")
        chunks[0] = (b"IHDR", bytes(ihdr))
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_invalid_filter_byte_is_rejected(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        chunks = [(kind, zlib.compress(b"\x05\x00\x00") if kind == b"IDAT" else payload) for kind, payload in chunks]
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_interlaced_png_is_rejected_by_documented_policy(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        chunks = png_chunks(VALID_PNG)
        ihdr = bytearray(chunks[0][1])
        ihdr[12] = 1
        chunks[0] = (b"IHDR", bytes(ihdr))
        self.add_review(root, build_png(chunks))
        self.assertFalse(MODULE.validate(root, True)["ok"])

    def test_valid_png_evidence_passes(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        self.add_review(root)
        self.assertTrue(MODULE.validate(root, True)["ok"])

    def test_directory_in_place_of_optional_artifact_returns_error(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        (root / "INFORMATION_ARCHITECTURE.md").mkdir()
        result = MODULE.validate(root, False)
        self.assertFalse(result["ok"])
        self.assertIn("artifact path is not a file: INFORMATION_ARCHITECTURE.md", result["errors"])

    def test_invalid_utf8_returns_structured_error(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        (root / "DESIGN_BRIEF.md").write_bytes(b"\xff\xfe\xfd")
        result = MODULE.validate(root, False)
        self.assertFalse(result["ok"])
        self.assertTrue(any("cannot read DESIGN_BRIEF.md" in error for error in result["errors"]))

    def test_portuguese_todos_is_not_treated_as_todo_marker(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        with (root / "TASKS.md").open("a", encoding="utf-8") as handle:
            handle.write("\nTodos os casos relevantes foram verificados.\n")
        self.assertTrue(MODULE.validate(root, False)["ok"])

    def test_literal_todo_marker_is_blocking(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        with (root / "TASKS.md").open("a", encoding="utf-8") as handle:
            handle.write("\nTODO revisar este fluxo.\n")
        result = MODULE.validate(root, False)
        self.assertFalse(result["ok"])
        self.assertTrue(any("unfilled template" in error for error in result["errors"]))

    def test_unfilled_placeholder_is_blocking(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        with (root / "DESIGN_BRIEF.md").open("a", encoding="utf-8") as handle:
            handle.write("\n[Hipótese — forma de validar]\n")
        result = MODULE.validate(root, False)
        self.assertFalse(result["ok"])
        self.assertTrue(any("unfilled template" in error for error in result["errors"]))

    def test_information_architecture_exact_headings(self) -> None:
        temp, root = self.make_feature()
        self.addCleanup(temp.cleanup)
        (root / "INFORMATION_ARCHITECTURE.md").write_text(IA, encoding="utf-8")
        self.assertTrue(MODULE.validate(root, False)["ok"])

    def test_cli_json_failure_has_no_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            missing = Path(temp) / "missing"
            run = subprocess.run(
                [sys.executable, str(SCRIPT), str(missing), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(run.returncode, 1)
        payload = json.loads(run.stdout)
        self.assertFalse(payload["ok"])
        self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()

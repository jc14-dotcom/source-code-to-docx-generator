import tempfile
import unittest
import zipfile
from pathlib import Path

from document_generator import DocumentGenerator
from framework_profiles import DJANGO
from scanner import ProjectScanner


class DocumentGeneratorTests(unittest.TestCase):
    def test_wrapped_line_estimate_uses_ceiling_division(self) -> None:
        self.assertEqual(DocumentGenerator._estimate_wrapped_lines("x" * 100), 1)
        self.assertEqual(DocumentGenerator._estimate_wrapped_lines("x" * 101), 2)

    def test_toc_tracks_sections_that_share_and_cross_pages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manage.py").write_text("# manage\n", encoding="utf-8")
            (root / "app").mkdir()
            (root / "app" / "models.py").write_text("x" * 100 + "\n" * 59, encoding="utf-8")
            (root / "app" / "views.py").write_text("def view(): pass\n", encoding="utf-8")

            scan = ProjectScanner(root, DJANGO).scan()
            generator = DocumentGenerator()
            entries = generator._calculate_toc(generator._group_files(scan), DJANGO)
            pages = {text: page for _, text, page in entries}

            self.assertEqual(pages["PART I - Root Files"], 4)
            self.assertEqual(pages["PART II - Application Source Code"], 6)
            self.assertEqual(pages["Models"], 7)
            self.assertEqual(pages["Views"], 8)

    def test_generated_docx_contains_redacted_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manage.py").write_text("# manage\n", encoding="utf-8")
            (root / "polls").mkdir()
            (root / "polls" / "models.py").write_text(
                "PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----\n"
                "fake-secret-material-123\n"
                "-----END RSA PRIVATE KEY-----'''\n",
                encoding="utf-8",
            )

            scan = ProjectScanner(root, DJANGO).scan()
            output = root / "documentation.docx"
            generator = DocumentGenerator()
            generator.generate(scan, output, DJANGO, "Smoke Test")

            xml = ""
            with zipfile.ZipFile(output) as archive:
                for name in archive.namelist():
                    if name.startswith("word/") and name.endswith(".xml"):
                        xml += archive.read(name).decode("utf-8", errors="replace")

            self.assertTrue(output.exists())
            self.assertEqual(generator.total_secrets_redacted, 1)
            self.assertNotIn("fake-secret-material-123", xml)
            self.assertIn("[REDACTED]", xml)


if __name__ == "__main__":
    unittest.main()

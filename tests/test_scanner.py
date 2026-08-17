import tempfile
import unittest
from pathlib import Path

from framework_profiles import DJANGO, EXPRESS
from scanner import ProjectScanner


class ScannerTests(unittest.TestCase):
    def test_discovers_conventional_django_app_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manage.py").write_text("", encoding="utf-8")
            (root / "polls").mkdir()
            (root / "polls" / "models.py").write_text("class Vote: pass", encoding="utf-8")
            (root / "polls" / "views.py").write_text("def index(): pass", encoding="utf-8")

            result = ProjectScanner(root, DJANGO).scan()
            paths = {file.relative_path.replace("\\", "/") for file in result.files}

            self.assertIn("polls/models.py", paths)
            self.assertIn("polls/views.py", paths)

    def test_excludes_nested_dependency_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text("{}", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "app.js").write_text("console.log('ok')", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "dependency.js").write_text("secret", encoding="utf-8")

            result = ProjectScanner(root, EXPRESS).scan()
            paths = {file.relative_path.replace("\\", "/") for file in result.files}

            self.assertIn("src/app.js", paths)
            self.assertNotIn("node_modules/dependency.js", paths)

    def test_excludes_environment_variants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text("", encoding="utf-8")
            (root / ".env.production").write_text("PASSWORD=secret", encoding="utf-8")
            (root / ".env.example").write_text("PASSWORD=example", encoding="utf-8")

            result = ProjectScanner(root, DJANGO).scan()
            paths = {file.relative_path.replace("\\", "/") for file in result.files}

            self.assertNotIn(".env.production", paths)
            self.assertIn(".env.example", paths)
            self.assertGreater(result.skipped_reasons.get("environment variant", 0), 0)

    def test_section_matching_uses_path_components(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "modelsmith.py").write_text("", encoding="utf-8")
            (root / "app").mkdir()
            (root / "app" / "models.py").write_text("", encoding="utf-8")

            result = ProjectScanner(root, DJANGO).scan()
            files = {
                file.relative_path.replace("\\", "/"): file
                for file in result.files
            }

            self.assertNotEqual(files["modelsmith.py"].file_type, "Models")
            self.assertEqual(files["app/models.py"].file_type, "Models")

    def test_reusing_scanner_does_not_accumulate_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text("", encoding="utf-8")
            scanner = ProjectScanner(root, DJANGO)

            first = scanner.scan()
            second = scanner.scan()

            self.assertEqual(first.total_files, second.total_files)
            self.assertEqual(len(first.files), len(second.files))
            self.assertEqual(first.files[0].relative_path, second.files[0].relative_path)

    def test_skips_have_structured_issue_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notes.bin").write_bytes(b"not source")
            result = ProjectScanner(root, DJANGO).scan()

            self.assertEqual(result.skipped_files, 1)
            self.assertEqual(result.issues[0].path, "notes.bin")
            self.assertEqual(result.issues[0].code, "outside profile and unsupported type")


if __name__ == "__main__":
    unittest.main()

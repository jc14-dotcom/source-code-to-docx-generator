import tempfile
import unittest
from pathlib import Path

from framework_detector import _requirements_has, detect_framework_details


class FrameworkDetectorTests(unittest.TestCase):
    def test_requirements_matching_ignores_comments_and_similar_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text(
                "# flask\nflask-restful==0.3.9\n", encoding="utf-8"
            )

            self.assertFalse(_requirements_has(root, "flask"))

    def test_requirements_matching_accepts_versioned_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text(
                "Flask>=3.0\n", encoding="utf-8"
            )

            self.assertTrue(_requirements_has(root, "flask"))

    def test_detection_returns_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text("flask\n", encoding="utf-8")

            result = detect_framework_details(root)

            self.assertIsNotNone(result)
            self.assertEqual(result.profile.name, "Flask")
            self.assertIn("flask dependency", result.evidence)


if __name__ == "__main__":
    unittest.main()

import unittest

from secrets_detector import SecretDetector


class SecretDetectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = SecretDetector()

    def test_redacts_complete_private_key_block(self) -> None:
        private_key = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "super-secret-key-material\n"
            "-----END RSA PRIVATE KEY-----"
        )

        redacted, count = self.detector.scan_and_redact(private_key)

        self.assertEqual(count, 1)
        self.assertEqual(redacted, "[REDACTED]")
        self.assertNotIn("super-secret-key-material", redacted)

    def test_redacts_common_provider_tokens(self) -> None:
        content = "github=ghp_abcdefghijklmnopqrstuvwxyz0123456789ABCD"

        redacted, count = self.detector.scan_and_redact(content)

        self.assertGreaterEqual(count, 1)
        self.assertNotIn("ghp_", redacted)

    def test_does_not_treat_generic_token_assignment_as_secret(self) -> None:
        content = "token = button.dataset.token"

        redacted, count = self.detector.scan_and_redact(content)

        self.assertEqual(count, 0)
        self.assertEqual(redacted, content)

    def test_preserves_public_certificate(self) -> None:
        certificate = (
            "-----BEGIN CERTIFICATE-----\n"
            "public-certificate-content\n"
            "-----END CERTIFICATE-----"
        )

        redacted, count = self.detector.scan_and_redact(certificate)

        self.assertEqual(count, 0)
        self.assertEqual(redacted, certificate)

    def test_find_labels_does_not_return_secret_values(self) -> None:
        content = 'DB_PASSWORD="do-not-log-this-value"'

        findings = self.detector.find_labels(content)

        self.assertEqual(findings, {"Database Password": 1})
        self.assertNotIn("do-not-log-this-value", str(findings))


if __name__ == "__main__":
    unittest.main()

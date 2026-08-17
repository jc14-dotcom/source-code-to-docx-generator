import re
from typing import Dict, Tuple

from config import SECRET_PATTERNS


class SecretDetector:
    def __init__(self) -> None:
        self._compiled: Dict[str, re.Pattern] = {}
        for label, pattern in SECRET_PATTERNS.items():
            self._compiled[label] = re.compile(pattern)

    def scan_and_redact(self, content: str) -> Tuple[str, int]:
        total_redactions = 0
        result = content
        for _label, pattern in self._compiled.items():
            matches = list(pattern.finditer(result))
            if matches:
                total_redactions += len(matches)
                result = pattern.sub("[REDACTED]", result)
        return result, total_redactions

    def find_labels(self, content: str) -> Dict[str, int]:
        """Return detected secret categories without exposing matched values."""
        findings: Dict[str, int] = {}
        for label, pattern in self._compiled.items():
            count = sum(1 for _ in pattern.finditer(content))
            if count:
                findings[label] = count
        return findings

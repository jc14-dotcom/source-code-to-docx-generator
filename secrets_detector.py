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
        for label, pattern in self._compiled.items():
            matches = pattern.findall(result)
            if matches:
                total_redactions += len(matches)
                result = pattern.sub("[REDACTED]", result)
        return result, total_redactions

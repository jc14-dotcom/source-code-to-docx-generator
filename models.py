from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class FileInfo:
    path: Path
    relative_path: str
    filename: str
    extension: str
    directory: str
    size_bytes: int
    last_modified: datetime
    language: str
    file_type: str
    part: str
    section: str


@dataclass
class DocumentStats:
    total_files: int = 0
    categories: Dict[str, int] = field(default_factory=dict)

    def increment(self, key: str) -> None:
        self.categories[key] = self.categories.get(key, 0) + 1

    def get(self, key: str) -> int:
        return self.categories.get(key, 0)


@dataclass(frozen=True)
class ScanIssue:
    path: str
    code: str
    message: str


@dataclass
class ScanResult:
    files: List[FileInfo] = field(default_factory=list)
    total_files: int = 0
    total_folders: int = 0
    skipped_files: int = 0
    skipped_reasons: Dict[str, int] = field(default_factory=dict)
    issues: List[ScanIssue] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stats: DocumentStats = field(default_factory=DocumentStats)

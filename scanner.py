import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from models import FileInfo, ScanIssue, ScanResult, DocumentStats
from framework_profiles import FrameworkProfile
from config import (
    EXCLUDE_DIRS,
    EXCLUDE_FILES,
    EXCLUDE_EXTENSIONS,
    COMMON_PROJECT_FILES,
    LANGUAGE_MAP,
)

logger = logging.getLogger("docgen")


class ProjectScanner:
    """Discover and classify source files for a configured framework."""

    def __init__(
        self,
        root: Path,
        profile: FrameworkProfile,
        include_dirs: Iterable[str] | None = None,
        include_files: Iterable[str] | None = None,
        exclude_dirs: Iterable[str] | None = None,
    ) -> None:
        self.root = root.resolve()
        self.profile = profile
        self._files: List[FileInfo] = []
        self._skipped: int = 0
        self._skipped_reasons: dict[str, int] = {}
        self._issues: List[ScanIssue] = []
        self._errors: List[str] = []
        self._folders_scanned: int = 0

        self._include_dirs = self._normalize_rules(
            list(profile.include_dirs) + list(include_dirs or [])
        )
        self._include_files = {
            self._normalize_path(value)
            for value in list(profile.include_files) + list(include_files or [])
        }
        all_excludes = list(EXCLUDE_DIRS) + list(profile.extra_exclude_dirs)
        all_excludes.extend(exclude_dirs or [])
        self._exclude_dirs = self._normalize_rules(all_excludes)

    @staticmethod
    def _normalize_path(value: str) -> str:
        return value.replace("\\", "/").strip("/").lower()

    @classmethod
    def _normalize_rules(cls, values: Iterable[str]) -> set[str]:
        return {cls._normalize_path(value) for value in values if value}

    @staticmethod
    def _path_starts_with(path: str, rule: str) -> bool:
        return path == rule or path.startswith(rule + "/")

    def _is_excluded_directory(self, relative: str, name: str) -> bool:
        candidate = self._normalize_path(f"{relative}/{name}" if relative else name)
        return any(
            candidate == rule or name.lower() == rule or self._path_starts_with(candidate, rule)
            for rule in self._exclude_dirs
        )

    def _record_skip(self, reason: str, path: str, message: str) -> None:
        self._skipped += 1
        self._skipped_reasons[reason] = self._skipped_reasons.get(reason, 0) + 1
        self._issues.append(ScanIssue(path=path, code=reason, message=message))

    def _reset_state(self) -> None:
        """Allow a scanner instance to be safely reused for another scan."""
        self._files.clear()
        self._skipped = 0
        self._skipped_reasons.clear()
        self._issues.clear()
        self._errors.clear()
        self._folders_scanned = 0

    def _should_include_file(self, relative: str) -> bool:
        normalized = self._normalize_path(relative)

        filename = Path(normalized).name
        if filename.lower() in {item.lower() for item in EXCLUDE_FILES}:
            return False

        ext = Path(filename).suffix.lower()
        if ext in EXCLUDE_EXTENSIONS:
            return False

        # Do not broadly include environment variants, which may contain real
        # credentials. `.env.example` remains available through profile rules.
        if filename.startswith(".env.") and filename != ".env.example":
            return False

        if normalized in self._include_files:
            return True

        for include_dir in self._include_dirs:
            if self._path_starts_with(normalized, include_dir):
                return True

        # Discover conventional source files even when a framework profile did
        # not list every application directory (for example Django apps).
        if filename in {name.lower() for name in COMMON_PROJECT_FILES}:
            return True
        if ext in {extension.lower() for extension in LANGUAGE_MAP}:
            return True

        return False

    def _detect_language(self, filepath: Path) -> str:
        name = filepath.name
        if name.endswith(".blade.php"):
            return "Blade Template"
        ext = filepath.suffix.lower()
        return LANGUAGE_MAP.get(ext, "Unknown")

    def _detect_file_type(self, relative_path: str, filename: str) -> str:
        normalized = self._normalize_path(relative_path)

        section_match = self._find_section_match(normalized)
        if section_match:
            return section_match[1]

        lang = self._detect_language(Path(relative_path))
        if lang != "Unknown":
            return lang

        lower = normalized
        if "test" in Path(filename).stem.lower():
            return "Test"
        if "config" in lower or "conf" in lower:
            return "Configuration"

        return "File"

    def _find_section_match(self, normalized: str) -> tuple[str, str] | None:
        matches: list[tuple[int, str, str]] = []
        for path_key, section_name in self.profile.section_map.items():
            key = self._normalize_path(path_key)
            components = normalized.split("/")
            if components:
                components[-1] = Path(components[-1]).stem.lower()
            key_components = key.split("/")
            for index in range(len(components) - len(key_components) + 1):
                if components[index:index + len(key_components)] == key_components:
                    matches.append((len(key_components), key, section_name))
                    break

        if not matches:
            return None

        _, key, section_name = max(matches, key=lambda item: item[0])
        return (key, section_name)

    def _match_to_section(self, relative_path: str) -> tuple[str, str]:
        normalized = self._normalize_path(relative_path)

        if "/" not in normalized:
            return ("I", "Root Files")

        section_match = self._find_section_match(normalized)
        if section_match:
            section_name = section_match[1]
            for part_num, part_title in self.profile.parts:
                if section_name.lower() in part_title.lower() or part_title.lower() in section_name.lower():
                    return (part_num, section_name)
            return ("II", section_name)

        for part_num, part_title in self.profile.parts:
            part_lower = part_title.lower()
            if any(kw in normalized.split("/") for kw in part_lower.split()):
                return (part_num, part_title)

        return ("Appendix", "Other")

    def scan(self) -> ScanResult:
        """Walk the project and return a deterministic scan result."""
        self._reset_state()
        logger.info(f"Scanning project: {self.root}")
        logger.info(f"Framework: {self.profile.name}")

        for dirpath, dirnames, filenames in os.walk(self.root):
            current = Path(dirpath)

            dirnames[:] = [
                d for d in dirnames
                if not self._is_excluded_directory(
                    str(current.relative_to(self.root)) if current != self.root else "",
                    d,
                )
            ]

            self._folders_scanned += 1

            for filename in filenames:
                filepath = current / filename
                try:
                    relative = str(filepath.relative_to(self.root))
                except ValueError:
                    continue

                if not self._should_include_file(relative):
                    normalized = self._normalize_path(relative)
                    filename = Path(normalized).name
                    if filename.lower() in {item.lower() for item in EXCLUDE_FILES}:
                        reason = "excluded filename"
                    elif filename.startswith(".env.") and filename != ".env.example":
                        reason = "environment variant"
                    elif Path(filename).suffix.lower() in EXCLUDE_EXTENSIONS:
                        reason = "excluded extension"
                    else:
                        reason = "outside profile and unsupported type"
                    self._record_skip(
                        reason,
                        relative,
                        f"Skipped because the file is {reason}.",
                    )
                    continue

                try:
                    stat = filepath.stat()
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime)
                except OSError as e:
                    self._errors.append(f"Cannot stat {relative}: {e}")
                    self._record_skip(
                        "stat error",
                        relative,
                        f"Cannot read file metadata: {e}",
                    )
                    continue

                language = self._detect_language(filepath)
                file_type = self._detect_file_type(relative, filename)
                part, section = self._match_to_section(relative)
                directory = filepath.parent.name

                info = FileInfo(
                    path=filepath,
                    relative_path=relative,
                    filename=filename,
                    extension=filepath.suffix,
                    directory=directory,
                    size_bytes=size,
                    last_modified=modified,
                    language=language,
                    file_type=file_type,
                    part=part,
                    section=section,
                )
                self._files.append(info)

        self._files.sort(key=lambda f: (
            next((i for i, (n, _) in enumerate(self.profile.parts) if n == f.part), 999),
            f.section,
            f.relative_path,
        ))

        stats = self._compute_stats()

        result = ScanResult(
            files=list(self._files),
            total_files=len(self._files),
            total_folders=self._folders_scanned,
            skipped_files=self._skipped,
            skipped_reasons=dict(self._skipped_reasons),
            issues=list(self._issues),
            errors=list(self._errors),
            stats=stats,
        )

        logger.info(f"Scan complete: {result.total_files} files, "
                     f"{result.skipped_files} skipped, "
                     f"{len(result.errors)} errors")

        return result

    def _compute_stats(self) -> DocumentStats:
        stats = DocumentStats()
        stats.total_files = len(self._files)

        for f in self._files:
            stats.increment(f.file_type)

            lang = f.language
            if lang != "Unknown":
                stats.increment(lang)

            ext = f.extension.lower()
            if ext:
                stats.increment(ext)

        return stats

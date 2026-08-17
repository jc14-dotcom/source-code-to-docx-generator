import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from models import FileInfo, ScanResult, DocumentStats
from framework_profiles import FrameworkProfile
from config import (
    EXCLUDE_DIRS,
    EXCLUDE_FILES,
    EXCLUDE_EXTENSIONS,
    LANGUAGE_MAP,
)

logger = logging.getLogger("docgen")


class ProjectScanner:
    def __init__(self, root: Path, profile: FrameworkProfile) -> None:
        self.root = root.resolve()
        self.profile = profile
        self._files: List[FileInfo] = []
        self._skipped: int = 0
        self._errors: List[str] = []
        self._folders_scanned: int = 0

        all_excludes = set(EXCLUDE_DIRS)
        all_excludes.update(profile.extra_exclude_dirs)
        self._exclude_dirs = all_excludes

    def _should_include_file(self, relative: str) -> bool:
        normalized = relative.replace("\\", "/")

        filename = Path(normalized).name
        if filename in EXCLUDE_FILES:
            return False

        ext = Path(filename).suffix.lower()
        if ext in EXCLUDE_EXTENSIONS:
            return False

        if normalized in self.profile.include_files:
            return True

        for include_dir in self.profile.include_dirs:
            if normalized.startswith(include_dir + "/") or normalized == include_dir:
                return True

        return False

    def _detect_language(self, filepath: Path) -> str:
        name = filepath.name
        if name.endswith(".blade.php"):
            return "Blade Template"
        ext = filepath.suffix.lower()
        return LANGUAGE_MAP.get(ext, "Unknown")

    def _detect_file_type(self, relative_path: str, filename: str) -> str:
        normalized = relative_path.replace("\\", "/")
        lower = normalized.lower()

        for path_key, section_name in self.profile.section_map.items():
            if path_key.lower() in lower:
                return section_name.rstrip("s") if section_name.endswith("s") and len(section_name) > 4 else section_name

        ext = filepath.suffix.lower() if (filepath := Path(filename)) else ""
        ext = Path(filename).suffix.lower()

        lang = self._detect_language(Path(relative_path))
        if lang != "Unknown":
            return lang

        if ext == ".js":
            return "JavaScript"
        if ext == ".ts":
            return "TypeScript"
        if ext == ".css":
            return "CSS"
        if ext == ".html":
            return "HTML"
        if ext == ".json":
            return "JSON"
        if ext == ".py":
            return "Python"
        if ext == ".php":
            return "PHP"

        if "test" in lower:
            return "Test"
        if "config" in lower or "conf" in lower:
            return "Configuration"

        return "File"

    def _match_to_section(self, relative_path: str) -> tuple[str, str]:
        normalized = relative_path.replace("\\", "/")

        if "/" not in normalized:
            return ("I", "Root Files")

        for path_key, section_name in self.profile.section_map.items():
            if path_key.lower() in normalized.lower():
                for part_num, part_title in self.profile.parts:
                    if section_name.lower() in part_title.lower():
                        return (part_num, section_name)
                    if part_title.lower() in section_name.lower():
                        return (part_num, section_name)
                return ("II", section_name)

        for part_num, part_title in self.profile.parts:
            part_lower = part_title.lower()
            if any(kw in normalized.lower() for kw in part_lower.split()):
                return (part_num, part_title)

        return ("Appendix", "Other")

    def scan(self) -> ScanResult:
        logger.info(f"Scanning project: {self.root}")
        logger.info(f"Framework: {self.profile.name}")

        for dirpath, dirnames, filenames in os.walk(self.root):
            current = Path(dirpath)

            dirnames[:] = [
                d for d in dirnames
                if d not in self._exclude_dirs
            ]

            self._folders_scanned += 1

            for filename in filenames:
                filepath = current / filename
                try:
                    relative = str(filepath.relative_to(self.root))
                except ValueError:
                    continue

                if not self._should_include_file(relative):
                    self._skipped += 1
                    continue

                try:
                    stat = filepath.stat()
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime)
                except OSError as e:
                    self._errors.append(f"Cannot stat {relative}: {e}")
                    self._skipped += 1
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
            files=self._files,
            total_files=len(self._files),
            total_folders=self._folders_scanned,
            skipped_files=self._skipped,
            errors=self._errors,
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

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from framework_profiles import (
    ALL_PROFILES,
    FrameworkProfile,
    LARAVEL,
    FLASK,
    DJANGO,
    EXPRESS,
    REACT,
    VUE,
    ANGULAR,
    VANILLA_PHP,
)

logger = logging.getLogger("docgen")


@dataclass(frozen=True)
class FrameworkDetection:
    profile: FrameworkProfile
    confidence: float
    evidence: List[str]


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _has_file(root: Path, filename: str) -> bool:
    return (root / filename).exists()


def _package_has_dep(root: Path, dep_name: str) -> bool:
    pkg = root / "package.json"
    if not pkg.exists():
        return False
    try:
        data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
        all_deps = {}
        all_deps.update(data.get("dependencies", {}))
        all_deps.update(data.get("devDependencies", {}))
        return dep_name in all_deps
    except Exception:
        return False


def _requirements_has(root: Path, package_name: str) -> bool:
    req = root / "requirements.txt"
    if not req.exists():
        return False
    wanted = re.sub(r"[-_.]+", "-", package_name.lower())
    for line in _read_text_safe(req).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "git+", "http:", "https:")):
            continue
        match = re.match(r"([A-Za-z0-9][A-Za-z0-9_.-]*)", line)
        if not match:
            continue
        found = re.sub(r"[-_.]+", "-", match.group(1).lower())
        if found == wanted:
            return True
    return False


def detect_framework_details(project_root: Path) -> FrameworkDetection | None:
    root = project_root.resolve()
    logger.info(f"Auto-detecting framework in: {root}")

    if _has_file(root, "artisan") and _has_file(root, "bootstrap/app.php"):
        logger.info("Detected: Laravel")
        return FrameworkDetection(LARAVEL, 1.0, ["artisan", "bootstrap/app.php"])

    if _has_file(root, "angular.json"):
        logger.info("Detected: Angular")
        return FrameworkDetection(ANGULAR, 1.0, ["angular.json"])

    if _has_file(root, "manage.py"):
        if _requirements_has(root, "django"):
            logger.info("Detected: Django")
            return FrameworkDetection(DJANGO, 0.95, ["manage.py", "django dependency"])

    if _requirements_has(root, "flask"):
        logger.info("Detected: Flask")
        return FrameworkDetection(FLASK, 0.9, ["flask dependency"])

    if _has_file(root, "package.json"):
        if _package_has_dep(root, "express"):
            logger.info("Detected: Express/Node.js")
            return FrameworkDetection(EXPRESS, 0.95, ["package.json", "express dependency"])
        if _package_has_dep(root, "react"):
            logger.info("Detected: React")
            return FrameworkDetection(REACT, 0.95, ["package.json", "react dependency"])
        if _package_has_dep(root, "vue"):
            logger.info("Detected: Vue")
            return FrameworkDetection(VUE, 0.95, ["package.json", "vue dependency"])

    php_files = list(root.glob("*.php"))
    if php_files:
        has_laravel_indicators = False
        for pf in php_files:
            content = _read_text_safe(pf)
            if "laravel" in content.lower():
                has_laravel_indicators = True
                break
        if not has_laravel_indicators:
            logger.info("Detected: Vanilla PHP")
            return FrameworkDetection(VANILLA_PHP, 0.7, ["root PHP file without Laravel indicators"])

    logger.info("Could not auto-detect framework")
    return None


def detect_framework(project_root: Path) -> FrameworkProfile | None:
    """Backward-compatible framework detection returning only the profile."""
    result = detect_framework_details(project_root)
    return result.profile if result else None

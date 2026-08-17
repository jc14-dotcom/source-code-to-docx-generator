import json
import logging
from pathlib import Path

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
    content = _read_text_safe(req).lower()
    return package_name.lower() in content


def detect_framework(project_root: Path) -> FrameworkProfile | None:
    root = project_root.resolve()
    logger.info(f"Auto-detecting framework in: {root}")

    if _has_file(root, "artisan") and _has_file(root, "bootstrap/app.php"):
        logger.info("Detected: Laravel")
        return LARAVEL

    if _has_file(root, "angular.json"):
        logger.info("Detected: Angular")
        return ANGULAR

    if _has_file(root, "manage.py"):
        if _requirements_has(root, "django"):
            logger.info("Detected: Django")
            return DJANGO

    if _requirements_has(root, "flask"):
        logger.info("Detected: Flask")
        return FLASK

    if _has_file(root, "package.json"):
        if _package_has_dep(root, "express"):
            logger.info("Detected: Express/Node.js")
            return EXPRESS
        if _package_has_dep(root, "react"):
            logger.info("Detected: React")
            return REACT
        if _package_has_dep(root, "vue"):
            logger.info("Detected: Vue")
            return VUE

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
            return VANILLA_PHP

    logger.info("Could not auto-detect framework")
    return None

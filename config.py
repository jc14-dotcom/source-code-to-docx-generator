from typing import Dict, List

EXCLUDE_DIRS: List[str] = [
    "vendor",
    "node_modules",
    "storage",
    ".github",
    ".git",
    "_archive",
    ".codegpt",
]

EXCLUDE_FILES: List[str] = [
    ".env",
    "desktop.ini",
    "Thumbs.db",
]

EXCLUDE_EXTENSIONS: List[str] = [
    ".log",
    ".sqlite",
    ".zip",
    ".rar",
]

SECRET_PATTERNS: Dict[str, str] = {
    "API Key": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']+["\']',
    "Google API Key": r'(?i)AIza[0-9A-Za-z\-_]{35}',
    "Firebase Key": r'(?i)(firebase|firestore)[_-]?key\s*[=:]\s*["\'][^"\']+["\']',
    "OpenAI Key": r'(?i)sk-[0-9A-Za-z]{48,}',
    "AWS Access Key ID": r'(?i)AKIA[0-9A-Z]{16}',
    "AWS Secret Key": r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\'][^"\']+["\']',
    "SMTP Password": r'(?i)(smtp[_-]?password|mail[_-]?password)\s*[=:]\s*["\'][^"\']+["\']',
    "Database Password": r'(?i)(db[_-]?password|database[_-]?password|DB_PASSWORD)\s*[=:]\s*["\'][^"\']+["\']',
    "Bearer Token": r'(?i)(bearer|token)\s*[=:]\s*["\'][A-Za-z0-9\-._~+/]+=*["\']',
    "Private Key": r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
    "Certificate": r'-----BEGIN CERTIFICATE-----',
    "JWT Secret": r'(?i)(jwt[_-]?secret|JWT_SECRET)\s*[=:]\s*["\'][^"\']+["\']',
}

LANGUAGE_MAP: Dict[str, str] = {
    ".php": "PHP",
    ".blade.php": "Blade Template",
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JSX",
    ".tsx": "TSX",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".html": "HTML",
    ".htm": "HTML",
    ".vue": "Vue",
    ".json": "JSON",
    ".xml": "XML",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".md": "Markdown",
    ".txt": "Text",
    ".env": "Environment",
    ".sql": "SQL",
    ".gitignore": "Git Ignore",
    ".twig": "Twig",
    ".hbs": "Handlebars",
    ".ejs": "EJS",
    ".pug": "Pug",
    ".rb": "Ruby",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".cpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".kt": "Kotlin",
}

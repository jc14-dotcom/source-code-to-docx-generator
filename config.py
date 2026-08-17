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
    ".docx",
    ".pdf",
]

COMMON_PROJECT_FILES: List[str] = [
    "Dockerfile",
    "Makefile",
    "Procfile",
    "pyproject.toml",
    "setup.cfg",
    "tox.ini",
    "webpack.config.js",
    "rollup.config.js",
]

SECRET_PATTERNS: Dict[str, str] = {
    # Match the complete PEM block. Redacting only the BEGIN line would leave
    # the private-key material in the generated document.
    "Private Key": (
        r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ED25519 |ENCRYPTED )?PRIVATE KEY-----'
        r'[\s\S]*?'
        r'-----END (?:RSA |EC |DSA |OPENSSH |ED25519 |ENCRYPTED )?PRIVATE KEY-----'
    ),
    "API Key": r'(?i)\b(?:api[_-]?key|apikey)\s*[=:]\s*["\'][^"\'\r\n]+["\']',
    "Google API Key": r'(?i)\bAIza[0-9A-Za-z\-_]{35}\b',
    "Firebase Key": r'(?i)\b(?:firebase|firestore)[_-]?key\s*[=:]\s*["\'][^"\'\r\n]+["\']',
    "OpenAI Key": r'(?i)\bsk-(?:proj-)?[0-9A-Za-z]{48,}\b',
    "AWS Access Key ID": r'\bAKIA[0-9A-Z]{16}\b',
    "AWS Secret Key": (
        r'(?i)\b(?:aws[_-]?secret[_-]?access[_-]?key|AWS_SECRET_ACCESS_KEY)'
        r'\s*[=:]\s*["\'][^"\'\r\n]+["\']'
    ),
    "SMTP Password": r'(?i)\b(?:smtp[_-]?password|mail[_-]?password)\s*[=:]\s*["\'][^"\'\r\n]+["\']',
    "Database Password": r'(?i)\b(?:db[_-]?password|database[_-]?password|DB_PASSWORD)\s*[=:]\s*["\'][^"\'\r\n]+["\']',
    "JWT Secret": r'(?i)\b(?:jwt[_-]?secret|JWT_SECRET)\s*[=:]\s*["\'][^"\'\r\n]+["\']',
    # Deliberately require an authorization header or the Bearer scheme. A
    # generic `token = ...` rule creates many false positives in source code.
    "Bearer Token": (
        r'(?i)\b(?:authorization|auth[_-]?header)\s*[=:]\s*["\']?\s*Bearer\s+'
        r'[A-Za-z0-9\-._~+/]+=*["\']?'
    ),
    "GitHub Token": r'\bgh[pousr]_[A-Za-z0-9_]{36,}\b',
    "Slack Token": r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b',
    "Stripe Secret Key": r'\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b',
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

# Source Code to DOCX Generator

Source Code to DOCX Generator is a Python tool that scans a software project and creates a formatted Microsoft Word document containing its source-code documentation.

It is designed for software documentation and copyright-registration workflows, including the document format used for IPOPHL-related submissions.

## Features

- Interactive GUI and command-line usage.
- Automatic framework detection with confidence and evidence reporting.
- Manual framework selection when automatic detection is uncertain.
- Support for:
  - Laravel
  - Flask
  - Vanilla PHP
  - Django
  - Express/Node.js
  - React
  - Vue
  - Angular
- Framework-aware source-file discovery and classification.
- Exclusion of dependency folders, caches, build output, environment variants, and generated document files.
- Detection and redaction of common credentials and private keys.
- Final safety validation of the generated DOCX before it replaces the output file.
- Formatted title page, summary, table of contents, metadata, headers, footers, and source-code sections.
- Deterministic estimated table-of-contents page numbers.

## How it works

```text
Select project
      ↓
Detect or select framework
      ↓
Scan and classify source files
      ↓
Redact detected secrets
      ↓
Calculate estimated TOC page numbers
      ↓
Generate and validate DOCX
```

The original project files are not modified. The program reads the project and writes a generated `.docx` document.

## Requirements

- Python 3.10 or newer
- `python-docx`
- Tkinter is optional and is only needed for the graphical folder and framework selectors.

## Installation

Clone the repository and open a terminal in the project folder:

```powershell
git clone https://github.com/jc14-dotcom/source-code-to-docx-generator.git
cd source-code-to-docx-generator
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

If PowerShell blocks script activation, you can run the program through the virtual environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

## Usage

### Interactive mode

Run the program without arguments:

```powershell
python main.py
```

The program will ask you to select the project folder, choose a framework if necessary, and enter the system name.

### Fully specified command

For repeatable or automated usage, provide the project path, framework, system name, and output filename:

```powershell
python main.py "C:\Path\To\YourProject" `
  --framework Django `
  --name "My Software System" `
  --output "my-documentation.docx"
```

The supported framework names are:

```text
Laravel
Flask
Vanilla PHP
Django
Express/Node.js
React
Vue
Angular
```

Relative output filenames are created inside the selected project folder. An absolute output path can be used when the document should be stored elsewhere.

### Display command-line options

```powershell
python main.py --help
```

## Security and secret redaction

Before source code is inserted into the DOCX, the program searches for several common secret formats, including:

- API keys
- Google and Firebase keys
- OpenAI keys
- AWS access and secret keys
- Database, SMTP, and JWT passwords
- Bearer authorization tokens
- GitHub, Slack, and Stripe tokens
- PEM private keys

Detected secrets are replaced with:

```text
[REDACTED]
```

Private keys are redacted as complete blocks, including their headers, contents, and ending lines.

Example:

```text
-----BEGIN PRIVATE KEY-----
secret-key-content
-----END PRIVATE KEY-----
```

becomes:

```text
[REDACTED]
```

The detector is pattern-based and cannot guarantee that every possible secret format will be found. Always review generated documents before sharing or submitting them.

## DOCX and table-of-contents behavior

The generated document contains:

- Title page
- System summary
- Table of contents
- Part and section headings
- File metadata
- Source code
- Header and footer information
- Page numbers

TOC page numbers are deterministic estimates based on the configured page size, margins, fonts, source-line wrapping, metadata, headings, and explicit page breaks.

Exact pagination can vary depending on the Word version, installed fonts, printer settings, and document-rendering environment. The generated document identifies the TOC numbers as estimated page numbers for this reason.

## Project structure

| File or folder | Purpose |
| --- | --- |
| `main.py` | Command-line and GUI entrypoint |
| `scanner.py` | File discovery, exclusions, classification, and scan statistics |
| `framework_detector.py` | Framework detection, confidence, and evidence |
| `framework_profiles.py` | Rules for supported frameworks |
| `secrets_detector.py` | Secret detection and redaction |
| `document_generator.py` | DOCX layout, TOC calculation, rendering, and safety validation |
| `models.py` | Typed scan and document data models |
| `config.py` | Exclusion lists, language mapping, and secret patterns |
| `tests/` | Automated regression and integration tests |

## Running the tests

Run the complete test suite with:

```powershell
python -m unittest discover -s tests -v
```

The tests cover:

- Secret detection and complete private-key redaction
- Framework detection and dependency matching
- File discovery and exclusion rules
- Path-based file classification
- DOCX generation and final secret validation
- TOC pagination calculations

## Development status

The current version includes the initial improvement phases for:

- Security and credential redaction
- Broader file discovery and framework classification
- Scanner and data-model cleanup
- Faster DOCX source rendering
- Deterministic TOC page estimation

Planned future improvements include:

- Renderer-assisted exact page-number verification
- Additional framework profiles and customizable profiles
- More non-interactive CLI options
- Packaging and continuous integration
- Additional output formats such as HTML or Markdown

## Contributing

When contributing:

1. Create a feature branch.
2. Make focused changes.
3. Add or update tests for behavior changes.
4. Run the complete test suite.
5. Explain the change and its test coverage in the pull request.

## License

No license file has been selected for this repository yet. Add a license before distributing the project publicly if specific reuse terms are required.

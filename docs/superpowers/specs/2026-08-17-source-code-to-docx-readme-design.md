# Source Code to DOCX Generator README Design

## Purpose

Create a root `README.md` that serves two audiences at the same time:

1. Developers who need to install, run, test, and extend the program.
2. Reviewers and evaluators who need to understand the program's purpose, workflow, capabilities, security behavior, and current limitations.

The README should be useful without requiring the reader to inspect the Python source first.

## Audience and tone

- Use plain, professional language.
- Lead with the program's purpose and outcome.
- Keep commands copyable for Windows PowerShell, while noting the equivalent Python entrypoint.
- Explain technical behavior briefly before showing implementation details.
- Be honest about estimated TOC page numbers and framework-profile limitations.

## Proposed README structure

### 1. Title and overview

Introduce the Source Code to DOCX Generator as a Python tool that scans selected software projects and creates a formatted DOCX source-code documentation package.

Explain that the generated document is intended to support software documentation and copyright-registration workflows, including the IPOPHL-oriented document format already present in the application.

### 2. Features

Describe the currently implemented capabilities:

- GUI and command-line project selection.
- Framework auto-detection and manual framework selection.
- Support for Laravel, Flask, Vanilla PHP, Django, Express/Node.js, React, Vue, and Angular profiles.
- Profile-based source discovery and conventional source-file discovery.
- Exclusion of dependencies, caches, build output, environment variants, and generated document files.
- Secret detection and redaction before source is written into the DOCX.
- Final DOCX safety validation before the output replaces the destination file.
- Framework evidence and confidence reporting.
- Deterministic estimated table-of-contents page numbers.

### 3. Workflow

Show the processing flow in simple terms:

`Select project → detect/select framework → scan and classify files → redact secrets → estimate TOC pages → generate and validate DOCX`

Explain that the original project files are not modified; only the generated documentation file is written.

### 4. Requirements and installation

Document:

- Python version expectation based on the current code's modern type-hint syntax.
- `python-docx` installation through `requirements.txt`.
- Optional GUI requirement: Tkinter availability for the graphical selectors.
- PowerShell commands for creating an environment and installing dependencies.

Avoid claiming a packaged installer or supported operating systems beyond what the repository demonstrates.

### 5. Usage

Include both modes:

- Interactive: `python main.py`
- Fully specified/headless-style command using project path, framework, system name, and output filename.

Explain the supported framework names and that an explicit framework can be used when auto-detection is uncertain.

Include a command for running the test suite.

### 6. Security behavior

Explain that detected secrets are replaced with `[REDACTED]`, including complete private-key blocks rather than only their headers.

Mention supported examples such as API keys, provider tokens, passwords, bearer authorization values, and private keys.

Clearly state that redaction is pattern-based and should not be treated as a guarantee that every possible secret format will be found. Recommend reviewing generated documents before sharing them.

### 7. DOCX and TOC behavior

Explain that the generator creates a formatted DOCX with title, summary, TOC, sections, metadata, source code, headers, footers, and page numbers.

State that TOC page numbers are deterministic estimates based on configured page dimensions, styles, source line wrapping, metadata, headings, and explicit page breaks. Exact Word-rendered pagination can vary by Word version, fonts, and rendering environment.

### 8. Project structure

Briefly describe the responsibilities of the main modules:

- `main.py`: CLI and GUI entrypoint.
- `scanner.py`: discovery, exclusions, classification, and scan statistics.
- `framework_detector.py`: framework detection and evidence.
- `framework_profiles.py`: supported framework rules.
- `secrets_detector.py`: pattern-based detection and redaction.
- `document_generator.py`: DOCX layout, TOC calculation, rendering, and safety validation.
- `models.py`: typed scan and document data models.
- `tests/`: regression and integration tests.

### 9. Testing

Provide the exact unittest discovery command and summarize the test areas: secret handling, framework detection, scanner behavior, DOCX generation, and TOC pagination estimates.

### 10. Development status and roadmap

Summarize completed improvement phases and identify future work without presenting estimates as guarantees. Future work may include renderer-assisted exact pagination, broader profiles, improved CLI automation, and packaging/CI.

### 11. Contributing and license

Include a concise contribution workflow: create a branch, add tests for behavior changes, run the test suite, and explain changes in the pull request.

Use a clearly marked license placeholder only if no license file exists; do not claim an unselected license.

## Acceptance criteria

- A new developer can install dependencies and run the generator from the README.
- A reviewer can understand the program's purpose and processing flow without reading source code.
- All commands refer to files and options that exist in the repository.
- Supported frameworks match `framework_profiles.py`.
- Security and TOC behavior are described accurately, including their limitations.
- The README contains no unmarked placeholders or unsupported claims.
- Markdown structure is readable on GitHub.

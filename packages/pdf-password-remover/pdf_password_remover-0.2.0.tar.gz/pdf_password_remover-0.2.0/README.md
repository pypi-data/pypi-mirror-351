# PDF Password Remover

A Python-based CLI tool to remove passwords from PDF files. Supports both single files and batch processing of directories. Includes an optional GUI file picker for convenience.

[![PyPI version](https://badge.fury.io/py/pdf-password-remover.svg)](https://badge.fury.io/py/pdf-password-remover)
[![Builds and Tests](https://github.com/thecasualdev17/pdf-password-remover/actions/workflows/build-test.yml/badge.svg)](https://github.com/thecasualdev17/pdf-password-remover/actions/workflows/build-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features
- ✅Remove passwords from individual PDF files or all PDFs in a directory
- ✅Optional GUI file/directory picker
- ✅Output unlocked PDFs to a specified directory
- ✅Simple command-line interface

## Installation

### From PyPI

Install the latest release from PyPI:
```sh
pip install pdf-password-remover
```

### From Source

1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd pdf-password-remover
   ```
2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

## Usage

Run the CLI tool using Poetry:

```sh
poetry run pdf-password-remover remove-password [INPUT_PATH] [PASSWORD] [--output OUTPUT_DIR]
```

Or, if installed via pip:

```sh
pdf-password-remover remove-password [INPUT_PATH] [PASSWORD] [--output OUTPUT_DIR]
```

- `INPUT_PATH`: Path to the password-protected PDF file or directory (optional, will prompt if omitted)
- `PASSWORD`: Password for the PDF file(s) (optional, will prompt if omitted)
- `--output`/`-o`: Directory to save the unlocked PDF file(s) (optional)

### Example

Remove password from a single file:
```sh
pdf-password-remover remove-password myfile.pdf mypassword
```

Batch process a directory and specify output directory:
```sh
pdf-password-remover remove-password ./pdfs mypassword --output ./unlocked
```

If you omit arguments, the tool will prompt you interactively and offer a GUI picker.

## Development

- Source code is in `src/pdf_password_remover/`
- Main CLI entry point: `main.py`
- PDF utilities: `pdf_utils.py`

## License
MIT


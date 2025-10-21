# textindex-ply

A simple, lightweight syntax and CLI for creating indexes in text documents,
parsed with PLY (Python Lex-Yacc).
It scans your text/Markdown for TextIndex markup and emits a basic index.
This repository contains the lexer, parser, index builder, and a small
command-line tool.

> Status: Alpha (0.1.0). Interface and syntax may change.

## Overview

textindex-ply provides:
- A tokenizer and parser (PLY-based) for a compact TextIndex markup.
- An index builder that turns parsed nodes into a simple HTML description list.
- A CLI `textindex-ply` that reads an input file and prints the generated index.

See the working notes in `textindex-docs.txt` for some additional background.
A richer example document is planned for
`src/textindex_ply/data/example_markdown.md`.

## Tech stack

- Language: Python 3.12+
- Parser: [PLY](https://www.dabeaz.com/ply/)
- Build backend: `uv_build` (for PEP 517 builds)
- Package/dependency manager: `uv` (lockfile present: `uv.lock`).
  Regular `pip` also works if preferred.
- Testing: `pytest` (+ `xdoctest` via pytest plugin)
- Lint/format: `ruff`, `pylint`

## Requirements

- Python >= 3.12
- A POSIX-like shell (macOS, Linux, WSL) or Windows PowerShell/CMD
- If using `uv`: install from https://docs.astral.sh/uv/
- If using `pip`: any recent `pip` will do

Runtime dependencies (installed automatically):
- `ply>=3.11`

Dev/test dependencies (optional):
- `pytest`, `pytest-cov`, `xdoctest`, `ruff`, `pylint`, `pyfakefs`

Defined in `pyproject.toml` under `[project]` and `[dependency-groups.dev]`.

## Installation

Using uv (recommended):

- From source, in an isolated environment:
  - Create and activate a virtual environment (managed by uv):
    - `uv venv` (creates .venv)
    - `source .venv/bin/activate` (Linux/macOS) or
      `.venv\\Scripts\\activate` (Windows)
  - Install:
    - `uv pip install -e .`  (editable) or
    - `uv pip install .`     (regular)

Using pip:

- Create/activate a virtual environment with your preferred tool, then:
  - `pip install -e .`  or `pip install .`

## CLI usage

The package exposes a console script named `textindex-ply`.

Basic usage:

- Read a file and print the index to stdout:
  - `textindex-ply path/to/input.md`

- Write the index to a file:
  - `textindex-ply path/to/input.md --output index.html`

- Verbose mode (adds a summary line to stderr/stdout):
  - `textindex-ply path/to/input.md -v`

CLI reference (from `src/textindex_ply/cli.py`):
- Positional: `input` (Path to the input Markdown/text file)
- Options: `-o/--output` (Path), `-v/--verbose` (flag)

Note: The current index builder outputs a simple HTML description list.
Further formatting and richer index features are planned.

## Example input

A more complete example is planned for:
`src/textindex_ply/data/example_markdown.md`.

- TODO: Provide a minimal snippet of TextIndex markup here once the syntax is
  finalized/documented in `textindex-docs.txt`.

## Python API (WIP)

While the CLI is the primary interface, you can also import pieces:

- `textindex_ply.lexer.make_lexer()`
- `textindex_ply.parser.make_parser()`
- `textindex_ply.index_builder.build_index()`

Example (pseudo):

```python
from textindex_ply.lexer import make_lexer
from textindex_ply.parser import make_parser
from textindex_ply.index_builder import build_index

text = open("input.md", "r", encoding="utf-8").read()
lexer = make_lexer()
ply_parser = make_parser()
ast_nodes = ply_parser.parse(text, lexer=lexer)
html_index = build_index(ast_nodes)
```

## Environment variables

- The CLI or library currently uses no required environment variables.
- TODO: If future configuration requires env vars (e.g., feature toggles),
  document them here.

## Development

- Create an environment (uv or your preferred tool) and install dev deps:
  - With uv: `uv pip install -e .[dev]` or
    `uv pip install -r <(uv export --group dev)`
    - Note: uv supports dependency groups from `pyproject.toml`.
  - With pip: install dev tools individually as listed above.

Common tasks:
- Lint (ruff): `ruff check .`
- Format (ruff): `ruff format .`
- Lint (pylint): `pylint src/textindex_ply`
- Run tests (pytest): `pytest -vvv`

pytest is configured via `[tool.pytest.ini_options]` in `pyproject.toml` to:
- Enable doctests (`--doctest-modules`)
- Enable xdoctest (`--xdoctest`)
- Increase verbosity (`-vvv`)
- Test paths: `src/textindex_ply/` and `tests/`

Coverage settings are present but coverage collection flags are currently
commented out in `pyproject.toml` (`addopts`).
You can run with coverage manually:
- `pytest --cov --cov-branch --cov-report=term --cov-report=xml:coverage.xml`

## Project structure

```
textindex_ply/
├─ pyproject.toml
├─ README.md
├─ CHANGELOG.md
├─ LICENSE.md
├─ CODE_OF_CONDUCT.md
├─ CONTRIBUTING.md
├─ uv.lock
├─ textindex-docs.txt
├─ src/
│  └─ textindex_ply/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ lexer.py
│     ├─ parser.py
│     ├─ ast.py
│     ├─ index_builder.py
│     ├─ directives.py
│     ├─ errors.py
│     ├─ utils.py
│     ├─ parsetab.py
│     └─ data/
│        ├─ __init__.py
│        └─ example_markdown.md
├─ tests/
│  ├─ conftest.py
│  ├─ test_cli.py
│  ├─ test_directive_args.py
│  ├─ test_index_builder.py
│  ├─ test_lexer.py
│  └─ test_parser.py
└─ coverage.xml (generated by coverage if enabled)
```

## Scripts and entry points

- Console script: `textindex-ply` → `textindex_ply.cli:main`
  (defined in `[project.scripts]`)
- Build: PEP 517 via `uv_build` (defined in `[build-system]`)
- No additional make/nox/tox scripts provided in this repo.

## Tests

- To run all tests: `pytest -vvv`
- To run doctests included in modules: `pytest --doctest-modules`
- To run xdoctest: `pytest --xdoctest`

If you use `uv`, you can also run tests via a one-off environment:
- `uv run pytest -vvv`

## Contributing

Please see `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

## License

GPL-3.0-or-later. See `LICENSE.md`.

## Changelog

See `CHANGELOG.md` for notable changes.

# Junie Guidelines for textindex_ply

These are the project-specific working rules for Junie in this repository.
They build on .ai/aiGuidelines.md and align with pyproject.toml.

## Project overview
- Name: textindex_ply
- Project summary: Provide a simple syntax to annotate indexes
  (in the end-of-a-book sense) in Markdown or other text documents using PLY.
- Package layout: src/textindex_ply/ (code), tests/ (pytest), docs/
  (Markdown docs)
- CLI entry point: textindex-ply -> textindex_ply.cli:main
- Python: >=3.12 (support 3.13 where reasonable)
- Dependencies: ply>=3.11

## Coding standards (must)
- Line length 80 chars. Wrap code, comments, and docstrings.
- Type hints everywhere; mypy strict, no implicit Any.
- Docstrings: Google style; include Args, Returns, Raises, Examples when
  helpful; examples xdoctest-ready.
- Prefer stdlib (pathlib, tomllib). Avoid heavy deps.
- Keep functions small, cohesive, and DRY. Avoid global state.

## Parser/Lexer (PLY) practices
- Keep lexer/token definitions separate from parser rules.
- Name tokens/rules clearly; document precedence and intent.
- Provide small runnable examples for any grammar changes.
- Raise descriptive errors with context (line/column/snippet when possible).

## Tooling expectations
- mypy: strict; narrow exceptions; explicit types.
- ruff: enforce formatting and lint rules per pyproject (D,E,I,N,R,W).
- pylint: respect limits (e.g., max-args=6); focused on disabling only with
  short justification.
- pytest/xdoctest: doctests enabled; xdoctest enabled; verbose (-vvv).

## Code organization
- Utility functions: full definition + docstring in one block.
- Class method order:
  1) __init__
  2) Public methods (alphabetical)
  3) Private/helper methods (alphabetical)
  4) Dunder methods (alphabetical)
- Keep cyclomatic complexity < 10; extract helpers.

## Testing requirements
- Tests live in tests/.
- Use pytest for unit tests.
- At least one test module per source module when adding/expanding features.
- Aim for >=80% per-file coverage.
- Fixtures go in conftest.py.
- Use pyfakefs for filesystem interactions.
- Provide doctest-ready examples in docstrings for core functions.

## CLI and API
- Do not break public API or CLI without a clear migration note.
- CLI should:
  - Use Typer for building CLI.
  - Use Rich for enhanced terminal output formatting.
  - Return non-zero exit codes on error; print actionable messages to stderr.
  - Be testable: isolate I/O; keep parsing/transform logic separate.
- Provide small, documented module-level functions for core operations.

## Documentation
- Update README examples when behavior changes.
- Additional Markdown documentation lives in docs/.
- Provide runnable examples for CLI and library functions.

## Git and commit messages

- Use gitmoji style, imperative mood, ≤ ~72 chars.
  - Examples:
    - :sparkles: (option) Add map_or_else helper
    - :bug: Fix Result comparison for None values
    - :memo: Update docs for Option.unwrap behavior
- Squash/amend to avoid WIP noise.

For general guidance, see .ai/aiGuidelines.md. Update this
file if the repository configuration changes.

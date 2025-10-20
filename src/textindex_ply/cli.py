#  textindex_ply - A simple, lightweight syntax for creating indexes in text
#  documents using ply.
#  Copyright © 2025 Michael Cummings <mgcummings@yahoo.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  SPDX-License-Identifier: GPL-3.0-or-later
# ##############################################################################

"""Command-line interface for textindex-ply."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .lexer import make_lexer
from .parser import make_parser
from .index_builder import build_index


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for textindex-ply."""
    parser = argparse.ArgumentParser(
        prog="textindex-ply",
        description="Generate an index from TextIndex markup using a PLY-based parser.",
    )
    parser.add_argument(
        "input", type=Path, help="Path to the input Markdown/text file."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file for processed text (default: stdout).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging.",
    )

    args = parser.parse_args(argv)

    text = args.input.read_text(encoding="utf-8")

    # Initialize components
    lexer = make_lexer()
    ply_parser = make_parser()
    index_data = ply_parser.parse(text, lexer=lexer)

    output = build_index(index_data)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)

    if args.verbose:
        print(f"Processed {args.input} -> {args.output or 'stdout'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

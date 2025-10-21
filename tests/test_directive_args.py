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

"""Tests for {index ...} directive argument parsing."""

from textindex_ply.ast import IndexDirective
from textindex_ply.lexer import make_lexer
from textindex_ply.parser import make_parser


def parse_text(text: str) -> IndexDirective:
    """Helper to lex + parse a TextIndex directive and return the AST node."""
    lexer = make_lexer()
    parser = make_parser()
    result = parser.parse(text, lexer=lexer)
    assert isinstance(result, IndexDirective)
    return result


def test_index_directive_with_single_arg():
    """Parses a single key=value pair."""
    result = parse_text('{index term="Foo"}')
    assert result.name == "index"
    assert result.args["term"] == "Foo"
    assert result.kind == "insert"


def test_index_directive_with_multiple_args():
    """Parses multiple key=value pairs."""
    result = parse_text('{index term="Foo" see="Bar" sort="baz"}')
    assert result.args == {"term": "Foo", "see": "Bar", "sort": "baz"}
    assert result.kind in ("insert", "see")  # accept derived kinds


def test_index_directive_kind_auto_see():
    """Auto-detects 'see' kind when see= is present."""
    result = parse_text('{index see="Bar"}')
    assert result.kind == "see"
    assert result.args["see"] == "Bar"


def test_index_directive_no_args():
    """Handles directive with no args gracefully."""
    result = parse_text("{index}")
    assert result.name == "index"
    assert result.args == {}
    assert result.kind == "insert"


def test_index_directive_kind_range():
    """Recognizes range directives."""
    result = parse_text('{index range="A–C"}')
    assert isinstance(result, IndexDirective)
    assert result.kind == "range"
    assert result.args["range"] == "A–C"

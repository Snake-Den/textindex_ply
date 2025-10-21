# noqa: D100
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

from textindex_ply.ast import IndexDirective, IndexRangeBlock
from textindex_ply.lexer import make_lexer
from textindex_ply.parser import make_parser


def parse_text(text: str):
    """Helper to create lexer and parser and return the parsed IndexMark."""
    lexer = make_lexer()
    parser = make_parser()
    return parser.parse(text, lexer=lexer)


def test_simple_mark_parsing():
    result = parse_text("{^heading}")
    assert result.heading == "heading"
    assert result.subheadings == []
    assert not result.crossrefs


def test_complex_mark_parsing():
    text = '{^"foo">bar|baz+qux[suffix]~"sort"!}'
    result = parse_text(text)

    assert result.heading == "foo"
    assert result.subheadings == ["bar"]
    assert result.crossrefs == ["baz", "qux"]
    assert result.suffix == "suffix"
    assert result.sort_key == "sort"
    assert result.emphasis is True
    assert result.closing is False


def test_alias_and_wildcard_parsing():
    # Alias examples
    result = parse_text("{^#term}")
    assert result.alias == "#term"
    assert result.wildcard is None

    result = parse_text("{^##secondary}")
    assert result.alias == "##secondary"

    # Wildcards
    result = parse_text("{^*}")
    assert result.wildcard == "*"

    result = parse_text("{^*^-}")
    assert result.wildcard == "*^-"


def test_index_directive_basic():
    lexer = make_lexer()
    parser = make_parser()

    result = parser.parse("{index}", lexer=lexer)
    assert isinstance(result, IndexDirective)
    assert result.kind == "insert"

    result = parser.parse("{index+}", lexer=lexer)
    assert result.kind == "open"

    result = parser.parse("{index-}", lexer=lexer)
    assert result.kind == "close"

    result = parser.parse("{index!}", lexer=lexer)
    assert result.kind == "force"


def test_index_range_block():
    text = '{index+ range="A–C"}foo bar{index-}'
    result = parse_text(text)
    assert isinstance(result, IndexRangeBlock)
    assert result.start.kind == "open"
    assert result.start.args["range"] == "A–C"
    assert result.end.kind == "close"
    assert "foo" in result.content


def test_processing_control_parsing():
    from textindex_ply.ast import ProcessingControl

    result = parse_text("{^-}")
    assert isinstance(result, ProcessingControl)
    assert not result.enabled

    result = parse_text("{^+}")
    assert isinstance(result, ProcessingControl)
    assert result.enabled

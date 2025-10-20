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

from textindex_ply.lexer import make_lexer


def token_types(text: str):
    return [t for t, _ in tokenize(text)]


def tokenize(text: str):
    """Helper: return list of (type, value) tuples."""
    lexer = make_lexer()
    lexer.input(text)
    return [(tok.type, tok.value) for tok in lexer]


def test_basic_lexer_tokens():
    tokens = [t for t, _ in tokenize('{^"foo"}')]
    assert tokens == ["LBRACE", "CARET", "QUOTED", "RBRACE"]


def test_heading_path_tokens():
    tokens = [t for t, _ in tokenize("foo>bar>baz")]
    assert tokens == ["TEXT", "GT", "TEXT", "GT", "TEXT"]


def test_suffix_and_sort_tokens():
    tokens = [t for t, _ in tokenize('[suffix]~"sortkey"')]
    assert tokens == ["LBRACKET", "TEXT", "RBRACKET", "TILDE", "QUOTED"]


def test_crossref_and_flags():
    tokens = [t for t, _ in tokenize("|foo;+bar!")]
    assert tokens == ["PIPE", "TEXT", "PLUS", "TEXT", "EXCL"]


def test_alias_and_wildcards():
    pairs = tokenize("#term ** *^")
    assert "HASH" in token_types("#term ** *^")
    assert any(val.startswith("*") for t, val in pairs if t == "TEXT")

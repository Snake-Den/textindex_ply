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
"""Lexical analyzer for TextIndex markup using PLY."""

from __future__ import annotations

import ply.lex as lex


# noinspection PyPep8Naming
def make_lexer() -> lex.Lexer:
    """Construct a PLY lexer for TextIndex."""
    tokens = (
        "LBRACE",
        "RBRACE",
        "CARET",
        "SLASH",
        "EXCL",
        "PIPE",
        "PLUS",
        "TILDE",
        "HASH",
        "GT",
        "LBRACKET",
        "RBRACKET",
        "QUOTED",
        "TEXT",
    )

    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_CARET = r"\^"
    t_SLASH = r"/"
    t_EXCL = r"!"
    t_PIPE = r"\|"
    t_PLUS = r"\+"
    t_TILDE = r"~"
    t_HASH = r"\#"
    t_GT = r">"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_ignore = " \t"

    # Explicit quote token rules — PLY-safe
    def t_DQUOTE_STRING(t):
        r'"(?:\\.|[^"\\])*"'
        t.type = "QUOTED"
        t.value = t.value[1:-1]
        return t

    def t_SQUOTE_STRING(t):
        r"'(?:\\.|[^'\\])*'"
        t.type = "QUOTED"
        t.value = t.value[1:-1]
        return t

    def t_WILDCARD(t):
        r"\*\*|\*\^\-|\*\^|\*"
        t.type = "TEXT"
        return t

    def t_TEXT(t):
        r"[^{}\[\]>|+~#/\^!\s]+"
        return t

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        print(f"Illegal character {t.value[0]!r} at line {t.lexer.lineno}")
        t.lexer.skip(1)

    return lex.lex()

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

"""Parser for TextIndex markup using PLY (LALR(1))."""

from __future__ import annotations

import ply.yacc as yacc
from .ast import IndexDirective, IndexMark


def make_parser() -> yacc.LRParser:
    """Create the PLY parser."""
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

    # ------------------------------
    # Grammar rules
    # ------------------------------

    def p_start(p):
        """start : mark
        | directive"""
        p[0] = p[1]

    def p_mark(p):
        """mark : LBRACE CARET heading_path opt_crossrefs opt_suffix opt_sort opt_flag RBRACE"""
        heading_path = p[3]
        alias = next((h for h in heading_path if h.startswith("#")), None)
        wildcard = next((h for h in heading_path if h.startswith("*")), None)

        p[0] = IndexMark(
            heading=heading_path[0],
            subheadings=heading_path[1:],
            crossrefs=p[4],
            suffix=p[5],
            sort_key=p[6],
            emphasis=p[7] == "!",
            closing=p[7] == "/",
            alias=alias,
            wildcard=wildcard,
        )

    def p_directive(p):
        """directive : LBRACE TEXT RBRACE"""
        # Matches things like {index}
        # Later, we’ll extend this to handle arguments, e.g. {index term="foo"}

        p[0] = IndexDirective(name=p[2])

    def p_heading_path(p):
        """heading_path : heading_part
        | heading_path GT heading_part"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_heading_part(p):
        """heading_part : TEXT
        | QUOTED
        | HASH TEXT
        | HASH HASH TEXT"""
        if len(p) == 2:
            # Normal or wildcard heading
            p[0] = p[1]
        elif len(p) == 3:
            # Alias (#term)
            p[0] = f"#{p[2]}"
        elif len(p) == 4:
            # Secondary alias (##term)
            p[0] = f"##{p[3]}"

    def p_opt_crossrefs(p):
        """opt_crossrefs : PIPE crossref_list
        | empty"""
        p[0] = p[2] if len(p) == 3 else []

    def p_crossref_list(p):
        """crossref_list : crossref
        | crossref_list PLUS crossref"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_crossref(p):
        """crossref : heading_path"""
        p[0] = ">".join(p[1])

    def p_opt_suffix(p):
        """opt_suffix : LBRACKET TEXT RBRACKET
        | empty"""
        p[0] = p[2] if len(p) == 4 else None

    def p_opt_sort(p):
        """opt_sort : TILDE TEXT
        | TILDE QUOTED
        | empty"""
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None

    def p_opt_flag(p):
        """opt_flag : EXCL
        | SLASH
        | empty"""
        p[0] = p[1] if len(p) == 2 else None

    def p_empty(p):
        """empty :"""
        p[0] = None

    def p_error(p):
        if p:
            print(
                f"Syntax error at {p.value!r} (line {getattr(p, 'lineno', '?')})"
            )
        else:
            print("Syntax error at EOF")

    return yacc.yacc(debug=False)

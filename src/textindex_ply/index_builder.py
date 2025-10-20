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

"""Builds a structured index from parsed TextIndex AST nodes."""

from __future__ import annotations

from typing import List
from .ast import IndexMark


def build_index(entries: List[IndexMark]) -> str:
    """Convert a list of index marks into a simple textual index (placeholder)."""
    if not entries:
        return "<p><em>No index entries found.</em></p>"

    out = ["<dl class='index textindex'>"]
    for entry in entries:
        out.append(f"  <dt>{entry.heading}</dt>")
    out.append("</dl>")
    return "\n".join(out)

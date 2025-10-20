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

"""AST node definitions for TextIndex markup."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(slots=True)
class IndexMark:
    """Represents a single index mark in the document."""

    heading: str
    alias: Optional[str] = None
    closing: bool = False
    crossrefs: List[str] = field(default_factory=list)
    emphasis: bool = False
    sort_key: Optional[str] = None
    subheadings: List[str] = field(default_factory=list)
    suffix: Optional[str] = None
    wildcard: Optional[str] = None


@dataclass(slots=True)
class IndexDirective:
    """Represents a {index ...} directive in TextIndex markup."""

    args: Dict[str, Any] = field(default_factory=dict)
    kind: str = "insert"
    name: str = "index"
    options: dict[str, str] = field(default_factory=dict)
    raw: str = ""  # full text of the directive

    def __repr__(self) -> str:
        if self.args:
            return f"<IndexDirective {self.name} args={self.args}>"
        return f"<IndexDirective {self.name}>"

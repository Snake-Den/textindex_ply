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
class IndexDirective:
    """Represents a {index ...} directive in TextIndex markup."""

    name: str = "index"
    kind: str = "insert"
    args: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Determine the directive kind from suffix or args,
        unless kind was explicitly set by the parser
        (e.g. for open/close/force).
        """
        # ✅ Respect explicit non-insert kinds from parser
        if getattr(self, "kind", None) in {"open", "close", "force"}:
            return

        # Infer kind automatically if parser didn't set a specific one
        if getattr(self, "suffix", None) == "+":
            self.kind = "open"
        elif getattr(self, "suffix", None) == "-":
            self.kind = "close"
        elif getattr(self, "suffix", None) == "!":
            self.kind = "force"
        elif "see" in getattr(self, "args", {}):
            self.kind = "see"
        elif "range" in getattr(self, "args", {}):
            self.kind = "range"
        else:
            self.kind = "insert"

    def __repr__(self) -> str:
        if self.args:
            return f"<IndexDirective name={self.name!r} kind={self.kind!r} args={self.args}>"
        return f"<IndexDirective name={self.name!r} kind={self.kind!r}>"


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


@dataclass
class IndexRangeBlock:
    """Represents an open/close index block with inner content."""

    start: IndexDirective
    content: list
    end: IndexDirective

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
from .ast import IndexDirective, IndexMark, IndexRangeBlock, ProcessingControl


def build_index(entries: List[IndexMark]) -> str:
    """Convert a list of index marks into a simple textual index (placeholder)."""
    if not entries:
        return "<p><em>No index entries found.</em></p>"

    out = ["<dl class='index textindex'>"]
    for entry in entries:
        out.append(f"  <dt>{entry.heading}</dt>")
    out.append("</dl>")
    return "\n".join(out)


class IndexBuilder:
    """Constructs an index tree or entries from parsed AST nodes."""

    def __init__(self):
        self.entries = []
        self.processing_enabled = True  # True until disabled

    def process(self, nodes):
        """Process a list of AST nodes."""
        for node in nodes:
            # --- Handle enable/disable directives ---
            if isinstance(node, ProcessingControl):
                self.processing_enabled = node.enabled
                continue

            # --- Skip everything if processing disabled ---
            if not self.processing_enabled:
                continue

            # --- Handle AST node types ---
            if isinstance(node, IndexMark):
                self.handle_mark(node)
            elif isinstance(node, IndexDirective):
                self.handle_directive(node)
            elif isinstance(node, IndexRangeBlock):
                self.handle_range_block(node)
            else:
                # Ignore plain text and unrecognized items
                continue

    def handle_mark(self, mark: IndexMark):
        """Handle a single index mark."""
        self.entries.append(
            {"type": "mark", "heading": mark.heading, "sub": mark.subheadings}
        )

    def handle_directive(self, directive: IndexDirective):
        """Handle index directive (insert, see, etc.)."""
        self.entries.append(
            {
                "type": "directive",
                "name": directive.name,
                "kind": directive.kind,
            }
        )

    def handle_range_block(self, block: IndexRangeBlock):
        """Handle a range block, respecting enable/disable state inside."""
        if not self.processing_enabled:
            return  # skip the whole block

        # Process the block's internal content safely
        inner_builder = IndexBuilder()
        inner_builder.processing_enabled = self.processing_enabled
        inner_builder.process(block.content)

        self.entries.append(
            {
                "type": "range_block",
                "range": block.start.args.get("range"),
                "content": inner_builder.entries,
            }
        )

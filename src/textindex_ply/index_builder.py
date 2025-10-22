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
    """Constructs structured index entries from parsed AST nodes."""

    def __init__(self):
        self.entries = []
        self.processing_enabled = True

    def process(self, nodes):
        """Process a list of AST nodes."""
        for node in nodes:
            # --- Enable/disable sections ---
            if isinstance(node, ProcessingControl):
                self.processing_enabled = node.enabled
                continue

            if not self.processing_enabled:
                continue

            # --- Dispatch by node type ---
            if isinstance(node, IndexMark):
                self.handle_mark(node)
            elif isinstance(node, IndexDirective):
                self.handle_directive(node)
            elif isinstance(node, IndexRangeBlock):
                self.handle_range_block(node)

    # ------------------------------------------------------------------
    # Individual node handlers
    # ------------------------------------------------------------------
    def handle_directive(self, directive: IndexDirective):
        """Handle {index...} directives of various kinds using match/case."""
        args = directive.args or {}

        # helper
        def arg_value(*keys: str) -> str | None:
            for key in keys:
                if key in args:
                    return args[key]
            return None

        match directive.kind:
            case "insert" | "open" | "close" | "force":
                self.entries.append(
                    {
                        "type": "directive",
                        "kind": directive.kind,
                        "name": directive.name,
                        "args": args,
                    }
                )
            case "range":
                self.entries.append(
                    {
                        "type": "range",
                        "name": directive.name,
                        "label": arg_value("range"),  # ✅ add label field
                        "args": args,
                    }
                )
            case "see" | "seealso":
                self.entries.append(
                    {
                        "type": "xref",
                        "xref_kind": directive.kind,  # ✅ ensure both see & seealso covered
                        "target": arg_value(directive.kind),
                        "args": args,
                    }
                )
            case _:
                self.entries.append(
                    {
                        "type": "unknown_directive",
                        "kind": directive.kind,
                        "args": args,
                    }
                )

    def handle_mark(self, mark: IndexMark):
        """Handle a {mark} tag."""
        self.entries.append(
            {
                "type": "mark",
                "heading": mark.heading,
                "subheadings": mark.subheadings,
            }
        )

    def handle_node(self, node):
        """Dispatch handler based on node type."""
        match node.__class__.__name__:
            case "IndexDirective":
                self.handle_directive(node)
            case "IndexMark":
                self.handle_mark(node)
            case "IndexRangeBlock":
                self.handle_range_block(node)
            case _:
                # Ignore or handle unexpected nodes gracefully
                pass

    def handle_range_block(self, block: "IndexRangeBlock"):
        """Handle range blocks like {index+ range="A–C"}...{index-}."""
        start_label = block.start.args.get("range") if block.start else None
        entry = {
            "type": "range_block",
            "label": start_label,
            "content": [],
        }

        # Recursively process inner content
        for element in block.content:
            if isinstance(
                element, (IndexDirective, IndexMark, IndexRangeBlock)
            ):
                self.handle_node(element)
                entry["content"].append(self.entries[-1])
            elif isinstance(element, str):
                entry["content"].append({"type": "text", "value": element})

        self.entries.append(entry)

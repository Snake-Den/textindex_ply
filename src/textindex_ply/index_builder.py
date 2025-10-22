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
    """Walks the parsed AST and converts it into structured index entries.
    Handles index directives, marks, range blocks, and processing control.
    """

    def __init__(self):
        self.entries = []
        self.index: dict[str, dict] = {}
        self.processing_enabled = True

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------
    def process(self, nodes):
        """Process a list of AST nodes."""
        for node in nodes:
            match node:
                # ✅ Toggle processing state on/off
                case ProcessingControl(enabled=enabled):
                    self.processing_enabled = enabled
                    continue

                # ✅ Skip all other nodes while disabled
                case _ if not self.processing_enabled:
                    continue
                # ✅ Dispatch based on node type
                case IndexDirective():
                    self.handle_directive(node)
                case IndexMark():
                    self.handle_mark(node)
                case IndexRangeBlock():
                    self.handle_range_block(node)
                case _:
                    self.entries.append(
                        {"type": "unknown", "value": repr(node)}
                    )

    def handle_directive(self, directive: IndexDirective):
        """Handle {index...} directives using Python match/case."""
        args = directive.args or {}

        def arg_value(*keys: str) -> str | None:
            """Return the first matching argument value."""
            for key in keys:
                if key in args:
                    return args[key]
            return None

        match directive.kind:
            # Basic index entry directive
            case "insert" | "open" | "close" | "force":
                entry = {
                    "type": "directive",
                    "kind": directive.kind,
                    "name": directive.name,
                    "args": args,
                }

            # Range directive (e.g., {index range="A–C"})
            case "range":
                entry = {
                    "type": "range",
                    "name": directive.name,
                    "label": arg_value("range"),
                    "args": args,
                }

            # Cross-reference directive (see / seealso)
            case "see" | "seealso":
                entry = {
                    "type": "xref",
                    "xref_kind": directive.kind,
                    "target": args.get(directive.kind),
                }

            # Processing control (enable / disable)
            case "disable":
                self.enabled = False
                entry = {"type": "control", "action": "disable"}

            case "enable":
                self.enabled = True
                entry = {"type": "control", "action": "enable"}

            # Unknown directive fallback
            case _:
                entry = {
                    "type": "unknown_directive",
                    "kind": directive.kind,
                    "args": directive.args,
                }

        self.entries.append(entry)

    def handle_mark(self, mark: IndexMark):
        """Handle ^ marks and convert to index entries."""
        # Ensure subheadings is always a list
        if not isinstance(mark.subheadings, list):
            mark.subheadings = []

        # Record the mark itself
        entry = {
            "type": "mark",
            "heading": mark.heading,
            "subheadings": mark.subheadings,
            "crossrefs": mark.crossrefs,
            "suffix": mark.suffix,
            "sort_key": mark.sort_key,
            "emphasis": mark.emphasis,
            "closing": mark.closing,
            "alias": mark.alias,
            "wildcard": mark.wildcard,
        }
        self.entries.append(entry)

        # --- Build hierarchical index structure ---
        full_path = [mark.heading] + list(mark.subheadings or [])
        current = self.index

        for i, part in enumerate(full_path):
            # Create missing branch node
            if part not in current:
                current[part] = {}

            # Move into the next level
            current = current[part]

            # Ensure that for the last node, we still have a dict container
            if i == len(full_path) - 1 and not isinstance(current, dict):
                current = {}

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

    def handle_range_block(self, block: IndexRangeBlock):
        """Handle {index+ ...}{index-} range blocks."""
        label = block.start.args.get("range") or block.start.args.get("label")

        # Normalize the block’s content
        normalized_content = []
        for c in block.content:
            if isinstance(c, str):
                normalized_content.append({"type": "text", "value": c})
            elif isinstance(c, dict):
                normalized_content.append(c)
            else:
                normalized_content.append({"type": "node", "value": repr(c)})

        self.entries.append(
            {
                "type": "range_block",
                "label": label,
                "start": block.start.args.get("range"),
                "end": block.end.kind,
                "content": normalized_content,
            }
        )

    def finalize(self):
        """
        Group, sort, and merge index entries into a structured form.
        Returns a dict mapping initial letters (A–Z) to sorted entries.
        """
        grouped = self.group_entries()
        for letter, items in grouped.items():
            grouped[letter] = self.merge_duplicates(self.sort_entries(items))
        self.index = grouped
        return grouped

    def group_entries(self):
        """Group entries by their starting letter (A–Z)."""
        grouped = {}
        for entry in self.entries:
            if entry["type"] not in {"directive", "range"}:
                continue
            label = (
                entry["args"].get("term")
                or entry["args"].get("range")
                or entry.get("label")
            )
            if not label:
                continue
            key = label[0].upper()
            grouped.setdefault(key, []).append(entry)
        return grouped

    def sort_entries(self, items):
        """Sort entries alphabetically by term or label."""
        return sorted(
            items, key=lambda e: e.get("label") or e["args"].get("term", "")
        )

    def merge_duplicates(self, items):
        """Merge duplicate index entries with the same label."""
        merged = []
        seen = {}
        for e in items:
            label = e.get("label") or e["args"].get("term") or ""
            if label in seen:
                seen[label]["refs"].extend(e.get("refs", []))
            else:
                entry = {**e, "refs": e.get("refs", [])}
                merged.append(entry)
                seen[label] = entry
        return merged

    def as_dict(self):
        """Return finalized index as a dictionary."""
        return self.index or self.finalize()

    def as_json(self):
        """Return finalized index as JSON string."""
        import json

        return json.dumps(self.as_dict(), indent=2)

    def _insert_hierarchy(self, path: list[str]):
        """Insert a nested entry path like ['Fruit', 'Citrus', 'Oranges'] into the index tree."""
        current = self.index
        for part in path:
            if part not in current:
                current[part] = {}
            current = current[part]

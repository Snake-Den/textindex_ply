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

from textindex_ply.ast import (
    IndexDirective,
    IndexMark,
    IndexRangeBlock,
    ProcessingControl,
)
from textindex_ply.index_builder import IndexBuilder


def test_processing_control_behavior():
    builder = IndexBuilder()
    nodes = [
        IndexMark(heading="A", subheadings=[]),
        ProcessingControl(enabled=False),
        IndexMark(heading="B", subheadings=[]),  # should be skipped
        ProcessingControl(enabled=True),
        IndexMark(heading="C", subheadings=[]),
    ]

    builder.process(nodes)
    headings = [e["heading"] for e in builder.entries if e["type"] == "mark"]
    assert headings == ["A", "C"]


def test_processing_control_skips_range_blocks():
    builder = IndexBuilder()

    range_block = IndexRangeBlock(
        start=IndexDirective(name="index", kind="open", args={"range": "A–C"}),
        content=[IndexMark(heading="B", subheadings=[])],
        end=IndexDirective(name="index", kind="close"),
    )

    nodes = [
        IndexMark(heading="A", subheadings=[]),
        ProcessingControl(enabled=False),
        range_block,  # should be skipped entirely
        ProcessingControl(enabled=True),
        IndexMark(heading="C", subheadings=[]),
    ]

    builder.process(nodes)

    entries = [
        e for e in builder.entries if e["type"] in ("mark", "range_block")
    ]
    assert len(entries) == 2
    assert entries[0]["heading"] == "A"
    assert entries[1]["heading"] == "C" or entries[1]["type"] == "mark"

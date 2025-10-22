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


def test_basic_index_entry():
    builder = IndexBuilder()
    builder.process([IndexMark(heading="Foo", subheadings=["Bar"])])
    assert builder.entries[0]["heading"] == "Foo"
    assert builder.entries[0]["subheadings"] == ["Bar"]


def test_index_directive_see_and_seealso():
    builder = IndexBuilder()
    see_dir = IndexDirective(name="index", kind="see", args={"see": "Bar"})
    seealso_dir = IndexDirective(
        name="index", kind="seealso", args={"seealso": "Baz"}
    )
    builder.process([see_dir, seealso_dir])

    see_entry = builder.entries[0]
    seealso_entry = builder.entries[1]

    assert see_entry["type"] == "xref"
    assert see_entry["xref_kind"] == "see"
    assert see_entry["target"] == "Bar"

    assert seealso_entry["xref_kind"] == "seealso"
    assert seealso_entry["target"] == "Baz"


def test_index_directive_range():
    builder = IndexBuilder()
    dir = IndexDirective(name="index", kind="range", args={"range": "A–C"})
    builder.process([dir])
    assert builder.entries[0]["type"] == "range"
    assert builder.entries[0]["label"] == "A–C"


def test_index_builder_range_block():
    """Ensure IndexBuilder correctly processes a range block."""
    start = IndexDirective(name="index", kind="open", args={"range": "A–C"})
    end = IndexDirective(name="index", kind="close")
    block = IndexRangeBlock(start=start, content=["alpha", "beta"], end=end)

    builder = IndexBuilder()
    builder.handle_node(block)

    assert builder.entries, "No entries were recorded"
    entry = builder.entries[-1]

    # Check that the entry was interpreted as a range block
    assert entry["type"] == "range_block"
    assert entry["label"] == "A–C"
    assert any(
        isinstance(c, dict) and c.get("type") == "text"
        for c in entry["content"]
    )
    assert entry["content"][0]["value"] == "alpha"
    assert entry["content"][1]["value"] == "beta"


def test_index_builder_finalize_groups_and_sorts():
    builder = IndexBuilder()
    builder.entries = [
        {"type": "directive", "args": {"term": "banana"}},
        {"type": "directive", "args": {"term": "apple"}},
        {"type": "directive", "args": {"term": "avocado"}},
    ]
    result = builder.finalize()
    assert "A" in result
    assert "B" in result
    assert [e["args"]["term"] for e in result["A"]] == ["apple", "avocado"]


def test_index_builder_merge_duplicates():
    builder = IndexBuilder()
    builder.entries = [
        {"type": "directive", "args": {"term": "Apple"}},
        {"type": "directive", "args": {"term": "Apple"}},
    ]
    grouped = builder.finalize()
    assert len(grouped["A"]) == 1
    assert "refs" in grouped["A"][0]


def test_index_builder_hierarchy_basic():
    """Ensure hierarchical paths are inserted correctly into
    IndexBuilder.index.
    """
    builder = IndexBuilder()

    # Simulate hierarchical marks: ^Fruit>Citrus>Oranges and ^Fruit>Apples
    mark1 = IndexMark(
        heading="Fruit",
        subheadings=["Citrus", "Oranges"],
        crossrefs=[],
        suffix=None,
        sort_key=None,
        emphasis=False,
        closing=False,
        alias=None,
        wildcard=None,
    )
    mark2 = IndexMark(
        heading="Fruit",
        subheadings=["Apples"],
        crossrefs=[],
        suffix=None,
        sort_key=None,
        emphasis=False,
        closing=False,
        alias=None,
        wildcard=None,
    )

    builder.process([mark1, mark2])

    # Top-level heading should exist
    assert "Fruit" in builder.index

    # Nested structure under Fruit should have both Citrus and Apples
    fruit_index = builder.index["Fruit"]
    assert "Citrus" in fruit_index
    assert "Apples" in fruit_index

    # Verify deeper nesting under Citrus → Oranges
    assert "Oranges" in fruit_index["Citrus"]
    assert builder.index["Fruit"]["Citrus"]["Oranges"] == {}


def test_index_builder_hierarchy_multiple_branches():
    """Test that unrelated hierarchies are kept separate."""
    builder = IndexBuilder()

    mark_a = IndexMark(
        heading="Animals",
        subheadings=["Mammals", "Dogs"],
        crossrefs=[],
        suffix=None,
        sort_key=None,
        emphasis=False,
        closing=False,
        alias=None,
        wildcard=None,
    )
    mark_b = IndexMark(
        heading="Animals",
        subheadings=["Birds", "Parrots"],
        crossrefs=[],
        suffix=None,
        sort_key=None,
        emphasis=False,
        closing=False,
        alias=None,
        wildcard=None,
    )
    mark_c = IndexMark(
        heading="Plants",
        subheadings=["Trees", "Oak"],
        crossrefs=[],
        suffix=None,
        sort_key=None,
        emphasis=False,
        closing=False,
        alias=None,
        wildcard=None,
    )

    builder.process([mark_a, mark_b, mark_c])

    # Verify that Animals and Plants are distinct roots
    assert set(builder.index.keys()) == {"Animals", "Plants"}

    # Each branch should contain proper subpaths
    assert "Mammals" in builder.index["Animals"]
    assert "Birds" in builder.index["Animals"]
    assert "Trees" in builder.index["Plants"]

    # Deepest nodes should be empty dicts
    assert builder.index["Animals"]["Mammals"]["Dogs"] == {}
    assert builder.index["Plants"]["Trees"]["Oak"] == {}

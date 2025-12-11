"""
Test suite for text chunking functionality in rag_utils.build_utils.

Tests the chunk_text_by_lines() function for sequential text document processing.
"""

import pytest
import sys
from pathlib import Path

# Use centralized path utilities
from tests.utils.paths import PROJECT_ROOT

# Add rag_utils to path
sys.path.insert(0, str(PROJECT_ROOT))
from rag_utils.build_utils import chunk_text_by_lines


def test_chunk_text_by_lines_basic():
    """Test basic chunking with default parameters."""
    # Create test text with exactly 25 lines
    lines = [f"Line {i}" for i in range(25)]
    raw_text = "\n".join(lines)
    
    # Chunk with defaults (10 lines per chunk, 4 line overlap)
    chunks = chunk_text_by_lines(raw_text, "test.txt")
    
    # With 25 lines, chunk_size=10, overlap=4, step=6:
    # Chunk 0: lines 0-9 (10 lines), start=0
    # Chunk 1: lines 6-15 (10 lines), start=6
    # Chunk 2: lines 12-21 (10 lines), start=12
    # Chunk 3: lines 18-24 (7 lines), start=18
    # Chunk 4: lines 24-24 (1 line), start=24
    assert len(chunks) == 5, f"Expected 5 chunks, got {len(chunks)}"
    
    # Verify first chunk
    assert chunks[0].page_content.startswith("Line 0")
    assert chunks[0].page_content.endswith("Line 9")
    
    # Verify overlap: chunk 1 should start at line 6
    assert chunks[1].page_content.startswith("Line 6")
    
    # Verify last chunk is shorter
    assert "Line 24" in chunks[3].page_content


def test_chunk_text_by_lines_metadata():
    """Test that metadata is correctly generated."""
    raw_text = "\n".join([f"Line {i}" for i in range(15)])
    
    chunks = chunk_text_by_lines(raw_text, "VILWIN.txt", document_type="sequential")
    
    # Check first chunk metadata
    assert chunks[0].metadata["source"] == "VILWIN.txt"
    assert chunks[0].metadata["document_type"] == "sequential"
    assert chunks[0].metadata["source_id"] == "VILWIN"
    assert chunks[0].metadata["chunk_index"] == 0
    
    # Check second chunk has incremented index
    assert chunks[1].metadata["chunk_index"] == 1
    assert chunks[1].metadata["source_id"] == "VILWIN"


def test_chunk_text_by_lines_no_modification():
    """Test that text is NOT modified (zero modification rule)."""
    # Create text with various edge cases: empty lines, whitespace, special chars
    raw_text = "Line 1\n\nLine 3 with  spaces\n\tLine 4 with tab\n    Line 5 indented\nLine 6"
    
    chunks = chunk_text_by_lines(raw_text, "test.txt", chunk_size=3, chunk_overlap=1)
    
    # First chunk should preserve empty line and exact spacing
    expected_first = "Line 1\n\nLine 3 with  spaces"
    assert chunks[0].page_content == expected_first, \
        f"Text was modified. Expected:\n{repr(expected_first)}\nGot:\n{repr(chunks[0].page_content)}"
    
    # Second chunk should preserve tab and indentation
    expected_second = "Line 3 with  spaces\n\tLine 4 with tab\n    Line 5 indented"
    assert chunks[1].page_content == expected_second, \
        f"Text was modified. Expected:\n{repr(expected_second)}\nGot:\n{repr(chunks[1].page_content)}"


def test_chunk_text_by_lines_custom_parameters():
    """Test chunking with custom chunk_size and chunk_overlap."""
    lines = [f"Line {i}" for i in range(20)]
    raw_text = "\n".join(lines)
    
    # Test with chunk_size=5, overlap=2
    chunks = chunk_text_by_lines(raw_text, "test.txt", chunk_size=5, chunk_overlap=2)
    
    # Chunk 0: lines 0-4
    # Chunk 1: lines 3-7 (step = 5-2 = 3)
    # Chunk 2: lines 6-10
    # etc.
    
    # Verify first chunk has 5 lines
    first_lines = chunks[0].page_content.split("\n")
    assert len(first_lines) == 5
    assert first_lines[0] == "Line 0"
    assert first_lines[4] == "Line 4"
    
    # Verify overlap: chunk 1 should start at line 3 (overlap of 2)
    second_lines = chunks[1].page_content.split("\n")
    assert second_lines[0] == "Line 3"


def test_chunk_text_by_lines_overlap_behavior():
    """Test that overlap is calculated correctly."""
    lines = [f"Line {i}" for i in range(15)]
    raw_text = "\n".join(lines)
    
    chunks = chunk_text_by_lines(raw_text, "test.txt", chunk_size=10, chunk_overlap=4)
    
    # Chunk 0: lines 0-9, start=0
    # Chunk 1: lines 6-14 (9 lines), start=6
    # Chunk 2: lines 12-14 (3 lines), start=12
    assert len(chunks) == 3
    
    # Verify the overlap: last 4 lines of chunk 0 should be first 4 lines of chunk 1
    chunk0_lines = chunks[0].page_content.split("\n")
    chunk1_lines = chunks[1].page_content.split("\n")
    
    # Lines 6-9 appear in both chunks
    assert chunk0_lines[-4:] == chunk1_lines[:4]
    assert chunk0_lines[-4] == "Line 6"
    assert chunk1_lines[0] == "Line 6"


def test_chunk_text_by_lines_empty_text():
    """Test behavior with empty input."""
    chunks = chunk_text_by_lines("", "empty.txt")
    
    # Empty text should produce one empty chunk
    assert len(chunks) == 1
    assert chunks[0].page_content == ""
    assert chunks[0].metadata["source"] == "empty.txt"


def test_chunk_text_by_lines_single_line():
    """Test behavior with single line input."""
    chunks = chunk_text_by_lines("Single line", "single.txt")
    
    assert len(chunks) == 1
    assert chunks[0].page_content == "Single line"
    assert chunks[0].metadata["chunk_index"] == 0


def test_chunk_text_by_lines_source_id_extraction():
    """Test that source_id is correctly extracted from various filenames."""
    test_cases = [
        ("file.txt", "FILE"),
        ("VILWIN.txt", "VILWIN"),
        ("document.doc", "DOCUMENT"),
        ("multi.part.name.txt", "MULTI.PART.NAME"),
        ("NoExtension", "NOEXTENSION"),
    ]
    
    for filename, expected_source_id in test_cases:
        chunks = chunk_text_by_lines("test content", filename)
        assert chunks[0].metadata["source_id"] == expected_source_id, \
            f"Failed for filename: {filename}"


def test_chunk_text_by_lines_returns_documents():
    """Test that function returns proper LangChain Document objects."""
    raw_text = "Line 1\nLine 2\nLine 3"
    chunks = chunk_text_by_lines(raw_text, "test.txt")
    
    # Should return a list
    assert isinstance(chunks, list)
    
    # Each item should be a Document with page_content and metadata
    for chunk in chunks:
        assert hasattr(chunk, "page_content")
        assert hasattr(chunk, "metadata")
        assert isinstance(chunk.page_content, str)
        assert isinstance(chunk.metadata, dict)


def test_chunk_text_by_lines_validates_overlap():
    """Test that function rejects invalid chunk_overlap values."""
    raw_text = "Line 1\nLine 2\nLine 3"
    
    # Test overlap equal to chunk_size (would cause infinite loop)
    with pytest.raises(ValueError, match="chunk_overlap.*must be less than chunk_size"):
        chunk_text_by_lines(raw_text, "test.txt", chunk_size=10, chunk_overlap=10)
    
    # Test overlap greater than chunk_size (would cause infinite loop)
    with pytest.raises(ValueError, match="chunk_overlap.*must be less than chunk_size"):
        chunk_text_by_lines(raw_text, "test.txt", chunk_size=10, chunk_overlap=15)

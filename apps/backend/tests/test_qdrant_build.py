"""
Simple test to verify the build script creates a persistent Qdrant collection.
"""

import pytest
import os
from pathlib import Path
from qdrant_client import QdrantClient

# Import build function from tools directory
import sys
tools_path = Path(__file__).resolve().parents[3] / "tools"
sys.path.insert(0, str(tools_path))
from build_qdrant_collection import main as build_main


@pytest.fixture
def temp_qdrant_path(tmp_path):
    """Isolated test directory for Qdrant database"""
    test_dir = tmp_path / "qdrant_test"
    test_dir.mkdir()
    return str(test_dir)


@pytest.fixture
def csv_path():
    """Path to test CSV file"""
    csv = Path(__file__).parent.parent / "data" / "Thudbot_Hint_Data_1.csv"
    if not csv.exists():
        pytest.skip(f"CSV file not found: {csv}")
    return str(csv)


@pytest.fixture
def skip_if_no_openai_key():
    """Skip test if OpenAI API key not available"""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")


def test_build_script_creates_collection(temp_qdrant_path, csv_path, skip_if_no_openai_key, monkeypatch):
    """Test that the build script creates a working Qdrant collection"""
    # Mock sys.argv to pass paths to the script using named flags
    monkeypatch.setattr("sys.argv", [
        "build_qdrant_collection.py",
        "--csv-path", csv_path,
        "--qdrant-path", temp_qdrant_path
    ])
    
    # Run the build script
    build_main()
    
    # Verify collection was created
    client = QdrantClient(path=temp_qdrant_path)
    try:
        assert client.collection_exists("Thudbot_Hints")
        
        # Verify collection has documents
        collection_info = client.get_collection("Thudbot_Hints")
        assert collection_info.points_count > 0
        
        print(f"✅ Test passed! Collection has {collection_info.points_count} documents")
    finally:
        # Properly close client to release locks
        client.close()


def test_build_script_respects_existing_db(temp_qdrant_path, csv_path, skip_if_no_openai_key, monkeypatch, capsys):
    """Test that the build script detects and respects existing databases"""
    # Mock sys.argv using named flags
    monkeypatch.setattr("sys.argv", [
        "build_qdrant_collection.py",
        "--csv-path", csv_path,
        "--qdrant-path", temp_qdrant_path
    ])
    
    # First run: Create the database
    build_main()
    
    # Second run: Should detect existing database and exit gracefully
    build_main()
    
    # Check that some indication of existing database was given
    # (checking for key concepts, not exact wording)
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "already" in output_lower or "exists" in output_lower
    assert "delete" in output_lower or "remove" in output_lower

# tests/test_functions.py

import pytest
import os
import sys
import pandas as pd
from pathlib import Path

# Add the src directory to the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_hint_data_exists():
    """Test that the hint CSV file exists and is not empty."""
    hint_file = Path("data/Thudbot_Hint_Data_1.csv")
    assert hint_file.exists(), "Hint CSV file should exist"
    
    # Test that file is not empty
    assert hint_file.stat().st_size > 0, "Hint CSV file should not be empty"

def test_hint_data_structure():
    """Test that the hint CSV has the expected structure."""
    hint_file = Path("data/Thudbot_Hint_Data_1.csv")
    
    if not hint_file.exists():
        pytest.skip("Hint CSV file not found")
    
    df = pd.read_csv(hint_file)
    
    # Test that we have data
    assert len(df) > 0, "Hint CSV should contain data"
    
    # Test that expected columns exist (based on actual CSV structure)
    expected_columns = ["question", "hint_text"]  # Actual columns from the CSV
    for col in expected_columns:
        assert col in df.columns, f"Column '{col}' should exist in hint CSV"

def test_agent_imports():
    """Test that agent module imports correctly."""
    try:
        from agent import get_thud_agent, initialize_thudbot
        assert callable(get_thud_agent), "get_thud_agent should be callable"
        assert callable(initialize_thudbot), "initialize_thudbot should be callable"
    except ImportError as e:
        pytest.fail(f"Failed to import agent functions: {e}")

def test_api_imports():
    """Test that API module imports correctly."""
    try:
        from api import app
        assert app is not None, "FastAPI app should be created"
    except ImportError as e:
        pytest.fail(f"Failed to import API components: {e}")

def test_required_files_exist():
    """Test that all required project files exist."""
    required_files = [
        "src/agent.py",
        "src/api.py", 
        "requirements.txt",
        "pyproject.toml"
    ]
    
    for file_path in required_files:
        assert Path(file_path).exists(), f"Required file {file_path} should exist"

def test_agent_initialization():
    """Test that agent can be initialized without API calls."""
    # Test basic agent setup without requiring API keys
    try:
        from agent import initialize_thudbot
        # This should work even without API keys (validates imports, data loading, etc.)
        agent = initialize_thudbot()
        assert agent is not None, "Agent should be created"
    except Exception as e:
        # If it fails due to missing API key, that's expected/ok
        if "API key" in str(e) or "api_key" in str(e):
            pytest.skip(f"Agent initialization skipped - missing API key: {e}")
        else:
            pytest.fail(f"Agent initialization failed unexpectedly: {e}")

def test_fastapi_app_creation():
    """Test that FastAPI app can be created without starting server."""
    try:
        from api import app
        assert app is not None, "FastAPI app should be created"
        # Check that basic routes exist
        routes = [route.path for route in app.routes]
        assert "/api/chat" in routes, "API chat endpoint should exist"
    except Exception as e:
        pytest.fail(f"FastAPI app creation failed: {e}")

def test_basic_math():
    """Simple test to ensure pytest is working."""
    assert 1 + 1 == 2

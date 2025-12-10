# apps/backend/tests/utils/paths.py
"""
Shared test utilities for resolving project paths.

Avoids hardcoded directory depth in regression scripts and other tests.
"""

from pathlib import Path
import sys

# The repository root: go up 5 levels from this file
PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Now calculate other useful paths
BACKEND_ROOT = PROJECT_ROOT / "apps" / "backend"
TESTS_ROOT = BACKEND_ROOT / "tests"
REGRESSION_ROOT = TESTS_ROOT / "regression"
REGRESSION_RESULTS_ROOT = REGRESSION_ROOT / "results"
DATA_ROOT = BACKEND_ROOT / "data"
TOOLS_ROOT = PROJECT_ROOT / "tools"

def add_project_root_to_path():
    """Ensure PROJECT_ROOT is on sys.path for standalone scripts."""
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


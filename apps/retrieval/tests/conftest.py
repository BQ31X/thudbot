#!/usr/bin/env python3
"""
Pytest configuration for retrieval service tests.
"""
import sys
from pathlib import Path

# Add retrieval service to Python path for imports
retrieval_root = Path(__file__).parent.parent
sys.path.insert(0, str(retrieval_root))


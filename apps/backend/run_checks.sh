#!/bin/bash
# Backend test runner - run all backend checks
# Usage: ./run_checks.sh

echo "🧪 Running backend tests..."

# Phase 1: Run fast pytest suite
echo "🔬 Running pytest suite..."
uv run pytest

# Check if basic tests passed
if [ $? -eq 0 ]; then
    echo "✅ Basic tests passed!"
    echo ""
    echo "🔍 Running critical regression check..."
    
      echo ""
    
    # Phase 2: Run quick regression test (10 questions) - only outside CI
    if [ "$CI" != "true" ]; then
        echo "🔍 Running critical regression check..."
        python tests/regression/run_quick_regression.py
    else
        echo "🚫 Skipping regression test in CI (needs API key)"
    fi
    
    # Check if regression tests passed
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ All backendtests passed!"
        exit 0
    else
        echo ""
        echo "❌ Critical regression test failed! (Fix issues before proceeding)."
        echo "   Check the regression test output above for details."
        exit 1
    fi
else
    echo ""
    echo "❌ Basic tests failed! (Fix issues before proceeding)."
    exit 1
fi
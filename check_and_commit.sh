#!/bin/bash
# Quick script to run fast tests before committing
# Usage: ./check_and_commit.sh "your commit message"

echo "🧪 Running tests before commit..."

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
        echo "✅ All tests passed! Proceeding with commit..."
        
        # Stage all changes and commit
        git add .
        
        if [ -n "$1" ]; then
            git commit -m "$1"
            echo "🎉 Committed with message: $1"
        else
            echo "ℹ️  No commit message provided. Staging files only."
            echo "   Run: git commit -m 'your message' to complete"
        fi
    else
        echo ""
        echo "❌ Critical regression test failed! Fix issues before committing."
        echo "   Check the regression test output above for details."
        exit 1
    fi
else
    echo ""
    echo "❌ Basic tests failed! Fix issues before committing."
    exit 1
fi
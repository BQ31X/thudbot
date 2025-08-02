#!/bin/bash
# Quick script to run fast tests before committing
# Usage: ./check_and_commit.sh "your commit message"

echo "🧪 Running tests before commit..."

# The `uv run pytest` command will find and execute all tests.
# This assumes pytest is installed and your tests are correctly formatted.
uv run pytest

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests passed! Proceeding with commit..."
    
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
    echo "❌ Tests failed! Fix issues before committing."
    exit 1
fi
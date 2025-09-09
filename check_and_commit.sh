#!/bin/bash
# Master script to run all checks and commit
# Usage: ./check_and_commit.sh "your commit message"

echo "🚀 Running all project checks..."

# Run backend checks
echo "📱 Checking backend..."
cd apps/backend && ./run_checks.sh
backend_result=$?
cd ../..

if [ $backend_result -eq 0 ]; then
    echo ""
    echo "✅ All checks passed! Proceeding with commit..."
    
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
    echo "❌ Backend checks failed! Fix issues before committing."
    exit 1
fi
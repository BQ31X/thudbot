#!/bin/bash
# Deployment script for thudbot app node
# Usage: ./deploy-app.sh

set -e  # Exit on error

echo "🚀 Deploying Thudbot App Node"

# Set retrieval API URL (customize per environment)
export RETRIEVAL_API_URL=http://45.79.143.75:8001
echo "🔧 Using Retrieval API: $RETRIEVAL_API_URL"

# Verify required secrets exist
if ! docker secret ls | grep -q openai_api_key; then
  echo "❌ Error: openai_api_key secret not found"
  echo "   Create with: echo 'your_key' | docker secret create openai_api_key -"
  exit 1
fi

if ! docker secret ls | grep -q langchain_api_key; then
  echo "❌ Error: langchain_api_key secret not found"
  echo "   Create with: echo 'your_key' | docker secret create langchain_api_key -"
  exit 1
fi

echo "✅ Secrets verified"
echo "✅ RETRIEVAL_API_URL=$RETRIEVAL_API_URL"

# Deploy stack
echo "📦 Deploying stack..."
docker stack deploy -c compose.prod.app.yml thudbot

echo "✅ Deployment complete!"
echo ""
echo "Check status:"
echo "  docker service ls"
echo "  docker service logs thudbot_backend -f"
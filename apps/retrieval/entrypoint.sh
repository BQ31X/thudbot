#!/bin/bash
# Optional Docker secrets to environment variables converter
# Falls back gracefully if secrets don't exist

if [ -f "/run/secrets/openai_api_key" ]; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai_api_key)
fi

# Execute whatever command was passed to the container
exec "$@"


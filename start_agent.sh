#!/bin/bash

# Navigate to project directory
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent || exit 1

# Set environment variables
export DIAL_API_KEY="dial-fxbasxs2h6t7brhnbqs36omhe2y"
export ORCHESTRATION_MODEL="gpt-4o"
export DIAL_URL="https://ai-proxy.lab.epam.com"
export UMS_MCP_URL="http://localhost:8005/mcp"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"

# Activate virtual environment
source .venv/bin/activate || exit 1

# Install uvicorn if not present
pip show uvicorn > /dev/null 2>&1 || pip install uvicorn[standard]

# Start the agent
echo "Starting UMS UI Agent..."
echo "Environment: DIAL_API_KEY is set: $([ -n \"$DIAL_API_KEY\" ] && echo 'yes' || echo 'no')"
python -m agent.app


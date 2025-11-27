#!/bin/bash

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

# Start agent in background
nohup python run_agent.py > agent.log 2>&1 &
AGENT_PID=$!

echo "Agent started with PID: $AGENT_PID"
echo "Log file: agent.log"
echo "Waiting for agent to initialize..."

# Wait and check health
sleep 5
for i in {1..10}; do
    if curl -s http://localhost:8011/health > /dev/null 2>&1; then
        echo "✓ Agent is healthy and running!"
        break
    fi
    echo "Waiting... ($i/10)"
    sleep 2
done

echo ""
echo "Agent status:"
curl -s http://localhost:8011/health | python3 -m json.tool 2>/dev/null || echo "Agent may still be starting..."


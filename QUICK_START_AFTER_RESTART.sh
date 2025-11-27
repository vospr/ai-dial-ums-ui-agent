#!/bin/bash

echo "🚀 Quick Start After Restart"
echo "============================"
echo ""

# Navigate to project
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent || exit 1

echo "📍 Current directory: $(pwd)"
echo ""

# Step 1: Check IP address
echo "1️⃣  Checking IP address..."
echo "   Your current IP addresses:"
ipconfig.exe | grep IPv4 || echo "   Run 'ipconfig' in PowerShell to see your IP"
echo ""
echo "   ⚠️  If IP changed, update index_network.html line 468"
echo ""

# Step 2: Start Docker services
echo "2️⃣  Starting Docker services..."
docker compose up -d

if [ $? -eq 0 ]; then
    echo "   ✅ Docker services starting..."
    echo "   ⏳ Waiting 30 seconds for services to initialize..."
    sleep 30
else
    echo "   ❌ Failed to start Docker services"
    exit 1
fi

# Step 3: Verify Docker services
echo ""
echo "3️⃣  Verifying Docker services..."
docker compose ps

echo ""
echo "   Testing services..."
curl -s http://localhost:8041/health > /dev/null && echo "   ✅ User Service: OK" || echo "   ⚠️  User Service: Not ready yet"
curl -s http://localhost:8005/health > /dev/null && echo "   ✅ UMS MCP Server: OK" || echo "   ⚠️  UMS MCP Server: Not ready yet"
docker exec ai-dial-ums-ui-agent-redis-ums-1 redis-cli ping > /dev/null 2>&1 && echo "   ✅ Redis: OK" || echo "   ⚠️  Redis: Not ready yet"

# Step 4: Activate virtual environment
echo ""
echo "4️⃣  Activating Python environment..."
source .venv/bin/activate || exit 1

# Step 5: Set environment variables
echo ""
echo "5️⃣  Setting environment variables..."
export DIAL_API_KEY='dial-fxbasxs2h6t7brhnbqs36omhe2y'
export ORCHESTRATION_MODEL='gpt-4o'
export DIAL_URL='https://ai-proxy.lab.epam.com'
export UMS_MCP_URL='http://localhost:8005/mcp'
export REDIS_HOST='localhost'
export REDIS_PORT='6379'

echo "   ✅ Environment variables set"

# Step 6: Start agent
echo ""
echo "6️⃣  Starting agent..."
nohup python run_agent.py > agent.log 2>&1 &
AGENT_PID=$!

echo "   Agent starting with PID: $AGENT_PID"
echo "   ⏳ Waiting 15 seconds for agent to initialize..."
sleep 15

# Step 7: Verify agent
echo ""
echo "7️⃣  Verifying agent..."
HEALTH=$(curl -s http://localhost:8011/health 2>&1)

if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Agent is healthy!"
    echo "   Response: $HEALTH"
else
    echo "   ⚠️  Agent may still be starting..."
    echo "   Response: $HEALTH"
    echo "   Check logs: tail -50 agent.log"
fi

# Step 8: Summary
echo ""
echo "============================"
echo "✅ Setup Complete!"
echo "============================"
echo ""
echo "📊 Status:"
echo "   - Docker services: Running"
echo "   - Agent: $(curl -s http://localhost:8011/health > /dev/null && echo 'Running' || echo 'Starting...')"
echo ""
echo "🌐 Next Steps:"
echo "   1. Check your IP: ipconfig | findstr IPv4"
echo "   2. Update index_network.html if IP changed"
echo "   3. Configure Windows Firewall (ports 8011, 8080)"
echo "   4. Start HTTP server: ./start_http_server.sh"
echo ""
echo "🔗 Access URLs:"
echo "   - Local UI: http://localhost:8080/index_network.html"
echo "   - Network UI: http://YOUR_IP:8080/index_network.html"
echo "   - Agent API: http://localhost:8011"
echo ""
echo "📝 Logs:"
echo "   - Agent: tail -f agent.log"
echo "   - Docker: docker compose logs -f"
echo ""


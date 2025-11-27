# Testing and Sharing Guide

## 🔧 Issue Fixed

**Problem:** `AttributeError: 'dict' object has no attribute 'function'` in `dial_client.py`

**Solution:** Changed tool_call access from object attributes to dictionary keys:
- `tool_call.function.name` → `tool_call["function"]["name"]`
- `tool_call.function.arguments` → `tool_call["function"]["arguments"]`
- `tool_call.id` → `tool_call["id"]`

## ✅ Testing the Fix

### Step 1: Start the Agent

```bash
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./start_agent_background.sh"
```

Or manually:
```bash
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && source .venv/bin/activate && export DIAL_API_KEY='dial-fxbasxs2h6t7brhnbqs36omhe2y' && export ORCHESTRATION_MODEL='gpt-4o' && nohup python run_agent.py > agent.log 2>&1 &"
```

### Step 2: Verify Agent is Running

```bash
# Check health endpoint
wsl bash -c "curl -s http://localhost:8011/health"

# Expected output:
# {"status":"healthy","conversation_manager_initialized":true}
```

### Step 3: Test in UI

1. Open the UI: `file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index.html`
2. Try these test queries:
   - `Search for users named John`
   - `Find users with email containing gmail.com`
   - `Search the web for DIAL platform information`

### Step 4: Check Logs

```bash
wsl bash -c "tail -f /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent/agent.log"
```

## 🌐 Sharing with Other Users

### Option 1: Local Network Access (Same Network)

#### Step 1: Find Your IP Address

**In WSL:**
```bash
wsl bash -c "hostname -I | awk '{print \$1}'"
```

**Or in Windows PowerShell:**
```powershell
ipconfig | findstr IPv4
```

#### Step 2: Update HTML for Network Access

The agent already listens on `0.0.0.0:8011`, so it's accessible on the network.

**Create a network-accessible version of index.html:**

1. Copy `index.html` to `index_network.html`
2. Update the API_URL in the new file:
   ```javascript
   const API_URL = 'http://YOUR_IP_ADDRESS:8011';
   // Example: const API_URL = 'http://192.168.1.100:8011';
   ```

#### Step 3: Share with Other Users

**For users on the same network:**
1. Share the `index_network.html` file
2. Tell them to open it in their browser
3. They can access: `http://YOUR_IP_ADDRESS:8011`

**Important:** Make sure Windows Firewall allows connections on port 8011:
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "UMS Agent" -Direction Inbound -LocalPort 8011 -Protocol TCP -Action Allow
```

### Option 2: Serve via HTTP Server (Easier)

#### Step 1: Create a Simple HTTP Server Script

Create `serve_ui.py`:
```python
import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving UI at http://localhost:{PORT}/index.html")
    print(f"Agent API should be at http://localhost:8011")
    webbrowser.open(f'http://localhost:{PORT}/index.html')
    httpd.serve_forever()
```

#### Step 2: Run the Server

```bash
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && python3 serve_ui.py"
```

#### Step 3: Share Network Access

1. Find your IP: `wsl bash -c "hostname -I | awk '{print \$1}'"`
2. Share: `http://YOUR_IP:8080/index.html`
3. Users can access the UI, but they need the agent running on your machine

### Option 3: Full Network Setup (Best for Demos)

#### Step 1: Configure Agent for Network Access

The agent already listens on `0.0.0.0:8011`, so it's ready for network access.

#### Step 2: Get Your IP Address

```bash
wsl bash -c "ip addr show eth0 | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1"
```

#### Step 3: Update index.html for Network

Create `index_network.html` with:
```javascript
// Replace localhost with your IP
const API_URL = 'http://YOUR_IP_ADDRESS:8011';
```

#### Step 4: Configure Windows Firewall

```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "UMS Agent API" -Direction Inbound -LocalPort 8011 -Protocol TCP -Action Allow
```

#### Step 5: Share Access

**Share these URLs:**
- UI: `http://YOUR_IP:8080/index_network.html` (if using HTTP server)
- Or: Share the `index_network.html` file directly
- Agent API: `http://YOUR_IP:8011` (for direct API access)

## 🧪 Test Script

Create `test_agent.sh`:

```bash
#!/bin/bash

echo "🧪 Testing UMS UI Agent"
echo "======================"

# Test 1: Health Check
echo ""
echo "1. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8011/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Agent is healthy"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Agent health check failed"
    exit 1
fi

# Test 2: Create Conversation
echo ""
echo "2. Testing conversation creation..."
CONV_RESPONSE=$(curl -s -X POST http://localhost:8011/conversations \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Conversation"}')
CONV_ID=$(echo "$CONV_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$CONV_ID" ]; then
    echo "   ✅ Conversation created: $CONV_ID"
else
    echo "   ❌ Failed to create conversation"
    exit 1
fi

# Test 3: Send Message (Non-streaming)
echo ""
echo "3. Testing message sending..."
MESSAGE_RESPONSE=$(curl -s -X POST "http://localhost:8011/conversations/$CONV_ID/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":{"role":"user","content":"Hello"},"stream":false}')

if echo "$MESSAGE_RESPONSE" | grep -q "content"; then
    echo "   ✅ Message sent successfully"
    echo "   Response preview: $(echo "$MESSAGE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['content'][:50])" 2>/dev/null)..."
else
    echo "   ❌ Failed to send message"
    echo "   Response: $MESSAGE_RESPONSE"
    exit 1
fi

echo ""
echo "✅ All tests passed!"
```

Run it:
```bash
wsl bash -c "chmod +x /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent/test_agent.sh && cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./test_agent.sh"
```

## 📋 Quick Reference

### Start Everything
```bash
# 1. Start Docker services
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose up -d"

# 2. Start Agent
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./start_agent_background.sh"

# 3. Open UI
start "" "file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index.html"
```

### Check Status
```bash
# Docker services
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose ps"

# Agent health
wsl bash -c "curl -s http://localhost:8011/health"

# Agent process
wsl bash -c "ps aux | grep run_agent | grep -v grep"
```

### Stop Everything
```bash
# Stop agent
wsl bash -c "pkill -f run_agent"

# Stop Docker
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose down"
```

## 🎯 Demo Checklist

Before demonstrating to others:

- [ ] All Docker services running and healthy
- [ ] Agent is running and responding to health checks
- [ ] UI loads without errors
- [ ] Can create conversations
- [ ] Can send messages and get responses
- [ ] Tool calls work (search_user, duckduckgo_search)
- [ ] Network access configured (if sharing)
- [ ] Firewall rules set (if sharing)

## 🐛 Troubleshooting

### Agent won't start
1. Check logs: `wsl bash -c "tail -50 /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent/agent.log"`
2. Verify dependencies: `wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && source .venv/bin/activate && pip list | grep -E 'openai|fastapi|redis'"`
3. Check environment variables are set

### Network access not working
1. Verify agent listens on 0.0.0.0: `wsl bash -c "netstat -tuln | grep 8011"`
2. Check Windows Firewall
3. Verify IP address is correct
4. Test from another machine: `curl http://YOUR_IP:8011/health`

### UI shows "network error"
1. Check agent is running: `wsl bash -c "curl http://localhost:8011/health"`
2. Check browser console (F12) for CORS errors
3. Verify API_URL in index.html matches agent URL
4. Check agent logs for errors


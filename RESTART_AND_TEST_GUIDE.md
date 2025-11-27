# Step-by-Step Guide: Restart and Test

## 📋 Before Restarting

### Step 1: Note Current Status
- ✅ Agent fix applied (tool_call dictionary access)
- ✅ `index_network.html` configured with IP: `192.168.8.8:8011`
- ✅ HTTP server script ready
- ✅ All files saved

### Step 2: Save Any Work
- Close any open files
- Save all changes
- Note your current IP: **192.168.8.8**

---

## 🔄 After Restarting

### Step 1: Open WSL Terminal
1. Press `Win + R`
2. Type: `wsl`
3. Press Enter
4. Or open PowerShell and type: `wsl`

### Step 2: Navigate to Project
```bash
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent
```

### Step 3: Verify IP Address (Important!)
Your IP might change after restart. Check it:

**In PowerShell:**
```powershell
ipconfig | findstr IPv4
```

**Or in WSL:**
```bash
wsl bash -c "ipconfig.exe | grep IPv4"
```

**Look for your main network IP** (usually starts with 192.168.x.x or 10.x.x.x)

**If IP changed:**
- Update `index_network.html` line 468:
  ```javascript
  const API_URL = 'http://YOUR_NEW_IP:8011';
  ```

### Step 4: Start Docker Services
```bash
# Start all Docker services
docker compose up -d

# Wait 30 seconds for services to initialize
sleep 30

# Verify services are running
docker compose ps
```

**Expected output:** All services should show "Up" status:
- `userservice` - Up
- `ums-mcp-server` - Up  
- `redis-ums` - Up (healthy)
- `redis-insight` - Up

**If services fail:**
```bash
# Check logs
docker compose logs

# Restart if needed
docker compose restart
```

### Step 5: Verify Docker Services Health
```bash
# Check User Service
curl http://localhost:8041/health
# Expected: {"status":"healthy"}

# Check UMS MCP Server
curl http://localhost:8005/health
# Expected: {"status":"healthy"}

# Check Redis
docker exec ai-dial-ums-ui-agent-redis-ums-1 redis-cli ping
# Expected: PONG
```

### Step 6: Start the Agent
```bash
# Method 1: Using the startup script
./start_agent_background.sh

# Method 2: Manual start
source .venv/bin/activate
export DIAL_API_KEY='dial-fxbasxs2h6t7brhnbqs36omhe2y'
export ORCHESTRATION_MODEL='gpt-4o'
export DIAL_URL='https://ai-proxy.lab.epam.com'
export UMS_MCP_URL='http://localhost:8005/mcp'
export REDIS_HOST='localhost'
export REDIS_PORT='6379'
nohup python run_agent.py > agent.log 2>&1 &
```

**Wait 10-15 seconds for agent to start**

### Step 7: Verify Agent is Running
```bash
# Check health endpoint
curl http://localhost:8011/health

# Expected output:
# {"status":"healthy","conversation_manager_initialized":true}

# Check agent process
ps aux | grep run_agent | grep -v grep

# Check agent logs (if needed)
tail -20 agent.log
```

**If agent fails to start:**
```bash
# Check logs for errors
tail -50 agent.log

# Common issues:
# - Missing dependencies: pip install -r requirements.txt
# - Port in use: Check what's using port 8011
# - Environment variables not set: Re-export them
```

### Step 8: Update IP in index_network.html (if changed)
If your IP changed after restart:

```bash
# Edit the file (or use your editor)
# Change line 468 from:
# const API_URL = 'http://192.168.8.8:8011';
# To your new IP:
# const API_URL = 'http://YOUR_NEW_IP:8011';
```

**Quick IP update command:**
```bash
# Replace YOUR_NEW_IP with actual IP
sed -i "s/192.168.8.8/YOUR_NEW_IP/g" index_network.html
```

### Step 9: Configure Windows Firewall
**Run PowerShell as Administrator:**

```powershell
# Allow Agent API (port 8011)
New-NetFirewallRule -DisplayName "UMS Agent API" -Direction Inbound -LocalPort 8011 -Protocol TCP -Action Allow

# Allow HTTP Server (port 8080)
New-NetFirewallRule -DisplayName "UMS UI HTTP Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

**Note:** If rules already exist, you'll get an error - that's OK, they're already configured.

### Step 10: Start HTTP Server
**In a new WSL terminal or PowerShell:**

```bash
# Navigate to project
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent

# Start HTTP server
./start_http_server.sh
```

**Or in PowerShell:**
```powershell
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && python3 serve_ui.py"
```

**You should see:**
```
==========================================
🌐 UMS UI Agent - HTTP Server
==========================================
📁 Serving directory: /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent
🔗 Local access: http://localhost:8080/index_network.html
🌍 Network access: http://192.168.8.8:8080/index_network.html
```

---

## 🧪 Testing

### Test 1: Local Access
1. **Open browser:**
   - Go to: `http://localhost:8080/index_network.html`
   - Or: `file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index_network.html`

2. **Test the UI:**
   - Click "New Chat"
   - Type: `Search for users named John`
   - Press Enter
   - Should see response without "network error"

### Test 2: Agent API Health
```bash
# In WSL
curl http://localhost:8011/health

# Expected: {"status":"healthy","conversation_manager_initialized":true}
```

### Test 3: Create Conversation
```bash
curl -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Conversation"}'

# Should return conversation JSON with ID
```

### Test 4: Send Message
```bash
# First, get conversation ID from previous test
CONV_ID="your-conversation-id-here"

curl -X POST "http://localhost:8011/conversations/$CONV_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","content":"Hello"},"stream":false}'

# Should return assistant response
```

### Test 5: Network Access (from another machine)
**From another computer on the same network:**

```bash
# Test HTTP server
curl http://192.168.8.8:8080/index_network.html

# Test agent API
curl http://192.168.8.8:8011/health

# Expected: {"status":"healthy","conversation_manager_initialized":true}
```

**Or open in browser:**
- `http://192.168.8.8:8080/index_network.html`

---

## ✅ Success Checklist

After restart, verify:

- [ ] Docker services running (`docker compose ps`)
- [ ] User Service healthy (`curl http://localhost:8041/health`)
- [ ] UMS MCP Server healthy (`curl http://localhost:8005/health`)
- [ ] Redis responding (`docker exec ... redis-cli ping`)
- [ ] Agent running (`curl http://localhost:8011/health`)
- [ ] IP address checked and updated in `index_network.html` if changed
- [ ] Windows Firewall configured (ports 8011 and 8080)
- [ ] HTTP server running (port 8080 accessible)
- [ ] UI loads in browser
- [ ] Can create conversations
- [ ] Can send messages and get responses
- [ ] No "network error" messages

---

## 🐛 Troubleshooting

### Issue: Docker services won't start
```bash
# Check Docker is running
docker ps

# Restart Docker services
docker compose down
docker compose up -d

# Check logs
docker compose logs
```

### Issue: Agent won't start
```bash
# Check Python environment
source .venv/bin/activate
python --version

# Reinstall dependencies if needed
pip install -r requirements.txt

# Check environment variables
echo $DIAL_API_KEY

# Check logs
tail -50 agent.log
```

### Issue: Port already in use
```bash
# Check what's using port 8011
netstat -ano | findstr :8011

# Check what's using port 8080
netstat -ano | findstr :8080

# Kill process if needed (replace PID)
# taskkill /PID <PID> /F
```

### Issue: IP address changed
```bash
# Find new IP
ipconfig | findstr IPv4

# Update index_network.html manually or:
sed -i "s/192.168.8.8/NEW_IP/g" index_network.html
```

### Issue: Can't access from network
1. **Check firewall:**
   ```powershell
   Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*UMS*"}
   ```

2. **Verify IP:**
   ```powershell
   ipconfig | findstr IPv4
   ```

3. **Test from local machine first:**
   ```bash
   curl http://YOUR_IP:8011/health
   ```

### Issue: UI shows "network error"
1. **Check agent is running:**
   ```bash
   curl http://localhost:8011/health
   ```

2. **Check browser console (F12):**
   - Look for CORS errors
   - Check API URL is correct

3. **Verify index_network.html has correct IP:**
   - Line 468 should have your current IP

---

## 📝 Quick Reference Commands

### Start Everything (Copy-Paste Ready)
```bash
# 1. Navigate
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent

# 2. Start Docker
docker compose up -d
sleep 30

# 3. Start Agent
source .venv/bin/activate
export DIAL_API_KEY='dial-fxbasxs2h6t7brhnbqs36omhe2y'
export ORCHESTRATION_MODEL='gpt-4o'
nohup python run_agent.py > agent.log 2>&1 &
sleep 10

# 4. Verify
curl http://localhost:8011/health

# 5. Start HTTP Server (in new terminal)
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent
python3 serve_ui.py
```

### Check Status
```bash
# Docker
docker compose ps

# Agent
curl http://localhost:8011/health
ps aux | grep run_agent | grep -v grep

# Services
curl http://localhost:8041/health
curl http://localhost:8005/health
```

### Stop Everything
```bash
# Stop agent
pkill -f run_agent

# Stop HTTP server
pkill -f serve_ui

# Stop Docker
docker compose down
```

---

## 🎯 Expected Test Results

### After successful setup:

1. **Docker Services:**
   - All 4 services running
   - Health checks passing

2. **Agent:**
   - Health endpoint returns: `{"status":"healthy","conversation_manager_initialized":true}`
   - Can create conversations
   - Can send messages
   - Tool calls work (no AttributeError)

3. **UI:**
   - Loads without errors
   - Can create new chats
   - Messages send and receive
   - Streaming works
   - No "network error" messages

4. **Network Access:**
   - Accessible from other machines
   - Both UI and API respond

---

## 📞 Need Help?

If something doesn't work:

1. **Check logs:**
   - Agent: `tail -50 agent.log`
   - Docker: `docker compose logs`

2. **Verify each step:**
   - Go through checklist above
   - Test each component individually

3. **Common fixes:**
   - Restart Docker services
   - Re-export environment variables
   - Check IP address hasn't changed
   - Verify firewall rules

Good luck with your testing! 🚀


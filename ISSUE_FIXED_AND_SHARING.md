# Issue Fixed & Sharing Guide

## ✅ Issue Identified and Fixed

### Problem
The UI was showing "Error: network error" when trying to use tool calls. The root cause was in `agent/clients/dial_client.py`:

**Error:** `AttributeError: 'dict' object has no attribute 'function'`

### Root Cause
The `_collect_tool_calls` method returns a list of dictionaries, but the `_call_tools` method was trying to access them as objects with attributes.

### Fix Applied
Changed lines 220-221 and 235, 260 in `dial_client.py`:

**Before:**
```python
tool_name = tool_call.function.name
tool_args = json.loads(tool_call.function.arguments)
tool_call_id=tool_call.id
```

**After:**
```python
tool_name = tool_call["function"]["name"]
tool_args = json.loads(tool_call["function"]["arguments"])
tool_call_id=tool_call["id"]
```

## 🧪 Testing the Fix

### Quick Test
```bash
# Run the test script
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./test_agent.sh"
```

### Manual Test
1. **Start the agent:**
   ```bash
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./start_agent_background.sh"
   ```

2. **Open the UI:**
   - File: `file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index.html`
   - Or use HTTP server: `python serve_ui.py` then open `http://localhost:8080/index.html`

3. **Test queries:**
   - `Search for users named John`
   - `Find users with email containing gmail.com`
   - `Search the web for DIAL platform information`

## 🌐 Sharing with Other Users

### Method 1: Same Network Access (Recommended for Demos)

#### Step 1: Find Your IP Address
```bash
# In WSL
wsl bash -c "ip addr show eth0 | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1"

# Or in Windows PowerShell
ipconfig | findstr IPv4
```

#### Step 2: Allow Firewall Access
```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "UMS Agent API" -Direction Inbound -LocalPort 8011 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "UMS UI Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

#### Step 3: Create Network-Accessible HTML
The agent already listens on `0.0.0.0:8011`, so it's network-accessible. You just need to:

1. **Option A: Use the HTTP server** (Easiest)
   ```bash
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && python3 serve_ui.py"
   ```
   Then share: `http://YOUR_IP:8080/index.html`
   
   **Note:** Users will still need the agent API. Update `index.html` line 465:
   ```javascript
   const API_URL = 'http://YOUR_IP:8011';  // Replace YOUR_IP with your actual IP
   ```

2. **Option B: Create network HTML file**
   - Copy `index.html` to `index_network.html`
   - Change line 465: `const API_URL = 'http://YOUR_IP:8011';`
   - Share the file or serve it via HTTP server

#### Step 4: Share Access
**Share with users on the same network:**
- UI URL: `http://YOUR_IP:8080/index.html` (if using HTTP server)
- Or: Share `index_network.html` file directly
- Agent API: `http://YOUR_IP:8011` (must be running on your machine)

### Method 2: Direct File Share (Simplest)

1. **Share the files:**
   - `index.html` (for localhost access)
   - Or create `index_network.html` with your IP

2. **User instructions:**
   - User opens the HTML file in their browser
   - They need to update `API_URL` to point to your machine's IP
   - They need your agent running on port 8011

### Method 3: Full Demo Setup

For a complete demo where users can access everything:

1. **Start all services:**
   ```bash
   # Terminal 1: Docker services
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose up -d"
   
   # Terminal 2: Agent
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./start_agent_background.sh"
   
   # Terminal 3: UI Server
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && python3 serve_ui.py"
   ```

2. **Configure network access:**
   - Update `index.html` API_URL to your IP
   - Configure Windows Firewall
   - Share the URL

3. **Share access:**
   ```
   UI: http://YOUR_IP:8080/index.html
   Agent API: http://YOUR_IP:8011
   ```

## 📋 Complete Startup Sequence

### For Local Testing
```bash
# 1. Start Docker
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose up -d"

# 2. Wait for services (30 seconds)
wsl bash -c "sleep 30"

# 3. Start Agent
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./start_agent_background.sh"

# 4. Open UI
start "" "file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index.html"
```

### For Network Sharing
```bash
# 1-3. Same as above

# 4. Start UI Server
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && python3 serve_ui.py"

# 5. Share URL: http://YOUR_IP:8080/index.html
```

## 🎯 Demo Checklist

Before demonstrating:

- [x] Bug fixed (tool_call dictionary access)
- [ ] Docker services running
- [ ] Agent running and healthy
- [ ] UI loads without errors
- [ ] Can create conversations
- [ ] Tool calls work (no more network errors)
- [ ] Network access configured (if sharing)
- [ ] Firewall rules set (if sharing)
- [ ] Test queries work

## 🔍 Verification Commands

```bash
# Check Docker
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose ps"

# Check Agent
wsl bash -c "curl -s http://localhost:8011/health"

# Check Agent Process
wsl bash -c "ps aux | grep run_agent | grep -v grep"

# Test Agent
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./test_agent.sh"
```

## 🐛 Troubleshooting

### Agent won't start
- Check logs: `wsl bash -c "tail -50 /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent/agent.log"`
- Verify environment variables
- Check Python dependencies

### Still getting network errors
- Verify fix was applied: Check `dial_client.py` lines 220-221 use dictionary access
- Restart agent after fix
- Check agent logs for new errors

### Network access not working
- Verify agent listens on 0.0.0.0 (it does by default)
- Check Windows Firewall
- Verify IP address is correct
- Test from another machine: `curl http://YOUR_IP:8011/health`

## 📝 Files Created

1. **TESTING_AND_SHARING.md** - Comprehensive guide
2. **test_agent.sh** - Automated test script
3. **serve_ui.py** - HTTP server for UI
4. **start_agent_background.sh** - Agent startup script
5. **ISSUE_FIXED_AND_SHARING.md** - This file

## ✅ Next Steps

1. **Test the fix:**
   ```bash
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./test_agent.sh"
   ```

2. **Verify in UI:**
   - Open the UI
   - Try a query that uses tools
   - Should work without "network error"

3. **Prepare for sharing:**
   - Get your IP address
   - Configure firewall
   - Start UI server
   - Share the URL


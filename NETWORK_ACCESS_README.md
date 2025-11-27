# Network Access Setup

## ✅ Created: `index_network.html`

A network-accessible version of the UI has been created with your IP address configured.

### Current Configuration

- **API URL**: `http://172.30.85.214:8011`
- **File**: `index_network.html`

### ⚠️ Important Note

The IP address `172.30.85.214` is your **WSL IP address**. For other machines on your network to access the agent, you may need to:

1. **Find your Windows host IP address:**
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" on your main network adapter (usually Wi-Fi or Ethernet).

2. **Update `index_network.html`:**
   - Open `index_network.html`
   - Find line 468: `const API_URL = 'http://172.30.85.214:8011';`
   - Replace `172.30.85.214` with your Windows host IP address

### How to Use

#### Option 1: Direct File Access
1. Share `index_network.html` with other users
2. They open it in their browser
3. Make sure your agent is running and accessible on the network

#### Option 2: HTTP Server (Recommended)
1. Start the HTTP server:
   ```bash
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && python3 serve_ui.py"
   ```

2. Share the URL:
   - Local: `http://localhost:8080/index_network.html`
   - Network: `http://YOUR_IP:8080/index_network.html`

### Network Access Requirements

1. **Agent must be running:**
   ```bash
   wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && ./start_agent_background.sh"
   ```

2. **Windows Firewall must allow connections:**
   ```powershell
   # Run as Administrator
   New-NetFirewallRule -DisplayName "UMS Agent API" -Direction Inbound -LocalPort 8011 -Protocol TCP -Action Allow
   ```

3. **Agent must listen on 0.0.0.0** (already configured in `app.py`)

### Testing Network Access

From another machine on the same network:
```bash
# Test agent health
curl http://YOUR_IP:8011/health

# Should return: {"status":"healthy","conversation_manager_initialized":true}
```

### Troubleshooting

**Can't connect from other machines:**
- Verify Windows host IP (not WSL IP) is used in `index_network.html`
- Check Windows Firewall allows port 8011
- Ensure agent is running: `wsl bash -c "curl http://localhost:8011/health"`
- Test from another machine: `curl http://YOUR_IP:8011/health`

**WSL IP vs Windows Host IP:**
- WSL IP (172.30.85.214): Only accessible from within WSL
- Windows Host IP: Accessible from other machines on the network
- For network sharing, use Windows Host IP

### Quick IP Check

**Windows Host IP:**
```powershell
ipconfig | findstr IPv4
```

**WSL IP:**
```bash
wsl bash -c "hostname -I"
```


# Quick Reference - After Restart

## 🚀 Fast Start (Copy-Paste)

```bash
# Open WSL and run:
cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent
./QUICK_START_AFTER_RESTART.sh
```

## 📋 Manual Steps

### 1. Check IP Address
```powershell
ipconfig | findstr IPv4
```
**If IP changed:** Update `index_network.html` line 468

### 2. Start Docker
```bash
docker compose up -d
sleep 30
docker compose ps
```

### 3. Start Agent
```bash
source .venv/bin/activate
export DIAL_API_KEY='dial-fxbasxs2h6t7brhnbqs36omhe2y'
export ORCHESTRATION_MODEL='gpt-4o'
nohup python run_agent.py > agent.log 2>&1 &
sleep 15
curl http://localhost:8011/health
```

### 4. Configure Firewall
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "UMS Agent API" -Direction Inbound -LocalPort 8011 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "UMS UI HTTP Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### 5. Start HTTP Server
```bash
python3 serve_ui.py
```

## ✅ Verify

```bash
# Docker
docker compose ps

# Agent
curl http://localhost:8011/health

# Services
curl http://localhost:8041/health
curl http://localhost:8005/health
```

## 🌐 Access

- **Local:** `http://localhost:8080/index_network.html`
- **Network:** `http://YOUR_IP:8080/index_network.html`

## 🐛 Quick Fixes

**Agent won't start:**
```bash
tail -50 agent.log
source .venv/bin/activate
pip install -r requirements.txt
```

**IP changed:**
```bash
# Find new IP
ipconfig | findstr IPv4

# Update file (replace NEW_IP)
sed -i "s/192.168.8.8/NEW_IP/g" index_network.html
```

**Port in use:**
```bash
netstat -ano | findstr :8011
netstat -ano | findstr :8080
```

## 📝 Full Guide

See `RESTART_AND_TEST_GUIDE.md` for detailed instructions.


# Quick Start Guide - UMS UI Agent

## ✅ Setup Complete!

All services have been started and the application is ready for testing.

## 📊 Service Status

### Check Docker Services
```bash
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose ps"
```

### Check Agent Status
```bash
wsl bash -c "curl -s http://localhost:8011/health"
```

### Check All Services Health
```bash
# User Service
wsl bash -c "curl -s http://localhost:8041/health"

# UMS MCP Server
wsl bash -c "curl -s http://localhost:8005/health"

# Redis
wsl bash -c "docker exec ai-dial-ums-ui-agent-redis-ums-1 redis-cli ping"
```

## 🌐 Access Points

- **UI Chat Interface**: `file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index.html`
- **Agent API**: `http://localhost:8011`
- **Redis Insight**: `http://localhost:6380`

## 🚀 Restart Services

### Restart Docker Services
```bash
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose restart"
```

### Restart Agent
```bash
# Stop current agent
wsl bash -c "pkill -f 'run_agent.py'"

# Start agent
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && source .venv/bin/activate && nohup python run_agent.py > agent.log 2>&1 &"
```

## 📝 View Logs

### Agent Logs
```bash
wsl bash -c "tail -f /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent/agent.log"
```

### Docker Logs
```bash
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose logs -f"
```

## 🧪 Test Queries

Try these in the UI:

1. **Simple Search**: `Search for users named John`
2. **Email Search**: `Find users with email containing gmail.com`
3. **Web Search**: `Search the web for DIAL platform information`
4. **Add User**: `Add a new user named Alice Johnson`
5. **Get Details**: `Can you tell me more about the first user?`

## 🛑 Stop Everything

```bash
# Stop agent
wsl bash -c "pkill -f 'run_agent.py'"

# Stop Docker services
wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose down"
```

## 🔍 Troubleshooting

### Agent not responding?
1. Check if process is running: `wsl bash -c "ps aux | grep run_agent"`
2. Check logs: `wsl bash -c "tail -50 /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent/agent.log"`
3. Restart agent using commands above

### Docker services not healthy?
1. Check status: `wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose ps"`
2. View logs: `wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose logs"`
3. Restart: `wsl bash -c "cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent && docker compose restart"`

### Port conflicts?
- Port 8041: User Service
- Port 8005: UMS MCP Server
- Port 6379: Redis
- Port 8011: Agent API
- Port 6380: Redis Insight

Check what's using a port: `wsl bash -c "netstat -tuln | grep <PORT>"`


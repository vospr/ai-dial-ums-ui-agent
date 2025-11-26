# UMS UI Agent - Implementation Guide

## 🚀 **Quick Start**

This guide provides step-by-step instructions to set up, run, and test the UMS UI Agent system.

---

## 📋 **Prerequisites**

- ✅ Python 3.11+ installed
- ✅ Docker and Docker Compose installed
- ✅ DIAL API Key from https://ai-proxy.lab.epam.com
- ✅ Git configured
- ✅ EPAM VPN connection (for internal API access)

---

## 🛠️ **Installation Steps**

### **Step 1: Clone Repository**

```bash
cd C:\Users\AndreyPopov
git clone https://github.com/vospr/ai-dial-ums-ui-agent.git
cd ai-dial-ums-ui-agent
```

### **Step 2: Create Virtual Environment**

```bash
# Create venv
python -m venv .venv

# Activate venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Verify activation
python --version
```

### **Step 3: Install Dependencies**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify key packages
pip list | findstr "openai fastapi redis mcp"
```

**Expected packages:**
- openai==2.0.0
- fastapi==0.118.0
- redis[hiredis]==5.0.0
- fastmcp==2.10.1

### **Step 4: Set Environment Variables**

```bash
# Windows PowerShell
$env:DIAL_API_KEY="dial-YOUR-ACTUAL-KEY-HERE"
$env:DIAL_MODEL="gpt-4o"

# Windows CMD
set DIAL_API_KEY=dial-YOUR-ACTUAL-KEY-HERE
set DIAL_MODEL=gpt-4o

# Linux/Mac
export DIAL_API_KEY="dial-YOUR-ACTUAL-KEY-HERE"
export DIAL_MODEL="gpt-4o"
```

**Verify:**
```bash
echo $env:DIAL_API_KEY  # PowerShell
echo %DIAL_API_KEY%     # CMD
echo $DIAL_API_KEY      # Linux/Mac
```

---

## 🐳 **Docker Services Setup**

### **Step 1: Start Docker Services**

```bash
# Start all services (UMS, UMS MCP, Redis, Redis Insight)
docker compose up -d

# Wait for services to be healthy
docker compose ps
```

**Expected Services:**
- `userservice` (port 8041)
- `ums-mcp-server` (port 8005)
- `redis-ums` (port 6379)
- `redis-insight` (port 6380)

### **Step 2: Verify Services**

```bash
# Check UMS MCP Server
curl http://localhost:8005/health

# Check User Service
curl http://localhost:8041/health

# Check Redis
docker exec ai-dial-ums-ui-agent-redis-ums-1 redis-cli ping
```

**Expected:** All services return healthy status

### **Step 3: Access Redis Insight (Optional)**

Open browser: **http://localhost:6380**

**To view conversations:**
1. Click "Add Database"
2. Host: `redis-ums`
3. Port: `6379`
4. Name: `UMS Conversations`

---

## 🚀 **Start Application**

### **Step 1: Start Backend Server**

```bash
# Make sure virtual environment is activated
python -m agent.app
```

**Expected Output:**
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8011 (Press CTRL+C to quit)
```

**Startup Process:**
1. Connects to UMS MCP (HTTP)
2. Connects to Fetch MCP (HTTP)
3. Connects to DuckDuckGo MCP (stdio via Docker)
4. Collects all tools
5. Connects to Redis
6. Initializes ConversationManager

### **Step 2: Verify Backend**

```bash
# Health check
curl http://localhost:8011/health

# Expected response:
# {"status":"healthy","conversation_manager_initialized":true}
```

### **Step 3: Open Frontend**

**Option A: Direct File**
- Open `index.html` in browser
- File path: `C:\Users\AndreyPopov\ai-dial-ums-ui-agent\index.html`

**Option B: Simple HTTP Server**
```bash
# Python 3
python -m http.server 8080

# Then open: http://localhost:8080/index.html
```

**Note:** Frontend expects backend at `http://localhost:8011`

---

## 🧪 **Testing**

### **Test 1: Create Conversation**

**Via Browser:**
1. Click "+ New Chat"
2. Type message: "Hello, can you help me find users?"
3. Press Enter or Click Send

**Expected:**
- Conversation created automatically
- Message sent to agent
- Response streams in real-time
- Conversation appears in sidebar

**Via API:**
```bash
curl -X POST http://localhost:8011/conversations \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Test Conversation\"}"
```

### **Test 2: List Conversations**

**Via Browser:**
- Conversations appear in sidebar automatically

**Via API:**
```bash
curl http://localhost:8011/conversations
```

**Expected:** JSON array of conversation summaries

### **Test 3: Get Conversation**

**Via Browser:**
- Click conversation in sidebar

**Via API:**
```bash
curl http://localhost:8011/conversations/{conversation_id}
```

**Expected:** Full conversation with messages

### **Test 4: Chat with Agent**

**Test Queries:**

1. **Search Users:**
   ```
   Find all users with surname Smith
   ```

2. **Get User by ID:**
   ```
   Get user information for ID 1
   ```

3. **Create User:**
   ```
   Create a new user named John Doe with email john@example.com
   ```

4. **Update User:**
   ```
   Update user ID 1, change email to newemail@example.com
   ```

5. **Delete User:**
   ```
   Delete user with ID 1
   ```

**Expected Behavior:**
- Agent uses appropriate tools
- Responses are helpful and accurate
- Tool calls visible in conversation (if tool messages included)
- Conversation persists after refresh

### **Test 5: Streaming**

**Observe:**
- Typing indicator appears
- Response streams word-by-word
- Markdown renders correctly
- UI updates smoothly

### **Test 6: Delete Conversation**

**Via Browser:**
- Hover over conversation in sidebar
- Click "Delete" button
- Confirm deletion

**Via API:**
```bash
curl -X DELETE http://localhost:8011/conversations/{conversation_id}
```

**Expected:** Conversation removed from list

---

## 🐛 **Troubleshooting**

### **Issue: MCP Client Connection Failed**

**Symptom:** `RuntimeError: MCP client not connected`

**Solution:**
```bash
# Check MCP servers are running
docker compose ps

# Check UMS MCP health
curl http://localhost:8005/health

# Check logs
docker compose logs ums-mcp-server
```

### **Issue: Redis Connection Failed**

**Symptom:** `ConnectionError` or `redis.exceptions.ConnectionError`

**Solution:**
```bash
# Check Redis is running
docker compose ps redis-ums

# Test Redis connection
docker exec ai-dial-ums-ui-agent-redis-ums-1 redis-cli ping

# Check Redis logs
docker compose logs redis-ums
```

### **Issue: DuckDuckGo MCP Not Working**

**Symptom:** Tool calls fail for DuckDuckGo tools

**Solution:**
```bash
# Check Docker image exists
docker images | findstr duckduckgo

# Pull image if needed
docker pull mcp/duckduckgo:latest

# Check stdio client logs in application output
```

### **Issue: Frontend Can't Connect to Backend**

**Symptom:** Network errors in browser console

**Solution:**
1. Check backend is running: `curl http://localhost:8011/health`
2. Check CORS is enabled (should be `allow_origins=["*"]`)
3. Check browser console for specific error
4. Verify API_URL in index.html: `const API_URL = 'http://localhost:8011';`

### **Issue: Conversations Not Persisting**

**Symptom:** Conversations disappear after restart

**Solution:**
```bash
# Check Redis persistence
docker exec ai-dial-ums-ui-agent-redis-ums-1 redis-cli KEYS "conversation:*"

# Check Redis data directory
docker volume ls
docker volume inspect ai-dial-ums-ui-agent_redis-data
```

### **Issue: Streaming Interrupted**

**Symptom:** Partial responses, connection drops

**Solution:**
- Check network stability
- Check backend logs for errors
- Verify DIAL API key is valid
- Check DIAL API rate limits

---

## 📊 **Monitoring**

### **View Application Logs**

**Real-time:**
```bash
# Application logs (already visible in terminal)
# Look for:
# - MCP connection logs
# - Tool call logs
# - Conversation save logs
# - Error logs
```

### **View Docker Logs**

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ums-mcp-server
docker compose logs -f redis-ums
```

### **View Redis Data**

**Via Redis Insight:**
1. Open http://localhost:6380
2. Connect to `redis-ums:6379`
3. Browse keys: `conversation:*`
4. View sorted set: `conversations:list`

**Via CLI:**
```bash
docker exec -it ai-dial-ums-ui-agent-redis-ums-1 redis-cli

# List all conversation keys
KEYS conversation:*

# Get conversation
GET conversation:{id}

# List conversation IDs (sorted)
ZREVRANGE conversations:list 0 -1
```

---

## 🧹 **Cleanup**

### **Stop Application**

```bash
# Stop backend (Ctrl+C in terminal)

# Stop Docker services
docker compose down

# Remove volumes (deletes all data)
docker compose down -v
```

### **Full Cleanup**

```bash
# Stop everything
docker compose down -v

# Remove Python cache
# Windows
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc

# Linux/Mac
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove venv (optional)
rm -rf .venv
```

---

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `DIAL_API_KEY` | DIAL API key | Required |
| `DIAL_MODEL` | Model to use | `gpt-4o` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |

### **MCP Server URLs**

**Hardcoded in `app.py`:**
- UMS MCP: `http://localhost:8005/mcp`
- Fetch MCP: `https://remote.mcpservers.org/fetch/mcp`
- DuckDuckGo: `mcp/duckduckgo:latest` (Docker image)

**To change:** Edit `agent/app.py` lifespan function

### **API Port**

**Backend:** Port 8011 (configurable in `app.py`)

**Frontend:** Expects backend at `http://localhost:8011` (configurable in `index.html`)

---

## 📈 **Performance Tips**

### **1. Connection Pooling**

**Current:** New connections per request
**Improvement:** Reuse MCP client connections

### **2. Redis Pipelining**

**Current:** Individual Redis commands
**Improvement:** Batch operations with pipeline

### **3. Frontend Caching**

**Current:** Fetch conversations on every load
**Improvement:** Cache conversation list, refresh on updates

### **4. Streaming Optimization**

**Current:** Yield every chunk immediately
**Improvement:** Buffer small chunks, yield in batches

---

## 🎓 **Best Practices**

1. **Always Set DIAL_API_KEY**
   ```bash
   export DIAL_API_KEY="your-key-here"
   ```

2. **Use Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate
   ```

3. **Check Services Before Starting**
   ```bash
   docker compose ps
   curl http://localhost:8005/health
   ```

4. **Monitor Logs During Development**
   ```bash
   docker compose logs -f
   ```

5. **Test Incrementally**
   - Start with health check
   - Test conversation creation
   - Test chat functionality
   - Test streaming

6. **Save Common Commands**
   ```bash
   # Add to ~/.bashrc or similar
   alias umsstart='docker compose up -d && python -m agent.app'
   alias umsstop='docker compose down'
   alias umslogs='docker compose logs -f'
   ```

---

## 🔗 **Quick Reference**

**Ports:**
- 8011: Backend API
- 8005: UMS MCP Server
- 8041: User Service
- 6379: Redis
- 6380: Redis Insight

**Key Endpoints:**
- `GET /health` - Health check
- `POST /conversations` - Create conversation
- `GET /conversations` - List conversations
- `GET /conversations/{id}` - Get conversation
- `DELETE /conversations/{id}` - Delete conversation
- `POST /conversations/{id}/chat` - Chat endpoint

**Key Commands:**
```bash
# Start everything
docker compose up -d
python -m agent.app

# Stop everything
docker compose down
# (Ctrl+C for backend)

# View logs
docker compose logs -f

# Test API
curl http://localhost:8011/health
```

---

## 🎉 **Success Checklist**

Before considering implementation complete:

- [ ] All Docker services running
- [ ] Backend starts without errors
- [ ] Frontend loads and connects to backend
- [ ] Can create conversations
- [ ] Can send messages and receive responses
- [ ] Streaming works smoothly
- [ ] Conversations persist after refresh
- [ ] Can delete conversations
- [ ] Tool calls execute successfully
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

## 📚 **Additional Resources**

- **STEPS.md** - Detailed planning, reasoning, and architecture
- **README.md** - Task overview and requirements
- **Docker Compose** - Service configuration
- **Flow Diagrams** - Visual architecture diagrams in `flow_diagrams/`

---

**Congratulations!** 🎉 You've successfully set up and tested the UMS UI Agent!

For questions or issues, refer to:
- DIAL Documentation: https://docs.epam-rail.com
- MCP Documentation: https://modelcontextprotocol.io
- Task Repository: https://github.com/vospr/ai-dial-ums-ui-agent


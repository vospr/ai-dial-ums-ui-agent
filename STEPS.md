# UMS UI Agent - Planning, Reasoning, and Execution Steps

## 🎯 **Task Overview**

**Goal:** Create a production-ready User Management System (UMS) Agent with Tool Use pattern and MCP (Model Context Protocol) integration, featuring a web-based chat UI with streaming responses and Redis-backed conversation persistence.

**Complexity Level:** ⭐⭐⭐⭐ (High - Production-Ready System)

**Key Innovation:** Combining multiple MCP servers (HTTP and stdio-based), streaming responses, conversation persistence, and a modern web UI in a single integrated system.

---

## 📋 **Table of Contents**

1. [Strategic Planning](#1-strategic-planning)
2. [Architectural Reasoning](#2-architectural-reasoning)
3. [Design Decisions](#3-design-decisions)
4. [Implementation Strategy](#4-implementation-strategy)
5. [MCP Client Architecture](#5-mcp-client-architecture)
6. [Streaming Implementation](#6-streaming-implementation)
7. [Conversation Persistence](#7-conversation-persistence)
8. [Frontend Architecture](#8-frontend-architecture)
9. [Execution Graphs](#9-execution-graphs)
10. [Performed Steps](#10-performed-steps)
11. [Lessons Learned](#11-lessons-learned)

---

## 1. **Strategic Planning**

### **1.1 Problem Analysis**

**What are we building?**

A complete end-to-end AI agent system with:
- **Backend:** FastAPI server with MCP client integration
- **Frontend:** Modern web UI with real-time streaming
- **Storage:** Redis for conversation persistence
- **MCP Integration:** Support for both HTTP and stdio-based MCP servers
- **Tool Calling:** Dynamic tool discovery and execution

**Why is this challenging?**

1. **Multiple MCP Protocols**
   - HTTP-based MCP (UMS, Fetch)
   - Stdio-based MCP (DuckDuckGo via Docker)
   - Different connection patterns for each

2. **Streaming Complexity**
   - SSE (Server-Sent Events) format
   - Tool calls during streaming
   - Recursive streaming for tool results

3. **State Management**
   - Conversation persistence in Redis
   - Message history reconstruction
   - Conversation list ordering

4. **Frontend-Backend Sync**
   - Real-time UI updates
   - Conversation state synchronization
   - Error handling and recovery

### **1.2 Success Criteria**

**Must Have:**
- ✅ All 3 MCP clients implemented (HTTP, stdio)
- ✅ Streaming and non-streaming modes work
- ✅ Conversations persist in Redis
- ✅ Frontend displays conversations correctly
- ✅ Tool calls execute successfully
- ✅ UI updates in real-time during streaming

**Should Have:**
- ✅ Error handling for MCP failures
- ✅ Graceful degradation
- ✅ Clear error messages
- ✅ Performance optimization

**Could Have:**
- 🔄 Conversation search/filtering
- 🔄 Export conversations
- 🔄 Multi-user support
- 🔄 Rate limiting

### **1.3 Risk Assessment**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MCP connection failures | Medium | High | Retry logic, error handling |
| Redis connection loss | Low | High | Connection pooling, health checks |
| Streaming interruptions | Medium | Medium | Error recovery, state restoration |
| Frontend state desync | Medium | Medium | Proper state management |
| Tool execution errors | Medium | Low | Error messages, fallback |

---

## 2. **Architectural Reasoning**

### **2.1 Why MCP?**

**Model Context Protocol (MCP)** provides:
- **Standardized Tool Interface:** All tools follow same protocol
- **Multiple Transport Options:** HTTP, stdio, WebSocket
- **Tool Discovery:** Dynamic tool registration
- **Type Safety:** JSON Schema validation

**Alternative Considered:** Direct API calls to each service
**Rejected:** Would require custom integration for each service, no standardization

### **2.2 Why Redis for Persistence?**

**Redis Advantages:**
- **Fast:** In-memory storage for quick access
- **Sorted Sets:** Natural conversation ordering
- **TTL Support:** Can expire old conversations
- **Pub/Sub:** Future real-time features

**Alternative Considered:** PostgreSQL, SQLite
**Rejected:** Overkill for conversation storage, slower for simple key-value lookups

### **2.3 Why FastAPI?**

**FastAPI Advantages:**
- **Async Support:** Native async/await
- **Type Safety:** Pydantic models
- **Auto Documentation:** OpenAPI/Swagger
- **Performance:** Fast, modern framework

**Alternative Considered:** Flask, Django
**Rejected:** Less async support, heavier frameworks

### **2.4 Why SSE for Streaming?**

**Server-Sent Events Advantages:**
- **Simple:** Easier than WebSockets for one-way streaming
- **HTTP-based:** Works through proxies/firewalls
- **Automatic Reconnection:** Browser handles it
- **Text-based:** Easy to debug

**Alternative Considered:** WebSockets
**Rejected:** More complex, bidirectional when we only need one-way

---

## 3. **Design Decisions**

### **3.1 MCP Client Abstraction**

**Decision:** Separate classes for HTTP and stdio transports

**Rationale:**
- Different connection patterns
- Different lifecycle management
- Clear separation of concerns

**Implementation:**
```python
class HttpMCPClient:
    - Uses streamablehttp_client
    - Manages HTTP session
    - Handles SSE responses

class StdioMCPClient:
    - Uses stdio_client with Docker
    - Manages subprocess
    - Handles stdio streams
```

### **3.2 Tool Name to Client Mapping**

**Decision:** Dictionary mapping tool names to MCP clients

**Rationale:**
- Fast lookup O(1)
- Supports multiple MCP servers
- Easy to add new servers

**Implementation:**
```python
tool_name_client_map: dict[str, HttpMCPClient | StdioMCPClient] = {
    "get_user_by_id": ums_mcp_client,
    "duckduckgo_search": ddg_mcp_client,
    ...
}
```

### **3.3 Conversation Storage Structure**

**Decision:** JSON documents in Redis with sorted set for ordering

**Structure:**
```json
{
  "id": "uuid",
  "title": "Conversation title",
  "messages": [...],
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

**Rationale:**
- Flexible: Easy to add fields
- Human-readable: JSON format
- Efficient: Redis sorted sets for ordering

### **3.4 Message Model**

**Decision:** Pydantic model with role enum

**Rationale:**
- Type safety
- Validation
- Easy serialization

**Implementation:**
```python
class Message(BaseModel):
    role: Role
    content: str | None
    tool_call_id: str | None
    tool_calls: list[dict] | None
```

### **3.5 Streaming Tool Calls**

**Decision:** Collect tool calls during streaming, execute after stream completes

**Rationale:**
- Tool calls arrive incrementally
- Need complete tool call before execution
- Simpler than interleaving execution

**Flow:**
1. Stream content chunks
2. Collect tool call deltas
3. After stream: collect complete tool calls
4. Execute tools
5. Recursively stream tool results

---

## 4. **Implementation Strategy**

### **4.1 Bottom-Up Approach**

**Order:**
1. **MCP Clients** (foundation)
2. **DIAL Client** (orchestration)
3. **Conversation Manager** (state)
4. **FastAPI App** (API)
5. **Frontend** (UI)

**Rationale:** Each layer depends on previous, test incrementally

### **4.2 Testing Strategy**

**Level 1: Unit Tests**
- MCP client connection
- Tool calling
- Message serialization

**Level 2: Integration Tests**
- Full conversation flow
- Redis persistence
- Streaming

**Level 3: E2E Tests**
- Browser automation
- Full user workflows

---

## 5. **MCP Client Architecture**

### **5.1 HTTP MCP Client**

**Connection Flow:**
```
1. Create streamablehttp_client(url)
2. Enter context → get read_stream, write_stream
3. Create ClientSession(read_stream, write_stream)
4. Initialize session
5. Ready for tool calls
```

**Key Methods:**
- `connect()` - Establish connection
- `get_tools()` - Discover available tools
- `call_tool()` - Execute tool

**Error Handling:**
- Connection failures → Retry with exponential backoff
- Tool errors → Return error message

### **5.2 Stdio MCP Client**

**Connection Flow:**
```
1. Create StdioServerParameters(command="docker", args=[...])
2. Create stdio_client(server_params)
3. Enter context → get read_stream, write_stream
4. Create ClientSession(read_stream, write_stream)
5. Initialize session
6. Ready for tool calls
```

**Docker Integration:**
- Runs MCP server in Docker container
- Communicates via stdin/stdout
- Container lifecycle managed by stdio_client

**Key Difference:** Docker subprocess vs HTTP connection

### **5.3 Tool Format Conversion**

**MCP Format → DIAL Format:**
```python
# MCP Tool
{
  "name": "get_user_by_id",
  "description": "...",
  "inputSchema": {...}
}

# DIAL Tool (OpenAI compatible)
{
  "type": "function",
  "function": {
    "name": "get_user_by_id",
    "description": "...",
    "parameters": {...}
  }
}
```

**Rationale:** DIAL uses OpenAI-compatible format, MCP uses Anthropic format

---

## 6. **Streaming Implementation**

### **6.1 Streaming Flow**

```
User Message
    ↓
DIAL API (stream=True)
    ↓
Chunks arrive incrementally
    ↓
Yield SSE format: "data: {...}\n\n"
    ↓
If tool calls detected:
    ↓
Collect complete tool calls
    ↓
Execute tools
    ↓
Recursive stream_response() call
    ↓
Final chunk: "data: [DONE]\n\n"
```

### **6.2 Tool Call Collection**

**Challenge:** Tool calls arrive as deltas during streaming

**Solution:** Collect deltas, reconstruct complete calls

```python
tool_deltas = []
async for chunk in stream:
    if delta.tool_calls:
        tool_deltas.extend(delta.tool_calls)

# After stream completes
tool_calls = _collect_tool_calls(tool_deltas)
```

**Collection Algorithm:**
1. Group deltas by index
2. Accumulate id, name, arguments, type
3. Return complete tool calls

### **6.3 SSE Format**

**Format:**
```
data: {"choices": [{"delta": {"content": "..."}, "index": 0}]}\n\n
data: {"choices": [{"delta": {"content": "..."}, "index": 0}]}\n\n
data: {"choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]}\n\n
data: [DONE]\n\n
```

**Rationale:** OpenAI-compatible format for frontend compatibility

---

## 7. **Conversation Persistence**

### **7.1 Storage Strategy**

**Redis Keys:**
- `conversation:{id}` - Conversation JSON document
- `conversations:list` - Sorted set (score = timestamp)

**Operations:**
- **Create:** SET + ZADD
- **Read:** GET
- **Update:** SET + ZADD (update score)
- **Delete:** DEL + ZREM
- **List:** ZREVRANGE (sorted by timestamp)

### **7.2 Message History**

**Structure:**
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "tool_calls": [...]},
    {"role": "tool", "content": "...", "tool_call_id": "..."}
  ]
}
```

**Reconstruction:**
1. Load conversation from Redis
2. Deserialize messages
3. Recreate Message objects
4. Add system prompt if empty

### **7.3 Conversation Ordering**

**Sorted Set Score:** Unix timestamp

**Query:** `ZREVRANGE conversations:list 0 -1`

**Result:** Most recent conversations first

---

## 8. **Frontend Architecture**

### **8.1 State Management**

**Global State:**
```javascript
let currentConversationId = null;
let conversationHistory = [];
let isStreaming = false;
```

**Rationale:** Simple, sufficient for single-user app

### **8.2 Streaming UI Updates**

**Flow:**
1. User sends message
2. Create conversation if needed
3. Start SSE connection
4. Receive chunks incrementally
5. Update message bubble in real-time
6. Handle tool calls (if visible)
7. Save conversation on completion

**UI Updates:**
- Typing indicator while waiting
- Message bubble appears on first chunk
- Content updates incrementally
- Markdown rendering for assistant messages

### **8.3 Error Handling**

**Frontend Errors:**
- Network failures → Show error message
- Invalid responses → Log and display error
- Streaming interruptions → Show partial content

**Recovery:**
- Retry button for failed requests
- Conversation state preserved
- Can resume after errors

---

## 9. **Execution Graphs**

### **9.1 Complete User Flow**

```
┌─────────────────────────────────────────────────────────┐
│                    User Opens Browser                    │
│                    (index.html loads)                    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend: loadConversations()                │
│              GET /conversations                          │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Backend: list_conversations()               │
│              Redis: ZREVRANGE conversations:list         │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend: Render Conversation List          │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              User Types Message & Sends                  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Frontend: streamResponse(userMessage)            │
│         Create conversation if needed                     │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Backend: POST /conversations/{id}/chat           │
│         ConversationManager.chat()                       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Load conversation from Redis                     │
│         Reconstruct message history                      │
│         Add system prompt if empty                       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         DialClient.stream_response(messages)             │
│         DIAL API call (stream=True)                      │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Stream chunks arrive                             │
│         Yield SSE format                                 │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Tool calls detected?                              │
│         YES → Collect tool calls                         │
│         NO  → Continue streaming                         │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Execute tools via MCP clients                    │
│         Add tool messages to history                     │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Recursive stream_response() call                 │
│         Stream tool results                              │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Save conversation to Redis                       │
│         Update updated_at timestamp                      │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│         Frontend: Update UI                              │
│         Reload conversation list                         │
└─────────────────────────────────────────────────────────┘
```

### **9.2 Tool Execution Flow**

```
LLM decides to call tool
    ↓
Tool call delta arrives
    ↓
Collect complete tool call
    ↓
Lookup MCP client in tool_name_client_map
    ↓
Call mcp_client.call_tool(name, args)
    ↓
MCP server executes tool
    ↓
Return result
    ↓
Add tool message to conversation
    ↓
Continue LLM processing with tool result
```

---

## 10. **Performed Steps**

### **Step 1: Repository Setup**
```bash
cd C:\Users\AndreyPopov
git clone https://github.com/vospr/ai-dial-ums-ui-agent.git
cd ai-dial-ums-ui-agent
```

### **Step 2: Implement StdioMCPClient**
- Created `agent/clients/stdio_mcp_client.py`
- Implemented `create()` class method
- Implemented `connect()` with Docker stdio
- Implemented `get_tools()` with format conversion
- Implemented `call_tool()` with error handling

**Key Implementation:**
```python
server_params = StdioServerParameters(
    command="docker",
    args=["run", "--rm", "-i", self.docker_image]
)
self._stdio_context = stdio_client(server_params)
read_stream, write_stream, _ = await self._stdio_context.__aenter__()
```

### **Step 3: Implement DialClient**
- Created `agent/clients/dial_client.py`
- Implemented `__init__()` with AsyncAzureOpenAI
- Implemented `response()` for non-streaming
- Implemented `stream_response()` for streaming
- Implemented `_collect_tool_calls()` for delta aggregation
- Implemented `_call_tools()` for tool execution

**Key Features:**
- Tool call collection during streaming
- Recursive streaming for tool results
- Error handling for missing tools

### **Step 4: Implement ConversationManager**
- Created `agent/conversation_manager.py`
- Implemented `create_conversation()` with Redis storage
- Implemented `list_conversations()` with sorted set
- Implemented `get_conversation()` with JSON deserialization
- Implemented `delete_conversation()` with cleanup
- Implemented `chat()` with streaming/non-streaming modes
- Implemented `_stream_chat()` with SSE yield
- Implemented `_non_stream_chat()` with response dict
- Implemented `_save_conversation_messages()` with message serialization
- Implemented `_save_conversation()` with Redis persistence

**Key Features:**
- Conversation ID generation (UUID)
- Timestamp management
- Message history reconstruction
- System prompt injection

### **Step 5: Write System Prompt**
- Created `agent/prompts.py`
- Wrote comprehensive SYSTEM_PROMPT covering:
  - Role & Purpose
  - Core Capabilities
  - Behavioral Rules
  - Error Handling
  - Boundaries
  - Workflow Examples

**Key Elements:**
- User management focus
- Tool usage guidance
- Error handling instructions
- Example workflows

### **Step 6: Implement FastAPI App**
- Created `agent/app.py`
- Implemented `lifespan()` context manager:
  - Initialize 3 MCP clients (UMS, Fetch, DuckDuckGo)
  - Collect all tools
  - Create DialClient
  - Connect to Redis
  - Create ConversationManager
- Implemented CORS middleware
- Implemented endpoints:
  - `GET /health` - Health check
  - `POST /conversations` - Create conversation
  - `GET /conversations` - List conversations
  - `GET /conversations/{id}` - Get conversation
  - `DELETE /conversations/{id}` - Delete conversation
  - `POST /conversations/{id}/chat` - Chat endpoint

**Key Features:**
- Async startup/shutdown
- Error handling
- StreamingResponse for SSE
- Pydantic models for validation

### **Step 7: Implement Frontend**
- Updated `index.html` JavaScript:
  - `loadConversations()` - Fetch and render conversation list
  - `loadConversation()` - Load conversation messages
  - `deleteConversation()` - Delete with confirmation
  - `streamResponse()` - Handle streaming chat

**Key Features:**
- Real-time UI updates
- Markdown rendering
- Typing indicators
- Error handling
- Conversation state management

### **Step 8: Fix Message Serialization**
- Updated `conversation_manager.py` to use `to_dict()` instead of `model_dump()`
- Ensured compatibility with Message model

---

## 11. **Lessons Learned**

### **11.1 Technical Insights**

**1. MCP Protocol Flexibility**
- HTTP and stdio transports work seamlessly
- Tool format conversion is straightforward
- Error handling needs to be transport-specific

**2. Streaming Complexity**
- Tool calls during streaming require careful handling
- Delta collection is essential
- Recursive streaming maintains conversation flow

**3. Redis Persistence**
- Sorted sets perfect for conversation ordering
- JSON storage flexible for schema evolution
- Timestamp-based scoring works well

**4. Frontend State Management**
- Simple global state sufficient for MVP
- Real-time updates require careful state synchronization
- Error recovery improves UX significantly

**5. Async/Await Patterns**
- Context managers essential for resource cleanup
- Proper async handling prevents resource leaks
- Error propagation needs careful attention

### **11.2 Design Patterns**

**Pattern 1: Client Abstraction**
- Separate classes for different transports
- Common interface for tool calling
- Easy to add new MCP servers

**Pattern 2: Tool Mapping**
- Dictionary for O(1) lookup
- Supports multiple servers
- Clear ownership of tools

**Pattern 3: Conversation Lifecycle**
- Create → Chat → Update → Delete
- Timestamp-based ordering
- Message history reconstruction

**Pattern 4: Streaming with Tools**
- Collect → Execute → Recurse
- Maintains conversation flow
- Handles nested tool calls

### **11.3 What Could Be Improved**

**1. Error Recovery**
- Retry logic for MCP failures
- Partial conversation recovery
- Better error messages

**2. Performance**
- Connection pooling for MCP clients
- Redis pipelining for batch operations
- Frontend caching

**3. Features**
- Conversation search/filtering
- Export conversations
- Multi-user support
- Rate limiting

**4. Testing**
- Unit tests for all components
- Integration tests for flows
- E2E tests with browser automation

**5. Monitoring**
- Logging improvements
- Metrics collection
- Health check enhancements

---

## 🎯 **Conclusion**

**UMS UI Agent** represents a complete production-ready AI agent system with:
- ✅ Multiple MCP server integration
- ✅ Streaming and non-streaming modes
- ✅ Redis-backed conversation persistence
- ✅ Modern web UI with real-time updates
- ✅ Comprehensive error handling
- ✅ Clean architecture and separation of concerns

**Key Innovation:** Seamless integration of HTTP and stdio MCP transports in a single system.

**Complexity Cost:** Streaming with tool calls requires careful state management.

**Ideal Use Case:** Production user management systems requiring AI assistance with persistent conversation history.

---

**Next:** See [Implementation.md](Implementation.md) for step-by-step setup and testing instructions.


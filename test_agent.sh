#!/bin/bash

echo "🧪 Testing UMS UI Agent"
echo "======================"

# Test 1: Health Check
echo ""
echo "1. Testing health endpoint..."
HEALTH=$(curl -s http://localhost:8011/health 2>&1)
if echo "$HEALTH" | grep -q "healthy"; then
    echo "   ✅ Agent is healthy"
    echo "   Response: $HEALTH"
else
    echo "   ❌ Agent health check failed"
    echo "   Response: $HEALTH"
    echo ""
    echo "   Trying to start agent..."
    cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent
    source .venv/bin/activate
    export DIAL_API_KEY='dial-fxbasxs2h6t7brhnbqs36omhe2y'
    export ORCHESTRATION_MODEL='gpt-4o'
    nohup python run_agent.py > agent.log 2>&1 &
    echo "   Agent starting in background. Wait 10 seconds and run this test again."
    exit 1
fi

# Test 2: Create Conversation
echo ""
echo "2. Testing conversation creation..."
CONV_RESPONSE=$(curl -s -X POST http://localhost:8011/conversations \
    -H "Content-Type: application/json" \
    -d '{"title":"Test Conversation"}' 2>&1)

if echo "$CONV_RESPONSE" | grep -q "id"; then
    CONV_ID=$(echo "$CONV_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "None" ]; then
        echo "   ✅ Conversation created: $CONV_ID"
    else
        echo "   ⚠️  Conversation created but ID extraction failed"
        echo "   Response: $CONV_RESPONSE"
    fi
else
    echo "   ❌ Failed to create conversation"
    echo "   Response: $CONV_RESPONSE"
    exit 1
fi

# Test 3: Send Message (Non-streaming)
if [ -n "$CONV_ID" ] && [ "$CONV_ID" != "None" ]; then
    echo ""
    echo "3. Testing message sending..."
    MESSAGE_RESPONSE=$(curl -s -X POST "http://localhost:8011/conversations/$CONV_ID/chat" \
        -H "Content-Type: application/json" \
        -d '{"message":{"role":"user","content":"Hello"},"stream":false}' 2>&1)

    if echo "$MESSAGE_RESPONSE" | grep -q "content"; then
        echo "   ✅ Message sent successfully"
        CONTENT_PREVIEW=$(echo "$MESSAGE_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('content', '')[:80])" 2>/dev/null || echo "Response received")
        echo "   Response preview: $CONTENT_PREVIEW..."
    else
        echo "   ⚠️  Message sent but response format unexpected"
        echo "   Response: $MESSAGE_RESPONSE"
    fi
fi

echo ""
echo "✅ Basic tests completed!"
echo ""
echo "Next steps:"
echo "1. Open UI: file:///C:/Users/AndreyPopov/ai-dial-ums-ui-agent/index.html"
echo "2. Try: 'Search for users named John'"
echo "3. Check logs: tail -f agent.log"


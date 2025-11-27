#!/bin/bash

cd /mnt/c/Users/AndreyPopov/ai-dial-ums-ui-agent || exit 1

echo "=========================================="
echo "🌐 Starting HTTP Server for UMS UI Agent"
echo "=========================================="
echo ""
echo "📁 Serving directory: $(pwd)"
echo "🔗 Local access: http://localhost:8080/index_network.html"
echo "🌍 Network access: http://192.168.8.8:8080/index_network.html"
echo ""
echo "⚠️  Make sure:"
echo "   1. Agent is running on port 8011"
echo "   2. Windows Firewall allows port 8080 and 8011"
echo "   3. Agent API URL in index_network.html is: http://192.168.8.8:8011"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

python3 serve_ui.py


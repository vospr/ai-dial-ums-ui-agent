#!/usr/bin/env python3
import os
import sys

# Set environment variables
os.environ['DIAL_API_KEY'] = 'dial-fxbasxs2h6t7brhnbqs36omhe2y'
os.environ['ORCHESTRATION_MODEL'] = 'gpt-4o'
os.environ['DIAL_URL'] = 'https://ai-proxy.lab.epam.com'
os.environ['UMS_MCP_URL'] = 'http://localhost:8005/mcp'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from agent.app import app
        import uvicorn
        print("Starting UMS Agent server on http://0.0.0.0:8011")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8011,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting agent: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


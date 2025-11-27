#!/usr/bin/env python3
"""
Simple HTTP server to serve the UI
Allows network access to the chat interface
"""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys

PORT = 8080
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Enable CORS for network access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Custom logging
        sys.stderr.write("%s - - [%s] %s\n" %
                        (self.address_string(),
                         self.log_date_time_string(),
                         format%args))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        server_address = httpd.server_address[0]
        print("=" * 60)
        print("🌐 UMS UI Agent - HTTP Server")
        print("=" * 60)
        print(f"📁 Serving directory: {DIRECTORY}")
        print(f"🔗 Local access: http://localhost:{PORT}/index_network.html")
        print(f"🌍 Network access: http://192.168.8.8:{PORT}/index_network.html")
        print("")
        print("⚠️  Note: Agent API must be running on port 8011")
        print("⚠️  Network version configured for IP: 192.168.8.8")
        print("")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        try:
            # Try to open browser automatically
            webbrowser.open(f'http://localhost:{PORT}/index_network.html')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")


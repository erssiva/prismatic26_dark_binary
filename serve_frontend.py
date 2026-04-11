#!/usr/bin/env python3
"""
Simple HTTP Server for serving the frontend UI
Serves on http://localhost:5000
"""

import http.server
import socketserver
import os

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow communication with API on port 8000
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"")
        print(f"╔════════════════════════════════════════════╗")
        print(f"║     Frontend Server Running                ║")
        print(f"║                                            ║")
        print(f"║   Open in Browser:                         ║")
        print(f"║   http://localhost:{PORT}                  ║")
        print(f"║                                            ║")
        print(f"║   API Server (backend): port 8000          ║")
        print(f"║   Press Ctrl+C to stop                     ║")
        print(f"╚════════════════════════════════════════════╝")
        print(f"")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

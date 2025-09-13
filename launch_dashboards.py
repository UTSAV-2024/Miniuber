#!/usr/bin/env python3
"""
Multi-port server setup for Mini Uber dashboards
Runs user, driver, and admin dashboards on different ports
"""

import subprocess
import time
import threading
import webbrowser
from pathlib import Path
import signal
import sys
import os

class DashboardServer:
    def __init__(self):
        self.processes = []
        self.ports = {
            'api': 8000,      # Main API server
            'user': 8001,     # User dashboard
            'driver': 8002,   # Driver dashboard  
            'admin': 8003     # Admin dashboard
        }
        
    def create_server_file(self, dashboard_type, port, html_file):
        """Create a simple HTTP server file for each dashboard"""
        server_content = f'''#!/usr/bin/env python3
"""
{dashboard_type.title()} Dashboard Server - Port {port}
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/{html_file}'
        return super().do_GET()

def start_server():
    server = HTTPServer(('localhost', {port}), CORSRequestHandler)
    print(f"🚀 {dashboard_type.title()} Dashboard running at http://localhost:{port}")
    
    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\\n{dashboard_type.title()} dashboard server stopped.")
        server.shutdown()

if __name__ == "__main__":
    start_server()
'''
        
        filename = f"{dashboard_type}_server.py"
        with open(filename, 'w') as f:
            f.write(server_content)
        
        # Make executable
        os.chmod(filename, 0o755)
        return filename
    
    def start_api_server(self):
        """Start the main FastAPI server"""
        print(f"🔧 Starting API server on port {self.ports['api']}...")
        
        # Check if main.py exists
        if not Path('main.py').exists():
            print("❌ main.py not found! Make sure you're in the correct directory.")
            return None
            
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'main:app',
            '--host', '0.0.0.0',
            '--port', str(self.ports['api']),
            '--reload'
        ])
        
        return process
    
    def start_dashboard_server(self, dashboard_type, html_file):
        """Start a dashboard server"""
        port = self.ports[dashboard_type]
        
        # Check if HTML file exists
        if not Path(html_file).exists():
            print(f"❌ {html_file} not found!")
            return None
        
        print(f"🌐 Starting {dashboard_type} dashboard on port {port}...")
        
        # Create server file
        server_file = self.create_server_file(dashboard_type, port, html_file)
        
        # Start server
        process = subprocess.Popen([sys.executable, server_file])
        
        return process
    
    def start_all_servers(self):
        """Start all servers"""
        print("🚀 Starting Mini Uber Multi-Dashboard System...")
        print("=" * 50)
        
        # Start API server first
        api_process = self.start_api_server()
        if api_process:
            self.processes.append(('API Server', api_process))
            time.sleep(3)  # Wait for API to start
        
        # Start dashboard servers
        dashboards = [
            ('user', 'user_dashboard.html'),
            ('driver', 'driver_dashboard.html'), 
            ('admin', 'admin_dashboard.html')
        ]
        
        for dashboard_type, html_file in dashboards:
            process = self.start_dashboard_server(dashboard_type, html_file)
            if process:
                self.processes.append((f"{dashboard_type.title()} Dashboard", process))
                time.sleep(1)
        
        print("\\n" + "=" * 50)
        print("🎉 All servers started successfully!")
        print("\\n📱 Access your dashboards:")
        print(f"   👤 User Dashboard:   http://localhost:{self.ports['user']}")
        print(f"   🚗 Driver Dashboard: http://localhost:{self.ports['driver']}")  
        print(f"   👨‍💼 Admin Dashboard:  http://localhost:{self.ports['admin']}")
        print(f"   🔧 API Server:       http://localhost:{self.ports['api']}")
        print("\\n📝 API Documentation: http://localhost:8000/docs")
        print("\\n⚠️  Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Wait for user interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all_servers()
    
    def stop_all_servers(self):
        """Stop all servers gracefully"""
        print("\\n🛑 Stopping all servers...")
        
        for name, process in self.processes:
            try:
                print(f"   Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"   Error stopping {name}: {e}")
        
        # Clean up server files
        server_files = ['user_server.py', 'driver_server.py', 'admin_server.py']
        for file in server_files:
            try:
                if Path(file).exists():
                    os.remove(file)
            except Exception as e:
                print(f"   Error removing {file}: {e}")
        
        print("✅ All servers stopped successfully!")

def main():
    print("🚀 Mini Uber Multi-Dashboard Launcher")
    print("=" * 40)
    
    # Check required files
    required_files = [
        'main.py',
        'database.py', 
        'user_dashboard.html',
        'driver_dashboard.html',
        'admin_dashboard.html'
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\\nPlease ensure all files are in the current directory.")
        return
    
    print("✅ All required files found!")
    print("\\n🔄 Starting servers...")
    
    server = DashboardServer()
    server.start_all_servers()

if __name__ == "__main__":
    main()
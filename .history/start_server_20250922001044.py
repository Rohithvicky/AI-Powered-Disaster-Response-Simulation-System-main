#!/usr/bin/env python3
"""
AI Disaster Response Simulation Server Startup Script
"""
import uvicorn
from server import app

if __name__ == "__main__":
    print("🚀 Starting AI Disaster Response Simulation Server...")
    print("📊 Professional Dashboard: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("⚡ Server running on http://127.0.0.1:8000")
    print("🔄 Auto-reload enabled - server will restart on file changes")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "server:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
"""
AI Disaster Response Simulation Server Startup Script
"""
import uvicorn
from server import app

if __name__ == "__main__":
    print("🚀 Starting AI Disaster Response Simulation Server...")
    print("📊 Professional Dashboard: http://localhost:8000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("⚡ Server running on http://127.0.0.1:8000")
    print("🔄 Auto-reload enabled - server will restart on file changes")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "server:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

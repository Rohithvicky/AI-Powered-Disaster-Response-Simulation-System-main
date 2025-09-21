#!/usr/bin/env python3
"""
Simple startup script for the AI Disaster Response Simulation System
"""

import sys
import os
import subprocess

def main():
    print("🚀 AI Disaster Response Simulation System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("server.py"):
        print("❌ Error: server.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Check if web directory exists
    if not os.path.exists("web"):
        print("❌ Error: web directory not found. Please ensure all files are present.")
        sys.exit(1)
    
    print("✅ All files found. Starting server...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔧 API docs will be available at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([sys.executable, "server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
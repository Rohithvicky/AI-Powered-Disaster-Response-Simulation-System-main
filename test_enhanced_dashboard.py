#!/usr/bin/env python3
"""
Test script for the Enhanced AI Disaster Response Simulation Dashboard
Tests the web interface and API endpoints
"""

import requests
import json
import time
import webbrowser
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoints():
    """Test all API endpoints"""
    print("🚀 Testing Enhanced Dashboard API Endpoints...")
    
    # Test state endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/state")
        if response.status_code == 200:
            data = response.json()
            print("✅ /api/state - Working")
            print(f"   Grid size: {data['state']['grid_size']}")
            print(f"   Victims: {len(data['state']['victims'])}")
            print(f"   Hazards: {len(data['state']['hazards'])}")
        else:
            print(f"❌ /api/state - Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/state - Error: {e}")
    
    # Test telemetry endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/telemetry")
        if response.status_code == 200:
            data = response.json()
            print("✅ /api/telemetry - Working")
            print(f"   Risk history: {len(data.get('risk_history', []))} points")
        else:
            print(f"❌ /api/telemetry - Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/telemetry - Error: {e}")
    
    # Test reset endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/reset")
        if response.status_code == 200:
            print("✅ /api/reset - Working")
        else:
            print(f"❌ /api/reset - Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/reset - Error: {e}")
    
    # Test step endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/step")
        if response.status_code == 200:
            data = response.json()
            print("✅ /api/step - Working")
            print(f"   Time step: {data['state']['time_step']}")
        else:
            print(f"❌ /api/step - Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/step - Error: {e}")
    
    # Test recommend path endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/recommend_path")
        if response.status_code == 200:
            data = response.json()
            print("✅ /api/recommend_path - Working")
            print(f"   Path length: {data.get('length', 0)}")
        else:
            print(f"❌ /api/recommend_path - Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/recommend_path - Error: {e}")
    
    # Test legend endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/legend")
        if response.status_code == 200:
            data = response.json()
            print("✅ /api/legend - Working")
            print(f"   Terrain types: {len(data.get('terrain', {}))}")
        else:
            print(f"❌ /api/legend - Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ /api/legend - Error: {e}")

def test_simulation_flow():
    """Test complete simulation flow"""
    print("\n🔄 Testing Simulation Flow...")
    
    # Reset simulation
    try:
        response = requests.post(f"{BASE_URL}/api/reset")
        if response.status_code != 200:
            print("❌ Cannot reset simulation")
            return
        print("✅ Simulation reset")
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return
    
    # Run a few steps
    for i in range(3):
        try:
            response = requests.post(f"{BASE_URL}/api/step")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Step {i+1}: Time {data['state']['time_step']}, Victims saved: {data['stats']['victims_saved']}")
            else:
                print(f"❌ Step {i+1} failed")
                break
        except Exception as e:
            print(f"❌ Step {i+1} error: {e}")
            break
    
    # Get final summary
    try:
        response = requests.get(f"{BASE_URL}/api/summary")
        if response.status_code == 200:
            data = response.json()
            print("✅ Summary generated")
            print(f"   Final efficiency: {data.get('efficiency_score', 0):.3f}")
        else:
            print("❌ Summary failed")
    except Exception as e:
        print(f"❌ Summary error: {e}")

def check_web_interface():
    """Check if web interface is accessible"""
    print("\n🌐 Checking Web Interface...")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Web interface accessible")
            print("   Opening dashboard in browser...")
            webbrowser.open(BASE_URL)
        else:
            print(f"❌ Web interface returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("🚨 Enhanced AI Disaster Response Simulation Dashboard Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/state", timeout=5)
        print("✅ Server is running and responding")
    except Exception as e:
        print("❌ Server is not responding")
        print("   Please start the server with:")
        print("   python -m uvicorn web_server:app --host 127.0.0.1 --port 8000")
        return
    
    # Run tests
    test_api_endpoints()
    test_simulation_flow()
    check_web_interface()
    
    print("\n" + "=" * 60)
    print("🎯 Test Complete!")
    print("   The enhanced dashboard should now be open in your browser")
    print("   Features to test:")
    print("   - Modern glassmorphism design")
    print("   - Enhanced charts with animations")
    print("   - Professional metrics cards")
    print("   - Responsive layout")
    print("   - Tabbed chart interface")
    print("=" * 60)

if __name__ == "__main__":
    main()
